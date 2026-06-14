"""E12 applicant/candidate package intake API coverage."""

from __future__ import annotations

from hr_eval_lab.domain.schemas.workflow import (
    Applicant,
    CandidatePackage,
    CaseEvent,
    SourceDocument,
)
from tests.conftest import CountingProvider, HR_HEADERS, identity_headers

RESUME_TEXT = "Synthetic resume text for the E12 API facade."
COVER_TEXT = "Synthetic cover letter text for the E12 API facade."


def _case_body(**overrides):
    body = {
        "role_title": "Synthetic Applicant Intake Analyst",
        "department": "Synthetic Lab",
        "recruitment_type": "permanent",
    }
    body.update(overrides)
    return body


def _applicant_body(**overrides):
    body = {
        "synthetic": True,
        "candidate_ref": "E12-API-001",
        "display_label": "E12 API Candidate 001",
    }
    body.update(overrides)
    return body


def _document_body(**overrides):
    body = {
        "document_type": "resume",
        "source_origin": "manual_upload",
        "source_label": "Synthetic API resume",
        "file_name": "synthetic-api-resume.md",
        "mime_type": "text/markdown",
        "synthetic": True,
        "content_text": RESUME_TEXT,
    }
    body.update(overrides)
    return body


def _import_body(**overrides):
    body = {
        "synthetic": True,
        "candidates": [
            {
                "candidate_ref": "E12-API-002",
                "display_label": "E12 API Candidate 002",
                "documents": [
                    _document_body(
                        source_label="Synthetic API import resume",
                        file_name="synthetic-api-import-resume.md",
                        content_text="Synthetic imported resume.",
                    )
                ],
            }
        ],
    }
    body.update(overrides)
    return body


