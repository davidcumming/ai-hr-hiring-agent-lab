"""DT-004 — Escalation policy matrix (all three policy states explicit).

Related: AC-005, AC-006, BR-003, BR-004, BR-005, BR-006, UFM-008.

- record_only + trigger fired: triggers recorded, NO Mode C roles executed.
- configured escalated rigor: Mode C extension roles present + mandatory
  human review with configured_escalated provenance.
- auto_escalate + trigger fired: Mode C executes with policy_triggered
  provenance.
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas import council as c

from tests.conftest import get_record, post_evaluation, scripted_provider

MODE_C_ROLES = {c.ROLE_SECOND_SYNTHESIS_JUDGE, c.ROLE_RUBRIC_CALIBRATION_JUDGE}

#: Shallow-merge script forcing the synthesis_confidence_low trigger to fire.
LOW_CONFIDENCE_SCRIPT = {
    c.ROLE_SYNTHESIS_JUDGE: {"confidence": "low", "confidence_score": 10}
}


def _executed_roles(record: dict) -> set[str]:
    return {r["role_id"] for r in record["role_executions"]}


def test_record_only_records_triggers_without_mode_c(make_client):
    client = make_client(
        escalation="record_only", provider=scripted_provider(LOW_CONFIDENCE_SCRIPT)
    )
    response = post_evaluation(client, idempotency_key="dt004-record-only")
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"

    escalation = envelope["result"]["escalation"]
    assert escalation["policy"] == "record_only"
    assert "synthesis_confidence_low" in escalation["triggers_fired"]  # recorded
    assert escalation["mode_c_executed"] is False  # not acted on
    assert escalation["provenance"] == "none"
    assert "record_only" in escalation["rationale"]

    record = get_record(client, envelope["evaluation_id"])
    assert _executed_roles(record).isdisjoint(MODE_C_ROLES)  # NO Mode C roles ran
    assert record["effective_mode"] == "B"
    fired = {t["trigger_id"] for t in record["triggers"] if t["fired"]}
    assert "synthesis_confidence_low" in fired


def test_configured_escalated_runs_mode_c_with_mandatory_review(make_client):
    client = make_client(rigor="escalated")
    response = post_evaluation(client, idempotency_key="dt004-configured")
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"

    escalation = envelope["result"]["escalation"]
    assert escalation["provenance"] == "configured_escalated"
    assert escalation["mode_c_executed"] is True

    record = get_record(client, envelope["evaluation_id"])
    assert MODE_C_ROLES <= _executed_roles(record)  # Mode C roles present
    assert record["effective_mode"] == "C"
    assert record["escalation"]["human_review_mandatory_reason"] == "configured_escalated_mode"
    assert record["human_review"]["human_review_required"] is True
    assert "configured_escalated_mode" in record["human_review"]["reasons"]


def test_auto_escalate_trigger_fires_mode_c_with_policy_triggered_provenance(make_client):
    client = make_client(
        escalation="auto_escalate", provider=scripted_provider(LOW_CONFIDENCE_SCRIPT)
    )
    response = post_evaluation(client, idempotency_key="dt004-auto")
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"

    escalation = envelope["result"]["escalation"]
    assert escalation["policy"] == "auto_escalate"
    assert escalation["provenance"] == "policy_triggered"
    assert escalation["mode_c_executed"] is True
    assert "synthesis_confidence_low" in escalation["triggers_fired"]

    record = get_record(client, envelope["evaluation_id"])
    assert MODE_C_ROLES <= _executed_roles(record)
    assert record["effective_mode"] == "C"
    assert (
        record["escalation"]["human_review_mandatory_reason"]
        == "policy_triggered_escalation"
    )
    assert "policy_triggered_escalation" in record["human_review"]["reasons"]


def _all_supporting(role_id, packet, role_context, payload):
    """Script: reclassify every extracted item as supporting so the baseline
    C6 contrary-only situation cannot fire any trigger (quiet scenario)."""
    for item in payload["evidence_items"]:
        item["relation"] = "supporting"
    return payload


def test_auto_escalate_without_fired_trigger_stays_base_mode(make_client):
    """auto_escalate with nothing fired must NOT silently escalate (UFM-008)."""
    client = make_client(
        escalation="auto_escalate",
        provider=scripted_provider({c.ROLE_EVIDENCE_EXTRACTION: _all_supporting}),
    )
    response = post_evaluation(client, idempotency_key="dt004-auto-quiet")
    assert response.status_code == 200
    escalation = response.json()["result"]["escalation"]
    assert escalation["triggers_fired"] == []
    assert escalation["mode_c_executed"] is False
    assert escalation["provenance"] == "none"
