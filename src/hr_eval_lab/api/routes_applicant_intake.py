"""Applicant and candidate-package intake API for E12."""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from pydantic import ValidationError

from hr_eval_lab.api.auth import authenticate_and_authorize
from hr_eval_lab.api.errors import MalformedBodyError
from hr_eval_lab.cases.applicant_intake import (
    ApplicantIntakeService,
    ApplicantIntakeSnapshot,
)
from hr_eval_lab.domain.schemas.cases import (
    ApplicantCreateRequest,
    ApplicantImportRequest,
    ApplicantSetConfirmRequest,
    CandidateDocumentRegisterRequest,
    CaseEnvelope,
)

router = APIRouter()

CORRELATION_ID_HEADER = "X-Correlation-Id"

_HEADER_PARAMS_GET = [
    {
        "name": CORRELATION_ID_HEADER,
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": (
            "Optional caller-supplied correlation id, echoed on early failures. "
            "Completed applicant-intake responses return the case correlation id."
        ),
    }
]
_HEADER_PARAMS_POST = _HEADER_PARAMS_GET


def _request_schema_ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/components/schemas/{name}"}


def _request_body_schema(name: str) -> dict[str, object]:
    return {
        "required": True,
        "content": {
            "application/json": {
                "schema": _request_schema_ref(name),
            }
        },
    }


def _validation_detail(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['type']}"
        for error in exc.errors()
    )


async def _body_or_400(request: Request, model: type) -> object:
    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise MalformedBodyError("request body is not valid JSON")
    if not isinstance(body, dict):
        raise MalformedBodyError("request body must be a JSON object")
    try:
        return model.model_validate(body)
    except ValidationError as exc:
        raise MalformedBodyError(f"invalid request shape: {_validation_detail(exc)}")


def _set_correlation_header(request: Request, envelope: CaseEnvelope) -> CaseEnvelope:
    if envelope.correlation_id:
        request.state.correlation_id = envelope.correlation_id
    return envelope


def _service(request: Request) -> ApplicantIntakeService:
    return ApplicantIntakeService(request.app.state.workflow_storage)


def _unknown_case_envelope(case_id: str) -> CaseEnvelope:
    return CaseEnvelope(
        status="validation_failed",
        user_message="Unknown recruitment case id.",
        safe_details=f"no case exists for case_id '{case_id}'",
        errors=["unknown_case_id"],
    )


def _error_envelope(snapshot: ApplicantIntakeSnapshot, error: str) -> CaseEnvelope:
    messages = {
        "unknown_candidate_id": "Unknown candidate id for this recruitment case.",
        "duplicate_candidate_ref": "Duplicate candidate reference for this recruitment case.",
        "candidate_limit_exceeded": "First-demo applicant cap exceeded.",
        "unsupported_document_type": "Unsupported candidate document type.",
        "applicant_set_incomplete": "Applicant set cannot be confirmed yet.",
        "applicant_set_already_confirmed": "Applicant set has already been confirmed.",
        "applicant_set_locked": (
            "Applicant set has already been confirmed and cannot be modified in E12."
        ),
    }
    return CaseEnvelope(
        status="blocked" if snapshot.blocked else "validation_failed",
        case_id=snapshot.case_id,
        correlation_id=snapshot.correlation_id,
        user_message=messages.get(error, "Applicant intake validation failed."),
        safe_details=snapshot.safe_details,
        result=(
            snapshot.result.model_dump(mode="json")
            if snapshot.result is not None
            else None
        ),
        next_actions=snapshot.next_actions,
        errors=[error],
    )


def _completed_envelope(
    request: Request,
    snapshot: ApplicantIntakeSnapshot,
    user_message: str,
) -> CaseEnvelope:
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message=user_message,
            result=(
                snapshot.result.model_dump(mode="json")
                if snapshot.result is not None
                else None
            ),
            next_actions=snapshot.next_actions,
        ),
    )


