"""POST /api/evaluations and GET /api/evaluations/{evaluation_id} (FR-001…004).

Order of operations on every request (DT-009/DT-016 depend on this order):
  1. Authentication + role authorization — short-circuits everything.
  2. Malformed-body rejection (HTTP 400; no envelope status consumed).
  3. Semantic validation (unknown position/candidate -> ``validation_failed``).
  4. Idempotency check (replay -> stored result; ZERO council execution).
  5. Source resolution + sha256 verification (mismatch -> ``blocked``,
     zero council execution).
  6. Evidence packet build -> council orchestration -> gates -> persistence
     -> envelope.

The handlers take the raw ``Request`` so this ordering is owned by code, not
by framework parameter resolution.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from pydantic import ValidationError

from hr_eval_lab.api.auth import authenticate_and_authorize
from hr_eval_lab.api.envelope import Envelope
from hr_eval_lab.api.errors import MalformedBodyError
from hr_eval_lab.council.orchestrator import run_council
from hr_eval_lab.domain import ids
from hr_eval_lab.domain.schemas.request import EvaluationRequest
from hr_eval_lab.logging_setup import get_logger
from hr_eval_lab.persistence import idempotency
from hr_eval_lab.sources.fixture_store import (
    SourceIntegrityError,
    inline_source,
)

logger = get_logger("api")

router = APIRouter()

_REQUEST_BODY_SCHEMA = EvaluationRequest.model_json_schema()

#: Readiness-pack header contract (documented in OpenAPI for tool registration).
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
CORRELATION_ID_HEADER = "X-Correlation-Id"

_HEADER_PARAMS_POST = [
    {
        "name": IDEMPOTENCY_KEY_HEADER,
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": (
            "Idempotency key for the submission. Equivalent to the body field "
            "'idempotency_key'; provide either (or both with identical values "
            "— a mismatch is rejected with HTTP 400). Replays with the same "
            "key return the original result without re-running the council."
        ),
    },
    {
        "name": CORRELATION_ID_HEADER,
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": (
            "Optional caller-supplied correlation id, echoed on the response. "
            "The server-assigned correlation id of the evaluation is returned "
            "in the response envelope and in this response header."
        ),
    },
]

_HEADER_PARAMS_GET = [_HEADER_PARAMS_POST[1]]


def _set_correlation_header(request: Request, envelope: Envelope) -> Envelope:
    """Expose the envelope's correlation id to the response-header middleware."""
    if envelope.correlation_id:
        request.state.correlation_id = envelope.correlation_id
    return envelope


def _record_envelope(record: dict, replayed: bool = False) -> Envelope:
    """Build the POST envelope from a (possibly stored) full record."""
    status = record["status"]
    if status == "completed":
        user_message = (
            "Advisory evaluation completed. This output is decision support for "
            "a human reviewer; it is not a hiring decision."
        )
        safe_details = None
    else:
        failed = [g["gate_id"] for g in record["gate_results"] if g["result"] == "fail"]
        user_message = (
            "The evaluation was blocked by deterministic quality gates and "
            "requires human review."
        )
        safe_details = f"failed quality gates: {failed}"
    if replayed:
        user_message += " (Idempotent replay: original result returned; the council was not re-run.)"
    return Envelope(
        status=status,
        evaluation_id=record["evaluation_id"],
        correlation_id=record["correlation_id"],
        user_message=user_message,
        safe_details=safe_details,
        result=record.get("result"),
    )