def _create_case(client):
    response = client.post("/api/cases", json=_case_body(), headers=HR_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    return response.json()["case_id"]


def _blob_files(client):
    store = client.app.state.workflow_storage
    return sorted(path for path in store.blobs_root.rglob("*") if path.is_file())


def test_e12_api_all_routes_round_trip_with_metadata_only_payloads(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)
    case_id = _create_case(client)

    register = client.post(
        f"/api/cases/{case_id}/applicants",
        json=_applicant_body(),
        headers=HR_HEADERS,
    )
    assert register.status_code == 200
    register_payload = register.json()
    assert register_payload["status"] == "completed"
    assert register_payload["case_id"] == case_id
    assert register.headers["X-Correlation-Id"] == register_payload["correlation_id"]
    candidate_id = register_payload["result"]["applicant"]["candidate_id"]
    assert register_payload["result"]["package"]["package_status"] == "blocked"

    list_applicants = client.get(
        f"/api/cases/{case_id}/applicants",
        headers=HR_HEADERS,
    )
    assert list_applicants.status_code == 200
    listed_payload = list_applicants.json()
    assert listed_payload["status"] == "completed"
    assert listed_payload["result"]["case_id"] == case_id
    assert [item["candidate_id"] for item in listed_payload["result"]["applicants"]] == [
        candidate_id
    ]
    assert RESUME_TEXT not in str(listed_payload)

    get_applicant = client.get(
        f"/api/cases/{case_id}/applicants/{candidate_id}",
        headers=HR_HEADERS,
    )
    assert get_applicant.status_code == 200
    get_payload = get_applicant.json()
    assert get_payload["status"] == "completed"
    assert get_payload["result"]["applicant"]["candidate_id"] == candidate_id
    assert get_payload["result"]["documents"] == []
    assert RESUME_TEXT not in str(get_payload)

    register_document = client.post(
        f"/api/cases/{case_id}/candidates/{candidate_id}/documents",
        json=_document_body(),
        headers=HR_HEADERS,
    )
    assert register_document.status_code == 200
    document_payload = register_document.json()
    assert document_payload["status"] == "completed"
    assert document_payload["result"]["document"]["candidate_id"] == candidate_id
    assert document_payload["result"]["document"]["document_type"] == "resume"
    assert document_payload["result"]["package"]["package_status"] == "complete"
    assert "content_text" not in document_payload["result"]["document"]
    assert RESUME_TEXT not in str(document_payload)

    process_import = client.post(
        f"/api/cases/{case_id}/applicant-imports",
        json=_import_body(),
        headers=HR_HEADERS,
    )
    assert process_import.status_code == 200
    import_payload = process_import.json()
    assert import_payload["status"] == "completed"
    assert import_payload["result"]["imported_count"] == 1
    assert import_payload["result"]["document_count"] == 1
    assert import_payload["result"]["can_confirm"] is True
    imported_candidate_id = import_payload["result"]["applicants"][0]["candidate_id"]

    findings = client.get(
        f"/api/cases/{case_id}/import-findings",
        headers=HR_HEADERS,
    )
    assert findings.status_code == 200
    findings_payload = findings.json()
    assert findings_payload["status"] == "completed"
    assert findings_payload["result"]["findings"] == []
    assert findings_payload["result"]["can_confirm"] is True
    assert RESUME_TEXT not in str(findings_payload)

    confirm = client.post(
        f"/api/cases/{case_id}/applicant-set/confirm",
        json={"synthetic": True},
        headers=HR_HEADERS,
    )
    assert confirm.status_code == 200
    confirm_payload = confirm.json()
    assert confirm_payload["status"] == "completed"
    assert confirm_payload["result"]["confirmed_applicant_set_version"] == "v1"
    assert set(confirm_payload["result"]["confirmed_candidate_ids"]) == {
        candidate_id,
        imported_candidate_id,
    }
    assert confirm_payload["result"]["assessment_unlocked"] == "locked"
    assert "confirm_applicant_set" not in [
        action["action_id"] for action in confirm_payload["next_actions"]
    ]

    store = client.app.state.workflow_storage
    assert len(store.list_table_entities(Applicant, case_id)) == 2
    assert len(store.list_table_entities(SourceDocument, case_id)) == 2
    assert len(store.list_table_entities(CandidatePackage, case_id)) == 2
    assert [
        event.event_type for event in store.list_table_entities(CaseEvent, case_id)
    ] == [
        "case_created",
        "applicant_registered",
        "candidate_document_registered",
        "applicant_import_processed",
        "applicant_set_confirmed",
    ]
    assert store.peek_queue_messages() == []
    assert provider.calls == []


def test_e12_api_auth_runs_before_body_validation_and_denial_leaves_no_state(
    make_client,
):
    client = make_client()
    unauthorized = client.post(
        "/api/cases/case-any/applicants",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )
    assert unauthorized.status_code == 401
    assert unauthorized.json()["status"] == "unauthorized"

    case_id = _create_case(client)
    denied = client.post(
        f"/api/cases/{case_id}/applicants",
        json=_applicant_body(),
        headers=identity_headers(actor_id="u-nothr-e12", roles="reviewer"),
    )
    assert denied.status_code == 403
    assert denied.json()["status"] == "unauthorized"
    store = client.app.state.workflow_storage
    assert store.list_table_entities(Applicant, case_id) == []
    assert not any(store.blobs_root.rglob("*"))
    assert store.peek_queue_messages() == []

    denied_read = client.get(
        f"/api/cases/{case_id}/applicants",
        headers=identity_headers(actor_id="u-hm-e12", roles="hiring_manager"),
    )
    assert denied_read.status_code == 403
    assert denied_read.json()["status"] == "unauthorized"


def test_e12_api_malformed_shapes_are_400_semantic_failures_are_envelopes(
    make_client,
):
    client = make_client()
    case_id = _create_case(client)
    path = f"/api/cases/{case_id}/applicants"

    malformed_cases = [
        (None, b"not json {", {**HR_HEADERS, "Content-Type": "application/json"}),
        ([], None, HR_HEADERS),
        ({"synthetic": True}, None, HR_HEADERS),
        (_applicant_body(synthetic=False), None, HR_HEADERS),
        (_applicant_body(candidate_ref="   "), None, HR_HEADERS),
        (_applicant_body(model="not allowed"), None, HR_HEADERS),
    ]
    for json_body, content, headers in malformed_cases:
        if content is not None:
            response = client.post(path, content=content, headers=headers)
        else:
            response = client.post(path, json=json_body, headers=headers)
        assert response.status_code == 400
        assert response.json()["error"] == "malformed_request_body"

    created = client.post(path, json=_applicant_body(), headers=HR_HEADERS)
    assert created.status_code == 200
    candidate_id = created.json()["result"]["applicant"]["candidate_id"]
    blob_files_before_semantic_failures = _blob_files(client)

    duplicate = client.post(
        path,
        json=_applicant_body(candidate_ref=" e12-api-001 "),
        headers=HR_HEADERS,
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["status"] == "validation_failed"
    assert duplicate.json()["errors"] == ["duplicate_candidate_ref"]

    unsupported = client.post(
        f"/api/cases/{case_id}/candidates/{candidate_id}/documents",
        json=_document_body(document_type="transcript"),
        headers=HR_HEADERS,
    )
    assert unsupported.status_code == 200
    assert unsupported.json()["status"] == "validation_failed"
    assert unsupported.json()["errors"] == ["unsupported_document_type"]
    assert _blob_files(client) == blob_files_before_semantic_failures
    store = client.app.state.workflow_storage
    assert store.list_table_entities(SourceDocument, case_id) == []

    bad_document_shape = client.post(
        f"/api/cases/{case_id}/candidates/{candidate_id}/documents",
        json={**_document_body(), "content_text": "   "},
        headers=HR_HEADERS,
    )
    assert bad_document_shape.status_code == 400

    blocked_confirm = client.post(
        f"/api/cases/{case_id}/applicant-set/confirm",
        json={"synthetic": True},
        headers=HR_HEADERS,
    )
    assert blocked_confirm.status_code == 200
    assert blocked_confirm.json()["status"] == "blocked"
    assert blocked_confirm.json()["errors"] == ["applicant_set_incomplete"]

    unknown_case = client.get(
        "/api/cases/case-missing/import-findings",
        headers=HR_HEADERS,
    )
    assert unknown_case.status_code == 200
    assert unknown_case.json()["status"] == "validation_failed"
    assert unknown_case.json()["errors"] == ["unknown_case_id"]


def test_e12_api_import_findings_report_missing_resume_without_raw_text(make_client):
    client = make_client()
    case_id = _create_case(client)

    imported = client.post(
        f"/api/cases/{case_id}/applicant-imports",
        json=_import_body(
            candidates=[
                {
                    "candidate_ref": "E12-API-COVER-ONLY",
                    "display_label": "Cover Only Candidate",
                    "documents": [
                        _document_body(
                            document_type="cover_letter",
                            source_label="Synthetic API cover letter",
                            file_name="synthetic-api-cover.md",
                            content_text=COVER_TEXT,
                        )
                    ],
                }
            ]
        ),
        headers=HR_HEADERS,
    )

    assert imported.status_code == 200
    import_payload = imported.json()
    assert import_payload["status"] == "completed"
    assert import_payload["result"]["can_confirm"] is False
    assert import_payload["result"]["findings"][0]["finding_type"] == (
        "missing_required_resume"
    )
    assert COVER_TEXT not in str(import_payload)

    findings = client.get(
        f"/api/cases/{case_id}/import-findings",
        headers=HR_HEADERS,
    )
    assert findings.status_code == 200
    findings_payload = findings.json()
    assert findings_payload["result"]["findings"][0]["severity"] == "blocking"
    assert findings_payload["result"]["packages"][0]["package_status"] == "blocked"
    assert COVER_TEXT not in str(findings_payload)


def test_e12_api_locked_candidate_document_mutation_returns_safe_envelope(make_client):
    client = make_client()
    case_id = _create_case(client)
    imported = client.post(
        f"/api/cases/{case_id}/applicant-imports",
        json=_import_body(),
        headers=HR_HEADERS,
    )
    assert imported.status_code == 200
    assert imported.json()["status"] == "completed"
    candidate_id = imported.json()["result"]["applicants"][0]["candidate_id"]

    confirm = client.post(
        f"/api/cases/{case_id}/applicant-set/confirm",
        json={"synthetic": True},
        headers=HR_HEADERS,
    )
    assert confirm.status_code == 200
    assert confirm.json()["status"] == "completed"

    raw_text = "Synthetic post-confirmation document text must not leak."
    store = client.app.state.workflow_storage
    blobs_before = _blob_files(client)
    documents_before = store.list_table_entities(SourceDocument, case_id)
    packages_before = store.list_table_entities(CandidatePackage, case_id)
    events_before = store.list_table_entities(CaseEvent, case_id)

    locked = client.post(
        f"/api/cases/{case_id}/candidates/{candidate_id}/documents",
        json=_document_body(
            source_label="Rejected after confirmation",
            file_name="rejected-after-confirmation.md",
            content_text=raw_text,
        ),
        headers=HR_HEADERS,
    )

    assert locked.status_code == 200
    payload = locked.json()
    assert payload["status"] == "validation_failed"
    assert payload["case_id"] == case_id
    assert payload["errors"] == ["applicant_set_locked"]
    assert payload["user_message"] == (
        "Applicant set has already been confirmed and cannot be modified in E12."
    )
    assert payload["safe_details"] == "confirmed_applicant_set_version='v1'"
    assert raw_text not in str(payload)
    assert _blob_files(client) == blobs_before
    assert store.list_table_entities(SourceDocument, case_id) == documents_before
    assert store.list_table_entities(CandidatePackage, case_id) == packages_before
    assert store.list_table_entities(CaseEvent, case_id) == events_before
