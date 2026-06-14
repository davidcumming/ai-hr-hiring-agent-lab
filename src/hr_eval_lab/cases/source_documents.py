"""Deterministic source-document registry over the workflow storage seam."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal, cast

from hr_eval_lab.cases.service import HR_WORKFLOW_ROLE, RecruitmentCaseService
from hr_eval_lab.domain import ids
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    CaseNextAction,
    SourceDocumentGetResult,
    SourceDocumentListResult,
    SourceDocumentRegisterRequest,
    SourceDocumentRegistrationResult,
    SourceDocumentSummary,
)
from hr_eval_lab.domain.schemas.workflow import (
    CaseEvent,
    CaseTask,
    RecruitmentCase,
    SourceDocument,
    WorkflowGate,
)
from hr_eval_lab.domain.schemas.workflow_artifacts import role_source_raw_path
from hr_eval_lab.persistence.workflow_storage import WorkflowStorageBackend

SourceDocumentError = Literal["unknown_case_id", "unknown_document_id"]
SourceDocumentResult = (
    SourceDocumentRegistrationResult | SourceDocumentListResult | SourceDocumentGetResult
)


@dataclass(frozen=True)
class SourceDocumentSnapshot:
    case_id: str | None = None
    correlation_id: str | None = None
    result: SourceDocumentResult | None = None
    next_actions: list[CaseNextAction] = field(default_factory=list)
    error: SourceDocumentError | None = None


class SourceDocumentService:
    """Source-document intake logic over ``WorkflowStorageBackend`` only."""

    def __init__(
        self,
        storage: WorkflowStorageBackend,
        *,
        document_id_fn: Callable[[], str] = ids.new_document_id,
        event_id_fn: Callable[[], str] = ids.new_event_id,
        now_fn: Callable[[], str] = ids.utc_now_iso,
    ) -> None:
        self._storage = storage
        self._document_id_fn = document_id_fn
        self._event_id_fn = event_id_fn
        self._now_fn = now_fn

    def register_document(
        self,
        case_id: str,
        request: SourceDocumentRegisterRequest,
        actor: ActorContext,
    ) -> SourceDocumentSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return SourceDocumentSnapshot(error="unknown_case_id")

        created_at = self._now_fn()
        document_id = self._document_id_fn()
        event_id = self._event_id_fn()
        blob_path = role_source_raw_path(case_id, document_id)
        blob_ref = self._storage.write_blob_artifact(
            blob_path,
            request.content_text.encode("utf-8"),
        )

        document = SourceDocument(
            PartitionKey=case_id,
            RowKey=f"doc#{document_id}",
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case_id,
            document_id=document_id,
            document_type=request.document_type,
            source_label=request.source_label,
            source_origin=request.source_origin,
            blob_path=blob_ref.blob_path,
            mime_type=request.mime_type,
            file_name=request.file_name,
            size_bytes=blob_ref.size_bytes,
            sha256=blob_ref.sha256,
            processing_status="registered",
            version="v1",
            synthetic=True,
        )
        self._storage.upsert_table_entity(document)

        event = CaseEvent(
            PartitionKey=case_id,
            RowKey=f"{created_at}#{event_id}",
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case_id,
            event_id=event_id,
            event_type="source_document_registered",
            actor_id=actor.actor_id,
            actor_role=HR_WORKFLOW_ROLE,
            artifact_id=document_id,
            artifact_version=document.version,
            summary="Source document registered.",
            safe_details={
                "document_id": document_id,
                "document_type": request.document_type,
                "source_origin": request.source_origin,
                "source_label": request.source_label,
                "file_name": request.file_name,
                "mime_type": request.mime_type,
                "blob_path": blob_ref.blob_path,
                "sha256": blob_ref.sha256,
                "size_bytes": blob_ref.size_bytes,
                "synthetic": True,
                "processing_status": document.processing_status,
            },
        )
        self._storage.upsert_table_entity(event)
        self._complete_source_document_task_and_gate(
            case_id=case_id,
            updated_at=created_at,
            actor=actor,
            event_id=event_id,
        )

        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during document intake")
        documents = self._list_document_entities(case_id)
        return SourceDocumentSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=SourceDocumentRegistrationResult(
                case=case_snapshot.result.case,
                document=self._document_summary(document),
                documents_count=len(documents),
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def list_documents(self, case_id: str) -> SourceDocumentSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return SourceDocumentSnapshot(error="unknown_case_id")
        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return SourceDocumentSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=SourceDocumentListResult(
                case_id=case_id,
                documents=[
                    self._document_summary(document)
                    for document in self._list_document_entities(case_id)
                ],
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def get_document(self, case_id: str, document_id: str) -> SourceDocumentSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return SourceDocumentSnapshot(error="unknown_case_id")
        document = cast(
            SourceDocument | None,
            self._storage.get_table_entity(
                SourceDocument,
                case_id,
                f"doc#{document_id}",
            ),
        )
        if document is None:
            return SourceDocumentSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unknown_document_id",
            )
        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return SourceDocumentSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=SourceDocumentGetResult(
                case_id=case_id,
                document=self._document_summary(document),
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def _get_case(self, case_id: str) -> RecruitmentCase | None:
        return cast(
            RecruitmentCase | None,
            self._storage.get_table_entity(RecruitmentCase, case_id, "case"),
        )

    def _case_snapshot(self, case_id: str):
        return RecruitmentCaseService(self._storage).get_case(case_id)

    def _list_document_entities(self, case_id: str) -> list[SourceDocument]:
        return [
            cast(SourceDocument, row)
            for row in sorted(
                self._storage.list_table_entities(SourceDocument, partition_key=case_id),
                key=lambda row: row.RowKey,
            )
        ]

    def _complete_source_document_task_and_gate(
        self,
        *,
        case_id: str,
        updated_at: str,
        actor: ActorContext,
        event_id: str,
    ) -> None:
        task = cast(
            CaseTask | None,
            self._storage.get_table_entity(
                CaseTask,
                case_id,
                "task#attach_source_documents",
            ),
        )
        if task is not None and task.status in {"open", "blocked"}:
            self._storage.upsert_table_entity(
                task.model_copy(
                    update={
                        "status": "completed",
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                        "completion_event_id": event_id,
                    }
                )
            )

        gate = cast(
            WorkflowGate | None,
            self._storage.get_table_entity(
                WorkflowGate,
                case_id,
                "gate#source_documents_required",
            ),
        )
        if gate is not None and gate.gate_status not in {"satisfied", "waived"}:
            self._storage.upsert_table_entity(
                gate.model_copy(
                    update={
                        "gate_status": "satisfied",
                        "blocking_reasons": [],
                        "last_checked_at": updated_at,
                        "satisfied_by_event_id": event_id,
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                    }
                )
            )

    def _document_summary(self, document: SourceDocument) -> SourceDocumentSummary:
        return SourceDocumentSummary(
            document_id=document.document_id,
            document_type=document.document_type,
            source_origin=document.source_origin,
            source_label=document.source_label,
            blob_path=document.blob_path,
            mime_type=document.mime_type,
            file_name=document.file_name,
            size_bytes=document.size_bytes if document.size_bytes is not None else 0,
            sha256=document.sha256,
            processing_status=document.processing_status,
            version=document.version,
            created_at=document.created_at,
            synthetic=document.synthetic,
        )
