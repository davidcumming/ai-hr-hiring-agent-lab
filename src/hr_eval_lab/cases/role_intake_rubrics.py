"""Deterministic role-intake and rubric services for the E11 facade."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal, cast

from hr_eval_lab.cases.service import HR_WORKFLOW_ROLE, RecruitmentCaseService
from hr_eval_lab.domain import ids
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    ApprovedRubricRegisterRequest,
    CaseNextAction,
    RoleIntakeArtifactResult,
    RoleIntakeCreateRequest,
    RoleIntakeGetResult,
    RubricArtifactResult,
    RubricGetResult,
    RubricListResult,
    WorkflowArtifactSummary,
)
from hr_eval_lab.domain.schemas.workflow import (
    Approval,
    ArtifactVersion,
    CaseEvent,
    CaseTask,
    RecruitmentCase,
    SourceDocument,
    WorkflowGate,
)
from hr_eval_lab.domain.schemas.workflow_artifacts import (
    role_intake_artifact_path,
    rubric_artifact_path,
)
from hr_eval_lab.persistence.workflow_storage import WorkflowStorageBackend

RoleIntakeRubricError = Literal[
    "unknown_case_id",
    "source_documents_required",
    "unknown_source_document_id",
    "role_intake_version_exists",
    "role_intake_not_found",
    "rubric_version_exists",
    "unknown_rubric_version",
    "approved_by_actor_mismatch",
]

RoleIntakeRubricResult = (
    RoleIntakeArtifactResult
    | RoleIntakeGetResult
    | RubricArtifactResult
    | RubricListResult
    | RubricGetResult
)

ROLE_INTAKE_ARTIFACT_ID = "role_intake"
ROLE_INTAKE_ARTIFACT_TYPE = "role_intake"
RUBRIC_ARTIFACT_ID = "screening_rubric"
RUBRIC_ARTIFACT_TYPE = "screening_rubric"


@dataclass(frozen=True)
class RoleIntakeRubricSnapshot:
    case_id: str | None = None
    correlation_id: str | None = None
    result: RoleIntakeRubricResult | None = None
    next_actions: list[CaseNextAction] = field(default_factory=list)
    error: RoleIntakeRubricError | None = None


class RoleIntakeRubricService:
    """Role-intake and approved-rubric logic over ``WorkflowStorageBackend``."""

    def __init__(
        self,
        storage: WorkflowStorageBackend,
        *,
        approval_id_fn: Callable[[], str] = ids.new_approval_id,
        event_id_fn: Callable[[], str] = ids.new_event_id,
        now_fn: Callable[[], str] = ids.utc_now_iso,
    ) -> None:
        self._storage = storage
        self._approval_id_fn = approval_id_fn
        self._event_id_fn = event_id_fn
        self._now_fn = now_fn

    def create_role_intake(
        self,
        case_id: str,
        request: RoleIntakeCreateRequest,
        actor: ActorContext,
    ) -> RoleIntakeRubricSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return RoleIntakeRubricSnapshot(error="unknown_case_id")

        source_documents = self._resolve_source_documents(case_id, request)
        if source_documents is None:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unknown_source_document_id",
            )
        if not source_documents:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="source_documents_required",
            )

        version = request.intake_version
        row_key = self._artifact_row_key(ROLE_INTAKE_ARTIFACT_TYPE, version)
        if self._storage.get_table_entity(ArtifactVersion, case_id, row_key) is not None:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="role_intake_version_exists",
            )

        created_at = self._now_fn()
        event_id = self._event_id_fn()
        blob_path = role_intake_artifact_path(case_id, version)
        source_document_ids = [document.document_id for document in source_documents]
        payload = {
            "artifact_type": ROLE_INTAKE_ARTIFACT_TYPE,
            "case_id": case_id,
            "version": version,
            "intake_title": request.intake_title,
            "role_purpose": request.role_purpose,
            "responsibilities": request.responsibilities,
            "required_qualifications": request.required_qualifications,
            "preferred_qualifications": request.preferred_qualifications,
            "business_context": request.business_context,
            "role_risks": request.role_risks,
            "open_questions": request.open_questions,
            "source_document_ids": source_document_ids,
            "source_documents": [
                self._safe_source_document_ref(document)
                for document in source_documents
            ],
            "created_at": created_at,
            "created_by_actor_id": actor.actor_id,
            "created_by_role": HR_WORKFLOW_ROLE,
            "synthetic": True,
        }
        blob_ref = self._storage.write_blob_artifact(blob_path, payload)
        self._supersede_prior_artifacts(
            case_id=case_id,
            artifact_type=ROLE_INTAKE_ARTIFACT_TYPE,
            new_version=version,
            updated_at=created_at,
            actor=actor,
        )

        artifact = ArtifactVersion(
            PartitionKey=case_id,
            RowKey=row_key,
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case_id,
            artifact_id=ROLE_INTAKE_ARTIFACT_ID,
            artifact_type=ROLE_INTAKE_ARTIFACT_TYPE,
            version=version,
            status="approved",
            blob_path=blob_ref.blob_path,
            source_document_ids=source_document_ids,
            sha256=blob_ref.sha256,
            approved_version_required=True,
            synthetic=True,
        )
        self._storage.upsert_table_entity(artifact)

        self._storage.upsert_table_entity(
            CaseEvent(
                PartitionKey=case_id,
                RowKey=f"{created_at}#{event_id}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=case.correlation_id,
                case_id=case_id,
                event_id=event_id,
                event_type="role_intake_artifact_created",
                actor_id=actor.actor_id,
                actor_role=HR_WORKFLOW_ROLE,
                artifact_id=ROLE_INTAKE_ARTIFACT_ID,
                artifact_version=version,
                summary="Role intake artifact created.",
                safe_details={
                    "artifact_type": ROLE_INTAKE_ARTIFACT_TYPE,
                    "artifact_id": ROLE_INTAKE_ARTIFACT_ID,
                    "version": version,
                    "blob_path": blob_ref.blob_path,
                    "sha256": blob_ref.sha256,
                    "source_document_ids": source_document_ids,
                    "synthetic": True,
                },
            )
        )
        self._storage.upsert_table_entity(
            case.model_copy(
                update={
                    "active_intake_version": version,
                    "updated_at": created_at,
                    "updated_by_actor_id": actor.actor_id,
                    "updated_by_role": HR_WORKFLOW_ROLE,
                }
            )
        )
        self._complete_task_and_gate(
            case_id=case_id,
            task_row_key="task#complete_role_intake",
            gate_row_key="gate#role_intake_required",
            updated_at=created_at,
            actor=actor,
            event_id=event_id,
        )

        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during role intake")
        return RoleIntakeRubricSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=RoleIntakeArtifactResult(
                case=case_snapshot.result.case,
                artifact=self._artifact_summary(artifact),
                role_intake=payload,
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def get_role_intake(self, case_id: str) -> RoleIntakeRubricSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return RoleIntakeRubricSnapshot(error="unknown_case_id")
        if case.active_intake_version is None:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="role_intake_not_found",
            )
        artifact = self._get_artifact(
            case_id,
            ROLE_INTAKE_ARTIFACT_TYPE,
            case.active_intake_version,
        )
        payload = self._read_artifact_json(artifact)
        if artifact is None or payload is None:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="role_intake_not_found",
            )
        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return RoleIntakeRubricSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=RoleIntakeGetResult(
                case_id=case_id,
                artifact=self._artifact_summary(artifact),
                role_intake=payload,
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def register_rubric(
        self,
        case_id: str,
        request: ApprovedRubricRegisterRequest,
        actor: ActorContext,
    ) -> RoleIntakeRubricSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return RoleIntakeRubricSnapshot(error="unknown_case_id")
        if (
            request.approved_by_actor_id is not None
            and request.approved_by_actor_id != actor.actor_id
        ):
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="approved_by_actor_mismatch",
            )

        version = request.rubric_version
        row_key = self._artifact_row_key(RUBRIC_ARTIFACT_TYPE, version)
        if self._storage.get_table_entity(ArtifactVersion, case_id, row_key) is not None:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="rubric_version_exists",
            )

        created_at = self._now_fn()
        event_id = self._event_id_fn()
        approval_id = self._approval_id_fn()
        blob_path = rubric_artifact_path(case_id, version)
        payload = {
            "artifact_type": RUBRIC_ARTIFACT_TYPE,
            "case_id": case_id,
            "rubric_title": request.rubric_title,
            "rubric_version": version,
            "criteria": [
                criterion.model_dump(mode="json") for criterion in request.criteria
            ],
            "approved_by_actor_id": actor.actor_id,
            "approved_by_role": HR_WORKFLOW_ROLE,
            "approved_at": created_at,
            "synthetic": True,
        }
        blob_ref = self._storage.write_blob_artifact(blob_path, payload)
        self._supersede_prior_artifacts(
            case_id=case_id,
            artifact_type=RUBRIC_ARTIFACT_TYPE,
            new_version=version,
            updated_at=created_at,
            actor=actor,
        )

        artifact = ArtifactVersion(
            PartitionKey=case_id,
            RowKey=row_key,
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case_id,
            artifact_id=RUBRIC_ARTIFACT_ID,
            artifact_type=RUBRIC_ARTIFACT_TYPE,
            version=version,
            status="approved",
            blob_path=blob_ref.blob_path,
            source_document_ids=[],
            sha256=blob_ref.sha256,
            approved_version_required=True,
            synthetic=True,
        )
        self._storage.upsert_table_entity(artifact)

        self._storage.upsert_table_entity(
            Approval(
                PartitionKey=case_id,
                RowKey=f"approval#{approval_id}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=case.correlation_id,
                case_id=case_id,
                approval_id=approval_id,
                artifact_id=RUBRIC_ARTIFACT_ID,
                artifact_type=RUBRIC_ARTIFACT_TYPE,
                artifact_version=version,
                actor_id=actor.actor_id,
                actor_role=HR_WORKFLOW_ROLE,
                decision="approved",
                comments="Single synthetic HR lab approval recorded by E11.",
                decided_at=created_at,
                synthetic=True,
            )
        )
        self._storage.upsert_table_entity(
            CaseEvent(
                PartitionKey=case_id,
                RowKey=f"{created_at}#{event_id}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=case.correlation_id,
                case_id=case_id,
                event_id=event_id,
                event_type="rubric_approved",
                actor_id=actor.actor_id,
                actor_role=HR_WORKFLOW_ROLE,
                artifact_id=RUBRIC_ARTIFACT_ID,
                artifact_version=version,
                summary="Screening rubric approved.",
                safe_details={
                    "artifact_type": RUBRIC_ARTIFACT_TYPE,
                    "artifact_id": RUBRIC_ARTIFACT_ID,
                    "rubric_version": version,
                    "approval_id": approval_id,
                    "blob_path": blob_ref.blob_path,
                    "sha256": blob_ref.sha256,
                    "criteria_count": len(request.criteria),
                    "synthetic": True,
                },
            )
        )
        self._storage.upsert_table_entity(
            case.model_copy(
                update={
                    "active_rubric_version": version,
                    "updated_at": created_at,
                    "updated_by_actor_id": actor.actor_id,
                    "updated_by_role": HR_WORKFLOW_ROLE,
                }
            )
        )
        self._complete_task_and_gate(
            case_id=case_id,
            task_row_key="task#approve_rubric",
            gate_row_key="gate#rubric_approval_required",
            updated_at=created_at,
            actor=actor,
            event_id=event_id,
        )

        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during rubric approval")
        return RoleIntakeRubricSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=RubricArtifactResult(
                case=case_snapshot.result.case,
                artifact=self._artifact_summary(artifact),
                approval_id=approval_id,
                rubric=payload,
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def list_rubrics(self, case_id: str) -> RoleIntakeRubricSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return RoleIntakeRubricSnapshot(error="unknown_case_id")
        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return RoleIntakeRubricSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=RubricListResult(
                case_id=case_id,
                active_rubric_version=case.active_rubric_version,
                rubrics=[
                    self._artifact_summary(artifact)
                    for artifact in self._list_artifacts(case_id, RUBRIC_ARTIFACT_TYPE)
                ],
            ),
            next_actions=case_snapshot.result.next_actions,
        )

    def get_rubric(self, case_id: str, rubric_version: str) -> RoleIntakeRubricSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return RoleIntakeRubricSnapshot(error="unknown_case_id")
        artifact = self._get_artifact(case_id, RUBRIC_ARTIFACT_TYPE, rubric_version)
        payload = self._read_artifact_json(artifact)
        if artifact is None or payload is None:
            return RoleIntakeRubricSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unknown_rubric_version",
            )
        case_snapshot = self._case_snapshot(case_id)
        if case_snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return RoleIntakeRubricSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=RubricGetResult(
                case_id=case_id,
                artifact=self._artifact_summary(artifact),
                rubric=payload,
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

    def _resolve_source_documents(
        self,
        case_id: str,
        request: RoleIntakeCreateRequest,
    ) -> list[SourceDocument] | None:
        if request.source_document_ids:
            documents: list[SourceDocument] = []
            for document_id in request.source_document_ids:
                document = cast(
                    SourceDocument | None,
                    self._storage.get_table_entity(
                        SourceDocument,
                        case_id,
                        f"doc#{document_id}",
                    ),
                )
                if document is None or document.candidate_id is not None:
                    return None
                documents.append(document)
            return documents

        return [
            cast(SourceDocument, row)
            for row in sorted(
                self._storage.list_table_entities(SourceDocument, partition_key=case_id),
                key=lambda row: row.RowKey,
            )
            if cast(SourceDocument, row).candidate_id is None
            and cast(SourceDocument, row).processing_status != "excluded"
        ]

    def _safe_source_document_ref(self, document: SourceDocument) -> dict[str, object]:
        return {
            "document_id": document.document_id,
            "document_type": document.document_type,
            "source_origin": document.source_origin,
            "source_label": document.source_label,
            "blob_path": document.blob_path,
            "sha256": document.sha256,
            "processing_status": document.processing_status,
            "version": document.version,
            "created_at": document.created_at,
            "synthetic": document.synthetic,
        }

    def _artifact_row_key(self, artifact_type: str, version: str) -> str:
        return f"artifact#{artifact_type}#{version}"

    def _get_artifact(
        self, case_id: str, artifact_type: str, version: str
    ) -> ArtifactVersion | None:
        return cast(
            ArtifactVersion | None,
            self._storage.get_table_entity(
                ArtifactVersion,
                case_id,
                self._artifact_row_key(artifact_type, version),
            ),
        )

    def _list_artifacts(self, case_id: str, artifact_type: str) -> list[ArtifactVersion]:
        return [
            cast(ArtifactVersion, artifact)
            for artifact in sorted(
                self._storage.list_table_entities(ArtifactVersion, partition_key=case_id),
                key=lambda row: row.RowKey,
            )
            if cast(ArtifactVersion, artifact).artifact_type == artifact_type
        ]

    def _read_artifact_json(self, artifact: ArtifactVersion | None):
        if artifact is None:
            return None
        return self._storage.read_blob_json(artifact.blob_path)

    def _artifact_summary(self, artifact: ArtifactVersion) -> WorkflowArtifactSummary:
        return WorkflowArtifactSummary(
            artifact_id=artifact.artifact_id,
            artifact_type=artifact.artifact_type,
            version=artifact.version,
            status=artifact.status,
            blob_path=artifact.blob_path,
            sha256=artifact.sha256,
            source_document_ids=artifact.source_document_ids,
            created_at=artifact.created_at,
            synthetic=artifact.synthetic,
        )

    def _supersede_prior_artifacts(
        self,
        *,
        case_id: str,
        artifact_type: str,
        new_version: str,
        updated_at: str,
        actor: ActorContext,
    ) -> None:
        for artifact in self._list_artifacts(case_id, artifact_type):
            if artifact.version == new_version or artifact.status != "approved":
                continue
            self._storage.upsert_table_entity(
                artifact.model_copy(
                    update={
                        "status": "superseded",
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                    }
                )
            )

    def _complete_task_and_gate(
        self,
        *,
        case_id: str,
        task_row_key: str,
        gate_row_key: str,
        updated_at: str,
        actor: ActorContext,
        event_id: str,
    ) -> None:
        task = cast(
            CaseTask | None,
            self._storage.get_table_entity(CaseTask, case_id, task_row_key),
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
            self._storage.get_table_entity(WorkflowGate, case_id, gate_row_key),
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
