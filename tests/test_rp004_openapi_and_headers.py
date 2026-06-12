"""RP-010, RP-011: OpenAPI readiness (operation IDs, headers, no provider
fields in the request schema) and Idempotency-Key header behaviour.
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import HR_HEADERS, post_evaluation

REPO_ROOT = Path(__file__).resolve().parent.parent
OPENAPI_PATH = REPO_ROOT / "openapi" / "evaluations-api.json"

FORBIDDEN_REQUEST_FIELDS = {
    "provider",
    "provider_id",
    "model",
    "model_deployment",
    "deployment",
    "endpoint",
    "agent_id",
    "agent",
    "ai_backend_type",
    "capability_profile",
}


def _spec() -> dict:
    return json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))


def test_rp010_openapi_parses_and_validates():
    from openapi_spec_validator import validate

    validate(_spec())


def test_rp010_stable_operation_ids_present():
    spec = _spec()
    assert spec["paths"]["/api/evaluations"]["post"]["operationId"] == "submitEvaluation"
    assert (
        spec["paths"]["/api/evaluations/{evaluation_id}"]["get"]["operationId"]
        == "getEvaluation"
    )


def test_rp010_headers_documented():
    spec = _spec()
    post_params = {
        p["name"] for p in spec["paths"]["/api/evaluations"]["post"].get("parameters", [])
    }
    assert {"Idempotency-Key", "X-Correlation-Id"} <= post_params
    get_params = {
        p["name"]
        for p in spec["paths"]["/api/evaluations/{evaluation_id}"]["get"].get(
            "parameters", []
        )
    }
    assert "X-Correlation-Id" in get_params


def test_rp010_request_schema_exposes_no_backend_selection():
    spec = _spec()
    schema = spec["paths"]["/api/evaluations"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    fields = set(schema.get("properties", {}).keys())
    assert not fields & FORBIDDEN_REQUEST_FIELDS


def test_rp011_header_only_idempotency_key(make_client):
    client = make_client()
    body = {"position_id": "pos-sample-001", "candidate_ref": "cand-sample-001"}
    headers = {**HR_HEADERS, "Idempotency-Key": "rp011-header"}
    first = client.post("/api/evaluations", json=body, headers=headers)
    assert first.status_code == 200 and first.json()["status"] == "completed"
    replay = client.post("/api/evaluations", json=body, headers=headers)
    assert replay.json()["evaluation_id"] == first.json()["evaluation_id"]
    assert "replay" in replay.json()["user_message"].lower()


def test_rp011_header_body_mismatch_is_http_400(make_client):
    client = make_client()
    body = {
        "position_id": "pos-sample-001",
        "candidate_ref": "cand-sample-001",
        "idempotency_key": "body-key",
    }
    response = client.post(
        "/api/evaluations",
        json=body,
        headers={**HR_HEADERS, "Idempotency-Key": "different-key"},
    )
    assert response.status_code == 400


def test_rp011_missing_both_keys_is_http_400(make_client):
    client = make_client()
    response = client.post(
        "/api/evaluations",
        json={"position_id": "pos-sample-001", "candidate_ref": "cand-sample-001"},
        headers=HR_HEADERS,
    )
    assert response.status_code == 400


def test_rp011_matching_header_and_body_accepted(make_client):
    client = make_client()
    response = post_evaluation(
        client,
        idempotency_key="rp011-match",
        headers={**HR_HEADERS, "Idempotency-Key": "rp011-match"},
    )
    assert response.status_code == 200


def test_rp010_correlation_header_on_responses(make_client):
    client = make_client()
    submit = post_evaluation(client, idempotency_key="rp010-corr")
    assert submit.headers.get("X-Correlation-Id") == submit.json()["correlation_id"]
    evaluation_id = submit.json()["evaluation_id"]
    retrieve = client.get(f"/api/evaluations/{evaluation_id}", headers=HR_HEADERS)
    assert retrieve.headers.get("X-Correlation-Id") == submit.json()["correlation_id"]
