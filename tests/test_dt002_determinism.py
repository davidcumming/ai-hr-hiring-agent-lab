"""DT-002 — Repeat-run determinism (the regression-baseline anchor).

Related: AC-003, BR-009, FR-012.

Two full pipeline runs with identical inputs (separate app instances and
persistence roots so idempotency replay cannot short-circuit the second run)
must produce serialized records that are byte-identical after normalizing
exactly the run-identity fields: ``evaluation_id`` (and its derived
``correlation_id``) and the two timestamps. Any other diff fails.
"""

from __future__ import annotations

import json

from hr_eval_lab.persistence.store import canonical_json

from tests.conftest import get_record, post_evaluation

_NORMALIZED = {
    "evaluation_id": "eval-NORMALIZED",
    "correlation_id": "corr-NORMALIZED",
    "created_at": "1970-01-01T00:00:00Z",
    "completed_at": "1970-01-01T00:00:00Z",
}


def _normalized_bytes(record: dict) -> bytes:
    record = json.loads(json.dumps(record))  # deep copy
    for field, placeholder in _NORMALIZED.items():
        assert field in record
        record[field] = placeholder
    return canonical_json(record).encode("utf-8")


def _run_once(make_client) -> dict:
    client = make_client()
    response = post_evaluation(client, idempotency_key="dt002-determinism")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    return get_record(client, response.json()["evaluation_id"])


def test_two_identical_runs_byte_identical_after_normalization(make_client):
    first = _run_once(make_client)
    second = _run_once(make_client)

    assert first["evaluation_id"] != second["evaluation_id"]  # fresh run identity
    assert _normalized_bytes(first) == _normalized_bytes(second)


def test_persisted_blob_is_canonical_json(make_client):
    """The blob on disk is canonical JSON (sorted keys, fixed separators)."""
    client = make_client()
    response = post_evaluation(client, idempotency_key="dt002-canonical")
    evaluation_id = response.json()["evaluation_id"]
    store = client.app.state.store
    # Readiness-pack layout: evaluations/{evaluation_id}/record.json
    blob_path = store.root / "evaluations" / evaluation_id / "record.json"
    raw = blob_path.read_text(encoding="utf-8")
    assert raw == canonical_json(json.loads(raw))
