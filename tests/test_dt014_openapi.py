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
        "/api/cases/{case_id}/applicant-imports",
        "/api/cases/{case_id}/applicant-set/confirm",
        "/api/cases/{case_id}/applicants",
        "/api/cases/{case_id}/applicants/{candidate_id}",
        "/api/cases/{case_id}/candidates/{candidate_id}/documents",
        "/api/cases/{case_id}/import-findings",
        "/api/cases/{case_id}/next-actions",
        "/api/cases/{case_id}/role-intake",
        "/api/cases/{case_id}/rubrics",
        "/api/cases/{case_id}/rubrics/{rubric_version}",
        "/api/cases/{case_id}/source-documents",
        "/api/cases/{case_id}/source-documents/{document_id}",
        "/api/evaluations",
        "/api/evaluations/retrieve",
        "/api/evaluations/{evaluation_id}",
    }
    assert "post" in paths["/api/cases"]
    assert "get" in paths["/api/cases/{case_id}"]
    assert "post" in paths["/api/cases/{case_id}/applicant-imports"]
    assert "post" in paths["/api/cases/{case_id}/applicant-set/confirm"]
    assert "post" in paths["/api/cases/{case_id}/applicants"]
    assert "get" in paths["/api/cases/{case_id}/applicants"]
    assert "get" in paths["/api/cases/{case_id}/applicants/{candidate_id}"]
    assert "post" in paths["/api/cases/{case_id}/candidates/{candidate_id}/documents"]
    assert "get" in paths["/api/cases/{case_id}/import-findings"]
    assert "get" in paths["/api/cases/{case_id}/next-actions"]
    assert "post" in paths["/api/cases/{case_id}/role-intake"]
    assert "get" in paths["/api/cases/{case_id}/role-intake"]
    assert "post" in paths["/api/cases/{case_id}/rubrics"]
    assert "get" in paths["/api/cases/{case_id}/rubrics"]
    assert "get" in paths["/api/cases/{case_id}/rubrics/{rubric_version}"]
    assert "post" in paths["/api/cases/{case_id}/source-documents"]
    assert "get" in paths["/api/cases/{case_id}/source-documents"]
    assert "get" in paths["/api/cases/{case_id}/source-documents/{document_id}"]
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
        paths["/api/cases/{case_id}/applicant-imports"]["post"]["operationId"]
        == "processApplicantImport"
    )
    assert (
        paths["/api/cases/{case_id}/applicant-set/confirm"]["post"]["operationId"]
        == "confirmApplicantSet"
    )
    assert (
        paths["/api/cases/{case_id}/applicants"]["post"]["operationId"]
        == "registerApplicant"
    )
    assert (
        paths["/api/cases/{case_id}/applicants"]["get"]["operationId"]
        == "listCaseApplicants"
    )
    assert (
        paths["/api/cases/{case_id}/applicants/{candidate_id}"]["get"]["operationId"]
        == "getCaseApplicant"
    )
    assert (
        paths["/api/cases/{case_id}/candidates/{candidate_id}/documents"]["post"][
            "operationId"
        ]
        == "registerCandidateDocument"
    )
    assert (
        paths["/api/cases/{case_id}/import-findings"]["get"]["operationId"]
        == "getImportFindings"
    )
    assert (
        paths["/api/cases/{case_id}/role-intake"]["post"]["operationId"]
        == "createRoleIntakeArtifact"
    )
    assert (
        paths["/api/cases/{case_id}/role-intake"]["get"]["operationId"]
        == "getCaseRoleIntake"
    )
    assert (
        paths["/api/cases/{case_id}/rubrics"]["post"]["operationId"]
        == "registerApprovedRubric"
    )
    assert (
        paths["/api/cases/{case_id}/rubrics"]["get"]["operationId"]
        == "listCaseRubrics"
    )
    assert (
        paths["/api/cases/{case_id}/rubrics/{rubric_version}"]["get"][
            "operationId"
        ]
        == "getCaseRubric"
    )
    assert (
        paths["/api/cases/{case_id}/source-documents"]["post"]["operationId"]
        == "registerSourceDocument"
    )
    assert (
        paths["/api/cases/{case_id}/source-documents"]["get"]["operationId"]
        == "listCaseSourceDocuments"
    )
    assert (
        paths["/api/cases/{case_id}/source-documents/{document_id}"]["get"][
            "operationId"
        ]
        == "getCaseSourceDocument"
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
    assert "SourceDocumentRegisterRequest" in components
    assert "RoleIntakeCreateRequest" in components
    assert "ApprovedRubricRegisterRequest" in components
    assert "RubricCriterionInput" in components
    assert "RubricRatingAnchorInput" in components
    assert "ApplicantCreateRequest" in components
    assert "CandidateDocumentRegisterRequest" in components
    assert "ApplicantImportCandidateInput" in components
    assert "ApplicantImportRequest" in components
    assert "ApplicantSetConfirmRequest" in components
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

    source_doc_request_body = paths["/api/cases/{case_id}/source-documents"]["post"][
        "requestBody"
    ]
    source_doc_schema = source_doc_request_body["content"]["application/json"]["schema"]
    assert source_doc_schema == {
        "$ref": "#/components/schemas/SourceDocumentRegisterRequest"
    }
    assert "$defs" not in source_doc_schema
    assert "#/$defs/" not in json.dumps(source_doc_request_body)

    source_doc_component = components["SourceDocumentRegisterRequest"]
    assert "$defs" not in source_doc_component
    assert {
        "document_type",
        "source_origin",
        "source_label",
        "file_name",
        "mime_type",
        "synthetic",
        "content_text",
    } == set(source_doc_component["properties"])
    assert source_doc_component["required"] == [
        "document_type",
        "source_origin",
        "synthetic",
        "content_text",
    ]

    role_intake_request_body = paths["/api/cases/{case_id}/role-intake"]["post"][
        "requestBody"
    ]
    role_intake_schema = role_intake_request_body["content"]["application/json"][
        "schema"
    ]
    assert role_intake_schema == {
        "$ref": "#/components/schemas/RoleIntakeCreateRequest"
    }
    assert "$defs" not in role_intake_schema
    assert "#/$defs/" not in json.dumps(role_intake_request_body)

    role_intake_component = components["RoleIntakeCreateRequest"]
    assert "$defs" not in role_intake_component
    assert {
        "synthetic",
        "intake_title",
        "role_purpose",
        "responsibilities",
        "required_qualifications",
        "intake_version",
        "preferred_qualifications",
        "business_context",
        "role_risks",
        "open_questions",
        "source_document_ids",
    } == set(role_intake_component["properties"])
    assert role_intake_component["required"] == [
        "synthetic",
        "intake_title",
        "role_purpose",
        "responsibilities",
        "required_qualifications",
    ]

    rubric_request_body = paths["/api/cases/{case_id}/rubrics"]["post"][
        "requestBody"
    ]
    rubric_schema = rubric_request_body["content"]["application/json"]["schema"]
    assert rubric_schema == {
        "$ref": "#/components/schemas/ApprovedRubricRegisterRequest"
    }
    assert "$defs" not in rubric_schema
    assert "#/$defs/" not in json.dumps(rubric_request_body)

    rubric_component = components["ApprovedRubricRegisterRequest"]
    assert "$defs" not in rubric_component
    assert {
        "synthetic",
        "rubric_title",
        "criteria",
        "rubric_version",
        "approved_by_actor_id",
    } == set(rubric_component["properties"])
    assert rubric_component["required"] == [
        "synthetic",
        "rubric_title",
        "criteria",
    ]

    applicant_request_body = paths["/api/cases/{case_id}/applicants"]["post"][
        "requestBody"
    ]
    applicant_schema = applicant_request_body["content"]["application/json"]["schema"]
    assert applicant_schema == {
        "$ref": "#/components/schemas/ApplicantCreateRequest"
    }
    assert "$defs" not in applicant_schema
    assert "#/$defs/" not in json.dumps(applicant_request_body)

    applicant_component = components["ApplicantCreateRequest"]
    assert "$defs" not in applicant_component
    assert {"synthetic", "candidate_ref", "display_label"} == set(
        applicant_component["properties"]
    )
    assert applicant_component["required"] == ["synthetic", "candidate_ref"]

    candidate_document_request_body = paths[
        "/api/cases/{case_id}/candidates/{candidate_id}/documents"
    ]["post"]["requestBody"]
    candidate_document_schema = candidate_document_request_body["content"][
        "application/json"
    ]["schema"]
    assert candidate_document_schema == {
        "$ref": "#/components/schemas/CandidateDocumentRegisterRequest"
    }
    assert "$defs" not in candidate_document_schema
    assert "#/$defs/" not in json.dumps(candidate_document_request_body)

    candidate_document_component = components["CandidateDocumentRegisterRequest"]
    assert "$defs" not in candidate_document_component
    assert {
        "document_type",
        "source_origin",
        "source_label",
        "file_name",
        "mime_type",
        "synthetic",
        "content_text",
    } == set(candidate_document_component["properties"])
    assert candidate_document_component["required"] == [
        "document_type",
        "source_origin",
        "synthetic",
        "content_text",
    ]
    # E12 keeps document_type as a string so semantic unsupported values return
    # a CaseEnvelope validation_failed outcome instead of a framework 400.
    assert candidate_document_component["properties"]["document_type"]["type"] == "string"
    assert "enum" not in candidate_document_component["properties"]["document_type"]

    import_request_body = paths["/api/cases/{case_id}/applicant-imports"]["post"][
        "requestBody"
    ]
    import_schema = import_request_body["content"]["application/json"]["schema"]
    assert import_schema == {
        "$ref": "#/components/schemas/ApplicantImportRequest"
    }
    assert "$defs" not in import_schema
    assert "#/$defs/" not in json.dumps(import_request_body)

    import_component = components["ApplicantImportRequest"]
    assert "$defs" not in import_component
    assert {"synthetic", "candidates"} == set(import_component["properties"])
    assert import_component["required"] == ["synthetic", "candidates"]

    import_candidate_component = components["ApplicantImportCandidateInput"]
    assert "$defs" not in import_candidate_component
    assert {"candidate_ref", "display_label", "documents"} == set(
        import_candidate_component["properties"]
    )
    assert import_candidate_component["required"] == ["candidate_ref"]

    confirm_request_body = paths["/api/cases/{case_id}/applicant-set/confirm"][
        "post"
    ]["requestBody"]
    confirm_schema = confirm_request_body["content"]["application/json"]["schema"]
    assert confirm_schema == {
        "$ref": "#/components/schemas/ApplicantSetConfirmRequest"
    }
    assert "$defs" not in confirm_schema
    assert "#/$defs/" not in json.dumps(confirm_request_body)

    confirm_component = components["ApplicantSetConfirmRequest"]
    assert "$defs" not in confirm_component
    assert {"synthetic", "applicant_set_version"} == set(
        confirm_component["properties"]
    )
    assert confirm_component["required"] == ["synthetic"]