@router.post(
    "/api/cases/{case_id}/applicants",
    response_model=CaseEnvelope,
    operation_id="registerApplicant",
    openapi_extra={
        "requestBody": _request_body_schema("ApplicantCreateRequest"),
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Register one synthetic applicant for a recruitment case",
    description=(
        "Registers one synthetic applicant and initializes a candidate package. "
        "The endpoint writes package metadata through the workflow Blob seam "
        "and writes Applicant, CandidatePackage, event, task, gate, and case "
        "state rows through the workflow Table seam. It does not start "
        "assessment, enqueue work, call Foundry/model backends, or alter "
        "Copilot Studio."
    ),
)
async def register_applicant(case_id: str, request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)
    body = await _body_or_400(request, ApplicantCreateRequest)

    snapshot = _service(request).register_applicant(
        case_id,
        body,  # type: ignore[arg-type]
        actor,
    )
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(request, _error_envelope(snapshot, snapshot.error))
    return _completed_envelope(request, snapshot, "Applicant registered.")


@router.get(
    "/api/cases/{case_id}/applicants",
    response_model=CaseEnvelope,
    operation_id="listCaseApplicants",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="List applicant and package metadata for one recruitment case",
    description=(
        "Returns applicant, candidate-package, and computed finding metadata "
        "for one recruitment case. The endpoint does not read or expose raw "
        "candidate document text."
    ),
)
async def list_case_applicants(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _service(request).list_applicants(case_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    return _completed_envelope(request, snapshot, "Applicant summaries retrieved.")


@router.get(
    "/api/cases/{case_id}/applicants/{candidate_id}",
    response_model=CaseEnvelope,
    operation_id="getCaseApplicant",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve one applicant package summary",
    description=(
        "Returns one applicant, candidate-document metadata summaries, package "
        "metadata, and computed findings. The endpoint does not read or expose "
        "raw candidate document text."
    ),
)
async def get_case_applicant(
    case_id: str,
    candidate_id: str,
    request: Request,
) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _service(request).get_applicant(case_id, candidate_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(request, _error_envelope(snapshot, snapshot.error))
    return _completed_envelope(request, snapshot, "Applicant summary retrieved.")


@router.post(
    "/api/cases/{case_id}/candidates/{candidate_id}/documents",
    response_model=CaseEnvelope,
    operation_id="registerCandidateDocument",
    openapi_extra={
        "requestBody": _request_body_schema("CandidateDocumentRegisterRequest"),
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Register one synthetic candidate document",
    description=(
        "Registers one synthetic candidate-linked document and refreshes the "
        "candidate package metadata artifact. Unsupported document types are "
        "reported as deterministic validation failures. The endpoint does not "
        "start assessment, enqueue work, call Foundry/model backends, or alter "
        "Copilot Studio."
    ),
)
async def register_candidate_document(
    case_id: str,
    candidate_id: str,
    request: Request,
) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)
    body = await _body_or_400(request, CandidateDocumentRegisterRequest)

    snapshot = _service(request).register_candidate_document(
        case_id,
        candidate_id,
        body,  # type: ignore[arg-type]
        actor,
    )
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(request, _error_envelope(snapshot, snapshot.error))
    return _completed_envelope(request, snapshot, "Candidate document registered.")


@router.post(
    "/api/cases/{case_id}/applicant-imports",
    response_model=CaseEnvelope,
    operation_id="processApplicantImport",
    openapi_extra={
        "requestBody": _request_body_schema("ApplicantImportRequest"),
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Process a deterministic synthetic applicant import",
    description=(
        "Processes a small synthetic applicant batch for the first demo. The "
        "whole batch is preflighted before writes, and the active applicant "
        "cap is five candidates. The endpoint writes candidate document raw "
        "Blobs, package metadata Blobs, Table metadata, and one case event. It "
        "does not create a persistent import manifest, start assessment, enqueue "
        "work, call Foundry/model backends, or alter Copilot Studio."
    ),
)
async def process_applicant_import(case_id: str, request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)
    body = await _body_or_400(request, ApplicantImportRequest)

    snapshot = _service(request).process_import(
        case_id,
        body,  # type: ignore[arg-type]
        actor,
    )
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(request, _error_envelope(snapshot, snapshot.error))
    return _completed_envelope(request, snapshot, "Applicant import processed.")


@router.get(
    "/api/cases/{case_id}/import-findings",
    response_model=CaseEnvelope,
    operation_id="getImportFindings",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Get computed applicant import findings",
    description=(
        "Computes applicant-import findings from Applicants, candidate-linked "
        "SourceDocuments, and CandidatePackages. Findings are not persisted as "
        "a separate v1 table."
    ),
)
async def get_import_findings(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _service(request).get_import_findings(case_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    return _completed_envelope(request, snapshot, "Import findings retrieved.")


@router.post(
    "/api/cases/{case_id}/applicant-set/confirm",
    response_model=CaseEnvelope,
    operation_id="confirmApplicantSet",
    openapi_extra={
        "requestBody": _request_body_schema("ApplicantSetConfirmRequest"),
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Confirm the applicant set for later assessment readiness",
    description=(
        "Confirms the applicant set only when at least one complete candidate "
        "package exists and no active applicant has blocking findings. A "
        "successful confirmation satisfies only the applicant-set gate; "
        "assessment remains locked for later readiness/assessment slices."
    ),
)
async def confirm_applicant_set(case_id: str, request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)
    body = await _body_or_400(request, ApplicantSetConfirmRequest)

    snapshot = _service(request).confirm_applicant_set(
        case_id,
        body,  # type: ignore[arg-type]
        actor,
    )
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(request, _error_envelope(snapshot, snapshot.error))
    return _completed_envelope(request, snapshot, "Applicant set confirmed.")
