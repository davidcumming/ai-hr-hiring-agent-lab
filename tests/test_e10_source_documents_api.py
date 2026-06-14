"""E10 source-document API coverage and non-goal pins."""

from __future__ import annotations

from hr_eval_lab.domain.schemas.workflow import (
    ArtifactVersion,
    CaseEvent,
    SourceDocument,
)
from tests.conftest import CountingProvider, HR_HEADERS, identity_headers

CONTENT = "Synthetic source text for the E10 API facade."


def _case_body(**overrides):
    body = {
        "role_title": "Synthetic HR Analyst",
        "department": "Synthetic Lab",
        "recruitment_type": "permanent",
    }
    body.update(overrides)
    return body


def _document_body(**overrides):
    body = {
        "document_type": "job_description",
        "source_origin": "manual_upload",
        "source_label": "Synthetic role brief",
        "file_name": "synthetic-role-brief.txt",
        "mime_type": "text/plain",
        "synthetic": True,
        "content_text": CONTENT,
    }
    body.update(overrides)
    return body


def _create_case(client):
    response = client.post("/api/cases", json=_case_body(), headers=HR_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    return response.json()["case_id"]


def test_e10_source_document_api_register_list_and_get_round_trip(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)
    case_id = _create_case(client)

    register = client.post(
        f"/api/cases/{case_id}/source-documents",
        json=_document_body(),
        headers=HR_HEADERS,
    )

    assert register.status_code == 200
    envelope = register.json()
    assert envelope["status"] == "completed"
    assert envelope["case_id"] == case_id
    assert envelope["correlation_id"].startswith("corr-")
    assert register.headers["X-Correlation-Id"] == envelope["correlation_id"]
    assert "attach_source_documents" not in [
        action["action_id"] for action in envelope["next_actions"]
    ]

    result = envelope["result"]
    document = result["document"]
    assert result["case"]["case_id"] == case_id
    assert result["documents_count"] == 1
    assert document["document_id"].startswith("doc-")
    assert document["document_type"] == "job_description"
    assert document["source_origin"] == "manual_upload"
    assert document["source_label"] == "Synthetic role brief"
    assert document["mime_type"] == "text/plain"
    assert document["file_name"] == "synthetic-role-brief.txt"
    assert document["blob_path"].endswith(f"/{document['document_id']}/raw")
    assert document["size_bytes"] == len(CONTENT.encode("utf-8"))
    assert "content_text" not in document
    assert CONTENT not in str(envelope)

    store = client.app.state.workflow_storage
    assert store.read_blob_bytes(document["blob_path"]) == CONTENT.encode("utf-8")
    assert len(store.list_table_entities(SourceDocument, case_id)) == 1
    assert len(store.list_table_entities(ArtifactVersion, case_id)) == 0
    assert [
        event.event_type
        for event in store.list_table_entities(CaseEvent, case_id)
    ] == ["case_created", "source_document_registered"]
    assert store.peek_queue_messages() == []
    assert provider.calls == []

    listed = client.get(
        f"/api/cases/{case_id}/source-documents",
        headers=HR_HEADERS,
    )
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert listed_payload["status"] == "completed"
    assert listed_payload["result"]["case_id"] == case_id
    assert [doc["document_id"] for doc in listed_payload["result"]["documents"]] == [
        document["document_id"]
    ]
    assert CONTENT not in str(listed_payload)

    retrieved = client.get(
        f"/api/cases/{case_id}/source-documents/{document['document_id']}",
        headers=HR_HEADERS,
    )
    assert retrieved.status_code == 200
    retrieved_payload = retrieved.json()
    assert retrieved_payload["status"] == "completed"
    assert retrieved_payload["result"]["document"]["document_id"] == document["document_id"]
    assert "content_text" not in retrieved_payload["result"]["document"]
    assert CONTENT not in str(retrieved_payload)


def test_e10_source_document_api_auth_runs_before_body_validation(client):
    response = client.post(
        "/api/cases/case-any/source-documents",
        content=b"not json {",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401
    assert response.json()["status"] == "unauthorized"


def test_e10_source_document_api_denied_request_leaves_no_document_state(make_client):
    client = make_client()
    case_id = _create_case(client)

    response = client.post(
        f"/api/cases/{case_id}/source-documents",
        json=_document_body(),
        headers=identity_headers(actor_id="u-nothr-e10", roles="reviewer"),
    )

    assert response.status_code == 403
    assert response.json()["status"] == "unauthorized"
    store = client.app.state.workflow_storage
    assert store.list_table_entities(SourceDocument, case_id) == []
    assert not any(store.blobs_root.rglob("*"))
    assert store.peek_queue_messages() == []


def test_e10_source_document_api_malformed_bodies_http_400(client):
    case_id = _create_case(client)
    path = f"/api/cases/{case_id}/source-documents"

    cases = [
        (None, b"not json {", {**HR_HEADERS, "Content-Type": "application/json"}),
        ([], None, HR_HEADERS),
        (
            {
                "document_type": "job_description",
                "source_origin": "manual_upload",
                "synthetic": True,
            },
            None,
            HR_HEADERS,
        ),
        ({**_document_body(), "sha256": "0" * 64}, None, HR_HEADERS),
        (_document_body(synthetic=False), None, HR_HEADERS),
        (_document_body(mime_type="application/pdf"), None, HR_HEADERS),
        (_document_body(source_origin="generated"), None, HR_HEADERS),
        (_document_body(document_type="resume"), None, HR_HEADERS),
        (_document_body(content_text="   "), None, HR_HEADERS),
        (_document_body(content_text="x" * 20_001), None, HR_HEADERS),
    ]

    for json_body, content, headers in cases:
        if content is not None:
            response = client.post(path, content=content, headers=headers)
        else:
            response = client.post(path, json=json_body, headers=headers)
        assert response.status_code == 400
        assert response.json()["error"] == "malformed_request_body"


def test_e10_source_document_api_unknown_case_and_document_envelopes(make_client):
    client = make_client()

    register_missing_case = client.post(
        "/api/cases/case-missing/source-documents",
        json=_document_body(),
        headers=HR_HEADERS,
    )
    assert register_missing_case.status_code == 200
    assert register_missing_case.json()["status"] == "validation_failed"
    assert register_missing_case.json()["errors"] == ["unknown_case_id"]

    list_missing_case = client.get(
        "/api/cases/case-missing/source-documents",
        headers=HR_HEADERS,
    )
    assert list_missing_case.status_code == 200
    assert list_missing_case.json()["errors"] == ["unknown_case_id"]

    store = client.app.state.workflow_storage
    assert store.list_table_entities(SourceDocument) == []
    assert not any(store.blobs_root.rglob("*"))
    assert store.peek_queue_messages() == []

    case_id = _create_case(client)
    missing_document = client.get(
        f"/api/cases/{case_id}/source-documents/doc-missing",
        headers=HR_HEADERS,
    )
    assert missing_document.status_code == 200
    payload = missing_document.json()
    assert payload["status"] == "validation_failed"
    assert payload["case_id"] == case_id
    assert payload["errors"] == ["unknown_document_id"]
