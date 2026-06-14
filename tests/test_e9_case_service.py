"""E9 recruitment case service over the workflow storage seam."""

from __future__ import annotations

from hr_eval_lab.cases.service import RecruitmentCaseService
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import RecruitmentCaseCreateRequest
from hr_eval_lab.domain.schemas.workflow import (
    CaseEvent,
    CaseParticipant,
    CaseTask,
    RecruitmentCase,
    WorkflowGate,
)
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore

TS = "2026-06-13T12:00:00Z"


def _actor(actor_id: str = "u-hr-e9") -> ActorContext:
    return ActorContext(
        actor_id=actor_id,
        display="E9 HR Owner",
        roles=["hr"],
        resolved_role="hr",
    )


def _request(**overrides) -> RecruitmentCaseCreateRequest:
    body = {
        "role_title": "Synthetic HR Analyst",
        "department": "Synthetic Lab",
        "recruitment_type": "permanent",
    }
    body.update(overrides)
    return RecruitmentCaseCreateRequest.model_validate(body)


def _service(store: LocalWorkflowStore, case_id: str = "case-e9-001"):
    event_ids = iter(["evt-e9-001", "evt-e9-002"])
    return RecruitmentCaseService(
        store,
        case_id_fn=lambda: case_id,
        event_id_fn=lambda: next(event_ids),
        now_fn=lambda: TS,
    )


def _task_types(tasks: list[CaseTask]) -> set[str]:
    return {task.task_type for task in tasks}


def test_e9_create_case_with_missing_hiring_manager_persists_initial_state(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    snapshot = _service(store).create_case(_request(), _actor())

    assert snapshot.case_id == "case-e9-001"
    assert snapshot.correlation_id == "corr-e9-001"
    assert snapshot.result.case.primary_hiring_manager_actor_id is None
    assert snapshot.result.case.case_title == "Synthetic HR Analyst - Synthetic Lab"
    assert [a.action_id for a in snapshot.result.next_actions] == [
        "attach_source_documents",
        "complete_role_intake",
        "confirm_hiring_manager",
    ]

    cases = store.list_table_entities(RecruitmentCase, "case-e9-001")
    participants = store.list_table_entities(CaseParticipant, "case-e9-001")
    tasks = store.list_table_entities(CaseTask, "case-e9-001")
    gates = store.list_table_entities(WorkflowGate, "case-e9-001")
    events = store.list_table_entities(CaseEvent, "case-e9-001")

    assert len(cases) == 1
    assert len(participants) == 1
    assert participants[0].case_role == "hr_specialist"
    assert len(tasks) == 3
    assert _task_types(tasks) == {
        "complete_role_intake",
        "attach_source_documents",
        "confirm_hiring_manager",
    }
    assert len(gates) == 5
    assert {gate.gate_id for gate in gates} == {
        "role_intake_required",
        "source_documents_required",
        "rubric_approval_required",
        "applicant_set_confirmation_required",
        "assessment_unlocked",
    }
    assert len(events) == 1
    assert events[0].event_type == "case_created"
    assert events[0].created_by_actor_id == "u-hr-e9"
    assert events[0].created_by_role == "hr_specialist"
    assert store.peek_queue_messages() == []
    assert not any(store.blobs_root.rglob("*"))


def test_e9_create_case_with_confirmed_hiring_manager_omits_confirmation_task(
    tmp_path,
):
    store = LocalWorkflowStore(tmp_path)
    request = _request(
        case_title="Synthetic analyst search",
        hiring_manager={
            "actor_id": "u-hm-e9",
            "display_name": "E9 Hiring Manager",
            "confirmed": True,
        },
    )

    snapshot = _service(store, case_id="case-e9-002").create_case(request, _actor())

    assert snapshot.result.case.primary_hiring_manager_actor_id == "u-hm-e9"
    assert snapshot.result.case.case_title == "Synthetic analyst search"
    participants = store.list_table_entities(CaseParticipant, "case-e9-002")
    tasks = store.list_table_entities(CaseTask, "case-e9-002")

    assert {participant.case_role for participant in participants} == {
        "hr_specialist",
        "hiring_manager",
    }
    assert _task_types(tasks) == {"complete_role_intake", "attach_source_documents"}
    assert "confirm_hiring_manager" not in [
        action.action_id for action in snapshot.result.next_actions
    ]


def test_e9_get_case_does_not_fabricate_missing_case_state(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    store.upsert_table_entity(
        RecruitmentCase(
            PartitionKey="case-e9-partial",
            RowKey="case",
            created_at=TS,
            created_by_actor_id="u-hr-e9",
            created_by_role="hr_specialist",
            correlation_id="corr-e9-partial",
            case_id="case-e9-partial",
            case_title="Partial persisted case",
            role_title="Synthetic Role",
            department="Synthetic Lab",
            recruitment_type="permanent",
            case_status="intake_pending",
            current_stage="stage_1_start_or_continue",
            current_gate="role_intake_required",
            hr_owner_actor_id="u-hr-e9",
        )
    )

    snapshot = _service(store, case_id="unused").get_case("case-e9-partial")

    assert snapshot is not None
    assert snapshot.result.participants == []
    assert snapshot.result.open_tasks == []
    assert snapshot.result.gates == []
    assert snapshot.result.events == []
    assert snapshot.result.next_actions == []


def test_e9_next_actions_report_open_tasks_and_gate_blockers(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    service = _service(store)
    service.create_case(_request(), _actor())

    snapshot = service.get_next_actions("case-e9-001")

    assert snapshot is not None
    assert [task.task_type for task in snapshot.result.open_tasks] == [
        "attach_source_documents",
        "complete_role_intake",
        "confirm_hiring_manager",
    ]
    assert snapshot.result.blocked_tasks == []
    assert {gate.gate_id for gate in snapshot.result.active_gate_blockers} == {
        "role_intake_required",
        "source_documents_required",
        "rubric_approval_required",
        "applicant_set_confirmation_required",
        "assessment_unlocked",
    }
    assert all("model" not in action.description.lower() for action in snapshot.result.next_actions)
