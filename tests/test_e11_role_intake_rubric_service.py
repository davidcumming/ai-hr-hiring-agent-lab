"""E11 role-intake and approved-rubric service coverage."""

from __future__ import annotations

from hr_eval_lab.cases.role_intake_rubrics import RoleIntakeRubricService
from hr_eval_lab.cases.service import RecruitmentCaseService
from hr_eval_lab.cases.source_documents import SourceDocumentService
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    ApprovedRubricRegisterRequest,
    RecruitmentCaseCreateRequest,
    RoleIntakeCreateRequest,
    SourceDocumentRegisterRequest,
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
    role_source_raw_path,
    rubric_artifact_path,
)
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore

TS = "2026-06-14T12:00:00Z"
CASE_ID = "case-e11-001"
DOC_ID = "doc-e11-001"
SOURCE_TEXT = "Synthetic source text for E11 role intake. No applicant material."


def _actor(actor_id: str = "u-hr-e11") -> ActorContext:
    return ActorContext(
        actor_id=actor_id,
        display="E11 HR Owner",
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


def _document_request() -> SourceDocumentRegisterRequest:
    return SourceDocumentRegisterRequest.model_validate(
        {
            "document_type": "job_description",
            "source_origin": "manual_upload",
            "source_label": "Synthetic source brief",
            "file_name": "synthetic-source-brief.txt",
            "mime_type": "text/plain",
            "synthetic": True,
            "content_text": SOURCE_TEXT,
        }
    )


def _role_intake_request(**overrides) -> RoleIntakeCreateRequest:
    body = {
        "synthetic": True,
        "intake_title": "Synthetic Intake Analyst intake",
        "role_purpose": "Coordinate deterministic hiring lab intake work.",
        "responsibilities": ["Maintain synthetic intake records."],
        "required_qualifications": ["Experience with structured HR workflows."],
        "preferred_qualifications": ["Experience with Azure-shaped lab workflows."],
        "business_context": "Synthetic team expansion.",
        "role_risks": ["Ambiguous source documents."],
        "open_questions": ["Confirm interview panel."],
    }
    body.update(overrides)
    return RoleIntakeCreateRequest.model_validate(body)


def _rubric_request(**overrides) -> ApprovedRubricRegisterRequest:
    body = {
        "synthetic": True,
        "rubric_title": "Synthetic intake analyst screening rubric",
        "criteria": [
            {
                "criterion_id": "workflow_experience",
                "label": "Workflow experience",
                "description": "Experience operating structured HR workflows.",
                "weight": 60,
                "rating_scale": [
                    {
                        "score": 0,
                        "label": "No evidence",
                        "description": "No relevant workflow evidence.",
                    },
                    {
                        "score": 5,
                        "label": "Strong evidence",
                        "description": "Clear relevant workflow evidence.",
                    },
                ],
                "evidence_expectations": ["Role-source references only."],
            },
            {
                "criterion_id": "documentation_quality",
                "label": "Documentation quality",
                "description": "Can maintain clear synthetic case documentation.",
                "weight": 40,
                "rating_scale": [
                    {
                        "score": 0,
                        "label": "No evidence",
                        "description": "No documentation evidence.",
                    },
                    {
                        "score": 5,
                        "label": "Strong evidence",
                        "description": "Clear documentation evidence.",
                    },
                ],
            },
        ],
    }
    body.update(overrides)
    return ApprovedRubricRegisterRequest.model_validate(body)


def _create_case(store: LocalWorkflowStore, case_id: str = CASE_ID) -> None:
    RecruitmentCaseService(
        store,
        case_id_fn=lambda: case_id,
        event_id_fn=lambda: "evt-e11-case-created",
        now_fn=lambda: TS,
    ).create_case(_case_request(), _actor())


def _register_source_document(store: LocalWorkflowStore, case_id: str = CASE_ID) -> None:
    SourceDocumentService(
        store,
        document_id_fn=lambda: DOC_ID,
        event_id_fn=lambda: "evt-e11-source-document-registered",
        now_fn=lambda: TS,
    ).register_document(case_id, _document_request(), _actor())


def _service(store: LocalWorkflowStore, event_id: str = "evt-e11-service"):
    return RoleIntakeRubricService(
        store,
        approval_id_fn=lambda: "approval-e11-001",
        event_id_fn=lambda: event_id,
        now_fn=lambda: TS,
    )


def test_e11_role_intake_writes_blob_artifact_metadata_event_and_task_gate_updates(
    tmp_path,
):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    _register_source_document(store)

    snapshot = _service(store, "evt-e11-role-intake-created").create_role_intake(
        CASE_ID,
        _role_intake_request(),
        _actor(),
    )

    assert snapshot.error is None
    assert snapshot.result is not None
    assert [action.action_id for action in snapshot.next_actions] == [
        "confirm_hiring_manager"
    ]
    assert SOURCE_TEXT not in str(snapshot.result.model_dump(mode="json"))

    blob_path = role_intake_artifact_path(CASE_ID, "v1")
    artifact_payload = store.read_blob_json(blob_path)
    assert artifact_payload["intake_title"] == "Synthetic Intake Analyst intake"
    assert artifact_payload["source_document_ids"] == [DOC_ID]
    assert artifact_payload["source_documents"][0]["document_id"] == DOC_ID
    assert "content_text" not in artifact_payload["source_documents"][0]
    assert SOURCE_TEXT not in str(artifact_payload)

    artifacts = store.list_table_entities(ArtifactVersion, CASE_ID)
    role_artifacts = [
        artifact for artifact in artifacts if artifact.artifact_type == "role_intake"
    ]
    assert len(role_artifacts) == 1
    artifact = role_artifacts[0]
    assert artifact.RowKey == "artifact#role_intake#v1"
    assert artifact.status == "approved"
    assert artifact.blob_path == blob_path
    assert artifact.source_document_ids == [DOC_ID]
    assert artifact.approved_version_required is True

    case = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    assert case is not None
    assert case.active_intake_version == "v1"
    assert case.case_status == "intake_pending"

    events = store.list_table_entities(CaseEvent, CASE_ID)
    assert [event.event_type for event in events] == [
        "case_created",
        "source_document_registered",
        "role_intake_artifact_created",
    ]
    assert events[-1].safe_details["source_document_ids"] == [DOC_ID]

    task = store.get_table_entity(CaseTask, CASE_ID, "task#complete_role_intake")
    assert task is not None
    assert task.status == "completed"
    assert task.completion_event_id == "evt-e11-role-intake-created"

    gate = store.get_table_entity(WorkflowGate, CASE_ID, "gate#role_intake_required")
    assert gate is not None
    assert gate.gate_status == "satisfied"
    assert gate.blocking_reasons == []
    assert gate.satisfied_by_event_id == "evt-e11-role-intake-created"
    assert store.peek_queue_messages() == []


def test_e11_role_intake_requires_existing_case_and_source_documents(tmp_path):
    store = LocalWorkflowStore(tmp_path)

    missing_case = _service(store).create_role_intake(
        "case-missing",
        _role_intake_request(),
        _actor(),
    )
    assert missing_case.error == "unknown_case_id"
    assert store.list_table_entities(ArtifactVersion) == []
    assert not any(store.blobs_root.rglob("*"))

    _create_case(store)
    missing_docs = _service(store).create_role_intake(
        CASE_ID,
        _role_intake_request(),
        _actor(),
    )
    assert missing_docs.error == "source_documents_required"
    assert store.list_table_entities(ArtifactVersion, CASE_ID) == []
    assert store.peek_queue_messages() == []


def test_e11_role_intake_rejects_duplicate_version_before_extra_blob_write(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    _register_source_document(store)

    service = _service(store, "evt-e11-role-v1")
    created = service.create_role_intake(CASE_ID, _role_intake_request(), _actor())
    assert created.error is None
    blob_files_before = sorted(path for path in store.blobs_root.rglob("*") if path.is_file())

    duplicate = _service(store, "evt-e11-role-duplicate").create_role_intake(
        CASE_ID,
        _role_intake_request(role_purpose="Changed purpose."),
        _actor(),
    )

    assert duplicate.error == "role_intake_version_exists"
    assert sorted(path for path in store.blobs_root.rglob("*") if path.is_file()) == (
        blob_files_before
    )
    assert [
        artifact.version
        for artifact in store.list_table_entities(ArtifactVersion, CASE_ID)
        if artifact.artifact_type == "role_intake"
    ] == ["v1"]

    v2 = _service(store, "evt-e11-role-v2").create_role_intake(
        CASE_ID,
        _role_intake_request(intake_version="v2"),
        _actor(),
    )
    assert v2.error is None
    role_artifacts = {
        artifact.version: artifact.status
        for artifact in store.list_table_entities(ArtifactVersion, CASE_ID)
        if artifact.artifact_type == "role_intake"
    }
    assert role_artifacts == {"v1": "superseded", "v2": "approved"}
    case = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    assert case is not None
    assert case.active_intake_version == "v2"


def test_e11_role_intake_does_not_fabricate_missing_task_or_gate_rows(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    store.upsert_table_entity(
        RecruitmentCase(
            PartitionKey="case-e11-partial",
            RowKey="case",
            created_at=TS,
            created_by_actor_id="u-hr-e11",
            created_by_role="hr_specialist",
            correlation_id="corr-e11-partial",
            case_id="case-e11-partial",
            case_title="Partial E11 case",
            role_title="Synthetic Role",
            department="Synthetic Lab",
            recruitment_type="permanent",
            case_status="intake_pending",
            current_stage="stage_1_start_or_continue",
            current_gate="role_intake_required",
            hr_owner_actor_id="u-hr-e11",
        )
    )
    raw_path = role_source_raw_path("case-e11-partial", DOC_ID)
    raw_ref = store.write_blob_artifact(raw_path, SOURCE_TEXT.encode("utf-8"))
    store.upsert_table_entity(
        SourceDocument(
            PartitionKey="case-e11-partial",
            RowKey=f"doc#{DOC_ID}",
            created_at=TS,
            created_by_actor_id="u-hr-e11",
            created_by_role="hr_specialist",
            correlation_id="corr-e11-partial",
            case_id="case-e11-partial",
            document_id=DOC_ID,
            document_type="job_description",
            source_origin="manual_upload",
            blob_path=raw_ref.blob_path,
            sha256=raw_ref.sha256,
            size_bytes=raw_ref.size_bytes,
            processing_status="registered",
            version="v1",
        )
    )

    snapshot = _service(store).create_role_intake(
        "case-e11-partial",
        _role_intake_request(),
        _actor(),
    )

    assert snapshot.error is None
    assert len(store.list_table_entities(ArtifactVersion, "case-e11-partial")) == 1
    assert store.list_table_entities(CaseTask, "case-e11-partial") == []
    assert store.list_table_entities(WorkflowGate, "case-e11-partial") == []
    assert store.peek_queue_messages() == []


def test_e11_rubric_writes_blob_artifact_approval_event_and_gate_update(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)

    snapshot = _service(store, "evt-e11-rubric-approved").register_rubric(
        CASE_ID,
        _rubric_request(),
        _actor(),
    )

    assert snapshot.error is None
    assert snapshot.result is not None
    assert snapshot.result.approval_id == "approval-e11-001"
    blob_path = rubric_artifact_path(CASE_ID, "v1")
    payload = store.read_blob_json(blob_path)
    assert payload["rubric_title"] == "Synthetic intake analyst screening rubric"
    assert payload["approved_by_actor_id"] == "u-hr-e11"
    assert len(payload["criteria"]) == 2

    artifact = store.get_table_entity(
        ArtifactVersion,
        CASE_ID,
        "artifact#screening_rubric#v1",
    )
    assert artifact is not None
    assert artifact.artifact_type == "screening_rubric"
    assert artifact.status == "approved"
    assert artifact.blob_path == blob_path
    assert artifact.approved_version_required is True

    approvals = store.list_table_entities(Approval, CASE_ID)
    assert len(approvals) == 1
    assert approvals[0].artifact_version == "v1"
    assert approvals[0].actor_id == "u-hr-e11"
    assert approvals[0].decision == "approved"

    case = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    assert case is not None
    assert case.active_rubric_version == "v1"
    assert case.case_status == "intake_pending"

    rubric_gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#rubric_approval_required",
    )
    assert rubric_gate is not None
    assert rubric_gate.gate_status == "satisfied"
    assert rubric_gate.blocking_reasons == []
    assert rubric_gate.satisfied_by_event_id == "evt-e11-rubric-approved"

    assessment_gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#assessment_unlocked",
    )
    assert assessment_gate is not None
    assert assessment_gate.gate_status == "locked"
    assert store.peek_queue_messages() == []


def test_e11_rubric_rejects_duplicate_version_and_actor_mismatch(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)

    created = _service(store).register_rubric(CASE_ID, _rubric_request(), _actor())
    assert created.error is None
    duplicate = _service(store, "evt-e11-rubric-duplicate").register_rubric(
        CASE_ID,
        _rubric_request(rubric_title="Changed rubric"),
        _actor(),
    )
    assert duplicate.error == "rubric_version_exists"

    mismatch = _service(store, "evt-e11-rubric-mismatch").register_rubric(
        CASE_ID,
        _rubric_request(rubric_version="v2", approved_by_actor_id="u-other"),
        _actor(),
    )
    assert mismatch.error == "approved_by_actor_mismatch"
    assert [
        artifact.version
        for artifact in store.list_table_entities(ArtifactVersion, CASE_ID)
        if artifact.artifact_type == "screening_rubric"
    ] == ["v1"]
    assert store.peek_queue_messages() == []

    v2 = _service(store, "evt-e11-rubric-v2").register_rubric(
        CASE_ID,
        _rubric_request(rubric_version="v2"),
        _actor(),
    )
    assert v2.error is None
    rubric_artifacts = {
        artifact.version: artifact.status
        for artifact in store.list_table_entities(ArtifactVersion, CASE_ID)
        if artifact.artifact_type == "screening_rubric"
    }
    assert rubric_artifacts == {"v1": "superseded", "v2": "approved"}
    case = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    assert case is not None
    assert case.active_rubric_version == "v2"


def test_e11_get_role_intake_and_rubrics_are_metadata_safe(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    _register_source_document(store)
    service = _service(store)
    service.create_role_intake(CASE_ID, _role_intake_request(), _actor())
    service.register_rubric(CASE_ID, _rubric_request(), _actor())

    role_snapshot = service.get_role_intake(CASE_ID)
    assert role_snapshot.error is None
    assert role_snapshot.result is not None
    role_payload = role_snapshot.result.model_dump(mode="json")
    assert role_payload["artifact"]["version"] == "v1"
    assert SOURCE_TEXT not in str(role_payload)

    list_snapshot = service.list_rubrics(CASE_ID)
    assert list_snapshot.error is None
    assert list_snapshot.result is not None
    assert list_snapshot.result.active_rubric_version == "v1"
    assert [rubric.version for rubric in list_snapshot.result.rubrics] == ["v1"]

    get_snapshot = service.get_rubric(CASE_ID, "v1")
    assert get_snapshot.error is None
    assert get_snapshot.result is not None
    assert get_snapshot.result.rubric["rubric_version"] == "v1"

    missing = service.get_rubric(CASE_ID, "v-missing")
    assert missing.error == "unknown_rubric_version"
