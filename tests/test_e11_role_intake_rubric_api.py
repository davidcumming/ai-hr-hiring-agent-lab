"""E11 role-intake and approved-rubric API coverage."""

from __future__ import annotations

from hr_eval_lab.domain.schemas.workflow import (
    Approval,
    ArtifactVersion,
    CaseEvent,
    RecruitmentCase,
)
from tests.conftest import CountingProvider, HR_HEADERS, identity_headers

SOURCE_TEXT = "Synthetic source text for the E11 API facade."


def _case_body(**overrides):
    body = {
        "role_title": "Synthetic Intake Analyst",
        "department": "Synthetic Lab",
        "recruitment_type": "permanent",
    }
    body.update(overrides)
    return body


def _source_document_body(**overrides):
    body = {
        "document_type": "job_description",
        "source_origin": "manual_upload",
        "source_label": "Synthetic E11 role brief",
        "file_name": "synthetic-e11-role-brief.txt",
        "mime_type": "text/plain",
        "synthetic": True,
        "content_text": SOURCE_TEXT,
    }
    body.update(overrides)
    return body


def _role_intake_body(**overrides):
    body = {
        "synthetic": True,
        "intake_title": "Synthetic Intake Analyst intake",
        "role_purpose": "Coordinate deterministic E11 hiring lab intake work.",
        "responsibilities": ["Maintain synthetic intake records."],
        "required_qualifications": ["Experience with structured HR workflows."],
        "preferred_qualifications": ["Experience with Azure-shaped lab workflows."],
        "business_context": "Synthetic team expansion.",
        "role_risks": ["Ambiguous source documents."],
        "open_questions": ["Confirm interview panel."],
    }
    body.update(overrides)
    return body


def _rubric_body(**overrides):
    body = {
        "synthetic": True,
        "rubric_title": "Synthetic intake analyst screening rubric",
        "criteria": [
            {
                "criterion_id": "workflow_experience",
                "label": "Workflow experience",
                "description": "Experience operating structured HR workflows.",
                "weight": 60,
                "rating_scale": [
                    {
                        "score": 0,
                        "label": "No evidence",
                        "description": "No relevant workflow evidence.",
                    },
                    {
                        "score": 5,
                        "label": "Strong evidence",
                        "description": "Clear relevant workflow evidence.",
                    },
                ],
                "evidence_expectations": ["Role-source references only."],
            },
            {
                "criterion_id": "documentation_quality",
                "label": "Documentation quality",
                "description": "Can maintain clear synthetic case documentation.",
                "weight": 40,
                "rating_scale": [
                    {
                        "score": 0,
                        "label": "No evidence",
                        "description": "No documentation evidence.",
                    },
                    {
                        "score": 5,
                        "label": "Strong evidence",
                        "description": "Clear documentation evidence.",
                    },
                ],
            },
        ],
    }
    body.update(overrides)
    return body


