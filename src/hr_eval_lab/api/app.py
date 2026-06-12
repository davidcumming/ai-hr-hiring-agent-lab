"""FastAPI app factory — wiring + exception handlers.

``create_app(config=..., provider=...)`` lets tests inject explicit config
objects, scripted mock providers, and temp persistence roots without touching
the committed config file. The default path loads ``config/lab-config.toml``
and constructs the UNSCRIPTED deterministic mock provider.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from hr_eval_lab import __version__
from hr_eval_lab.api.errors import (
    ApiError,
    MalformedBodyError,
    api_error_handler,
    malformed_body_handler,
)
from hr_eval_lab.api.routes_evaluations import router
from hr_eval_lab.config import LabConfig, load_config
from hr_eval_lab.logging_setup import get_logger
from hr_eval_lab.persistence.store import LocalStore
from hr_eval_lab.providers.base import CouncilProvider, select_provider
from hr_eval_lab.sources.fixture_store import FixtureStore

OPENAPI_TITLE = "AI HR Hiring Agent Lab — Candidate Evaluation Council API"
OPENAPI_VERSION = "1.0.0"
OPENAPI_DESCRIPTION = (
    "Advisory, evidence-grounded single-candidate evaluation "
    "(slice-e1-candidate-evaluation-council). Every result is decision support "
    "for a human reviewer (decision_support_only=true, "
    "human_review_required=true) — never a hiring decision, ranking, or "
    "candidate contact. Authentication uses SIMULATED lab identity headers "
    "(X-Lab-Actor-Id, X-Lab-Roles; the 'hr' role is required for both "
    "endpoints); this is a lab stand-in, never an Entra substitute. Envelope "
    "status vocabulary: completed | blocked | validation_failed | unauthorized "
    "are emitted; needs_input and error are RESERVED (declared, never emitted "
    "by this slice). HTTP mapping per the adopted API contracts: business "
    "outcomes return 200 with the envelope status; 400 malformed body; 401 "
    "missing identity; 403 authenticated without the required role."
)


def create_app(
    config: LabConfig | None = None,
    provider: CouncilProvider | None = None,
    fixtures_root: str | Path = "fixtures",
) -> FastAPI:
    config = config or load_config()
    provider = provider or select_provider(config)

    app = FastAPI(
        title=OPENAPI_TITLE,
        version=OPENAPI_VERSION,
        description=OPENAPI_DESCRIPTION,
    )
    app.state.config = config
    app.state.provider = provider
    app.state.store = LocalStore(config.persistence.root)
    app.state.fixtures = FixtureStore(fixtures_root)

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(MalformedBodyError, malformed_body_handler)

    # Belt-and-braces: any framework-level body validation failure is mapped to
    # HTTP 400 (FR-003) rather than FastAPI's default 422.
    async def _validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "malformed_request_body", "detail": "request validation failed"},
        )

    app.add_exception_handler(RequestValidationError, _validation_handler)

    app.include_router(router)

    logger = get_logger("app")
    logger.info(
        "app created version=%s ai_backend_type=%s rigor_default=%s escalation_policy=%s",
        __version__,
        config.provider.ai_backend_type,
        config.rigor.default_mode,
        config.escalation.policy,
    )
    return app
