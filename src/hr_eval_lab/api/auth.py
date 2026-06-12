"""Simulated lab identity (header stub) + role authorization (FR-002).

Header-based SIMULATED identities are a lab stand-in consistent with the
identity-design trusted-boundary rule: the facade validates identity and
authorization before any validation, fixture access, or persistence side
effect. This is NEVER an Entra substitute; real identity arrives with live
wiring under the deferred ADR.

Authorization rule (PO §2.2.1, case-less): global role group only — ``hr`` is
required for both POST and GET. All other roles (including ``admin_lab``) and
unauthenticated callers are rejected (401 missing/invalid identity; 403
authenticated-without-hr, envelope status ``unauthorized`` in both cases).
"""

from __future__ import annotations

from fastapi import Request

from hr_eval_lab.api.errors import ApiError
from hr_eval_lab.domain.schemas.audit import ActorContext

#: Lab role vocabulary (identity/RBAC design doc).
LAB_ROLES = {
    "hr",
    "hiring_manager",
    "reviewer",
    "auditor",
    "admin_lab",
    "admin_prod",
    "support",
}

HEADER_ACTOR_ID = "X-Lab-Actor-Id"
HEADER_ACTOR_DISPLAY = "X-Lab-Actor-Display"
HEADER_ROLES = "X-Lab-Roles"

REQUIRED_ROLE = "hr"


def authenticate_and_authorize(request: Request) -> ActorContext:
    """Auth FIRST: short-circuits before any other processing (DT-009)."""
    actor_id = (request.headers.get(HEADER_ACTOR_ID) or "").strip()
    if not actor_id:
        raise ApiError(
            http_status=401,
            envelope_status="unauthorized",
            user_message="Missing or invalid lab identity.",
            safe_details=f"required header {HEADER_ACTOR_ID} absent or empty",
        )

    raw_roles = request.headers.get(HEADER_ROLES) or ""
    roles = [r.strip() for r in raw_roles.split(",") if r.strip()]
    known_roles = [r for r in roles if r in LAB_ROLES]

    if REQUIRED_ROLE not in known_roles:
        raise ApiError(
            http_status=403,
            envelope_status="unauthorized",
            user_message="This operation requires the 'hr' lab role.",
            safe_details="authenticated actor lacks the required global role",
        )

    return ActorContext(
        actor_id=actor_id,
        display=request.headers.get(HEADER_ACTOR_DISPLAY),
        roles=known_roles,
        resolved_role=REQUIRED_ROLE,
    )
