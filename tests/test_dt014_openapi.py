"""DT-014 — OpenAPI validation + contract-vs-implementation conformance.

Related: AC-017, FR-010, RF-005.

The committed openapi/evaluations-api.json must (a) be a valid OpenAPI
document (openapi-spec-validator) and (b) byte-match the document regenerated
from the live app factory (scripts/export_openapi.py --check semantics), so
contract and implementation cannot silently diverge. The emitted status
vocabulary is asserted against the document's envelope schema.
"""

from __future__ import annotations

import json
import subprocess
import sys

from openapi_spec_validator import validate as validate_spec

from tests.conftest import REPO_ROOT

OPENAPI_PATH = REPO_ROOT / "openapi" / "evaluations-api.json"


def _committed_spec() -> dict:
    return json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))


def test_committed_document_is_valid_openapi():
    validate_spec(_committed_spec())


def test_committed_document_matches_regenerated_output():
    """export_openapi.py --check: exit 0 means zero drift."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "export_openapi.py"), "--check"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"OpenAPI drift detected:\n{result.stderr}"


def test_routes_and_status_vocabulary_conform():
    spec = _committed_spec()
    paths = spec["paths"]
    assert set(paths) == {
        "/api/cases",
        "/api/cases/{case_id}",
        "/api/cases/{case_id}/next-actions",
        "/api/evaluations",
        "/api/evaluations/retrieve",
        "/api/evaluations/{evaluation_id}",
    }
    assert "post" in paths["/api/cases"]
    assert "get" in paths["/api/cases/{case_id}"]
    assert "get" in paths["/api/cases/{case_id}/next-actions"]
    assert "post" in paths["/api/evaluations"]
    assert "post" in paths["/api/evaluations/retrieve"]
    assert "get" in paths["/api/evaluations/{evaluation_id}"]
    assert paths["/api/cases"]["post"]["operationId"] == "createRecruitmentCase"
    assert paths["/api/cases/{case_id}"]["get"]["operationId"] == "getRecruitmentCase"
    assert (
        paths["/api/cases/{case_id}/next-actions"]["get"]["operationId"]
        == "getCaseNextActions"
    )
    assert (
        paths["/api/evaluations/retrieve"]["post"]["operationId"]
        == "retrieveEvaluationForCopilot"
    )

    # The envelope schema's status enum is the adopted fixed vocabulary
    # (emitted four + the two declared-reserved values).
    envelope = spec["components"]["schemas"]["Envelope"]
    status_schema = envelope["properties"]["status"]
    assert set(status_schema["enum"]) == {
        "completed",
        "blocked",
        "validation_failed",
        "unauthorized",
        "needs_input",
        "error",
    }
    # Reserved statuses are documented as reserved, never emitted.
    description = spec["info"]["description"]
    assert "RESERVED" in description

    # Request body documents the single request schema source.
    request_schema = paths["/api/evaluations"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    for field in ("position_id", "idempotency_key", "requested_rigor"):
        assert field in request_schema["properties"]

    retrieve_schema = paths["/api/evaluations/retrieve"]["post"]["requestBody"][
        "content"
    ]["application/json"]["schema"]
    assert set(retrieve_schema["properties"]) == {"evaluation_id"}
    assert retrieve_schema["required"] == ["evaluation_id"]

    case_request_body = paths["/api/cases"]["post"]["requestBody"]
    case_request_schema = case_request_body["content"]["application/json"]["schema"]
    assert case_request_schema == {
        "$ref": "#/components/schemas/RecruitmentCaseCreateRequest"
    }
    assert "$defs" not in case_request_schema
    assert "#/$defs/" not in json.dumps(case_request_body)

    components = spec["components"]["schemas"]
    assert "RecruitmentCaseCreateRequest" in components
    assert "HiringManagerInput" in components
    create_case_component = components["RecruitmentCaseCreateRequest"]
    assert "$defs" not in create_case_component
    assert {
        "role_title",
        "department",
        "recruitment_type",
        "case_title",
        "hiring_manager",
    } == set(create_case_component["properties"])
    assert create_case_component["required"] == [
        "role_title",
        "department",
        "recruitment_type",
    ]

    case_envelope = spec["components"]["schemas"]["CaseEnvelope"]
    assert "next_actions" in case_envelope["properties"]
    assert "case_id" in case_envelope["properties"]
