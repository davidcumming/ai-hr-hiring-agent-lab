"""Escalation decision logic (BR-003…BR-006; OQ-002 decided: auto_escalate
is IMPLEMENTED behind server-side config, default remains record_only).

``escalation_provenance`` (none | configured_escalated | policy_triggered) is
recorded on every record — silence in either direction is structurally
impossible (UFM-008).
"""

from __future__ import annotations

from dataclasses import dataclass

from hr_eval_lab.config import EscalationPolicy, RigorMode
from hr_eval_lab.domain.schemas.evaluation import TriggerResult


@dataclass
class EscalationDecision:
    policy: EscalationPolicy
    provenance: str  # none | configured_escalated | policy_triggered
    triggers_fired: list[str]
    run_mode_c: bool
    rationale: str
    human_review_mandatory_reason: str | None


def decide_escalation(
    effective_rigor: RigorMode,
    policy: EscalationPolicy,
    triggers: list[TriggerResult],
) -> EscalationDecision:
    fired = [t.trigger_id for t in triggers if t.fired]

    if effective_rigor == "escalated":
        return EscalationDecision(
            policy=policy,
            provenance="configured_escalated",
            triggers_fired=fired,
            run_mode_c=True,
            rationale=(
                "Server configuration sets effective_rigor=escalated; the Mode C "
                "extension roles execute unconditionally and human review is "
                "mandatory (BR-003)."
            ),
            human_review_mandatory_reason="configured_escalated_mode",
        )

    if fired and policy == "auto_escalate":
        return EscalationDecision(
            policy=policy,
            provenance="policy_triggered",
            triggers_fired=fired,
            run_mode_c=True,
            rationale=(
                f"Escalation triggers fired ({', '.join(fired)}) and "
                "escalation.policy=auto_escalate; the Mode C extension roles "
                "execute with policy_triggered provenance (BR-005, implemented "
                "branch per OQ-002 decision)."
            ),
            human_review_mandatory_reason="policy_triggered_escalation",
        )

    if fired:
        return EscalationDecision(
            policy=policy,
            provenance="none",
            triggers_fired=fired,
            run_mode_c=False,
            rationale=(
                f"Escalation triggers fired ({', '.join(fired)}) but "
                "escalation.policy=record_only: triggers, rationale, and "
                "human-review flags are recorded; NO Mode C roles run (BR-004)."
            ),
            human_review_mandatory_reason=None,
        )

    return EscalationDecision(
        policy=policy,
        provenance="none",
        triggers_fired=[],
        run_mode_c=False,
        rationale="No escalation trigger fired; no escalation occurred.",
        human_review_mandatory_reason=None,
    )
