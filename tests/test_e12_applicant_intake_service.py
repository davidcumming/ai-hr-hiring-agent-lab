"""E12 applicant/candidate package intake service coverage."""

from __future__ import annotations

from pathlib import Path

from hr_eval_lab.cases.applicant_intake import ApplicantIntakeService
from hr_eval_lab.cases.service import RecruitmentCaseService
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    ApplicantCreateRequest,
    ApplicantImportRequest,
    ApplicantSetConfirmRequest,
    CandidateDocumentRegisterRequest,
    RecruitmentCaseCreateRequest,
)
from hr_eval_lab.domain.schemas.workflow import (
    Applicant,
    CandidatePackage,
    CaseEvent,
    CaseTask,
    RecruitmentCase,
    SourceDocument,
    WorkflowGate,
)
from hr_eval_lab.domain.schemas.workflow_artifacts import (
    candidate_document_raw_path,
    candidate_package_path,
)
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore

TS = "2026-06-14T12:00:00Z"
CASE_ID = "case-e12-001"
RESUME_TEXT = "Synthetic resume content for E12 package intake."


def _actor(actor_id: str = "u-hr-e12") -> ActorContext:
    return ActorContext(
        actor_id=actor_id,
        display="E12 HR Owner",
        roles=["hr"],
        resolved_role="hr",
    )


def _case_request() -> RecruitmentCaseCreateRequest:
    return RecruitmentCaseCreateRequest.model_validate(
        {
            "role_title": "Synthetic Applicant Intake Analyst",
            "department": "Synthetic Lab",
            "recruitment_type": "permanent",
        }
    )


def _create_case(store: LocalWorkflowStore, case_id: str = CASE_ID) -> None:
    RecruitmentCaseService(
        store,
        case_id_fn=lambda: case_id,
        event_id_fn=lambda: "evt-e12-case-created",
        now_fn=lambda: TS,
    ).create_case(_case_request(), _actor())


def _service(
    store: LocalWorkflowStore,
    *,
    candidate_ids: list[str] | None = None,
    document_ids: list[str] | None = None,
    event_ids: list[str] | None = None,
) -> ApplicantIntakeService:
    candidate_iter = iter(candidate_ids or ["cand-e12-001"])
    document_iter = iter(document_ids or ["doc-e12-001"])
    event_iter = iter(event_ids or ["evt-e12-applicant-intake"])
    return ApplicantIntakeService(
        store,
        candidate_id_fn=lambda: next(candidate_iter),
        document_id_fn=lambda: next(document_iter),
        event_id_fn=lambda: next(event_iter),
        now_fn=lambda: TS,
    )


def _applicant_request(**overrides) -> ApplicantCreateRequest:
    body = {
        "synthetic": True,
        "candidate_ref": "E12-CAND-001",
        "display_label": "Synthetic Candidate 001",
    }
    body.update(overrides)
    return ApplicantCreateRequest.model_validate(body)


def _document_request(**overrides) -> CandidateDocumentRegisterRequest:
    body = {
        "document_type": "resume",
        "source_origin": "manual_upload",
        "source_label": "Synthetic resume",
        "file_name": "synthetic-resume.md",
        "mime_type": "text/markdown",
        "synthetic": True,
        "content_text": RESUME_TEXT,
    }
    body.update(overrides)
    return CandidateDocumentRegisterRequest.model_validate(body)


def _import_request(candidates: list[dict]) -> ApplicantImportRequest:
    return ApplicantImportRequest.model_validate(
        {"synthetic": True, "candidates": candidates}
    )


def _blob_files(store: LocalWorkflowStore) -> list[Path]:
    return sorted(path for path in store.blobs_root.rglob("*") if path.is_file())


