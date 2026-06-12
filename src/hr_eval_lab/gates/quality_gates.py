"""The six deterministic quality gates (FR-008, DT-006).

All gates are deterministic code; each produces
``{gate_id, result, reason, details_safe}`` recorded on every run. Any gate
failure maps to envelope status ``blocked`` (within the adopted vocabulary —
API-contracts §5.6 precedent), with the full record still persisted and a
human-review queue entry written.

Gate 3 interpretation note (recorded design decision): the pass condition is
"every score cites >=1 mechanically resolving supporting reference" — except a
criterion carrying an explicit ``missing_evidence_note`` with the conservative
floor posture, which is the BR-013/DT-015 sanctioned path (missing evidence is
surfaced, never fabricated; fabricated citations remain the UFM-003 blocking
fail this gate exists to catch).
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas.audit import EvidencePacket, RoleExecution
from hr_eval_lab.domain.schemas.evaluation import GateResult

#: Prohibited factor / proxy terms that must never appear as scoring rationale
#: (BR-008; rubric prohibited_factors_note). Scanned over rationale fields.
PROHIBITED_RATIONALE_TERMS = (
    "age",
    "gender",
    "race",
    "religion",
    "nationality",
    "national origin",
    "disability",
    "family status",
    "married",
    "children",
    "school prestige",
    "address prestige",
    "employment gap",
    "photograph",
)

GATE_IDS = [
    "schema_validity",
    "all_criteria_scored",
    "evidence_per_score",
    "no_prohibited_factors",
    "human_review_flag_present",
    "groundedness_heuristic",
]


def _resolvable_ids(packet: EvidencePacket, evidence_items: list[dict]) -> set[str]:
    ids = {seg.segment_id for seg in packet.segments}
    ids.update(i["evidence_id"] for i in evidence_items)
    return ids


def run_gates(
    packet: EvidencePacket,
    role_executions: list[RoleExecution],
    evidence_items: list[dict],
    synthesis: dict | None,
    fairness: dict | None,
    flags_present: bool,
) -> list[GateResult]:
    """Run all six gates; always returns all six results in fixed order."""
    results: list[GateResult] = []
    criteria_ids = [c.criterion_id for c in packet.rubric.criteria]
    evaluations = (synthesis or {}).get("criterion_evaluations", [])
    by_criterion = {e["criterion_id"]: e for e in evaluations}

    # Gate 1 — schema validity (retry accounting done by the orchestrator;
    # a role left schema-invalid after its single bounded retry fails here).
    invalid = [r.role_id for r in role_executions if not r.schema_valid]
    over_retried = [r.role_id for r in role_executions if r.retry_count > 1]
    ok = not invalid and not over_retried
    results.append(
        GateResult(
            gate_id="schema_validity",
            result="pass" if ok else "fail",
            reason=(
                "every role output validated against its declared schema "
                "(retry_count <= 1)"
                if ok
                else f"schema-invalid role output after bounded retry: {invalid or over_retried}"
            ),
        )
    )

    # Gate 2 — all-criteria-scored
    missing = [cid for cid in criteria_ids if cid not in by_criterion]
    bad_scores = [
        e["criterion_id"]
        for e in evaluations
        if not isinstance(e.get("score"), int) or not (1 <= e["score"] <= 5)
    ]
    ok = synthesis is not None and not missing and not bad_scores
    results.append(
        GateResult(
            gate_id="all_criteria_scored",
            result="pass" if ok else "fail",
            reason=(
                f"all {len(criteria_ids)} rubric criteria carry an integer score 1-5"
                if ok
                else f"criteria unscored or out of range: missing={missing}, invalid={bad_scores}"
            ),
        )
    )

    # Gate 3 — evidence-per-score (see module docstring for the recorded
    # missing-evidence-note interpretation).
    resolvable = _resolvable_ids(packet, evidence_items)
    gate3_failures = []
    for e in evaluations:
        citations = list(e.get("supporting_evidence", [])) + list(
            e.get("contrary_evidence", [])
        )
        unresolved = [c for c in citations if c not in resolvable]
        if unresolved:
            gate3_failures.append(f"{e['criterion_id']}: unresolvable {unresolved}")
        elif not e.get("supporting_evidence") and not e.get("missing_evidence_note"):
            gate3_failures.append(
                f"{e['criterion_id']}: no supporting citation and no missing-evidence note"
            )
    ok = synthesis is not None and not gate3_failures
    results.append(
        GateResult(
            gate_id="evidence_per_score",
            result="pass" if ok else "fail",
            reason=(
                "every score cites resolvable evidence or carries an explicit "
                "missing-evidence note"
                if ok
                else "; ".join(gate3_failures) or "no synthesis output"
            ),
        )
    )

    # Gate 4 — no-prohibited-factors (deterministic scan over scoring
    # rationale fields; auditor findings must be surfaced, never dropped).
    rationale_hits = []
    for e in evaluations:
        text = str(e.get("rationale", "")).lower()
        for term in PROHIBITED_RATIONALE_TERMS:
            if term in text:
                rationale_hits.append(f"{e['criterion_id']}: '{term}'")
    auditor_dropped = False
    if fairness is not None:
        flagged_ids = {f.get("finding_id") for f in fairness.get("findings", [])}
        auditor_dropped = bool(fairness.get("prohibited_factor_violations")) and not flagged_ids
    ok = not rationale_hits and not auditor_dropped
    results.append(
        GateResult(
            gate_id="no_prohibited_factors",
            result="pass" if ok else "fail",
            reason=(
                "no prohibited factor or proxy term appears as scoring rationale; "
                "auditor findings preserved"
                if ok
                else f"prohibited-factor terms in rationale: {rationale_hits}"
                + ("; auditor findings dropped" if auditor_dropped else "")
            ),
        )
    )

    # Gate 5 — human-review flags present (belt-and-braces: the Literal[True]
    # schema makes the failing state nearly unconstructible).
    results.append(
        GateResult(
            gate_id="human_review_flag_present",
            result="pass" if flags_present else "fail",
            reason=(
                "decision_support_only=true and human_review_required=true present"
                if flags_present
                else "mandatory advisory flags missing or not true"
            ),
        )
    )

    # Gate 6 — groundedness heuristic
    segments_by_id = {seg.segment_id: seg.text for seg in packet.segments}
    ungrounded = []
    for item in evidence_items:
        segment_text = segments_by_id.get(item["segment_id"])
        if segment_text is None or item["quote"] not in segment_text:
            ungrounded.append(item["evidence_id"])
    note_missing = [
        e["criterion_id"]
        for e in evaluations
        if not e.get("supporting_evidence") and not e.get("missing_evidence_note")
    ]
    ok = not ungrounded and not note_missing
    results.append(
        GateResult(
            gate_id="groundedness_heuristic",
            result="pass" if ok else "fail",
            reason=(
                "quoted evidence spans verbatim in referenced segments; "
                "missing-evidence notes present where required"
                if ok
                else f"ungrounded quotes: {ungrounded}; criteria missing notes: {note_missing}"
            ),
        )
    )

    return results
