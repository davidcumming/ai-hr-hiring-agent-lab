"""FastAPI app factory — wiring + exception handlers.

``create_app(config=..., provider=...)`` lets tests inject explicit config
objects, scripted mock providers, and temp persistence roots without touching
the committed config file. The default path loads ``config/lab-config.toml``
and constructs the UNSCRIPTED deterministic mock provider.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.json_schema import models_json_schema

from hr_eval_lab import __version__
from hr_eval_lab.api.errors import (
    ApiError,
    MalformedBodyError,
    api_error_handler,
    malformed_body_handler,
)
from hr_eval_lab.api.routes_cases import router as cases_router
from hr_eval_lab.api.routes_diagnostics import router as diagnostics_router
from hr_eval_lab.api.routes_evaluations import router as evaluations_router
from hr_eval_lab.api.routes_role_intake_rubrics import router as role_intake_rubrics_router
from hr_eval_lab.api.routes_source_documents import router as source_documents_router
from hr_eval_lab.config import LabConfig, load_config
from hr_eval_lab.domain.schemas.cases import (
    ApprovedRubricRegisterRequest,
    HiringManagerInput,
    RecruitmentCaseCreateRequest,
    RoleIntakeCreateRequest,
    RubricCriterionInput,
    RubricRatingAnchorInput,
    SourceDocumentRegisterRequest,
)
from hr_eval_lab.logging_setup import get_logger
from hr_eval_lab.persistence.backend import select_backend
from hr_eval_lab.persistence.store import LocalStore
from hr_eval_lab.persistence.workflow_storage import select_workflow_storage
from hr_eval_lab.providers.base import CouncilProvider, select_provider
from hr_eval_lab.sources.fixture_store import FixtureStore

OPENAPI_TITLE = "AI HR Hiring Agent Lab API"
OPENAPI_VERSION = "1.0.0"
OPENAPI_DESCRIPTION = (
    "Advisory, evidence-grounded single-candidate evaluation plus the E9 "
    "recruitment-case state foundation, E10 source-document registry, and "
    "E11 role-intake/rubric foundation. "
    "Evaluation results are decision "
    "support for a human reviewer (decision_support_only=true, "
    "human_review_required=true) — never a hiring decision, ranking, or "
    "candidate contact. Case endpoints create and retrieve deterministic "
    "workflow state, source-document endpoints register small synthetic "
    "inline role source text, and E11 endpoints version synthetic role-intake "
    "and approved rubric artifacts through the workflow Table/Blob seam only; "
    "they do not import applicants, create candidate packages, start assessment "
    "jobs, send notifications, call Foundry/model backends, create queue "
    "messages, unlock assessment, or change Copilot Studio. Authentication uses SIMULATED lab identity "
    "headers (X-Lab-Actor-Id, X-Lab-Roles; the 'hr' role is required); this "
    "is a lab stand-in, never an Entra substitute. Envelope status vocabulary: "
    "completed | blocked | validation_failed | unauthorized are emitted; "
    "needs_input and error are RESERVED. HTTP mapping per the adopted API "
    "contracts: business outcomes return 200 with the envelope status; 400 "
    "malformed body; 401 missing identity; 403 authenticated without the "
    "required role."
)


def _case_request_component_schemas() -> dict[str, Any]:
    _, definitions = models_json_schema(
        [
            (RecruitmentCaseCreateRequest, "validation"),
            (HiringManagerInput, "validation"),
            (SourceDocumentRegisterRequest, "validation"),
            (RoleIntakeCreateRequest, "validation"),
            (ApprovedRubricRegisterRequest, "validation"),
            (RubricCriterionInput, "validation"),
            (RubricRatingAnchorInput, "validation"),
        ],
        ref_template="#/components/schemas/{model}",
    )
    return definitions["$defs"]


def _install_case_openapi_components(app: FastAPI) -> None:
    original_openapi = app.openapi

    def _openapi() -> dict[str, Any]:
        schema = original_openapi()
        schemas = schema.setdefault("components", {}).setdefault("schemas", {})
        schemas.update(_case_request_component_schemas())
        return schema

    app.openapi = _openapi


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
    # Storage backend is resolved from [storage] config at app construction —
    # selecting azure_blob without complete config (or without the storage
    # gate explicitly enabled) fails closed here with StorageNotConfiguredError.
    app.state.store = LocalStore(config.persistence.root, backend=select_backend(config))
    app.state.workflow_storage = select_workflow_storage(config)
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

    # Readiness pack: X-Correlation-Id response header. The route handlers set
    # request.state.correlation_id from the envelope (server-assigned id);
    # otherwise a caller-supplied X-Correlation-Id is echoed back.
    @app.middleware("http")
    async def _correlation_header(request: Request, call_next):
        response = await call_next(request)
        correlation_id = getattr(request.state, "correlation_id", None) or (
            request.headers.get("X-Correlation-Id")
        )
        if correlation_id:
            response.headers["X-Correlation-Id"] = correlation_id
        return response

    app.include_router(evaluations_router)
    app.include_router(cases_router)
    app.include_router(source_documents_router)
    app.include_router(role_intake_rubrics_router)
    app.include_router(diagnostics_router)
    _install_case_openapi_components(app)

    logger = get_logger("app")
    logger.info(
        "app created version=%s ai_backend_type=%s rigor_default=%s escalation_policy=%s",
        __version__,
        config.provider.ai_backend_type,
        config.rigor.default_mode,
        config.escalation.policy,
    )
    return app
