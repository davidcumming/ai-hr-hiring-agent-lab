"""Status/HTTP mapping per API-contracts §4 — C-COND-1 APPLIED.

The documented mapping is adopted (architecture-check §5/§8, condition
C-COND-1): business outcomes (``completed``/``blocked``/``validation_failed``)
return HTTP 200 with the status in the envelope; HTTP 400 only for a malformed
body (no envelope status consumed); HTTP 401 for missing/invalid identity vs
HTTP 403 for an authenticated role denial (both carry envelope status
``unauthorized``); 409 is never used (reserved for concurrency ``error``,
which this slice never emits).
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from hr_eval_lab.api.envelope import Envelope


class ApiError(Exception):
    """Auth-layer rejection carrying its HTTP code + safe envelope content."""

    def __init__(
        self,
        http_status: int,
        envelope_status: str,
        user_message: str,
        safe_details: str | None = None,
    ) -> None:
        super().__init__(user_message)
        self.http_status = http_status
        self.envelope_status = envelope_status
        self.user_message = user_message
        self.safe_details = safe_details


class MalformedBodyError(Exception):
    """Malformed request body -> HTTP 400 (HTTP-level rejection; no envelope
    status consumed). Details are field locations/types only — never values."""

    def __init__(self, safe_detail: str) -> None:
        super().__init__(safe_detail)
        self.safe_detail = safe_detail


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    envelope = Envelope(
        status=exc.envelope_status,  # type: ignore[arg-type]
        user_message=exc.user_message,
        safe_details=exc.safe_details,
        errors=[exc.envelope_status],
    )
    return JSONResponse(status_code=exc.http_status, content=envelope.model_dump(mode="json"))


async def malformed_body_handler(request: Request, exc: MalformedBodyError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "malformed_request_body", "detail": exc.safe_detail},
    )
