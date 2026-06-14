"""E9 case foundation API coverage and non-goal pins."""

from __future__ import annotations

import json

from hr_eval_lab.domain.schemas.workflow import (
    CaseEvent,
    CaseParticipant,
    CaseTask,
    RecruitmentCase,
    WorkflowGate,
)
from tests.conftest import CountingProvider, HR_HEADERS, identity_headers

CASE_PATHS = {
    "/api/cases",
    "/api/cases/{case_id}",
    "/api/cases/{case_id}/next-actions",
    "/api/cases/{case_id}/source-documents",
    "/api/cases/{case_id}/source-documents/{document_id}",
    "/api/cases/{case_id}/role-intake",
    "/api/cases/{case_id}/rubrics",
    "/api/cases/{case_id}/rubrics/{rubric_version}",
}


def _case_body(**overrides):
    body = {
        "role_title": "Synthetic HR Analyst",
        "department": "Synthetic Lab",
        "recruitment_type": "permanent",
    }
    body.update(overrides)
    return body


def _post_case(client, body=None, headers=None):
    return client.post(
        "/api/cases",
        json=body or _case_body(),
        headers=headers or HR_HEADERS,
    )


def _workflow_counts(client, case_id):
    store = client.app.state.workflow_storage
    return {
        "cases": len(store.list_table_entities(RecruitmentCase, case_id)),
        "participants": len(store.list_table_entities(CaseParticipant, case_id)),
        "tasks": len(store.list_table_entities(CaseTask, case_id)),
        "gates": len(store.list_table_entities(WorkflowGate, case_id)),
        "events": len(store.list_table_entities(CaseEvent, case_id)),
    }


def test_e9_case_api_create_get_and_next_actions_round_trip(make_client):
    client = make_client()

    create = _post_case(client)
    assert create.status_code == 200
    envelope = create.json()
    assert envelope["status"] == "completed"
    assert envelope["evaluation_id"] is None
    assert envelope["case_id"].startswith("case-")
    assert envelope["correlation_id"].startswith("corr-")
    assert create.headers["X-Correlation-Id"] == envelope["correlation_id"]
    assert [action["action_id"] for action in envelope["next_actions"]] == [
        "attach_source_documents",
        "complete_role_intake",
        "confirm_hiring_manager",
    ]

    case_id = envelope["case_id"]
    assert _workflow_counts(client, case_id) == {
        "cases": 1,
        "participants": 1,
        "tasks": 3,
        "gates": 5,
        "events": 1,
    }

    get_case = client.get(f"/api/cases/{case_id}", headers=HR_HEADERS)
    assert get_case.status_code == 200
    retrieved = get_case.json()
    assert retrieved["status"] == "completed"
    assert retrieved["case_id"] == case_id
    assert retrieved["result"]["case"]["case_status"] == "intake_pending"
    assert retrieved["result"]["case"]["hr_owner_actor_id"] == "u-hr-001"
    assert retrieved["result"]["events"][0]["event_type"] == "case_created"

    next_actions = client.get(f"/api/cases/{case_id}/next-actions", headers=HR_HEADERS)
    assert next_actions.status_code == 200
    actions = next_actions.json()
    assert actions["result"]["case_id"] == case_id
    assert len(actions["result"]["open_tasks"]) == 3
    assert len(actions["result"]["active_gate_blockers"]) == 5
    assert actions["next_actions"] == actions["result"]["next_actions"]


def test_e9_case_api_unknown_case_validation_failed(client):
    get_case = client.get("/api/cases/case-does-not-exist", headers=HR_HEADERS)
    assert get_case.status_code == 200
    assert get_case.json()["status"] == "validation_failed"
    assert get_case.json()["case_id"] is None
    assert "unknown_case_id" in get_case.json()["errors"]

    next_actions = client.get(
        "/api/cases/case-does-not-exist/next-actions", headers=HR_HEADERS
    )
    assert next_actions.status_code == 200
    assert next_actions.json()["status"] == "validation_failed"
    assert next_actions.json()["result"] is None


def test_e9_case_api_auth_runs_before_body_validation(client):
    response = client.post(
        "/api/cases",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401
    assert response.json()["status"] == "unauthorized"


def test_e9_case_api_denied_request_leaves_no_workflow_state(make_client):
    client = make_client()
    response = _post_case(
        client,
        headers=identity_headers(actor_id="u-nothr-e9", roles="reviewer"),
    )

    assert response.status_code == 403
    assert response.json()["status"] == "unauthorized"
    store = client.app.state.workflow_storage
    assert store.list_table_entities(RecruitmentCase) == []
    assert store.peek_queue_messages() == []


def test_e9_case_api_requires_hr_role_on_read(client):
    headers = identity_headers(actor_id="u-hm-e9", roles="hiring_manager")

    get_case = client.get("/api/cases/case-x", headers=headers)
    next_actions = client.get("/api/cases/case-x/next-actions", headers=headers)

    assert get_case.status_code == 403
    assert next_actions.status_code == 403
    assert get_case.json()["status"] == "unauthorized"
    assert next_actions.json()["status"] == "unauthorized"


def test_e9_case_api_malformed_bodies_http_400(client):
    malformed_json = client.post(
        "/api/cases",
        content=b"not json {",
        headers={**HR_HEADERS, "Content-Type": "application/json"},
    )
    assert malformed_json.status_code == 400
    assert malformed_json.json()["error"] == "malformed_request_body"

    non_object = client.post("/api/cases", json=[], headers=HR_HEADERS)
    assert non_object.status_code == 400

    missing_required = client.post(
        "/api/cases",
        json={"role_title": "Synthetic HR Analyst"},
        headers=HR_HEADERS,
    )
    assert missing_required.status_code == 400

    extra_field = client.post(
        "/api/cases",
        json={**_case_body(), "resume_text": "not allowed in E9"},
        headers=HR_HEADERS,
    )
    assert extra_field.status_code == 400

    blank_field = client.post(
        "/api/cases",
        json=_case_body(role_title="   "),
        headers=HR_HEADERS,
    )
    assert blank_field.status_code == 400


def test_e9_case_api_hiring_manager_input_creates_participant_without_confirm_task(
    make_client,
):
    client = make_client()
    body = _case_body(
        case_title="Synthetic case with manager",
        hiring_manager={
            "actor_id": "u-hm-e9",
            "display_name": "E9 Hiring Manager",
            "confirmed": True,
        },
    )

    response = _post_case(client, body=body)

    assert response.status_code == 200
    case_id = response.json()["case_id"]
    store = client.app.state.workflow_storage
    participants = store.list_table_entities(CaseParticipant, case_id)
    tasks = store.list_table_entities(CaseTask, case_id)

    assert {participant.case_role for participant in participants} == {
        "hr_specialist",
        "hiring_manager",
    }
    assert {task.task_type for task in tasks} == {
        "complete_role_intake",
        "attach_source_documents",
    }
    assert "confirm_hiring_manager" not in [
        action["action_id"] for action in response.json()["next_actions"]
    ]


def test_e9_case_api_does_not_call_provider_or_create_queue_or_blob(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)

    response = _post_case(client)

    assert response.status_code == 200
    assert provider.calls == []
    store = client.app.state.workflow_storage
    assert store.peek_queue_messages() == []
    assert not any(store.blobs_root.rglob("*"))


def test_e9_case_api_openapi_contract_and_route_non_goals(client):
    spec = client.app.openapi()
    paths = set(spec["paths"])

    assert CASE_PATHS <= paths
    assert {path for path in paths if path.startswith("/api/cases")} == CASE_PATHS
    assert spec["paths"]["/api/cases"]["post"]["operationId"] == "createRecruitmentCase"
    assert (
        spec["paths"]["/api/cases/{case_id}"]["get"]["operationId"]
        == "getRecruitmentCase"
    )
    assert (
        spec["paths"]["/api/cases/{case_id}/next-actions"]["get"]["operationId"]
        == "getCaseNextActions"
    )
    assert (
        spec["paths"]["/api/cases/{case_id}/source-documents"]["post"][
            "operationId"
        ]
        == "registerSourceDocument"
    )
    assert (
        spec["paths"]["/api/cases/{case_id}/role-intake"]["post"]["operationId"]
        == "createRoleIntakeArtifact"
    )
    assert (
        spec["paths"]["/api/cases/{case_id}/rubrics"]["post"]["operationId"]
        == "registerApprovedRubric"
    )
    case_schema = spec["components"]["schemas"]["CaseEnvelope"]
    assert "case_id" in case_schema["properties"]
    assert "next_actions" in case_schema["properties"]

    serialized_paths = json.dumps(sorted(paths))
    for deferred in (
        "notifications",
        "applicants",
        "assessments",
        "human-reviews",
        "final-recommendation",
        "search",
    ):
        assert deferred not in serialized_paths
