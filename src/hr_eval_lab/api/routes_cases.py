"""Recruitment case foundation API for E9.

Order of operations mirrors the evaluation facade:
  1. Authentication + role authorization.
  2. Malformed-body rejection for POST.
  3. Semantic service outcome in the standard envelope.

The route layer reads ``app.state.workflow_storage`` and passes it to the
case service. It does not import local or Azure storage implementations.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from pydantic import ValidationError

from hr_eval_lab.api.auth import authenticate_and_authorize
from hr_eval_lab.api.errors import MalformedBodyError
from hr_eval_lab.cases.service import RecruitmentCaseService
from hr_eval_lab.domain.schemas.cases import CaseEnvelope, RecruitmentCaseCreateRequest

router = APIRouter()

CORRELATION_ID_HEADER = "X-Correlation-Id"

_CREATE_CASE_BODY_SCHEMA_REF = {
    "$ref": "#/components/schemas/RecruitmentCaseCreateRequest"
}
_HEADER_PARAMS_GET = [
    {
        "name": CORRELATION_ID_HEADER,
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": (
            "Optional caller-supplied correlation id, echoed on early failures. "
            "Completed case responses return the case correlation id."
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


def _case_service(request: Request) -> RecruitmentCaseService:
    return RecruitmentCaseService(request.app.state.workflow_storage)


def _unknown_case_envelope(case_id: str) -> CaseEnvelope:
    return CaseEnvelope(
        status="validation_failed",
        user_message="Unknown recruitment case id.",
        safe_details=f"no case exists for case_id '{case_id}'",
        errors=["unknown_case_id"],
    )


@router.post(
    "/api/cases",
    response_model=CaseEnvelope,
    operation_id="createRecruitmentCase",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": _CREATE_CASE_BODY_SCHEMA_REF}},
        },
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Create a synthetic-safe recruitment case foundation",
    description=(
        "Creates the initial case, participant, task, gate, and event state "
        "for Stage 1 of the HR Hiring MVP workflow. This endpoint is "
        "deterministic service logic only: no applicant import, document "
        "upload, queue worker, Foundry/model execution, notification API, "
        "or Copilot Studio topic state is created."
    ),
)
async def create_recruitment_case(request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)

    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise MalformedBodyError("request body is not valid JSON")
    if not isinstance(body, dict):
        raise MalformedBodyError("request body must be a JSON object")
    try:
        create_request = RecruitmentCaseCreateRequest.model_validate(body)
    except ValidationError as exc:
        raise MalformedBodyError(f"invalid request shape: {_validation_detail(exc)}")

    snapshot = _case_service(request).create_case(create_request, actor)
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message=(
                "Recruitment case created. Complete the initial intake and "
                "source-document tasks before any assessment workflow can start."
            ),
            result=snapshot.result.model_dump(mode="json"),
            next_actions=snapshot.result.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}",
    response_model=CaseEnvelope,
    operation_id="getRecruitmentCase",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve one recruitment case state snapshot",
    description=(
        "Retrieves the persisted case summary, participants, open tasks, "
        "workflow gates, creation events, and deterministic next actions. "
        "The response does not fabricate missing workflow state."
    ),
)
async def get_recruitment_case(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _case_service(request).get_case(case_id)
    if snapshot is None:
        return _unknown_case_envelope(case_id)
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Recruitment case state retrieved.",
            result=snapshot.result.model_dump(mode="json"),
            next_actions=snapshot.result.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}/next-actions",
    response_model=CaseEnvelope,
    operation_id="getCaseNextActions",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve deterministic next actions for one recruitment case",
    description=(
        "Returns open or blocked tasks and active gate blockers in business "
        "language. No model-generated recommendations, notifications, "
        "or Copilot topic-variable state are produced."
    ),
)
async def get_case_next_actions(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _case_service(request).get_next_actions(case_id)
    if snapshot is None:
        return _unknown_case_envelope(case_id)
    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Recruitment case next actions retrieved.",
            result=snapshot.result.model_dump(mode="json"),
            next_actions=snapshot.result.next_actions,
        ),
    )
