"""Rigor resolver — pure function (DT-003; BR-001/BR-002/BR-003).

Rules:
- Server config wins, always.
- Hiring classification floors the result at ``high_impact`` unless server
  config explicitly sets otherwise (an explicit server ``standard`` IS the
  server winning; an explicit server ``escalated`` raises the result).
- The request body can NEVER lower the result; any downgrade attempt is
  ignored and recorded (UFM-002).
"""

from __future__ import annotations

from hr_eval_lab.config import RigorMode
from hr_eval_lab.domain.schemas.audit import RigorResolution

_ORDER: dict[str, int] = {"standard": 0, "high_impact": 1, "escalated": 2}

#: Risk classification assigned by the Request Normalizer for this workflow.
HIRING_CLASSIFICATION = "hiring_candidate_evaluation"


def resolve_rigor(
    server_default: RigorMode,
    risk_classification: str,
    requested_rigor: RigorMode | None,
) -> RigorResolution:
    """Compute effective rigor + auditable explanation (pure function)."""
    if server_default == "standard":
        effective: RigorMode = "standard"
        explanation = (
            "Server configuration explicitly sets rigor.default_mode=standard; "
            "server config wins over the hiring high-impact default (BR-001)."
        )
    elif server_default == "escalated":
        effective = "escalated"
        explanation = (
            "Server configuration explicitly sets rigor.default_mode=escalated; "
            "the escalated (Mode C) council path is mandatory (BR-003)."
        )
    else:
        effective = "high_impact"
        explanation = (
            f"Risk classification '{risk_classification}' is a hiring/candidate "
            "evaluation, which defaults to high_impact rigor (BR-001); server "
            "configuration concurs (rigor.default_mode=high_impact)."
        )

    downgrade_attempted = False
    downgrade_detail: str | None = None
    if requested_rigor is not None:
        if _ORDER[requested_rigor] < _ORDER[effective]:
            downgrade_attempted = True
            downgrade_detail = (
                f"Request asked for advisory rigor '{requested_rigor}', lower than "
                f"the server-resolved '{effective}'. The request body can never "
                "lower rigor (BR-002); the attempt is recorded and ignored."
            )
            explanation += " " + downgrade_detail
        else:
            explanation += (
                f" Request carried advisory requested_rigor='{requested_rigor}' "
                "(advisory only; server config remains authoritative)."
            )

    return RigorResolution(
        server_default=server_default,
        risk_classification=risk_classification,
        requested_rigor=requested_rigor,
        effective_rigor=effective,
        explanation=explanation,
        downgrade_attempted=downgrade_attempted,
        downgrade_detail=downgrade_detail,
    )
