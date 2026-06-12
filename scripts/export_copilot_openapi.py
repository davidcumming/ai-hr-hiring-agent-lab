"""Generate/check the curated Copilot Studio Swagger 2.0 registration artifact.

The FastAPI-generated OpenAPI 3.1 document remains the source API contract for
the app. This script derives a smaller Swagger 2.0 artifact for Copilot Studio
and Power Platform custom connector registration.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_OPENAPI_PATH = REPO_ROOT / "openapi" / "evaluations-api.json"
OUTPUT_PATH = REPO_ROOT / "openapi" / "copilot-studio" / "evaluations-tool.swagger.json"

EXPECTED_PATHS = {"/api/evaluations", "/api/evaluations/{evaluation_id}"}
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


def _load_source() -> dict[str, Any]:
    return json.loads(SOURCE_OPENAPI_PATH.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Cannot generate Copilot Swagger artifact: {message}")


def _validate_source(source: dict[str, Any]) -> None:
    _require(source.get("openapi") == "3.1.0", "source contract must remain OpenAPI 3.1.0")
    paths = source.get("paths", {})
    _require(set(paths) == EXPECTED_PATHS, f"source paths drifted: {sorted(paths)}")
    _require(
        paths["/api/evaluations"]["post"].get("operationId") == "submitEvaluation",
        "POST operationId drifted",
    )
    _require(
        paths["/api/evaluations/{evaluation_id}"]["get"].get("operationId")
        == "getEvaluation",
        "GET operationId drifted",
    )

    request_schema = paths["/api/evaluations"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    request_fields = set(request_schema.get("properties", {}))
    _require(
        not request_fields & FORBIDDEN_REQUEST_FIELDS,
        f"request exposes backend selection fields: {sorted(request_fields & FORBIDDEN_REQUEST_FIELDS)}",
    )
    _require(
        {"position_id", "candidate_ref", "idempotency_key"} <= request_fields,
        "request schema no longer exposes the expected lab fields",
    )

    envelope = source.get("components", {}).get("schemas", {}).get("Envelope", {})
    envelope_fields = set(envelope.get("properties", {}))
    _require(envelope_fields == EXPECTED_ENVELOPE_FIELDS, "envelope fields drifted")
    status_values = set(envelope["properties"]["status"]["enum"])
    _require(
        status_values
        == {
            "completed",
            "blocked",
            "validation_failed",
            "unauthorized",
            "needs_input",
            "error",
        },
        "envelope status vocabulary drifted",
    )


def _lab_header_parameters() -> list[dict[str, Any]]:
    return [
        {
            "name": "X-Lab-Actor-Id",
            "in": "header",
            "required": True,
            "type": "string",
            "default": "copilot-e4-lab-user",
            "description": (
                "Temporary E4 lab simulated actor id. This is not production "
                "identity and is replaced by a later Entra-auth slice."
            ),
            "x-ms-summary": "Lab actor id",
            "x-ms-visibility": "advanced",
        },
        {
            "name": "X-Lab-Roles",
            "in": "header",
            "required": True,
            "type": "string",
            "default": "hr",
            "description": (
                "Temporary E4 lab simulated role list. Use hr for this lab "
                "smoke. This is not production authorization."
            ),
            "x-ms-summary": "Lab roles",
            "x-ms-visibility": "advanced",
        },
        {
            "name": "X-Lab-Actor-Display",
            "in": "header",
            "required": False,
            "type": "string",
            "default": "Copilot E4 Lab User",
            "description": "Optional display name for the temporary E4 lab simulated actor.",
            "x-ms-summary": "Lab actor display",
            "x-ms-visibility": "advanced",
        },
    ]


def _common_response_example() -> dict[str, Any]:
    return {
        "status": "completed",
        "evaluation_id": "eval-e4-sample-0001",
        "case_id": None,
        "correlation_id": "corr-e4-sample-0001",
        "user_message": (
            "Advisory evaluation completed. This output is decision support "
            "for a human reviewer; it is not a hiring decision."
        ),
        "safe_details": None,
        "result": {
            "decision_support_only": True,
            "human_review_required": True,
            "ai_backend_type": "none",
            "provider_id": "deterministic_mock",
        },
        "errors": [],
        "warnings": [],
    }


def _build_swagger(source: dict[str, Any]) -> dict[str, Any]:
    info = source["info"]
    lab_headers = _lab_header_parameters()
    envelope_response = {
        "description": (
            "Standard response envelope. Business outcomes are returned in the "
            "envelope status and remain advisory decision support only."
        ),
        "schema": {"$ref": "#/definitions/Envelope"},
        "examples": {"application/json": _common_response_example()},
    }
    return {
        "swagger": "2.0",
        "info": {
            "title": "AI HR Hiring Agent Lab - Copilot Studio Evaluation Tools",
            "version": info.get("version", "1.0.0"),
            "description": (
                "Curated Swagger 2.0 registration artifact for Copilot Studio "
                "and Power Platform custom connector import. The source API "
                "contract remains openapi/evaluations-api.json (OpenAPI 3.1). "
                "This artifact exposes exactly two lab actions for synthetic "
                "single-candidate evaluation: submitEvaluation and getEvaluation."
            ),
        },
        "host": "function-app-host.example",
        "basePath": "/",
        "schemes": ["https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "function_key": {
                "type": "apiKey",
                "name": "x-functions-key",
                "in": "header",
                "description": (
                    "Azure Functions Function-level key supplied through the "
                    "secure Copilot Studio or Power Platform connection/auth "
                    "configuration. Do not commit the key value."
                ),
            }
        },
        "security": [{"function_key": []}],
        "paths": {
            "/api/evaluations": {
                "post": {
                    "tags": ["CandidateEvaluation"],
                    "operationId": "submitEvaluation",
                    "summary": "Submit one synthetic candidate evaluation",
                    "description": (
                        "Submit one synthetic candidate evaluation to the "
                        "advisory Calibrated Evaluation Council for a sample "
                        "position and approved rubric. Returns an evidence-"
                        "grounded envelope that always requires human review. "
                        "Never makes or implies a hiring decision."
                    ),
                    "security": [{"function_key": []}],
                    "parameters": [
                        *lab_headers,
                        {
                            "name": "Idempotency-Key",
                            "in": "header",
                            "required": False,
                            "type": "string",
                            "description": (
                                "Idempotency key for the submission. Equivalent "
                                "to body idempotency_key; provide one of the two."
                            ),
                            "x-ms-summary": "Idempotency key",
                        },
                        {
                            "name": "X-Correlation-Id",
                            "in": "header",
                            "required": False,
                            "type": "string",
                            "description": "Optional caller correlation id for tracing.",
                            "x-ms-summary": "Correlation id",
                            "x-ms-visibility": "advanced",
                        },
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/EvaluationRequest"},
                            "description": "Synthetic evaluation request body.",
                        },
                    ],
                    "responses": {"200": envelope_response},
                    "x-ms-examples": {
                        "Synthetic fixture evaluation": {
                            "parameters": {
                                "X-Lab-Actor-Id": "copilot-e4-lab-user",
                                "X-Lab-Roles": "hr",
                                "X-Lab-Actor-Display": "Copilot E4 Lab User",
                                "Idempotency-Key": "e4-copilot-sample-001",
                                "body": {
                                    "position_id": "pos-sample-001",
                                    "candidate_ref": "cand-sample-001",
                                },
                            },
                            "responses": {"200": {"body": _common_response_example()}},
                        }
                    },
                }
            },
            "/api/evaluations/{evaluation_id}": {
                "get": {
                    "tags": ["CandidateEvaluation"],
                    "operationId": "getEvaluation",
                    "summary": "Retrieve one persisted evaluation audit record",
                    "description": (
                        "Retrieve the persisted audit record for a prior "
                        "synthetic evaluation by evaluation_id. The returned "
                        "record is advisory decision support only and must be "
                        "reviewed by a human."
                    ),
                    "security": [{"function_key": []}],
                    "parameters": [
                        *lab_headers,
                        {
                            "name": "evaluation_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "Evaluation id returned by submitEvaluation.",
                            "x-ms-summary": "Evaluation id",
                        },
                        {
                            "name": "X-Correlation-Id",
                            "in": "header",
                            "required": False,
                            "type": "string",
                            "description": "Optional caller correlation id for tracing.",
                            "x-ms-summary": "Correlation id",
                            "x-ms-visibility": "advanced",
                        },
                    ],
                    "responses": {"200": envelope_response},
                    "x-ms-examples": {
                        "Synthetic evaluation audit retrieval": {
                            "parameters": {
                                "X-Lab-Actor-Id": "copilot-e4-lab-user",
                                "X-Lab-Roles": "hr",
                                "X-Lab-Actor-Display": "Copilot E4 Lab User",
                                "evaluation_id": "eval-e4-sample-0001",
                            },
                            "responses": {"200": {"body": _common_response_example()}},
                        }
                    },
                }
            },
        },
        "definitions": {
            "EvaluationRequest": {
                "type": "object",
                "additionalProperties": False,
                "required": ["position_id"],
                "description": (
                    "One synthetic fixture-reference lab evaluation request. "
                    "The E4 Copilot registration artifact intentionally does "
                    "not expose inline resume or cover-letter text fields."
                ),
                "properties": {
                    "position_id": {
                        "type": "string",
                        "description": "Known synthetic fixture position id.",
                        "default": "pos-sample-001",
                        "x-ms-summary": "Position id",
                    },
                    "candidate_ref": {
                        "type": "string",
                        "description": (
                            "Known synthetic fixture candidate reference. Use "
                            "cand-sample-001 for E4 registration smoke tests."
                        ),
                        "default": "cand-sample-001",
                        "x-ms-summary": "Candidate reference",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": (
                            "Optional idempotency key body field. Equivalent to "
                            "the Idempotency-Key header."
                        ),
                        "x-ms-summary": "Idempotency key",
                        "x-ms-visibility": "advanced",
                    },
                    "evaluation_question": {
                        "type": "string",
                        "description": "Optional synthetic lab focus question.",
                        "x-ms-summary": "Evaluation question",
                        "x-ms-visibility": "advanced",
                    },
                    "requested_rigor": {
                        "type": "string",
                        "enum": ["standard", "high_impact", "escalated"],
                        "description": (
                            "Optional advisory requested rigor. The server never "
                            "allows this to lower resolved rigor."
                        ),
                        "x-ms-summary": "Requested rigor",
                        "x-ms-visibility": "advanced",
                    },
                },
            },
            "Envelope": {
                "type": "object",
                "additionalProperties": False,
                "required": ["status"],
                "description": "Existing app response envelope, unchanged for E4.",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "completed",
                            "blocked",
                            "validation_failed",
                            "unauthorized",
                            "needs_input",
                            "error",
                        ],
                        "description": (
                            "Envelope status. needs_input and error are reserved "
                            "in the current app contract."
                        ),
                    },
                    "evaluation_id": {"type": "string", "x-nullable": True},
                    "case_id": {
                        "type": "string",
                        "x-nullable": True,
                        "description": "Always null for the current case-less lab workflow.",
                    },
                    "correlation_id": {"type": "string", "x-nullable": True},
                    "user_message": {"type": "string"},
                    "safe_details": {"type": "string", "x-nullable": True},
                    "result": {
                        "type": "object",
                        "x-nullable": True,
                        "additionalProperties": True,
                        "description": (
                            "Existing result payload. submitEvaluation returns "
                            "the advisory result; getEvaluation returns the full "
                            "persisted audit record."
                        ),
                    },
                    "errors": {"type": "array", "items": {"type": "string"}},
                    "warnings": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    }


def _serialize(spec: dict[str, Any]) -> str:
    return json.dumps(spec, indent=2, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="check that the committed curated Swagger artifact is up to date",
    )
    args = parser.parse_args(argv)

    source = _load_source()
    _validate_source(source)
    text = _serialize(_build_swagger(source))

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"Missing Copilot Swagger artifact: {OUTPUT_PATH}", file=sys.stderr)
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != text:
            diff = "".join(
                difflib.unified_diff(
                    current.splitlines(keepends=True),
                    text.splitlines(keepends=True),
                    fromfile=str(OUTPUT_PATH),
                    tofile="generated",
                )
            )
            print(f"DRIFT: curated Copilot Swagger differs:\n{diff}", file=sys.stderr)
            return 1
        print(f"Copilot Swagger artifact matches generated output: {OUTPUT_PATH}")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    print(f"Wrote Copilot Swagger artifact: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
