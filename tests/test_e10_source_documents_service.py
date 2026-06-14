"""E10 source-document service over the workflow storage seam."""

from __future__ import annotations

import hashlib

from hr_eval_lab.cases.service import RecruitmentCaseService
from hr_eval_lab.cases.source_documents import SourceDocumentService
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    RecruitmentCaseCreateRequest,
    SourceDocumentRegisterRequest,
)
from hr_eval_lab.domain.schemas.workflow import (
    ArtifactVersion,
    CaseEvent,
    CaseTask,
    RecruitmentCase,
    SourceDocument,
    WorkflowGate,
)
from hr_eval_lab.domain.schemas.workflow_artifacts import role_source_raw_path
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore

TS = "2026-06-14T12:00:00Z"
CASE_ID = "case-e10-001"
DOC_ID = "doc-e10-001"
CONTENT = "Synthetic role source text for a controlled E10 lab case."


def _actor(actor_id: str = "u-hr-e10") -> ActorContext:
    return ActorContext(
        actor_id=actor_id,
        display="E10 HR Owner",
        roles=["hr"],
        resolved_role="hr",
    )


def _case_request() -> RecruitmentCaseCreateRequest:
    return RecruitmentCaseCreateRequest.model_validate(
        {
            "role_title": "Synthetic Intake Analyst",
            "department": "Synthetic Lab",
            "recruitment_type": "permanent",
        }
    )


def _document_request(**overrides) -> SourceDocumentRegisterRequest:
    body = {
        "document_type": "job_description",
        "source_origin": "manual_upload",
        "source_label": "Synthetic role brief",
        "file_name": "synthetic-role-brief.txt",
        "mime_type": "text/plain",
        "synthetic": True,
        "content_text": CONTENT,
    }
    body.update(overrides)
    return SourceDocumentRegisterRequest.model_validate(body)


def _create_case(store: LocalWorkflowStore, case_id: str = CASE_ID) -> None:
    RecruitmentCaseService(
        store,
        case_id_fn=lambda: case_id,
        event_id_fn=lambda: "evt-e10-case-created",
        now_fn=lambda: TS,
    ).create_case(_case_request(), _actor())


def _source_service(store: LocalWorkflowStore, document_ids=None, event_ids=None):
    document_iter = iter(document_ids or [DOC_ID])
    event_iter = iter(event_ids or ["evt-e10-source-document-registered"])
    return SourceDocumentService(
        store,
        document_id_fn=lambda: next(document_iter),
        event_id_fn=lambda: next(event_iter),
        now_fn=lambda: TS,
    )


def test_e10_register_document_writes_blob_metadata_event_and_task_gate_updates(
    tmp_path,
):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)

    snapshot = _source_service(store).register_document(
        CASE_ID,
        _document_request(),
        _actor(),
    )

    assert snapshot.error is None
    assert snapshot.case_id == CASE_ID
    assert snapshot.correlation_id == "corr-e10-001"
    assert snapshot.result is not None
    assert snapshot.result.document.document_id == DOC_ID
    assert snapshot.result.documents_count == 1
    assert [action.action_id for action in snapshot.next_actions] == [
        "complete_role_intake",
        "confirm_hiring_manager",
    ]

    blob_path = role_source_raw_path(CASE_ID, DOC_ID)
    raw = store.read_blob_bytes(blob_path)
    assert raw == CONTENT.encode("utf-8")

    documents = store.list_table_entities(SourceDocument, CASE_ID)
    assert len(documents) == 1
    document = documents[0]
    assert document.RowKey == f"doc#{DOC_ID}"
    assert document.document_type == "job_description"
    assert document.source_origin == "manual_upload"
    assert document.source_label == "Synthetic role brief"
    assert document.blob_path == blob_path
    assert document.mime_type == "text/plain"
    assert document.file_name == "synthetic-role-brief.txt"
    assert document.size_bytes == len(CONTENT.encode("utf-8"))
    assert document.sha256 == hashlib.sha256(CONTENT.encode("utf-8")).hexdigest()
    assert document.processing_status == "registered"
    assert document.version == "v1"
    assert document.synthetic is True

    events = store.list_table_entities(CaseEvent, CASE_ID)
    assert [event.event_type for event in events] == [
        "case_created",
        "source_document_registered",
    ]
    source_event = events[1]
    assert source_event.artifact_id == DOC_ID
    assert source_event.artifact_version == "v1"
    assert source_event.safe_details["blob_path"] == blob_path
    assert CONTENT not in str(source_event.safe_details)

    assert store.list_table_entities(ArtifactVersion, CASE_ID) == []

    task = store.get_table_entity(
        CaseTask,
        CASE_ID,
        "task#attach_source_documents",
    )
    assert task is not None
    assert task.status == "completed"
    assert task.completion_event_id == "evt-e10-source-document-registered"

    source_gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#source_documents_required",
    )
    assert source_gate is not None
    assert source_gate.gate_status == "satisfied"
    assert source_gate.blocking_reasons == []
    assert source_gate.satisfied_by_event_id == "evt-e10-source-document-registered"

    assessment_gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#assessment_unlocked",
    )
    assert assessment_gate is not None
    assert assessment_gate.gate_status == "locked"
    assert assessment_gate.blocking_reasons == [
        "Assessment remains locked until prerequisite gates are satisfied."
    ]
    assert store.peek_queue_messages() == []


