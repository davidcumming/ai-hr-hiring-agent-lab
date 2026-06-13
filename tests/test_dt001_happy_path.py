"""DT-001 — Happy path, full FR-007 result envelope.

Related: AC-001, AC-002, FR-001, FR-007, BR-007, UFM-003, UFM-006.

POST a fixture-candidate evaluation, then GET the full audit record, asserting
every FR-007 envelope field: criterion scores 1-5 on all 6 rubric criteria,
supporting/contrary/missing evidence per criterion, disagreements with
resolution rationale, fairness block, confidence, limitations, advisory label
enum, both mandatory flags literal-true, effective rigor + explanation,
triggers + escalation policy, gate results, and provider metadata.
"""

from __future__ import annotations

from tests.conftest import HR_HEADERS, get_record, post_evaluation

ADVISORY_LABELS = {
    "advance_to_interview",
    "do_not_advance",
    "hold_for_review",
    "insufficient_evidence",
}

TRIGGER_IDS = {
    "score_variance_above_threshold",
    "evidence_packet_missing_required_criteria",
    "synthesis_confidence_low",
    "policy_fairness_severity_high",
    "recommendation_near_decision_threshold",
    "criterion_scored_with_no_direct_evidence",
}

GATE_IDS = {
    "schema_validity",
    "all_criteria_scored",
    "evidence_per_score",
    "no_prohibited_factors",
    "human_review_flag_present",
    "groundedness_heuristic",
}


def test_post_then_get_full_envelope(client):
    response = post_evaluation(client, idempotency_key="dt001-happy")
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"
    assert envelope["case_id"] is None  # case-less rule
    evaluation_id = envelope["evaluation_id"]
    assert evaluation_id and envelope["correlation_id"]

    result = envelope["result"]

    # Mandatory advisory flags — literal true, always (BR-007).
    assert result["decision_support_only"] is True
    assert result["human_review_required"] is True

    # Advisory label enum only — no decision/rank/contact vocabulary (UFM-006).
    assert result["recommendation_label"] in ADVISORY_LABELS

    # All six rubric criteria scored 1-5 with per-criterion evidence fields.
    evaluations = result["criterion_evaluations"]
    assert [e["criterion_id"] for e in evaluations] == ["C1", "C2", "C3", "C4", "C5", "C6"]
    for e in evaluations:
        assert isinstance(e["score"], int) and 1 <= e["score"] <= 5
        assert e["criterion_name"]
        assert e["rationale"]
        # supporting/contrary evidence + missing-evidence note per criterion:
        assert isinstance(e["supporting_evidence"], list)
        assert isinstance(e["contrary_evidence"], list)
        assert "missing_evidence_note" in e
        # Either real supporting evidence or an explicit missing note —
        # never a bare unevidenced score (UFM-003).
        assert e["supporting_evidence"] or e["missing_evidence_note"]

    # The sample candidate's cover letter carries contrary evidence on C6
    # ("not yet fully bilingual") — the contrary channel is populated.
    by_criterion = {e["criterion_id"]: e for e in evaluations}
    assert by_criterion["C6"]["contrary_evidence"]

    # Disagreements with resolution rationale (list may be empty; shape checked).
    assert isinstance(result["disagreements"], list)
    for d in result["disagreements"]:
        assert d["topic"] and d["positions"] and d["resolution_rationale"]

    # Fairness block.
    fairness = result["fairness"]
    assert fairness["reviewed"] is True
    assert fairness["overall_severity"] in {"info", "low", "medium", "high"}
    assert isinstance(fairness["findings"], list)
    assert isinstance(fairness["prohibited_factor_violations"], list)
    assert isinstance(fairness["anomalous_content_flags"], list)

    # Confidence + limitations.
    assert result["confidence"] in {"low", "medium", "high"}
    assert 0 <= result["confidence_score"] <= 100
    assert result["limitations"], "limitations must never be empty"

    # Rigor block: effective rigor + auditable explanation.
    rigor = result["rigor"]
    assert rigor["effective_rigor"] == "high_impact"
    assert "high_impact" in rigor["resolution_explanation"]
    assert rigor["downgrade_attempted"] is False

    # Escalation block: policy + provenance recorded on every result.
    escalation = result["escalation"]
    assert escalation["policy"] == "record_only"
    assert escalation["provenance"] in {"none", "configured_escalated", "policy_triggered"}
    assert isinstance(escalation["triggers_fired"], list)
    assert escalation["mode_c_executed"] is False
    assert escalation["rationale"]

    # All six triggers computed every run, each with value + threshold.
    triggers = result["triggers"]
    assert {t["trigger_id"] for t in triggers} == TRIGGER_IDS
    for t in triggers:
        assert isinstance(t["fired"], bool)
        assert t["computed_value"]
        assert t["threshold"]

    # All six deterministic gates recorded, all passing on the happy path.
    gates = result["quality_gates"]
    assert {g["gate_id"] for g in gates} == GATE_IDS
    assert all(g["result"] == "pass" for g in gates)
    assert all(g["reason"] for g in gates)

    # Provider truthfulness.
    assert result["ai_backend_type"] == "none"

    # ---- GET reconstructs the persisted full audit record -------------------
    record = get_record(client, evaluation_id)
    assert record["status"] == "completed"
    assert record["evaluation_id"] == evaluation_id
    assert record["result"]["recommendation_label"] == result["recommendation_label"]
    assert record["actor"]["actor_id"] == HR_HEADERS["X-Lab-Actor-Id"]
    assert "hr" in record["actor"]["roles"]
    assert record["effective_mode"] == "B"  # high_impact base composition

    # Provider metadata on every model-backed execution (nullable trace/eval
    # placeholders typed in, C-COND-2).
    model_executions = [r for r in record["role_executions"] if r["role_kind"] == "model"]
    assert model_executions
    for execution in model_executions:
        metadata = execution["provider_metadata"]
        assert metadata["ai_backend_type"] == "none"
        assert "trace_id" in metadata and "eval_run_id" in metadata
        assert metadata["orchestration_version"]
        assert metadata["role_schema_version"]
        assert execution["retry_count"] == 0
        assert execution["schema_valid"] is True

    body_retrieve = client.post(
        "/api/evaluations/retrieve",
        json={"evaluation_id": evaluation_id},
        headers=HR_HEADERS,
    )
    assert body_retrieve.status_code == 200
    body_envelope = body_retrieve.json()
    assert body_envelope["status"] == "completed"
    assert body_envelope["evaluation_id"] == evaluation_id
    assert body_envelope["correlation_id"] == envelope["correlation_id"]
    assert body_envelope["result"] == record
