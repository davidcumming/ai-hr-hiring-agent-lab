"""Copilot Studio curated Swagger artifact checks.

The FastAPI OpenAPI 3.1 document remains the source API contract. The E4
Swagger 2.0 file is a smaller custom-connector-compatible registration
artifact with the intended Copilot-facing actions.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from openapi_spec_validator import validate as validate_spec

from tests.conftest import REPO_ROOT

SOURCE_OPENAPI_PATH = REPO_ROOT / "openapi" / "evaluations-api.json"
COPILOT_SWAGGER_PATH = (
    REPO_ROOT / "openapi" / "copilot-studio" / "evaluations-tool.swagger.json"
)
REGISTRATION_GUIDE_PATH = (
    REPO_ROOT / "docs" / "integration" / "copilot-studio" / "registration-guide.md"
)
READINESS_DOC_PATH = REPO_ROOT / "docs" / "integration" / "copilot-studio-tool-readiness.md"

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

EXPECTED_ENVELOPE_FIELDS = {
    "status",
    "evaluation_id",
    "case_id",
    "correlation_id",
    "user_message",
    "safe_details",
    "result",
    "errors",
    "warnings",
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_strings(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child)
    elif isinstance(value, str):
        yield value


def test_copilot_swagger_exists_and_is_valid_swagger_2():
    spec = _json(COPILOT_SWAGGER_PATH)

    assert spec["swagger"] == "2.0"
    validate_spec(spec)


def test_source_openapi_31_contract_remains_distinct_and_checked():
    source = _json(SOURCE_OPENAPI_PATH)
    curated = _json(COPILOT_SWAGGER_PATH)

    assert source["openapi"] == "3.1.0"
    assert "swagger" not in source
    assert curated["swagger"] == "2.0"

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "export_openapi.py"), "--check"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr


def test_copilot_swagger_matches_generator():
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "export_copilot_openapi.py"),
            "--check",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr


def test_only_three_intended_actions_are_exposed():
    spec = _json(COPILOT_SWAGGER_PATH)
    assert set(spec["paths"]) == {
        "/api/evaluations",
        "/api/evaluations/retrieve",
        "/api/evaluations/{evaluation_id}",
    }
    assert set(spec["paths"]["/api/evaluations"]) == {"post"}
    assert set(spec["paths"]["/api/evaluations/retrieve"]) == {"post"}
    assert set(spec["paths"]["/api/evaluations/{evaluation_id}"]) == {"get"}
    assert spec["paths"]["/api/evaluations"]["post"]["operationId"] == "submitEvaluation"
    assert (
        spec["paths"]["/api/evaluations/retrieve"]["post"]["operationId"]
        == "retrieveEvaluationForCopilot"
    )
    assert (
        spec["paths"]["/api/evaluations/{evaluation_id}"]["get"]["operationId"]
        == "getEvaluation"
    )
    serialized_paths = json.dumps(spec["paths"])
    assert "/api/cases" not in serialized_paths
    assert "role-intake" not in serialized_paths
    assert "rubrics" not in serialized_paths
    assert "source-documents" not in serialized_paths
    assert "applicants" not in serialized_paths
    assert "candidates" not in serialized_paths
    assert "assessments" not in serialized_paths


def test_host_basepath_and_scheme_are_environment_neutral():
    spec = _json(COPILOT_SWAGGER_PATH)

    assert spec["host"] == "function-app-host.example"
    assert spec["basePath"] == "/"
    assert spec["schemes"] == ["https"]
    assert "azurewebsites.net" not in json.dumps(spec).lower()


def test_function_key_is_header_api_key_without_committed_value():
    spec = _json(COPILOT_SWAGGER_PATH)
    scheme = spec["securityDefinitions"]["function_key"]

    assert scheme == {
        "type": "apiKey",
        "name": "x-functions-key",
        "in": "header",
        "description": scheme["description"],
    }
    assert "Do not commit the key value" in scheme["description"]
    assert spec["security"] == [{"function_key": []}]
    for operation in (
        spec["paths"]["/api/evaluations"]["post"],
        spec["paths"]["/api/evaluations/retrieve"]["post"],
        spec["paths"]["/api/evaluations/{evaluation_id}"]["get"],
    ):
        assert operation["security"] == [{"function_key": []}]


def test_x_lab_headers_are_visible_and_marked_temporary():
    spec = _json(COPILOT_SWAGGER_PATH)

    for operation in (
        spec["paths"]["/api/evaluations"]["post"],
        spec["paths"]["/api/evaluations/retrieve"]["post"],
        spec["paths"]["/api/evaluations/{evaluation_id}"]["get"],
    ):
        headers = {
            p["name"]: p
            for p in operation["parameters"]
            if p.get("in") == "header" and p["name"].startswith("X-Lab-")
        }
        assert {"X-Lab-Actor-Id", "X-Lab-Roles", "X-Lab-Actor-Display"} <= set(headers)
        assert headers["X-Lab-Actor-Id"]["required"] is True
        assert headers["X-Lab-Roles"]["required"] is True
        assert headers["X-Lab-Roles"]["default"] == "hr"
        for header in headers.values():
            assert "Temporary E4 lab simulated" in header["description"] or (
                header["name"] == "X-Lab-Actor-Display"
            )


def test_request_schema_has_no_backend_selection_fields():
    spec = _json(COPILOT_SWAGGER_PATH)
    request_fields = set(spec["definitions"]["EvaluationRequest"]["properties"])

    assert not request_fields & FORBIDDEN_REQUEST_FIELDS
    assert {"position_id", "candidate_ref", "idempotency_key"} <= request_fields
    assert {"resume_text", "cover_letter_text"}.isdisjoint(request_fields)
    retrieve_fields = set(
        spec["definitions"]["EvaluationRetrieveRequest"]["properties"]
    )
    assert retrieve_fields == {"evaluation_id"}


def test_body_retrieve_operation_has_bindable_evaluation_id_input():
    spec = _json(COPILOT_SWAGGER_PATH)
    operation = spec["paths"]["/api/evaluations/retrieve"]["post"]
    body = next(p for p in operation["parameters"] if p["in"] == "body")

    assert operation["operationId"] == "retrieveEvaluationForCopilot"
    assert body["schema"] == {"$ref": "#/definitions/EvaluationRetrieveRequest"}
    assert "Copilot-friendly retrieve operation" in operation["description"]
    assert "stored topic variable" in operation["description"]
    assert "Dynamically fill with AI" not in operation["description"]


def test_envelope_fields_match_source_contract():
    source = _json(SOURCE_OPENAPI_PATH)
    curated = _json(COPILOT_SWAGGER_PATH)

    source_fields = set(source["components"]["schemas"]["Envelope"]["properties"])
    curated_fields = set(curated["definitions"]["Envelope"]["properties"])
    assert source_fields == EXPECTED_ENVELOPE_FIELDS
    assert curated_fields == EXPECTED_ENVELOPE_FIELDS
    assert (
        set(curated["definitions"]["Envelope"]["properties"]["status"]["enum"])
        == set(source["components"]["schemas"]["Envelope"]["properties"]["status"]["enum"])
    )


def test_examples_are_synthetic_only():
    spec = _json(COPILOT_SWAGGER_PATH)
    strings = "\n".join(_walk_strings(spec))
    request_fields = set(spec["definitions"]["EvaluationRequest"]["properties"])

    assert "pos-sample-001" in strings
    assert "cand-sample-001" in strings
    assert "synthetic" in strings.lower()
    assert "resume_text" not in request_fields
    assert "cover_letter_text" not in request_fields
    assert "Jordan" not in strings
    assert "Rivera" not in strings


def test_source_openapi_still_supports_inline_text_fields():
    source = _json(SOURCE_OPENAPI_PATH)
    request_schema = source["paths"]["/api/evaluations"]["post"]["requestBody"][
        "content"
    ]["application/json"]["schema"]
    source_fields = set(request_schema["properties"])

    assert {"resume_text", "cover_letter_text"} <= source_fields


def test_curated_artifacts_and_docs_do_not_contain_secrets_or_real_hosts():
    scan_paths = [COPILOT_SWAGGER_PATH, REGISTRATION_GUIDE_PATH, READINESS_DOC_PATH]
    text = "\n".join(path.read_text(encoding="utf-8") for path in scan_paths)
    lowered = text.lower()

    assert "azurewebsites.net" not in lowered
    assert "code=" not in lowered
    assert not re.search(r"(?<![a-z0-9_])(sig|sv|se|sp)=", lowered)
    for marker in (
        "defaultendpointsprotocol=",
        "accountkey=",
        "sharedaccesssignature=",
        "blobendpoint=",
    ):
        assert marker not in lowered
    assert not re.search(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
        lowered,
    )

    # The header name is expected. A concrete literal value after it is not.
    assert not re.search(
        r"x-functions-key\s*:\s*(?!\$\{HRHA_FUNCTION_KEY)(?!<function-key>)[A-Za-z0-9_./+=-]{8,}",
        text,
        flags=re.IGNORECASE,
    )