def test_e12_applicant_creation_writes_applicant_package_event_and_no_queue(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)

    snapshot = _service(
        store,
        candidate_ids=["cand-e12-001"],
        event_ids=["evt-e12-applicant-created"],
    ).register_applicant(CASE_ID, _applicant_request(), _actor())

    assert snapshot.error is None
    assert snapshot.result is not None
    assert snapshot.result.applicant.candidate_id == "cand-e12-001"
    assert snapshot.result.applicant.import_status == "incomplete"
    assert snapshot.result.package.package_status == "blocked"
    assert snapshot.result.package.required_document_status["resume"] == "missing"
    assert snapshot.result.findings[0].finding_type == "missing_required_resume"
    assert {"confirm_applicant_set", "resolve_import_findings"} <= {
        action.action_id for action in snapshot.next_actions
    }

    applicants = store.list_table_entities(Applicant, CASE_ID)
    packages = store.list_table_entities(CandidatePackage, CASE_ID)
    assert len(applicants) == 1
    assert applicants[0].RowKey == "candidate#cand-e12-001"
    assert applicants[0].candidate_ref == "E12-CAND-001"
    assert applicants[0].blocking_findings == ["missing_required_resume"]
    assert len(packages) == 1
    assert packages[0].RowKey == "package#cand-e12-001#v1"

    package_path = candidate_package_path(CASE_ID, "cand-e12-001", "v1")
    package_payload = store.read_blob_json(package_path)
    assert package_payload["artifact_type"] == "candidate_package"
    assert package_payload["documents"] == []
    assert package_payload["findings"][0]["finding_type"] == "missing_required_resume"

    events = store.list_table_entities(CaseEvent, CASE_ID)
    assert [event.event_type for event in events] == [
        "case_created",
        "applicant_registered",
    ]
    assert events[-1].safe_details["candidate_id"] == "cand-e12-001"
    assert store.peek_queue_messages() == []


