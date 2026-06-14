"""Source-document intake API for E10.

The route layer reads ``app.state.workflow_storage`` and passes it to the
source-document service. It does not import local or Azure storage
implementations, queue code, provider code, or Copilot tooling.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from pydantic import ValidationError

from hr_eval_lab.api.auth import authenticate_and_authorize
from hr_eval_lab.api.errors import MalformedBodyError
from hr_eval_lab.cases.source_documents import SourceDocumentService, SourceDocumentSnapshot
from hr_eval_lab.domain.schemas.cases import CaseEnvelope, SourceDocumentRegisterRequest

router = APIRouter()

CORRELATION_ID_HEADER = "X-Correlation-Id"

_REGISTER_SOURCE_DOCUMENT_BODY_SCHEMA_REF = {
    "$ref": "#/components/schemas/SourceDocumentRegisterRequest"
}
_HEADER_PARAMS_GET = [
    {
        "name": CORRELATION_ID_HEADER,
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": (
            "Optional caller-supplied correlation id, echoed on early failures. "
            "Completed source-document responses return the case correlation id."
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


def _source_document_service(request: Request) -> SourceDocumentService:
    return SourceDocumentService(request.app.state.workflow_storage)


def _unknown_case_envelope(case_id: str) -> CaseEnvelope:
    return CaseEnvelope(
        status="validation_failed",
        user_message="Unknown recruitment case id.",
        safe_details=f"no case exists for case_id '{case_id}'",
        errors=["unknown_case_id"],
    )


def _unknown_document_envelope(snapshot: SourceDocumentSnapshot, document_id: str) -> CaseEnvelope:
    return CaseEnvelope(
        status="validation_failed",
        case_id=snapshot.case_id,
        correlation_id=snapshot.correlation_id,
        user_message="Unknown source document id.",
        safe_details=f"no source document exists for document_id '{document_id}'",
        errors=["unknown_document_id"],
    )


@router.post(
    "/api/cases/{case_id}/source-documents",
    response_model=CaseEnvelope,
    operation_id="registerSourceDocument",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": _REGISTER_SOURCE_DOCUMENT_BODY_SCHEMA_REF
                }
            },
        },
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Register one synthetic-safe source document for a recruitment case",
    description=(
        "Registers one small synthetic inline text source document for an "
        "existing recruitment case. The raw text is written through the "
        "workflow Blob seam using the canonical role-source path, while "
        "metadata, one event, and deterministic task/gate updates are written "
        "through the workflow Table seam. This endpoint does not import "
        "applicants, create queue messages, call Foundry/model backends, "
        "or change Copilot Studio."
    ),
)
async def register_source_document(case_id: str, request: Request) -> CaseEnvelope:
    actor = authenticate_and_authorize(request)

    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise MalformedBodyError("request body is not valid JSON")
    if not isinstance(body, dict):
        raise MalformedBodyError("request body must be a JSON object")
    try:
        register_request = SourceDocumentRegisterRequest.model_validate(body)
    except ValidationError as exc:
        raise MalformedBodyError(f"invalid request shape: {_validation_detail(exc)}")

    snapshot = _source_document_service(request).register_document(
        case_id,
        register_request,
        actor,
    )
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)

    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Source document registered for the recruitment case.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}/source-documents",
    response_model=CaseEnvelope,
    operation_id="listCaseSourceDocuments",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="List source-document summaries for one recruitment case",
    description=(
        "Returns persisted source-document metadata summaries for one case. "
        "The endpoint does not fabricate missing documents and does not read "
        "or expose raw document text."
    ),
)
async def list_case_source_documents(case_id: str, request: Request) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _source_document_service(request).list_documents(case_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)

    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Source document summaries retrieved.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )


@router.get(
    "/api/cases/{case_id}/source-documents/{document_id}",
    response_model=CaseEnvelope,
    operation_id="getCaseSourceDocument",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve one source-document summary",
    description=(
        "Returns one persisted source-document metadata summary for an "
        "existing recruitment case. The endpoint does not read or expose raw "
        "document text."
    ),
)
async def get_case_source_document(
    case_id: str,
    document_id: str,
    request: Request,
) -> CaseEnvelope:
    authenticate_and_authorize(request)

    snapshot = _source_document_service(request).get_document(case_id, document_id)
    if snapshot.error == "unknown_case_id":
        return _unknown_case_envelope(case_id)
    if snapshot.error == "unknown_document_id":
        return _set_correlation_header(
            request,
            _unknown_document_envelope(snapshot, document_id),
        )

    return _set_correlation_header(
        request,
        CaseEnvelope(
            status="completed",
            case_id=snapshot.case_id,
            correlation_id=snapshot.correlation_id,
            user_message="Source document summary retrieved.",
            result=snapshot.result.model_dump(mode="json") if snapshot.result else None,
            next_actions=snapshot.next_actions,
        ),
    )
