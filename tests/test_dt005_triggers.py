"""DT-005 — Each of the six escalation triggers individually provoked.

Related: AC-006, FR-011, BR-004, UFM-009.

Every scenario starts from a "quiet" baseline (all extracted evidence
reclassified supporting, so no trigger fires by default) and scripts exactly
one provocation through the provider seam. All six triggers are computed and
recorded on every run regardless of policy (record_only here).
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas import council as c

from tests.conftest import post_evaluation, scripted_provider


def _all_supporting(role_id, packet, role_context, payload):
    for item in payload["evidence_items"]:
        item["relation"] = "supporting"
    return payload


def _drop_criterion(criterion_id):
    def _script(role_id, packet, role_context, payload):
        _all_supporting(role_id, packet, role_context, payload)
        payload["evidence_items"] = [
            i for i in payload["evidence_items"] if i["criterion_id"] != criterion_id
        ]
        return payload

    return _script


def _set_score(field, criterion_id, score):
    def _script(role_id, packet, role_context, payload):
        for entry in payload[field]:
            if entry["criterion_id"] == criterion_id:
                entry["score"] = score
        return payload

    return _script


def _run(make_client, key, script):
    base = {c.ROLE_EVIDENCE_EXTRACTION: _all_supporting}
    base.update(script)
    client = make_client(provider=scripted_provider(base))
    response = post_evaluation(client, idempotency_key=key)
    assert response.status_code == 200
    triggers = {t["trigger_id"]: t for t in response.json()["result"]["triggers"]}
    assert len(triggers) == 6  # all six computed every run (FR-011)
    return triggers


def _fired(triggers):
    return {tid for tid, t in triggers.items() if t["fired"]}


def test_quiet_baseline_fires_nothing(make_client):
    triggers = _run(make_client, "dt005-quiet", {})
    assert _fired(triggers) == set()
    for t in triggers.values():
        assert t["computed_value"] and t["threshold"]


def test_score_variance_above_threshold(make_client):
    triggers = _run(
        make_client,
        "dt005-variance",
        {c.ROLE_RISK_GAPS_ADVOCATE: _set_score("proposed_scores", "C1", 1)},
    )
    assert _fired(triggers) == {"score_variance_above_threshold"}
    assert "spread" in triggers["score_variance_above_threshold"]["computed_value"]


def test_evidence_packet_missing_required_criteria(make_client):
    triggers = _run(
        make_client,
        "dt005-missing-required",
        {c.ROLE_EVIDENCE_EXTRACTION: _drop_criterion("C2")},
    )
    assert "evidence_packet_missing_required_criteria" in _fired(triggers)
    assert "C2" in triggers["evidence_packet_missing_required_criteria"]["computed_value"]
    # Co-fires by construction: the unevidenced criterion is floored to 1 by
    # synthesis while advocates keep the keyword-anchored proposal, so the
    # no-direct-evidence and score-variance triggers also fire. Nothing else.
    assert _fired(triggers) <= {
        "evidence_packet_missing_required_criteria",
        "criterion_scored_with_no_direct_evidence",
        "score_variance_above_threshold",
    }


def test_synthesis_confidence_low(make_client):
    triggers = _run(
        make_client,
        "dt005-low-confidence",
        {c.ROLE_SYNTHESIS_JUDGE: {"confidence": "low", "confidence_score": 10}},
    )
    assert _fired(triggers) == {"synthesis_confidence_low"}
    assert "confidence_score=10" in triggers["synthesis_confidence_low"]["computed_value"]


def test_policy_fairness_severity_high(make_client):
    triggers = _run(
        make_client,
        "dt005-fairness-high",
        {c.ROLE_POLICY_FAIRNESS_AUDITOR: {"overall_severity": "high"}},
    )
    assert _fired(triggers) == {"policy_fairness_severity_high"}
    assert "high" in triggers["policy_fairness_severity_high"]["computed_value"]


def test_recommendation_near_decision_threshold(make_client):
    triggers = _run(
        make_client,
        "dt005-near-threshold",
        {c.ROLE_NEUTRAL_SCORING_JUDGE: _set_score("scores", "C1", 3)},
    )
    assert _fired(triggers) == {"recommendation_near_decision_threshold"}
    assert "C1" in triggers["recommendation_near_decision_threshold"]["computed_value"]


def test_criterion_scored_with_no_direct_evidence(make_client):
    triggers = _run(
        make_client,
        "dt005-no-direct-evidence",
        {c.ROLE_EVIDENCE_EXTRACTION: _drop_criterion("C6")},
    )
    # C6 is preferred, so the missing-required trigger must NOT fire; the
    # synthesis floor-vs-proposal spread co-fires score variance only.
    fired = _fired(triggers)
    assert "criterion_scored_with_no_direct_evidence" in fired
    assert "evidence_packet_missing_required_criteria" not in fired
    assert fired <= {
        "criterion_scored_with_no_direct_evidence",
        "score_variance_above_threshold",
    }
    assert "C6" in triggers["criterion_scored_with_no_direct_evidence"]["computed_value"]
