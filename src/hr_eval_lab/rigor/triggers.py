"""The six escalation-trigger computations — pure functions, EVERY run (FR-011).

All six are computed and recorded regardless of escalation policy; triggers are
audit data even when not acted on. For ``standard``-mode runs the roles not in
mode are recorded as ``not_computed_inputs`` with the trigger still evaluated
over available outputs — no silent omission.

Thresholds are source-controlled constants here (first-cut values; tuning is
deferred to the calibration slice, RF-008). Integer arithmetic only.
"""

from __future__ import annotations

from typing import Any

from hr_eval_lab.domain.schemas import council as c
from hr_eval_lab.domain.schemas.evaluation import TriggerResult

# Source-controlled thresholds (documented in current-state docs at Stage 12).
SCORE_VARIANCE_THRESHOLD = 3  # max-min spread across role-proposed scores
SYNTHESIS_CONFIDENCE_THRESHOLD = 40  # confidence_score below this fires
FAIRNESS_SEVERITY_THRESHOLD = "high"  # overall severity at/above this fires
THRESHOLD_PROXIMITY_MARGIN = 1  # required-criterion score within this of boundary 3
REQUIRED_CRITERIA_KINDS = ("required",)

TRIGGER_IDS = [
    "score_variance_above_threshold",
    "evidence_packet_missing_required_criteria",
    "synthesis_confidence_low",
    "policy_fairness_severity_high",
    "recommendation_near_decision_threshold",
    "criterion_scored_with_no_direct_evidence",
]


def _proposals_by_role(prior_outputs: dict[str, dict]) -> dict[str, dict[str, int]]:
    """role_id -> {criterion_id: proposed score} for all proposal-bearing roles."""
    out: dict[str, dict[str, int]] = {}
    role_fields = {
        c.ROLE_MERIT_ADVOCATE: "proposed_scores",
        c.ROLE_RISK_GAPS_ADVOCATE: "proposed_scores",
        c.ROLE_NEUTRAL_SCORING_JUDGE: "scores",
    }
    for role_id, field in role_fields.items():
        payload = prior_outputs.get(role_id)
        if payload:
            out[role_id] = {s["criterion_id"]: s["score"] for s in payload.get(field, [])}
    synthesis = prior_outputs.get(c.ROLE_SYNTHESIS_JUDGE)
    if synthesis:
        out[c.ROLE_SYNTHESIS_JUDGE] = {
            e["criterion_id"]: e["score"]
            for e in synthesis.get("criterion_evaluations", [])
        }
    return out


def compute_triggers(
    prior_outputs: dict[str, dict],
    required_criteria: list[str],
    roles_in_mode: list[str],
    rubric_criteria: list[str],
) -> list[TriggerResult]:
    """Compute all six triggers from base-mode outputs (pre-extension)."""
    results: list[TriggerResult] = []
    synthesis = prior_outputs.get(c.ROLE_SYNTHESIS_JUDGE, {})
    extraction = prior_outputs.get(c.ROLE_EVIDENCE_EXTRACTION, {})
    evaluations = synthesis.get("criterion_evaluations", [])

    # 1. score_variance_above_threshold
    proposals = _proposals_by_role(prior_outputs)
    max_spread = 0
    for criterion_id in rubric_criteria:
        scores = [m[criterion_id] for m in proposals.values() if criterion_id in m]
        if len(scores) >= 2:
            max_spread = max(max_spread, max(scores) - min(scores))
    not_computed_1 = [
        r
        for r in (c.ROLE_NEUTRAL_SCORING_JUDGE,)
        if r not in roles_in_mode
    ]
    results.append(
        TriggerResult(
            trigger_id="score_variance_above_threshold",
            fired=max_spread >= SCORE_VARIANCE_THRESHOLD,
            computed_value=f"max_criterion_score_spread={max_spread}",
            threshold=f"spread>={SCORE_VARIANCE_THRESHOLD}",
            not_computed_inputs=not_computed_1,
        )
    )

    # 2. evidence_packet_missing_required_criteria
    covered = {i["criterion_id"] for i in extraction.get("evidence_items", [])}
    missing_required = sorted(set(required_criteria) - covered)
    results.append(
        TriggerResult(
            trigger_id="evidence_packet_missing_required_criteria",
            fired=bool(missing_required),
            computed_value=f"required_criteria_without_evidence={missing_required}",
            threshold="any required criterion (C1-C4) with zero evidence items",
        )
    )

    # 3. synthesis_confidence_low
    confidence_score = int(synthesis.get("confidence_score", 0))
    results.append(
        TriggerResult(
            trigger_id="synthesis_confidence_low",
            fired=confidence_score < SYNTHESIS_CONFIDENCE_THRESHOLD,
            computed_value=f"confidence_score={confidence_score}",
            threshold=f"confidence_score<{SYNTHESIS_CONFIDENCE_THRESHOLD}",
        )
    )

    # 4. policy_fairness_severity_high
    auditor = prior_outputs.get(c.ROLE_POLICY_FAIRNESS_AUDITOR)
    not_computed_4 = (
        [] if c.ROLE_POLICY_FAIRNESS_AUDITOR in roles_in_mode else [c.ROLE_POLICY_FAIRNESS_AUDITOR]
    )
    severity = (auditor or {}).get("overall_severity", "info")
    results.append(
        TriggerResult(
            trigger_id="policy_fairness_severity_high",
            fired=severity == FAIRNESS_SEVERITY_THRESHOLD,
            computed_value=f"overall_severity={severity}",
            threshold=f"overall_severity>={FAIRNESS_SEVERITY_THRESHOLD}",
            not_computed_inputs=not_computed_4,
        )
    )

    # 5. recommendation_near_decision_threshold
    # Label boundary: required criteria score >= 3. Proximity = any required
    # criterion sitting exactly within the margin of that boundary.
    near = sorted(
        e["criterion_id"]
        for e in evaluations
        if e["criterion_id"] in required_criteria
        and abs(e["score"] - 3) < THRESHOLD_PROXIMITY_MARGIN
    )
    results.append(
        TriggerResult(
            trigger_id="recommendation_near_decision_threshold",
            fired=bool(near),
            computed_value=f"required_criteria_at_boundary={near}",
            threshold=(
                f"required criterion score within {THRESHOLD_PROXIMITY_MARGIN - 1} "
                "of the label boundary (anchor 3)"
            ),
        )
    )

    # 6. criterion_scored_with_no_direct_evidence
    unevidenced = sorted(
        e["criterion_id"] for e in evaluations if not e.get("supporting_evidence")
    )
    results.append(
        TriggerResult(
            trigger_id="criterion_scored_with_no_direct_evidence",
            fired=bool(unevidenced),
            computed_value=f"criteria_scored_without_direct_evidence={unevidenced}",
            threshold="any scored criterion with zero direct evidence citations",
        )
    )

    return results
