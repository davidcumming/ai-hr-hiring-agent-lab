"""Smoke test — happy path POST -> GET via TestClient (Stage 7, single test).

The full deterministic suite (DT-001…DT-018 per the implementation plan §5.1)
is authored in a second pass; this smoke test proves the pipeline end to end:
status completed, both mandatory advisory flags literal-true, actor/role
context persisted, and ai_backend_type none.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hr_eval_lab.api.app import create_app
from hr_eval_lab.config import LabConfig, PersistenceConfig

HR_HEADERS = {
    "X-Lab-Actor-Id": "u-hr-001",
    "X-Lab-Actor-Display": "Smoke Test HR User",
    "X-Lab-Roles": "hr,reviewer",
}


@pytest.fixture()
def client(tmp_path):
    config = LabConfig(persistence=PersistenceConfig(root=str(tmp_path / "lab-data")))
    app = create_app(config=config)
    return TestClient(app)


def test_happy_path_post_then_get(client):
    response = client.post(
        "/api/evaluations",
        json={
            "position_id": "pos-sample-001",
            "candidate_ref": "cand-sample-001",
            "idempotency_key": "smoke-001",
        },
        headers=HR_HEADERS,
    )
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"
    assert envelope["case_id"] is None  # case-less rule
    evaluation_id = envelope["evaluation_id"]
    assert evaluation_id

    result = envelope["result"]
    # Mandatory advisory invariants (BR-007) — literal true, always.
    assert result["decision_support_only"] is True
    assert result["human_review_required"] is True
    # Provider truthfulness: deterministic mock backend.
    assert result["ai_backend_type"] == "none"
    # Advisory enum only.
    assert result["recommendation_label"] in {
        "advance_to_interview",
        "do_not_advance",
        "hold_for_review",
        "insufficient_evidence",
    }
    # All six rubric criteria scored 1-5; all six triggers computed; six gates.
    assert len(result["criterion_evaluations"]) == 6
    assert all(1 <= e["score"] <= 5 for e in result["criterion_evaluations"])
    assert len(result["triggers"]) == 6
    assert len(result["quality_gates"]) == 6
    assert all(g["result"] == "pass" for g in result["quality_gates"])
    assert result["rigor"]["effective_rigor"] == "high_impact"

    # GET reconstructs the full audit record, incl. actor/role context.
    get_response = client.get(f"/api/evaluations/{evaluation_id}", headers=HR_HEADERS)
    assert get_response.status_code == 200
    record = get_response.json()["result"]
    assert record["status"] == "completed"
    assert record["actor"]["actor_id"] == "u-hr-001"
    assert "hr" in record["actor"]["roles"]
    assert record["actor"]["resolved_role"] == "hr"
    # Evidence-before-judgment: packet completion precedes the first model call.
    model_indices = [
        r["sequence_index"] for r in record["role_executions"] if r["role_kind"] == "model"
    ]
    assert record["packet_sequence_index"] < min(model_indices)
    # Every model-backed execution carries provider metadata with the
    # nullable trace/eval placeholders typed in (C-COND-2).
    for execution in record["role_executions"]:
        if execution["role_kind"] == "model":
            metadata = execution["provider_metadata"]
            assert metadata["ai_backend_type"] == "none"
            assert "trace_id" in metadata and "eval_run_id" in metadata
    assert record["human_review"]["human_review_required"] is True