def test_e12_duplicate_and_cap_rejections_happen_before_blob_writes(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    service = _service(
        store,
        candidate_ids=[
            "cand-e12-001",
            "cand-e12-002",
            "cand-e12-003",
            "cand-e12-004",
            "cand-e12-005",
            "cand-e12-006",
        ],
        event_ids=[
            "evt-e12-001",
            "evt-e12-002",
            "evt-e12-003",
            "evt-e12-004",
            "evt-e12-005",
            "evt-e12-006",
        ],
    )
    first = service.register_applicant(CASE_ID, _applicant_request(), _actor())
    assert first.error is None
    blob_files_after_first = _blob_files(store)

    duplicate = service.register_applicant(
        CASE_ID,
        _applicant_request(candidate_ref=" e12-cand-001 "),
        _actor(),
    )
    assert duplicate.error == "duplicate_candidate_ref"
    assert _blob_files(store) == blob_files_after_first
    assert len(store.list_table_entities(Applicant, CASE_ID)) == 1

    for index in range(2, 6):
        created = service.register_applicant(
            CASE_ID,
            _applicant_request(
                candidate_ref=f"E12-CAND-00{index}",
                display_label=f"Synthetic Candidate 00{index}",
            ),
            _actor(),
        )
        assert created.error is None
    blob_files_at_cap = _blob_files(store)

    capped = service.register_applicant(
        CASE_ID,
        _applicant_request(candidate_ref="E12-CAND-006"),
        _actor(),
    )
    assert capped.error == "candidate_limit_exceeded"
    assert _blob_files(store) == blob_files_at_cap
    assert len(store.list_table_entities(Applicant, CASE_ID)) == 5


def test_e12_candidate_document_registration_completes_package_metadata(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    service = _service(
        store,
        candidate_ids=["cand-e12-001"],
        document_ids=["doc-e12-resume"],
        event_ids=["evt-e12-applicant-created", "evt-e12-resume-registered"],
    )
    service.register_applicant(CASE_ID, _applicant_request(), _actor())

    snapshot = service.register_candidate_document(
        CASE_ID,
        "cand-e12-001",
        _document_request(),
        _actor(),
    )

    assert snapshot.error is None
    assert snapshot.result is not None
    assert snapshot.result.document.document_id == "doc-e12-resume"
    assert snapshot.result.document.candidate_id == "cand-e12-001"
    assert snapshot.result.package.package_status == "complete"
    assert snapshot.result.findings == []

    raw_path = candidate_document_raw_path(CASE_ID, "cand-e12-001", "doc-e12-resume")
    assert store.read_blob_bytes(raw_path) == RESUME_TEXT.encode("utf-8")
    documents = store.list_table_entities(SourceDocument, CASE_ID)
    assert len(documents) == 1
    assert documents[0].candidate_id == "cand-e12-001"
    assert documents[0].document_type == "resume"
    assert documents[0].blob_path == raw_path

    applicant = store.get_table_entity(Applicant, CASE_ID, "candidate#cand-e12-001")
    assert applicant is not None
    assert applicant.import_status == "imported"
    assert applicant.blocking_findings == []
    package = store.get_table_entity(
        CandidatePackage,
        CASE_ID,
        "package#cand-e12-001#v1",
    )
    assert package is not None
    assert package.package_status == "complete"
    assert package.document_ids == ["doc-e12-resume"]
    package_payload = store.read_blob_json(package.blob_path)
    assert package_payload["documents"][0]["document_id"] == "doc-e12-resume"
    assert "content_text" not in str(package_payload)
    assert RESUME_TEXT not in str(package_payload)

    events = store.list_table_entities(CaseEvent, CASE_ID)
    assert [event.event_type for event in events] == [
        "case_created",
        "applicant_registered",
        "candidate_document_registered",
    ]
    assert RESUME_TEXT not in str(events[-1].safe_details)
    assert store.peek_queue_messages() == []


def test_e12_missing_resume_produces_blocking_finding_and_blocked_package(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)

    snapshot = _service(
        store,
        candidate_ids=["cand-e12-missing-resume"],
        event_ids=["evt-e12-import"],
    ).process_import(
        CASE_ID,
        _import_request(
            [
                {
                    "candidate_ref": "E12-MISSING-RESUME",
                    "display_label": "Missing Resume Candidate",
                    "documents": [
                        _document_request(
                            document_type="cover_letter",
                            content_text="Synthetic cover letter only.",
                        ).model_dump(mode="json")
                    ],
                }
            ]
        ),
        _actor(),
    )

    assert snapshot.error is None
    assert snapshot.result is not None
    assert snapshot.result.imported_count == 1
    assert snapshot.result.document_count == 1
    assert snapshot.result.can_confirm is False
    assert snapshot.result.findings[0].severity == "blocking"
    assert snapshot.result.findings[0].finding_type == "missing_required_resume"
    assert snapshot.result.packages[0].package_status == "blocked"
    applicant = store.get_table_entity(
        Applicant,
        CASE_ID,
        "candidate#cand-e12-missing-resume",
    )
    assert applicant is not None
    assert applicant.import_status == "incomplete"
    assert applicant.blocking_findings == ["missing_required_resume"]


def test_e12_batch_import_accepts_five_and_rejects_unsupported_type_preflight(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    service = _service(
        store,
        candidate_ids=[
            "cand-e12-batch-001",
            "cand-e12-batch-002",
            "cand-e12-batch-003",
            "cand-e12-batch-004",
            "cand-e12-batch-005",
        ],
        document_ids=[
            "doc-e12-batch-001",
            "doc-e12-batch-002",
            "doc-e12-batch-003",
            "doc-e12-batch-004",
            "doc-e12-batch-005",
        ],
        event_ids=["evt-e12-batch-import"],
    )

    created = service.process_import(
        CASE_ID,
        _import_request(
            [
                {
                    "candidate_ref": f"E12-BATCH-00{index}",
                    "display_label": f"Batch Candidate 00{index}",
                    "documents": [_document_request().model_dump(mode="json")],
                }
                for index in range(1, 6)
            ]
        ),
        _actor(),
    )
    assert created.error is None
    assert created.result is not None
    assert created.result.imported_count == 5
    assert created.result.document_count == 5
    assert created.result.can_confirm is True
    assert len(store.list_table_entities(Applicant, CASE_ID)) == 5
    assert len(store.list_table_entities(SourceDocument, CASE_ID)) == 5
    assert len(store.list_table_entities(CandidatePackage, CASE_ID)) == 5

    second_store = LocalWorkflowStore(tmp_path / "unsupported")
    _create_case(second_store)
    rejected = _service(second_store).process_import(
        CASE_ID,
        _import_request(
            [
                {
                    "candidate_ref": "E12-UNSUPPORTED",
                    "display_label": "Unsupported Candidate",
                    "documents": [
                        _document_request(document_type="transcript").model_dump(
                            mode="json"
                        )
                    ],
                }
            ]
        ),
        _actor(),
    )
    assert rejected.error == "unsupported_document_type"
    assert second_store.list_table_entities(Applicant, CASE_ID) == []
    assert not any(second_store.blobs_root.rglob("*"))


def test_e12_confirmation_blocked_when_any_active_applicant_incomplete(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    _service(
        store,
        candidate_ids=["cand-e12-incomplete"],
        event_ids=["evt-e12-applicant-created", "evt-e12-confirm"],
    ).register_applicant(CASE_ID, _applicant_request(), _actor())

    snapshot = _service(store, event_ids=["evt-e12-confirm"]).confirm_applicant_set(
        CASE_ID,
        ApplicantSetConfirmRequest.model_validate({"synthetic": True}),
        _actor(),
    )

    assert snapshot.error == "applicant_set_incomplete"
    assert snapshot.blocked is True
    assert snapshot.result is not None
    assert snapshot.result.can_confirm is False
    gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#applicant_set_confirmation_required",
    )
    assert gate is not None
    assert gate.gate_status == "blocked"
    case = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    assert case is not None
    assert case.applicant_set_version is None


def test_e12_confirmation_succeeds_and_keeps_assessment_locked(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    service = _service(
        store,
        candidate_ids=["cand-e12-complete"],
        document_ids=["doc-e12-resume"],
        event_ids=["evt-e12-import", "evt-e12-confirm"],
    )
    imported = service.process_import(
        CASE_ID,
        _import_request(
            [
                {
                    "candidate_ref": "E12-COMPLETE",
                    "display_label": "Complete Candidate",
                    "documents": [_document_request().model_dump(mode="json")],
                }
            ]
        ),
        _actor(),
    )
    assert imported.error is None

    confirmed = service.confirm_applicant_set(
        CASE_ID,
        ApplicantSetConfirmRequest.model_validate({"synthetic": True}),
        _actor(),
    )

    assert confirmed.error is None
    assert confirmed.result is not None
    assert confirmed.result.confirmed_applicant_set_version == "v1"
    assert confirmed.result.confirmed_candidate_ids == ["cand-e12-complete"]
    assert confirmed.result.assessment_unlocked == "locked"
    assert "confirm_applicant_set" not in [
        action.action_id for action in confirmed.next_actions
    ]

    applicant = store.get_table_entity(
        Applicant,
        CASE_ID,
        "candidate#cand-e12-complete",
    )
    assert applicant is not None
    assert applicant.import_status == "confirmed"
    assert applicant.applicant_set_version == "v1"
    case = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    assert case is not None
    assert case.case_status == "applicants_pending"
    assert case.current_gate == "assessment_unlocked"
    assert case.applicant_set_version == "v1"
    gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#applicant_set_confirmation_required",
    )
    assert gate is not None
    assert gate.gate_status == "satisfied"
    task = store.get_table_entity(CaseTask, CASE_ID, "task#confirm_applicant_set")
    assert task is not None
    assert task.status == "completed"
    assessment_gate = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#assessment_unlocked",
    )
    assert assessment_gate is not None
    assert assessment_gate.gate_status == "locked"
    assert assessment_gate.blocking_reasons == [
        "Assessment remains locked until a later readiness/assessment slice explicitly unlocks it."
    ]
    assert store.peek_queue_messages() == []


def test_e12_applicant_package_mutations_are_rejected_after_confirmation_without_writes(
    tmp_path,
):
    store = LocalWorkflowStore(tmp_path)
    _create_case(store)
    service = _service(
        store,
        candidate_ids=["cand-e12-locked"],
        document_ids=["doc-e12-locked-resume"],
        event_ids=["evt-e12-import", "evt-e12-confirm"],
    )
    imported = service.process_import(
        CASE_ID,
        _import_request(
            [
                {
                    "candidate_ref": "E12-LOCKED",
                    "display_label": "Locked Candidate",
                    "documents": [_document_request().model_dump(mode="json")],
                }
            ]
        ),
        _actor(),
    )
    assert imported.error is None
    confirmed = service.confirm_applicant_set(
        CASE_ID,
        ApplicantSetConfirmRequest.model_validate({"synthetic": True}),
        _actor(),
    )
    assert confirmed.error is None

    case_before = store.get_table_entity(RecruitmentCase, CASE_ID, "case")
    gate_before = store.get_table_entity(
        WorkflowGate,
        CASE_ID,
        "gate#applicant_set_confirmation_required",
    )
    applicants_before = store.list_table_entities(Applicant, CASE_ID)
    documents_before = store.list_table_entities(SourceDocument, CASE_ID)
    packages_before = store.list_table_entities(CandidatePackage, CASE_ID)
    events_before = store.list_table_entities(CaseEvent, CASE_ID)
    blobs_before = _blob_files(store)

    locked_service = _service(
        store,
        candidate_ids=["cand-e12-should-not-write"],
        document_ids=["doc-e12-should-not-write"],
        event_ids=[
            "evt-e12-locked-applicant",
            "evt-e12-locked-document",
            "evt-e12-locked-import",
        ],
    )

    applicant_attempt = locked_service.register_applicant(
        CASE_ID,
        _applicant_request(
            candidate_ref="E12-AFTER-CONFIRM",
            display_label="After Confirm Candidate",
        ),
        _actor(),
    )
    document_attempt = locked_service.register_candidate_document(
        CASE_ID,
        "cand-e12-locked",
        _document_request(content_text="Synthetic text that must not be persisted."),
        _actor(),
    )
    import_attempt = locked_service.process_import(
        CASE_ID,
        _import_request(
            [
                {
                    "candidate_ref": "E12-IMPORT-AFTER-CONFIRM",
                    "display_label": "Import After Confirm",
                    "documents": [_document_request().model_dump(mode="json")],
                }
            ]
        ),
        _actor(),
    )

    for snapshot in (applicant_attempt, document_attempt, import_attempt):
        assert snapshot.error == "applicant_set_locked"
        assert snapshot.safe_details == "confirmed_applicant_set_version='v1'"

    assert _blob_files(store) == blobs_before
    assert store.get_table_entity(RecruitmentCase, CASE_ID, "case") == case_before
    assert (
        store.get_table_entity(
            WorkflowGate,
            CASE_ID,
            "gate#applicant_set_confirmation_required",
        )
        == gate_before
    )
    assert store.list_table_entities(Applicant, CASE_ID) == applicants_before
    assert store.list_table_entities(SourceDocument, CASE_ID) == documents_before
    assert store.list_table_entities(CandidatePackage, CASE_ID) == packages_before
    assert store.list_table_entities(CaseEvent, CASE_ID) == events_before
    assert case_before is not None
    assert case_before.current_stage == "stage_6_assessment_readiness_pending"
    assert case_before.current_gate == "assessment_unlocked"
    assert case_before.applicant_set_version == "v1"
