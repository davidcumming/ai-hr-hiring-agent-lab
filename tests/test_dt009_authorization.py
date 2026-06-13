"""DT-009 — Authorization matrix + actor/role audit provenance.

Related: AC-011, AC-013, FR-002, UFM-012.

hr role succeeds; missing identity -> HTTP 401; authenticated non-hr ->
HTTP 403 with envelope status ``unauthorized``; both endpoints enforce auth
FIRST; the persisted record carries actor identity + role context.
"""

from __future__ import annotations

import pytest

from tests.conftest import identity_headers, post_evaluation


def test_hr_role_succeeds_on_both_endpoints(client):
    headers = identity_headers(actor_id="u-hr-dt009", roles="hr")
    response = post_evaluation(client, idempotency_key="dt009-ok", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    evaluation_id = response.json()["evaluation_id"]

    get_response = client.get(f"/api/evaluations/{evaluation_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "completed"

    retrieve_response = client.post(
        "/api/evaluations/retrieve",
        json={"evaluation_id": evaluation_id},
        headers=headers,
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["status"] == "completed"


@pytest.mark.parametrize("method,path", [("post", "/api/evaluations"), ("get", "/api/evaluations/eval-x")])
def test_missing_identity_is_401_unauthorized(client, method, path):
    if method == "post":
        response = client.post(path, json={"position_id": "p", "idempotency_key": "k"})
    else:
        response = client.get(path)
    assert response.status_code == 401
    envelope = response.json()
    assert envelope["status"] == "unauthorized"
    assert "unauthorized" in envelope["errors"]


def test_missing_identity_on_body_retrieve_is_401_before_body_validation(client):
    response = client.post(
        "/api/evaluations/retrieve",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401
    envelope = response.json()
    assert envelope["status"] == "unauthorized"
    assert "unauthorized" in envelope["errors"]


@pytest.mark.parametrize(
    "roles",
    ["", "hiring_manager", "reviewer,auditor", "admin_lab", "made_up_role", "HR"],
)
@pytest.mark.parametrize("method,path", [("post", "/api/evaluations"), ("get", "/api/evaluations/eval-x")])
def test_authenticated_without_hr_role_is_403_unauthorized(client, roles, method, path):
    headers = identity_headers(actor_id="u-nothr-001", roles=roles)
    if method == "post":
        response = client.post(
            path,
            json={
                "position_id": "pos-sample-001",
                "candidate_ref": "cand-sample-001",
                "idempotency_key": "dt009-denied",
            },
            headers=headers,
        )
    else:
        response = client.get(path, headers=headers)
    assert response.status_code == 403
    assert response.json()["status"] == "unauthorized"


@pytest.mark.parametrize(
    "roles",
    ["", "hiring_manager", "reviewer,auditor", "admin_lab", "made_up_role", "HR"],
)
def test_authenticated_without_hr_role_on_body_retrieve_is_403_unauthorized(
    client, roles
):
    response = client.post(
        "/api/evaluations/retrieve",
        json={"evaluation_id": "eval-x"},
        headers=identity_headers(actor_id="u-nothr-002", roles=roles),
    )
    assert response.status_code == 403
    assert response.json()["status"] == "unauthorized"


def test_auth_runs_before_body_validation(client):
    """A malformed body from an unauthenticated caller is rejected 401, not
    400 — identity/role validation is FIRST."""
    response = client.post(
        "/api/evaluations",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401


def test_denied_request_leaves_no_persisted_state(make_client):
    client = make_client()
    client.post(
        "/api/evaluations",
        json={
            "position_id": "pos-sample-001",
            "candidate_ref": "cand-sample-001",
            "idempotency_key": "dt009-no-state",
        },
        headers=identity_headers(actor_id="u-nothr-002", roles="reviewer"),
    )
    store = client.app.state.store
    assert list((store.root / "evaluations").iterdir()) == []
    assert store.read_table("EvaluationEvidence.jsonl") == []


def test_actor_identity_and_role_context_persisted(make_client):
    client = make_client()
    headers = identity_headers(
        actor_id="u-hr-audit", roles="hr,reviewer,auditor", display="Audit Trail User"
    )
    response = post_evaluation(client, idempotency_key="dt009-audit", headers=headers)
    evaluation_id = response.json()["evaluation_id"]

    record = client.get(f"/api/evaluations/{evaluation_id}", headers=headers).json()["result"]
    actor = record["actor"]
    assert actor["actor_id"] == "u-hr-audit"
    assert actor["display"] == "Audit Trail User"
    assert set(actor["roles"]) == {"hr", "reviewer", "auditor"}
    assert actor["resolved_role"] == "hr"  # the role that authorized the call

    # Actor/role context also lands on every table-equivalent row (UFM-012).
    store = client.app.state.store
    evidence_rows = [
        r
        for r in store.read_table("EvaluationEvidence.jsonl")
        if r["PartitionKey"] == evaluation_id
    ]
    assert evidence_rows
    assert all(r["actor_id"] == "u-hr-audit" for r in evidence_rows)
    assert all(r["resolved_role"] == "hr" for r in evidence_rows)
    review_rows = [
        r
        for r in store.read_table("ReviewQueue.jsonl")
        if r["PartitionKey"] == evaluation_id
    ]
    assert review_rows and review_rows[0]["actor_id"] == "u-hr-audit"


def test_unknown_roles_are_filtered_from_persisted_context(make_client):
    """Roles outside the lab vocabulary never appear in the audit record."""
    client = make_client()
    headers = identity_headers(actor_id="u-hr-filter", roles="hr,not_a_real_role")
    response = post_evaluation(client, idempotency_key="dt009-filter", headers=headers)
    record = client.get(
        f"/api/evaluations/{response.json()['evaluation_id']}", headers=headers
    ).json()["result"]
    assert record["actor"]["roles"] == ["hr"]