def test_e10_list_and_get_documents_return_metadata_only(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    service = _source_service(
        store,
        document_ids=["doc-e10-001", "doc-e10-002"],
        event_ids=["evt-e10-doc-001", "evt-e10-doc-002"],
    )
    service.register_document(
        CASE_ID,
        _document_request(source_label="First source"),
        _actor(),
    )
    service.register_document(
        CASE_ID,
        _document_request(
            document_type="business_note",
            source_label="Second source",
            content_text="Second synthetic source document.",
        ),
        _actor(),
    )

    listed = service.list_documents(CASE_ID)
    assert listed.error is None
    assert listed.result is not None
    assert [doc.document_id for doc in listed.result.documents] == [
        "doc-e10-001",
        "doc-e10-002",
    ]

    retrieved = service.get_document(CASE_ID, "doc-e10-002")
    assert retrieved.error is None
    assert retrieved.result is not None
    payload = retrieved.result.model_dump(mode="json")
    assert payload["document"]["document_type"] == "business_note"
    assert payload["document"]["source_label"] == "Second source"
    assert "content_text" not in payload["document"]
    assert "Second synthetic source document." not in str(payload)
    assert store.peek_queue_messages() == []


def test_e10_unknown_case_does_not_write_blob_table_or_queue(tmp_path):
    store = LocalWorkflowStore(tmp_path)

    snapshot = _source_service(store).register_document(
        "case-missing",
        _document_request(),
        _actor(),
    )

    assert snapshot.error == "unknown_case_id"
    assert store.list_table_entities(SourceDocument) == []
    assert store.list_table_entities(CaseEvent) == []
    assert not any(store.blobs_root.rglob("*"))
    assert store.peek_queue_messages() == []


def test_e10_partial_case_does_not_fabricate_task_or_gate_rows(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    store.upsert_table_entity(
        RecruitmentCase(
            PartitionKey="case-e10-partial",
            RowKey="case",
            created_at=TS,
            created_by_actor_id="u-hr-e10",
            created_by_role="hr_specialist",
            correlation_id="corr-e10-partial",
            case_id="case-e10-partial",
            case_title="Partial E10 case",
            role_title="Synthetic Role",
            department="Synthetic Lab",
            recruitment_type="permanent",
            case_status="intake_pending",
            current_stage="stage_1_start_or_continue",
            current_gate="role_intake_required",
            hr_owner_actor_id="u-hr-e10",
        )
    )

    snapshot = _source_service(store).register_document(
        "case-e10-partial",
        _document_request(),
        _actor(),
    )

    assert snapshot.error is None
    assert len(store.list_table_entities(SourceDocument, "case-e10-partial")) == 1
    assert store.list_table_entities(CaseTask, "case-e10-partial") == []
    assert store.list_table_entities(WorkflowGate, "case-e10-partial") == []
    assert store.peek_queue_messages() == []