def _create_case(client):
    response = client.post("/api/cases", json=_case_body(), headers=HR_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    return response.json()["case_id"]


def _register_source_document(client, case_id):
    response = client.post(
        f"/api/cases/{case_id}/source-documents",
        json=_source_document_body(),
        headers=HR_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    return response.json()["result"]["document"]["document_id"]


def test_e11_role_intake_and_rubric_api_round_trip_metadata_safe(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)
    case_id = _create_case(client)
    document_id = _register_source_document(client, case_id)

    role_response = client.post(
        f"/api/cases/{case_id}/role-intake",
        json=_role_intake_body(source_document_ids=[document_id]),
        headers=HR_HEADERS,
    )

    assert role_response.status_code == 200
    role_envelope = role_response.json()
    assert role_envelope["status"] == "completed"
    assert role_envelope["case_id"] == case_id
    assert role_response.headers["X-Correlation-Id"] == role_envelope["correlation_id"]
    assert "complete_role_intake" not in [
        action["action_id"] for action in role_envelope["next_actions"]
    ]
    assert SOURCE_TEXT not in str(role_envelope)

    role_result = role_envelope["result"]
    assert role_result["artifact"]["artifact_type"] == "role_intake"
    assert role_result["artifact"]["version"] == "v1"
    assert role_result["role_intake"]["source_document_ids"] == [document_id]
    assert role_result["role_intake"]["source_documents"][0]["document_id"] == document_id
    assert "content_text" not in role_result["role_intake"]["source_documents"][0]
    assert role_result["case"]["active_intake_version"] == "v1"

    role_get = client.get(f"/api/cases/{case_id}/role-intake", headers=HR_HEADERS)
    assert role_get.status_code == 200
    assert role_get.json()["status"] == "completed"
    assert role_get.json()["result"]["artifact"]["version"] == "v1"
    assert SOURCE_TEXT not in str(role_get.json())

    rubric_response = client.post(
        f"/api/cases/{case_id}/rubrics",
        json=_rubric_body(approved_by_actor_id="u-hr-001"),
        headers=HR_HEADERS,
    )
    assert rubric_response.status_code == 200
    rubric_envelope = rubric_response.json()
    assert rubric_envelope["status"] == "completed"
    assert rubric_envelope["result"]["artifact"]["artifact_type"] == "screening_rubric"
    assert rubric_envelope["result"]["artifact"]["version"] == "v1"
    assert rubric_envelope["result"]["rubric"]["approved_by_actor_id"] == "u-hr-001"
    assert rubric_envelope["result"]["case"]["active_rubric_version"] == "v1"
    assert "rubric_approval_required" not in [
        gate["gate_id"]
        for gate in client.get(
            f"/api/cases/{case_id}/next-actions",
            headers=HR_HEADERS,
        ).json()["result"]["active_gate_blockers"]
    ]
    next_action_result = client.get(
        f"/api/cases/{case_id}/next-actions",
        headers=HR_HEADERS,
    ).json()["result"]
    assert {
        gate["gate_id"] for gate in next_action_result["active_gate_blockers"]
    } == {"applicant_set_confirmation_required", "assessment_unlocked"}

    list_rubrics = client.get(f"/api/cases/{case_id}/rubrics", headers=HR_HEADERS)
    assert list_rubrics.status_code == 200
    assert list_rubrics.json()["result"]["active_rubric_version"] == "v1"
    assert [item["version"] for item in list_rubrics.json()["result"]["rubrics"]] == [
        "v1"
    ]

    get_rubric = client.get(f"/api/cases/{case_id}/rubrics/v1", headers=HR_HEADERS)
    assert get_rubric.status_code == 200
    assert get_rubric.json()["result"]["rubric"]["rubric_version"] == "v1"

    store = client.app.state.workflow_storage
    assert len(store.list_table_entities(ArtifactVersion, case_id)) == 2
    assert len(store.list_table_entities(Approval, case_id)) == 1
    assert [
        event.event_type for event in store.list_table_entities(CaseEvent, case_id)
    ] == [
        "case_created",
        "source_document_registered",
        "role_intake_artifact_created",
        "rubric_approved",
    ]
    case = store.get_table_entity(RecruitmentCase, case_id, "case")
    assert case.active_intake_version == "v1"
    assert case.active_rubric_version == "v1"
    assert case.case_status == "intake_pending"
    assert store.peek_queue_messages() == []
    assert provider.calls == []


def test_e11_api_auth_runs_before_body_validation(client):
    role_response = client.post(
        "/api/cases/case-any/role-intake",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )
    rubric_response = client.post(
        "/api/cases/case-any/rubrics",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )

    assert role_response.status_code == 401
    assert rubric_response.status_code == 401
    assert role_response.json()["status"] == "unauthorized"
    assert rubric_response.json()["status"] == "unauthorized"


def test_e11_api_denied_requests_leave_no_e11_state(make_client):
    client = make_client()
    case_id = _create_case(client)
    _register_source_document(client, case_id)
    denied_headers = identity_headers(actor_id="u-nothr-e11", roles="reviewer")

    role_response = client.post(
        f"/api/cases/{case_id}/role-intake",
        json=_role_intake_body(),
        headers=denied_headers,
    )
    rubric_response = client.post(
        f"/api/cases/{case_id}/rubrics",
        json=_rubric_body(),
        headers=denied_headers,
    )

    assert role_response.status_code == 403
    assert rubric_response.status_code == 403
    assert role_response.json()["status"] == "unauthorized"
    assert rubric_response.json()["status"] == "unauthorized"
    store = client.app.state.workflow_storage
    assert store.list_table_entities(ArtifactVersion, case_id) == []
    assert store.list_table_entities(Approval, case_id) == []
    assert store.peek_queue_messages() == []


def test_e11_api_malformed_bodies_http_400(client):
    case_id = _create_case(client)
    _register_source_document(client, case_id)

    role_path = f"/api/cases/{case_id}/role-intake"
    role_cases = [
        (None, b"not json {", {**HR_HEADERS, "Content-Type": "application/json"}),
        ([], None, HR_HEADERS),
        ({"synthetic": True}, None, HR_HEADERS),
        (_role_intake_body(synthetic=False), None, HR_HEADERS),
        (_role_intake_body(responsibilities=[]), None, HR_HEADERS),
        (_role_intake_body(resume_text="not allowed"), None, HR_HEADERS),
        (_role_intake_body(blob_path="not allowed"), None, HR_HEADERS),
        (_role_intake_body(model="not allowed"), None, HR_HEADERS),
        (_role_intake_body(assessment_unlocked=True), None, HR_HEADERS),
    ]
    for json_body, content, headers in role_cases:
        if content is not None:
            response = client.post(role_path, content=content, headers=headers)
        else:
            response = client.post(role_path, json=json_body, headers=headers)
        assert response.status_code == 400
        assert response.json()["error"] == "malformed_request_body"

    rubric_path = f"/api/cases/{case_id}/rubrics"
    rubric_cases = [
        (None, b"not json {", {**HR_HEADERS, "Content-Type": "application/json"}),
        ([], None, HR_HEADERS),
        ({"synthetic": True}, None, HR_HEADERS),
        (_rubric_body(synthetic=False), None, HR_HEADERS),
        (_rubric_body(criteria=[]), None, HR_HEADERS),
        (_rubric_body(provider="not allowed"), None, HR_HEADERS),
        (_rubric_body(queue_hint="not allowed"), None, HR_HEADERS),
        (
            _rubric_body(
                criteria=[
                    {
                        **_rubric_body()["criteria"][0],
                        "rating_scale": [
                            {
                                "score": 5,
                                "label": "Only one anchor",
                                "description": "Invalid scale.",
                            }
                        ],
                    }
                ]
            ),
            None,
            HR_HEADERS,
        ),
    ]
    for json_body, content, headers in rubric_cases:
        if content is not None:
            response = client.post(rubric_path, content=content, headers=headers)
        else:
            response = client.post(rubric_path, json=json_body, headers=headers)
        assert response.status_code == 400
        assert response.json()["error"] == "malformed_request_body"


def test_e11_api_validation_failed_semantic_outcomes(make_client):
    client = make_client()

    missing_case_role = client.post(
        "/api/cases/case-missing/role-intake",
        json=_role_intake_body(),
        headers=HR_HEADERS,
    )
    assert missing_case_role.status_code == 200
    assert missing_case_role.json()["errors"] == ["unknown_case_id"]

    missing_case_rubric = client.post(
        "/api/cases/case-missing/rubrics",
        json=_rubric_body(),
        headers=HR_HEADERS,
    )
    assert missing_case_rubric.status_code == 200
    assert missing_case_rubric.json()["errors"] == ["unknown_case_id"]

    case_id = _create_case(client)
    no_docs = client.post(
        f"/api/cases/{case_id}/role-intake",
        json=_role_intake_body(),
        headers=HR_HEADERS,
    )
    assert no_docs.status_code == 200
    assert no_docs.json()["errors"] == ["source_documents_required"]

    document_id = _register_source_document(client, case_id)
    unknown_source = client.post(
        f"/api/cases/{case_id}/role-intake",
        json=_role_intake_body(source_document_ids=[document_id, "doc-missing"]),
        headers=HR_HEADERS,
    )
    assert unknown_source.status_code == 200
    assert unknown_source.json()["errors"] == ["unknown_source_document_id"]

    created_role = client.post(
        f"/api/cases/{case_id}/role-intake",
        json=_role_intake_body(source_document_ids=[document_id]),
        headers=HR_HEADERS,
    )
    assert created_role.json()["status"] == "completed"
    duplicate_role = client.post(
        f"/api/cases/{case_id}/role-intake",
        json=_role_intake_body(role_purpose="Changed purpose."),
        headers=HR_HEADERS,
    )
    assert duplicate_role.status_code == 200
    assert duplicate_role.json()["errors"] == ["role_intake_version_exists"]

    missing_role_get_case = _create_case(client)
    role_get = client.get(
        f"/api/cases/{missing_role_get_case}/role-intake",
        headers=HR_HEADERS,
    )
    assert role_get.status_code == 200
    assert role_get.json()["errors"] == ["role_intake_not_found"]

    mismatch = client.post(
        f"/api/cases/{case_id}/rubrics",
        json=_rubric_body(approved_by_actor_id="u-other"),
        headers=HR_HEADERS,
    )
    assert mismatch.status_code == 200
    assert mismatch.json()["errors"] == ["approved_by_actor_mismatch"]

    created_rubric = client.post(
        f"/api/cases/{case_id}/rubrics",
        json=_rubric_body(),
        headers=HR_HEADERS,
    )
    assert created_rubric.json()["status"] == "completed"
    duplicate_rubric = client.post(
        f"/api/cases/{case_id}/rubrics",
        json=_rubric_body(rubric_title="Changed rubric"),
        headers=HR_HEADERS,
    )
    assert duplicate_rubric.status_code == 200
    assert duplicate_rubric.json()["errors"] == ["rubric_version_exists"]

    missing_rubric = client.get(
        f"/api/cases/{case_id}/rubrics/v-missing",
        headers=HR_HEADERS,
    )
    assert missing_rubric.status_code == 200
    assert missing_rubric.json()["errors"] == ["unknown_rubric_version"]
    assert client.app.state.workflow_storage.peek_queue_messages() == []
