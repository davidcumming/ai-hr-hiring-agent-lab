"""Role-intake and approved-rubric API routes for E11."""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from pydantic import ValidationError

from hr_eval_lab.api.auth import authenticate_and_authorize
from hr_eval_lab.api.errors import MalformedBodyError
from hr_eval_lab.cases.role_intake_rubrics import (
    RoleIntakeRubricService,
    RoleIntakeRubricSnapshot,
)
from hr_eval_lab.domain.schemas.cases import (
    ApprovedRubricRegisterRequest,
    CaseEnvelope,
    RoleIntakeCreateRequest,
)

router = APIRouter()

CORRELATION_ID_HEADER = "X-Correlation-Id"

_ROLE_INTAKE_BODY_SCHEMA_REF = {"$ref": "#/components/schemas/RoleIntakeCreateRequest"}
_APPROVED_RUBRIC_BODY_SCHEMA_REF = {
    "$ref": "#/components/schemas/ApprovedRubricRegisterRequest"
}
_HEADER_PARAMS_GET = [
    {
        "name": CORRELATION_ID_HEADER,
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": (
            "Optional caller-supplied correlation id, echoed on early failures. "
            "Completed role-intake and rubric responses return the case correlation id."
        ),
    }
]
_HEADER_PARAMS_POST = _HEADER_PARAMS_GET


def _validation_detail(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['type']}"
        for error in exc.errors()
    )


def _set_correlation_header(request: Request, envelope: CaseEnvelope) -> CaseEnvelope:
    if envelope.correlation_id:
        request.state.correlation_id = envelope.correlation_id
    return envelope


def _service(request: Request) -> RoleIntakeRubricService:
    return RoleIntakeRubricService(request.app.state.workflow_storage)


def _unknown_case_envelope(case_id: str) -> CaseEnvelope:
    return CaseEnvelope(
        status="validation_failed",
        user_message="Unknown recruitment case id.",
        safe_details=f"no case exists for case_id '{case_id}'",
        errors=["unknown_case_id"],
    )


def _validation_failed_envelope(
    snapshot: RoleIntakeRubricSnapshot,
    error: str,
) -> CaseEnvelope:
    messages = {
        "source_documents_required": "Register at least one role source document before creating role intake.",
        "unknown_source_document_id": "One or more requested source documents were not found for this case.",
        "role_intake_version_exists": "Role intake version already exists for this case.",
        "role_intake_not_found": "No role intake artifact is registered for this case.",
        "rubric_version_exists": "Rubric version already exists for this case.",
        "unknown_rubric_version": "Unknown rubric version for this case.",
        "approved_by_actor_mismatch": "Rubric approval actor must match the authenticated HR actor.",
    }
    return CaseEnvelope(
        status="validation_failed",
        case_id=snapshot.case_id,
        correlation_id=snapshot.correlation_id,
        user_message=messages.get(error, "Request could not be completed."),
        errors=[error],
    )


async def _body_or_400(request: Request) -> dict:
    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise MalformedBodyError("request body is not valid JSON")
    if not isinstance(body, dict):
        raise MalformedBodyError("request body must be a JSON object")
    return body


@router.post(
    "/api/cases/{case_id}/role-intake",
    response_model=CaseEnvelope,
    operation_id="createRoleIntakeArtifact",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": _ROLE_INTAKE_BODY_SCHEMA_REF}},
        },
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Create one synthetic role-intake artifact for a recruitment case",
    description=(
        "Creates a deterministic synthetic role-intake artifact for an existing "
        "case using previously registered source-document metadata. The full "
        "artifact is written through the workflow Blob seam; metadata, one "
        "artifact-version row, one event, active case version, and existing "
        "task/gate updates are written through the workflow Table seam. This "
        "endpoint does not call models, enqueue work, import applicants, or "
        "change Copilot Studio."
    ),
)
async def create_role_intake(case_id: str, request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)

    try:
        role_intake_request = RoleIntakeCreateRequest.model_validate(
            await _body_or_400(request)
        )
    except ValidationError as exc:
        raise MalformedBodyError(f"invalid request shape: {_validation_detail(exc)}")

    snapshot = _service(request).create_role_intake(
        case_id,
        role_intake_request,
        actor,
    )
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(
            request,
            _validation_failed_envelope(snapshot, snapshot.error),
        )
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Role intake artifact created for the recruitment case.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}/role-intake",
    response_model=CaseEnvelope,
    operation_id="getCaseRoleIntake",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve the current role-intake artifact for a recruitment case",
    description=(
        "Returns the current role-intake artifact and artifact-version metadata "
        "for an existing recruitment case. Source-document references are "
        "metadata only; raw source text is not read or returned."
    ),
)
async def get_case_role_intake(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _service(request).get_role_intake(case_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(
            request,
            _validation_failed_envelope(snapshot, snapshot.error),
        )
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Role intake artifact retrieved.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )


@router.post(
    "/api/cases/{case_id}/rubrics",
    response_model=CaseEnvelope,
    operation_id="registerApprovedRubric",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": _APPROVED_RUBRIC_BODY_SCHEMA_REF}},
        },
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Register one approved synthetic screening rubric for a case",
    description=(
        "Registers an already-approved synthetic screening rubric version for "
        "an existing case. The endpoint stores the full rubric artifact in "
        "Blob, writes ArtifactVersions, Approvals, CaseEvents, active case "
        "version, and deterministic gate updates through the workflow Table "
        "seam. It does not generate rubrics with a model or unlock assessment."
    ),
)
async def register_approved_rubric(case_id: str, request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)

    try:
        rubric_request = ApprovedRubricRegisterRequest.model_validate(
            await _body_or_400(request)
        )
    except ValidationError as exc:
        raise MalformedBodyError(f"invalid request shape: {_validation_detail(exc)}")

    snapshot = _service(request).register_rubric(case_id, rubric_request, actor)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(
            request,
            _validation_failed_envelope(snapshot, snapshot.error),
        )
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Approved rubric registered for the recruitment case.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}/rubrics",
    response_model=CaseEnvelope,
    operation_id="listCaseRubrics",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="List screening rubric versions for one recruitment case",
    description=(
        "Returns persisted rubric artifact-version metadata for one case. The "
        "endpoint does not call models, inspect candidate data, or unlock assessment."
    ),
)
async def list_case_rubrics(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _service(request).list_rubrics(case_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Rubric versions retrieved.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}/rubrics/{rubric_version}",
    response_model=CaseEnvelope,
    operation_id="getCaseRubric",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve one approved screening rubric version",
    description=(
        "Returns one persisted synthetic rubric artifact by version for an "
        "existing recruitment case. The endpoint does not read applicant "
        "materials, queue assessments, or call a model."
    ),
)
async def get_case_rubric(
    case_id: str,
    rubric_version: str,
    request: Request,
) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _service(request).get_rubric(case_id, rubric_version)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error:
        return _set_correlation_header(
            request,
            _validation_failed_envelope(snapshot, snapshot.error),
        )
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Rubric version retrieved.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )
