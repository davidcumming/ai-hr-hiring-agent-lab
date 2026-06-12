"""DT-010 — Mandatory-flags invariant across ALL emitted/persisted records.

Related: AC-013, BR-007, UFM-005.

Every record emitted across completed, blocked, and escalated paths carries
``decision_support_only = true`` and ``human_review_required = true``. The
assertion is structural: every persisted blob is scanned, and the serializer
contract (Literal[True] fields) is proven unable to emit anything else.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from hr_eval_lab.domain.schemas import council as c
from hr_eval_lab.domain.schemas.audit import HumanReviewBlock
from hr_eval_lab.domain.schemas.evaluation import AdvisoryEvaluation

from tests.conftest import post_evaluation, scripted_provider


def _invalid_always(role_id, packet, role_context, payload):
    return {"bogus": "schema-invalid output"}


def test_flags_invariant_across_completed_blocked_and_escalated(make_client):
    # 1. Completed path (default config).
    completed_client = make_client()
    assert (
        post_evaluation(completed_client, idempotency_key="dt010-ok").json()["status"]
        == "completed"
    )

    # 2. Blocked path (persistent schema failure -> gate 1 fail).
    blocked_client = make_client(
        provider=scripted_provider({c.ROLE_MERIT_ADVOCATE: _invalid_always})
    )
    blocked = post_evaluation(blocked_client, idempotency_key="dt010-blocked").json()
    assert blocked["status"] == "blocked"
    # Even the blocked envelope's result carries the literal-true flags.
    assert blocked["result"]["decision_support_only"] is True
    assert blocked["result"]["human_review_required"] is True

    # 3. Escalated (Mode C) path.
    escalated_client = make_client(rigor="escalated")
    assert (
        post_evaluation(escalated_client, idempotency_key="dt010-esc").json()["status"]
        == "completed"
    )

    # Structural sweep: EVERY persisted full record on every store.
    scanned = 0
    for client in (completed_client, blocked_client, escalated_client):
        store = client.app.state.store
        # Readiness-pack layout: evaluations/{evaluation_id}/record.json
        for blob in sorted((store.root / "evaluations").glob("*/record.json")):
            record = json.loads(blob.read_text(encoding="utf-8"))
            scanned += 1
            assert record["human_review"]["human_review_required"] is True
            assert record["result"] is not None
            assert record["result"]["decision_support_only"] is True
            assert record["result"]["human_review_required"] is True
        # Review-queue rows exist for every record incl. blocked (BR-007).
        review_rows = store.read_table("ReviewQueue.jsonl")
        assert len(review_rows) == 1
        assert review_rows[0]["mandatory_reasons"]
    assert scanned == 3


def test_serializer_cannot_emit_false_flags():
    """Literal[True] schema enforcement: no code path can omit or flip the
    mandatory flags — constructing such a record is a validation error."""
    with pytest.raises(ValidationError):
        HumanReviewBlock(human_review_required=False, reasons=["x"])

    base = dict(
        recommendation_label="hold_for_review",
        criterion_evaluations=[],
        disagreements=[],
        fairness={
            "reviewed": True,
            "findings": [],
            "overall_severity": "info",
            "prohibited_factor_violations": [],
            "anomalous_content_flags": [],
        },
        confidence="low",
        confidence_score=10,
        limitations=["test"],
        rigor={
            "effective_rigor": "high_impact",
            "resolution_explanation": "x",
            "downgrade_attempted": False,
            "requested_rigor": None,
        },
        escalation={
            "policy": "record_only",
            "provenance": "none",
            "triggers_fired": [],
            "mode_c_executed": False,
            "rationale": "x",
        },
        triggers=[],
        quality_gates=[],
        ai_backend_type="none",
    )
    with pytest.raises(ValidationError):
        AdvisoryEvaluation(
            decision_support_only=False, human_review_required=True, **base
        )
    with pytest.raises(ValidationError):
        AdvisoryEvaluation(
            decision_support_only=True, human_review_required=False, **base
        )
    # And omission is equally unconstructible.
    with pytest.raises(ValidationError):
        AdvisoryEvaluation.model_validate(base)