@router.post(
    "/api/evaluations",
    response_model=Envelope,
    operation_id="submitEvaluation",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": _REQUEST_BODY_SCHEMA}},
        },
        "parameters": _HEADER_PARAMS_POST,
    },
    summary="Submit one candidate evaluation to the Calibrated Evaluation Council",
    description=(
        "Advisory-only: every result carries decision_support_only=true and "
        "human_review_required=true. Business outcomes (completed | blocked | "
        "validation_failed) return HTTP 200 with the status in the envelope; "
        "malformed bodies return HTTP 400; missing identity 401; authenticated "
        "callers without the 'hr' role 403 (envelope status 'unauthorized'). "
        "Envelope statuses 'needs_input' and 'error' are reserved and never "
        "emitted by this slice."
    ),
)
async def post_evaluation(request: Request) -> Envelope:
    state = request.app.state
    # 1. Auth first (raises 401/403 before anything else).
    actor = authenticate_and_authorize(request)

    # 2. Malformed body -> HTTP 400.
    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise MalformedBodyError("request body is not valid JSON")
    if not isinstance(body, dict):
        raise MalformedBodyError("request body must be a JSON object")
    try:
        eval_request = EvaluationRequest.model_validate(body)
    except ValidationError as exc:
        fields = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['type']}" for e in exc.errors()
        )
        raise MalformedBodyError(f"invalid request shape: {fields}")

    # Idempotency key: body field or Idempotency-Key header (readiness pack).
    header_key = request.headers.get(IDEMPOTENCY_KEY_HEADER)
    if (
        header_key
        and eval_request.idempotency_key
        and header_key != eval_request.idempotency_key
    ):
        raise MalformedBodyError(
            "Idempotency-Key header and body idempotency_key disagree"
        )
    idempotency_key = eval_request.idempotency_key or header_key
    if not idempotency_key:
        raise MalformedBodyError(
            "an idempotency key is required: body field 'idempotency_key' or "
            "Idempotency-Key header"
        )

    store = state.store
    fixtures = state.fixtures

    # 3. Semantic validation -> validation_failed (HTTP 200 per C-COND-1).
    if not fixtures.known_position(eval_request.position_id):
        return Envelope(
            status="validation_failed",
            user_message="Unknown position reference.",
            safe_details=f"position_id '{eval_request.position_id}' is not a known fixture",
            errors=["unknown_position"],
        )
    if eval_request.candidate_ref is not None and not fixtures.known_candidate(
        eval_request.candidate_ref
    ):
        return Envelope(
            status="validation_failed",
            user_message="Unknown candidate reference.",
            safe_details=f"candidate_ref '{eval_request.candidate_ref}' is not a known fixture",
            errors=["unknown_candidate"],
        )

    # 4. Idempotency (replay -> stored result, zero council execution).
    fingerprint = idempotency.request_fingerprint(body)
    existing = idempotency.lookup(store, idempotency_key)
    if existing is not None:
        if existing.request_fingerprint != fingerprint:
            return Envelope(
                status="validation_failed",
                user_message="Idempotency key was already used with a different payload.",
                safe_details="idempotency_key reuse with a different request fingerprint",
                errors=["idempotency_key_conflict"],
            )
        stored = store.load_record(existing.evaluation_id)
        logger.info(
            "idempotent replay evaluation_id=%s key_fingerprint_match=true",
            existing.evaluation_id,
        )
        return _set_correlation_header(request, _record_envelope(stored, replayed=True))

    # 5. Source resolution + sha256 verification (mismatch -> blocked).
    try:
        if eval_request.candidate_ref is not None:
            resume = fixtures.resolve(f"{eval_request.candidate_ref}:resume")
            cover_letter = fixtures.resolve(f"{eval_request.candidate_ref}:cover_letter")
        else:
            resume = inline_source("inline:resume", eval_request.resume_text or "")
            cover_letter = inline_source(
                "inline:cover_letter", eval_request.cover_letter_text or ""
            )
        job_description = fixtures.resolve(eval_request.position_id)
        rubric_json, rubric_source = fixtures.resolve_rubric_json()
    except SourceIntegrityError as exc:
        logger.info("source integrity blocked artifact=%s", exc.artifact_id)
        return Envelope(
            status="blocked",
            user_message=(
                "Source verification failed; the evaluation was blocked before "
                "any council execution."
            ),
            safe_details=exc.safe_detail(),
            errors=["source_integrity_failure"],
        )

    # 6. Council orchestration -> gates -> persistence -> envelope.
    evaluation_id = ids.new_evaluation_id()
    correlation_id = ids.correlation_id_for(evaluation_id)
    created_at = ids.utc_now_iso()
    record = run_council(
        config=state.config,
        provider=state.provider,
        request=eval_request,
        actor=actor,
        resume=resume,
        cover_letter=cover_letter,
        job_description=job_description,
        rubric_json=rubric_json,
        rubric_source=rubric_source,
        evaluation_id=evaluation_id,
        correlation_id=correlation_id,
        created_at=created_at,
        completed_at_fn=ids.utc_now_iso,
    )
    store.save_record(record)
    idempotency.record(
        store,
        idempotency_key=idempotency_key,
        evaluation_id=evaluation_id,
        fingerprint=fingerprint,
        created_at=created_at,
    )
    return _set_correlation_header(
        request, _record_envelope(record.model_dump(mode="json"))
    )


@router.get(
    "/api/evaluations/{evaluation_id}",
    response_model=Envelope,
    operation_id="getEvaluation",
    openapi_extra={"parameters": _HEADER_PARAMS_GET},
    summary="Retrieve the full audit record for one evaluation",
    description=(
        "Returns the persisted full audit record (every intermediate council "
        "output, rigor resolution, triggers, gate results, actor identity and "
        "role context) wrapped in the standard envelope. Requires the 'hr' role."
    ),
)
async def get_evaluation(evaluation_id: str, request: Request) -> Envelope:
    # 1. Auth first.
    authenticate_and_authorize(request)

    record = request.app.state.store.load_record(evaluation_id)
    if record is None:
        return Envelope(
            status="validation_failed",
            user_message="Unknown evaluation id.",
            safe_details=f"no record exists for evaluation_id '{evaluation_id}'",
            errors=["unknown_evaluation_id"],
        )
    return _set_correlation_header(
        request,
        Envelope(
            status="completed",
            evaluation_id=evaluation_id,
            correlation_id=record.get("correlation_id"),
            user_message=(
                "Full audit record retrieved. The contained evaluation is advisory "
                "decision support and requires human review."
            ),
            result=record,
        ),
    )
