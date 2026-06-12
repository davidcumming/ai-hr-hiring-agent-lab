"""Council composition — the 11-role registry and Mode A/B/C tables (FR-006).

Code roles are deterministic and facade-owned (no provider call, no token
cost). Model-backed roles execute only through the provider seam. The mode
tables are source-controlled; their version is recorded in the provider
metadata block of every record (ORCHESTRATION_VERSION).
"""

from __future__ import annotations

from hr_eval_lab.config import RigorMode
from hr_eval_lab.domain.schemas import council as c

#: All 11 council roles, in pipeline order, with their kind.
ROLE_REGISTRY: list[tuple[str, str]] = [
    (c.ROLE_REQUEST_NORMALIZER, "code"),  # 1
    (c.ROLE_SOURCE_INGESTION, "code"),  # 2
    (c.ROLE_EVIDENCE_EXTRACTION, "model"),  # 3
    (c.ROLE_RULES_VALIDATOR, "code"),  # 4
    (c.ROLE_MERIT_ADVOCATE, "model"),  # 5
    (c.ROLE_RISK_GAPS_ADVOCATE, "model"),  # 6
    (c.ROLE_NEUTRAL_SCORING_JUDGE, "model"),  # 7 (Mode B+)
    (c.ROLE_POLICY_FAIRNESS_AUDITOR, "model"),  # 8 (Mode B+)
    (c.ROLE_SYNTHESIS_JUDGE, "model"),  # 9
    (c.ROLE_QUALITY_GATES, "code"),  # 10
    (c.ROLE_PERSISTENCE_REVIEW_QUEUE, "code"),  # 11
]

#: Mode C extension roles (run only via the escalation decision).
MODE_C_EXTENSION_ROLES: list[str] = [
    c.ROLE_SECOND_SYNTHESIS_JUDGE,
    c.ROLE_RUBRIC_CALIBRATION_JUDGE,
]

#: Judgment-phase model roles per effective rigor (advocates, then scoring/
#: fairness where in mode, then the Synthesis Judge — evidence before judgment).
_JUDGMENT_ROLES_BY_RIGOR: dict[str, list[str]] = {
    "standard": [
        c.ROLE_MERIT_ADVOCATE,
        c.ROLE_RISK_GAPS_ADVOCATE,
        c.ROLE_SYNTHESIS_JUDGE,
    ],
    "high_impact": [
        c.ROLE_MERIT_ADVOCATE,
        c.ROLE_RISK_GAPS_ADVOCATE,
        c.ROLE_NEUTRAL_SCORING_JUDGE,
        c.ROLE_POLICY_FAIRNESS_AUDITOR,
        c.ROLE_SYNTHESIS_JUDGE,
    ],
}
# Escalated runs use the Mode B base composition; the Mode C extension roles
# are added by the escalation decision (configured_escalated provenance).
_JUDGMENT_ROLES_BY_RIGOR["escalated"] = list(_JUDGMENT_ROLES_BY_RIGOR["high_impact"])


def judgment_roles_for(effective_rigor: RigorMode) -> list[str]:
    return list(_JUDGMENT_ROLES_BY_RIGOR[effective_rigor])


def model_roles_in_mode(effective_rigor: RigorMode) -> list[str]:
    """All model-backed roles in the base mode (extraction + judgment)."""
    return [c.ROLE_EVIDENCE_EXTRACTION] + judgment_roles_for(effective_rigor)


def mode_letter(effective_rigor: RigorMode, mode_c_executed: bool) -> str:
    if mode_c_executed:
        return "C"
    return "A" if effective_rigor == "standard" else "B"
