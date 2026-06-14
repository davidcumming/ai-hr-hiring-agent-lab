"""Deterministic recruitment case service for the E9 facade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, cast

from hr_eval_lab.domain import ids
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    CaseEventSummary,
    CaseNextAction,
    CaseNextActionsResult,
    CaseParticipantSummary,
    CaseSummary,
    CaseTaskSummary,
    RecruitmentCaseCreateRequest,
    RecruitmentCaseResult,
    WorkflowGateSummary,
)
from hr_eval_lab.domain.schemas.workflow import (
    CaseEvent,
    CaseParticipant,
    CaseTask,
    RecruitmentCase,
    WorkflowGate,
)
from hr_eval_lab.persistence.workflow_storage import WorkflowStorageBackend

HR_WORKFLOW_ROLE = "hr_specialist"

_TASK_ACTION_TEXT: dict[str, tuple[str, str]] = {
    "complete_role_intake": (
        "Complete role intake",
        "Capture the role context before drafting postings, rubrics, or assessments.",
    ),
    "attach_source_documents": (
        "Attach source documents",
        "Add role source material before downstream workflow steps can proceed.",
    ),
    "confirm_hiring_manager": (
        "Confirm hiring manager",
        "Confirm the hiring manager participant before role approvals are requested.",
    ),
}


@dataclass(frozen=True)
class CaseSnapshot:
    case_id: str
    correlation_id: str | None
    result: RecruitmentCaseResult


@dataclass(frozen=True)
class NextActionsSnapshot:
    case_id: str
    correlation_id: str | None
    result: CaseNextActionsResult


class RecruitmentCaseService:
    """Case workflow logic over the E7/E8 workflow storage protocol only."""

    def __init__(
        self,
        storage: WorkflowStorageBackend,
        *,
        case_id_fn: Callable[[], str] = ids.new_case_id,
        event_id_fn: Callable[[], str] = ids.new_event_id,
        now_fn: Callable[[], str] = ids.utc_now_iso,
    ) -> None:
        self._storage = storage
        self._case_id_fn = case_id_fn
        self._event_id_fn = event_id_fn
        self._now_fn = now_fn

    def create_case(
        self,
        request: RecruitmentCaseCreateRequest,
        actor: ActorContext,
    ) -> CaseSnapshot:
        case_id = self._case_id_fn()
        correlation_id = ids.correlation_id_for_case(case_id)
        created_at = self._now_fn()
        hiring_manager = request.hiring_manager
        hiring_manager_actor_id = (
            hiring_manager.actor_id if hiring_manager is not None else None
        )

        case = RecruitmentCase(
            PartitionKey=case_id,
            RowKey="case",
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=correlation_id,
            case_id=case_id,
            case_title=request.resolved_case_title,
            role_title=request.role_title,
            department=request.department,
            recruitment_type=request.recruitment_type,
            case_status="intake_pending",
            current_stage="stage_1_start_or_continue",
            current_gate="role_intake_required",
            hr_owner_actor_id=actor.actor_id,
            primary_hiring_manager_actor_id=hiring_manager_actor_id,
        )
        entities = [case]

        entities.append(
            CaseParticipant(
                PartitionKey=case_id,
                RowKey=f"hr_specialist#{actor.actor_id}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=correlation_id,
                case_id=case_id,
                actor_id=actor.actor_id,
                display_name=actor.display,
                case_role=HR_WORKFLOW_ROLE,
                scope={"case_id": case_id},
                status="active",
            )
        )

        if hiring_manager is not None:
            entities.append(
                CaseParticipant(
                    PartitionKey=case_id,
                    RowKey=f"hiring_manager#{hiring_manager.actor_id}",
                    created_at=created_at,
                    created_by_actor_id=actor.actor_id,
                    created_by_role=HR_WORKFLOW_ROLE,
                    correlation_id=correlation_id,
                    case_id=case_id,
                    actor_id=hiring_manager.actor_id,
                    display_name=hiring_manager.display_name,
                    case_role="hiring_manager",
                    required_for_approval=True,
                    scope={"case_id": case_id},
                    status="active",
                )
            )

        entities.extend(
            self._initial_tasks(
                case_id=case_id,
                created_at=created_at,
                correlation_id=correlation_id,
                actor=actor,
                hiring_manager_actor_id=hiring_manager_actor_id,
                hiring_manager_confirmed=(
                    hiring_manager.confirmed if hiring_manager is not None else False
                ),
            )
        )
        entities.extend(
            self._initial_gates(
                case_id=case_id,
                created_at=created_at,
                correlation_id=correlation_id,
                actor=actor,
            )
        )

        event_id = self._event_id_fn()
        entities.append(
            CaseEvent(
                PartitionKey=case_id,
                RowKey=f"{created_at}#{event_id}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=correlation_id,
                case_id=case_id,
                event_id=event_id,
                event_type="case_created",
                actor_id=actor.actor_id,
                actor_role=HR_WORKFLOW_ROLE,
                summary="Recruitment case created.",
                safe_details={
                    "role_title": request.role_title,
                    "department": request.department,
                    "recruitment_type": request.recruitment_type,
                    "hiring_manager_supplied": hiring_manager is not None,
                    "hiring_manager_confirmed": (
                        hiring_manager.confirmed
                        if hiring_manager is not None
                        else False
                    ),
                },
            )
        )

        for entity in entities:
            self._storage.upsert_table_entity(entity)

        snapshot = self.get_case(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"created case {case_id!r} was not readable")
        return snapshot

    def get_case(self, case_id: str) -> CaseSnapshot | None:
        case = cast(
            RecruitmentCase | None,
            self._storage.get_table_entity(RecruitmentCase, case_id, "case"),
        )
        if case is None:
            return None

        participants = [
            cast(CaseParticipant, row)
            for row in self._storage.list_table_entities(
                CaseParticipant, partition_key=case_id
            )
        ]
        tasks = [
            cast(CaseTask, row)
            for row in self._storage.list_table_entities(CaseTask, partition_key=case_id)
        ]
        gates = [
            cast(WorkflowGate, row)
            for row in self._storage.list_table_entities(
                WorkflowGate, partition_key=case_id
            )
        ]
        events = [
            cast(CaseEvent, row)
            for row in self._storage.list_table_entities(
                CaseEvent, partition_key=case_id
            )
        ]

        open_tasks = [
            self._task_summary(task)
            for task in sorted(tasks, key=lambda task: task.RowKey)
            if task.status == "open"
        ]
        gate_summaries = [
            self._gate_summary(gate)
            for gate in sorted(gates, key=lambda gate: gate.RowKey)
        ]
        next_actions = self._next_actions(tasks, gates)

        return CaseSnapshot(
            case_id=case.case_id,
            correlation_id=case.correlation_id,
            result=RecruitmentCaseResult(
                case=self._case_summary(case),
                participants=[
                    self._participant_summary(participant)
                    for participant in sorted(
                        participants, key=lambda participant: participant.RowKey
                    )
                ],
                open_tasks=open_tasks,
                gates=gate_summaries,
                events=[
                    self._event_summary(event)
                    for event in sorted(events, key=lambda event: event.RowKey)
                ],
                next_actions=next_actions,
            ),
        )

    def get_next_actions(self, case_id: str) -> NextActionsSnapshot | None:
        snapshot = self.get_case(case_id)
        if snapshot is None:
            return None

        tasks = [
            cast(CaseTask, row)
            for row in self._storage.list_table_entities(CaseTask, partition_key=case_id)
        ]
        gates = [
            cast(WorkflowGate, row)
            for row in self._storage.list_table_entities(
                WorkflowGate, partition_key=case_id
            )
        ]
        open_tasks = [
            self._task_summary(task)
            for task in sorted(tasks, key=lambda task: task.RowKey)
            if task.status == "open"
        ]
        blocked_tasks = [
            self._task_summary(task)
            for task in sorted(tasks, key=lambda task: task.RowKey)
            if task.status == "blocked"
        ]
        active_gate_blockers = [
            self._gate_summary(gate)
            for gate in sorted(gates, key=lambda gate: gate.RowKey)
            if gate.gate_status in {"blocked", "locked"} and gate.blocking_reasons
        ]
        return NextActionsSnapshot(
            case_id=case_id,
            correlation_id=snapshot.correlation_id,
            result=CaseNextActionsResult(
                case_id=case_id,
                open_tasks=open_tasks,
                blocked_tasks=blocked_tasks,
                active_gate_blockers=active_gate_blockers,
                next_actions=self._next_actions(tasks, gates),
            ),
        )

    def _initial_tasks(
        self,
        *,
        case_id: str,
        created_at: str,
        correlation_id: str,
        actor: ActorContext,
        hiring_manager_actor_id: str | None,
        hiring_manager_confirmed: bool,
    ) -> list[CaseTask]:
        task_specs: list[dict[str, str | None]] = [
            {
                "task_id": "complete_role_intake",
                "task_type": "complete_role_intake",
                "assigned_role": HR_WORKFLOW_ROLE,
                "assigned_actor_id": actor.actor_id,
                "blocking_gate": "role_intake_required",
            },
            {
                "task_id": "attach_source_documents",
                "task_type": "attach_source_documents",
                "assigned_role": HR_WORKFLOW_ROLE,
                "assigned_actor_id": actor.actor_id,
                "blocking_gate": "source_documents_required",
            },
        ]
        if not hiring_manager_confirmed:
            task_specs.append(
                {
                    "task_id": "confirm_hiring_manager",
                    "task_type": "confirm_hiring_manager",
                    "assigned_role": (
                        "hiring_manager"
                        if hiring_manager_actor_id is not None
                        else HR_WORKFLOW_ROLE
                    ),
                    "assigned_actor_id": hiring_manager_actor_id or actor.actor_id,
                    "blocking_gate": "role_intake_required",
                }
            )

        return [
            CaseTask(
                PartitionKey=case_id,
                RowKey=f"task#{spec['task_id']}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=correlation_id,
                case_id=case_id,
                task_id=cast(str, spec["task_id"]),
                task_type=cast(str, spec["task_type"]),
                assigned_role=cast(str, spec["assigned_role"]),
                assigned_actor_id=spec["assigned_actor_id"],
                status="open",
                blocking_gate=spec["blocking_gate"],
            )
            for spec in task_specs
        ]

    def _initial_gates(
        self,
        *,
        case_id: str,
        created_at: str,
        correlation_id: str,
        actor: ActorContext,
    ) -> list[WorkflowGate]:
        gate_specs = [
            (
                "role_intake_required",
                "blocked",
                ["role_intake"],
                ["Role intake has not been completed."],
            ),
            (
                "source_documents_required",
                "blocked",
                ["source_documents"],
                ["Role source documents have not been attached."],
            ),
            (
                "rubric_approval_required",
                "blocked",
                ["approved_rubric_version"],
                ["Screening rubric has not been approved."],
            ),
            (
                "applicant_set_confirmation_required",
                "blocked",
                ["confirmed_applicant_set"],
                ["Applicant set has not been confirmed."],
            ),
            (
                "assessment_unlocked",
                "locked",
                [
                    "role_intake_required",
                    "source_documents_required",
                    "rubric_approval_required",
                    "applicant_set_confirmation_required",
                ],
                ["Assessment remains locked until prerequisite gates are satisfied."],
            ),
        ]
        return [
            WorkflowGate(
                PartitionKey=case_id,
                RowKey=f"gate#{gate_id}",
                created_at=created_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=correlation_id,
                case_id=case_id,
                gate_id=gate_id,
                gate_status=cast(str, status),
                required_inputs=required_inputs,
                blocking_reasons=blocking_reasons,
                last_checked_at=created_at,
            )
            for gate_id, status, required_inputs, blocking_reasons in gate_specs
        ]

    def _next_actions(
        self, tasks: list[CaseTask], gates: list[WorkflowGate]
    ) -> list[CaseNextAction]:
        del gates
        actions: list[CaseNextAction] = []
        for task in sorted(tasks, key=lambda task: task.RowKey):
            if task.status not in {"open", "blocked"}:
                continue
            label, description = _TASK_ACTION_TEXT.get(
                task.task_type,
                (
                    task.task_type.replace("_", " ").title(),
                    "Review this open recruitment-case task.",
                ),
            )
            actions.append(
                CaseNextAction(
                    action_id=task.task_type,
                    task_id=task.task_id,
                    label=label,
                    description=description,
                    assigned_role=task.assigned_role,
                    assigned_actor_id=task.assigned_actor_id,
                    blocker_ids=[task.blocking_gate] if task.blocking_gate else [],
                )
            )
        return actions

    def _case_summary(self, case: RecruitmentCase) -> CaseSummary:
        return CaseSummary(
            case_id=case.case_id,
            case_title=case.case_title,
            role_title=case.role_title,
            department=case.department,
            recruitment_type=case.recruitment_type,
            case_status=case.case_status,
            current_stage=case.current_stage,
            current_gate=case.current_gate,
            hr_owner_actor_id=case.hr_owner_actor_id,
            primary_hiring_manager_actor_id=case.primary_hiring_manager_actor_id,
            active_intake_version=case.active_intake_version,
            active_rubric_version=case.active_rubric_version,
            created_at=case.created_at,
            updated_at=case.updated_at,
            correlation_id=case.correlation_id,
            synthetic=case.synthetic,
        )

    def _participant_summary(
        self, participant: CaseParticipant
    ) -> CaseParticipantSummary:
        return CaseParticipantSummary(
            actor_id=participant.actor_id,
            display_name=participant.display_name,
            case_role=participant.case_role,
            required_for_review=participant.required_for_review,
            required_for_approval=participant.required_for_approval,
            scope=participant.scope,
            status=participant.status,
        )

    def _task_summary(self, task: CaseTask) -> CaseTaskSummary:
        return CaseTaskSummary(
            task_id=task.task_id,
            task_type=task.task_type,
            assigned_role=task.assigned_role,
            assigned_actor_id=task.assigned_actor_id,
            status=task.status,
            blocking_gate=task.blocking_gate,
        )

    def _gate_summary(self, gate: WorkflowGate) -> WorkflowGateSummary:
        return WorkflowGateSummary(
            gate_id=gate.gate_id,
            gate_status=gate.gate_status,
            required_inputs=gate.required_inputs,
            blocking_reasons=gate.blocking_reasons,
            last_checked_at=gate.last_checked_at,
        )

    def _event_summary(self, event: CaseEvent) -> CaseEventSummary:
        return CaseEventSummary(
            event_id=event.event_id,
            event_type=event.event_type,
            actor_id=event.actor_id,
            actor_role=event.actor_role,
            summary=event.summary,
            safe_details=event.safe_details,
            created_at=event.created_at,
        )
