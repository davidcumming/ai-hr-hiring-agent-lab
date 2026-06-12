"""DT-007 — Status vocabulary mapping (fixed vocabulary, no others emitted).

Related: AC-011, FR-003, BR-009, UFM-010.

- Unknown ``position_id`` -> envelope ``validation_failed`` (HTTP 200).
- Unknown ``candidate_ref`` -> envelope ``validation_failed`` (HTTP 200).
- Malformed body -> HTTP 400 (no envelope status consumed).
- Tampered source hash vs manifest -> envelope ``blocked`` with ZERO council
  execution (no provider call, no role output persisted).
- Valid request -> ``completed``.
"""

from __future__ import annotations

from tests.conftest import HR_HEADERS, CountingProvider, post_evaluation


def test_unknown_position_validation_failed(client):
    response = post_evaluation(
        client, idempotency_key="dt007-pos", position_id="pos-unknown-999"
    )
    assert response.status_code == 200  # business outcome, not HTTP error
    envelope = response.json()
    assert envelope["status"] == "validation_failed"
    assert "unknown_position" in envelope["errors"]
    assert envelope["evaluation_id"] is None


def test_unknown_candidate_validation_failed(client):
    response = post_evaluation(
        client, idempotency_key="dt007-cand", candidate_ref="cand-unknown-999"
    )
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "validation_failed"
    assert "unknown_candidate" in envelope["errors"]


def test_malformed_non_json_body_http_400(client):
    response = client.post(
        "/api/evaluations",
        content=b"this is not json {",
        headers={**HR_HEADERS, "Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "malformed_request_body"


def test_malformed_shape_http_400(client):
    # Missing idempotency_key and unknown extra field -> malformed shape.
    response = client.post(
        "/api/evaluations",
        json={"position_id": "pos-sample-001", "unexpected_field": True},
        headers=HR_HEADERS,
    )
    assert response.status_code == 400
    assert response.json()["error"] == "malformed_request_body"


def test_malformed_candidate_source_shape_http_400(client):
    # candidate_ref AND inline text together violates the request model.
    response = client.post(
        "/api/evaluations",
        json={
            "position_id": "pos-sample-001",
            "candidate_ref": "cand-sample-001",
            "resume_text": "inline text",
            "cover_letter_text": "inline text",
            "idempotency_key": "dt007-shape",
        },
        headers=HR_HEADERS,
    )
    assert response.status_code == 400


def test_tampered_source_hash_blocked_with_zero_council_execution(
    make_client, tampered_fixtures_root
):
    provider = CountingProvider()
    client = make_client(provider=provider, fixtures_root=tampered_fixtures_root)
    response = post_evaluation(client, idempotency_key="dt007-tampered")
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "blocked"
    assert "source_integrity_failure" in envelope["errors"]
    # Safe details only: artifact id + hash prefixes, never content.
    assert "sha256" in envelope["safe_details"]
    assert "TAMPERED" not in envelope["safe_details"]

    # ZERO council execution: no provider call, no role output persisted.
    assert provider.calls == []
    store = client.app.state.store
    assert list((store.root / "evaluations").iterdir()) == []
    assert store.read_table("EvaluationEvidence.jsonl") == []


def test_valid_request_completed(client):
    response = post_evaluation(client, idempotency_key="dt007-valid")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_unknown_evaluation_id_validation_failed(client):
    response = client.get("/api/evaluations/eval-does-not-exist", headers=HR_HEADERS)
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "validation_failed"
    assert "unknown_evaluation_id" in envelope["errors"]


def test_no_reserved_status_emitted(client):
    """needs_input / error are reserved — every emitted status here is in the
    four-value emitted vocabulary."""
    emitted = set()
    for key, position in [
        ("dt007-vocab-1", "pos-sample-001"),
        ("dt007-vocab-2", "pos-unknown"),
    ]:
        envelope = post_evaluation(
            client, idempotency_key=key, position_id=position
        ).json()
        emitted.add(envelope["status"])
    assert emitted <= {"completed", "blocked", "validation_failed", "unauthorized"}
