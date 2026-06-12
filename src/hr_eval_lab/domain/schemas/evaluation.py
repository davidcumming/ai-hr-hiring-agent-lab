"""Advisory evaluation result — the safe response contract (BR-007, §3.12).

Structural invariants enforced here, with NO code path around them:

- ``decision_support_only`` and ``human_review_required`` are typed as
  ``Literal[True]`` — a record without them, or with ``false``, cannot be
  constructed or serialized (DT-010's serializer-level assertion target).
- ``recommendation_label`` is a closed ADVISORY enum. No field for a hire or
  reject decision, cross-candidate ranking, or candidate contact exists in any
  schema in this package (UFM-006).
- Fairness block, disagreements, missing-evidence notes, confidence, and
  limitations are required fields (present even when empty).
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hr_eval_lab.config import AiBackendType, EscalationPolicy, RigorMode
from hr_eval_lab.domain.schemas.council import (
    Confidence,
    CriterionEvaluation,
    Disagreement,
    FairnessFinding,
    Severity,
)


class RecommendationLabel(str, Enum):
    """Closed advisory vocabulary — labels are decision SUPPORT, never decisions."""

    advance_to_interview = "advance_to_interview"
    do_not_advance = "do_not_advance"
    hold_for_review = "hold_for_review"
    insufficient_evidence = "insufficient_evidence"


class FairnessBlock(BaseModel):
    """Policy/fairness review block — required even when empty of findings."""

    model_config = ConfigDict(extra="forbid")

    reviewed: bool
    findings: list[FairnessFinding]
    overall_severity: Severity
    prohibited_factor_violations: list[str]
    anomalous_content_flags: list[str]  # segment ids flagged as instruction-like


class TriggerResult(BaseModel):
    """One escalation-trigger computation — recorded on EVERY run (FR-011)."""

    model_config = ConfigDict(extra="forbid")

    trigger_id: str
    fired: bool
    computed_value: str
    threshold: str
    not_computed_inputs: list[str] = Field(default_factory=list)


class GateResult(BaseModel):
    """One deterministic quality-gate result (FR-008)."""

    model_config = ConfigDict(extra="forbid")

    gate_id: str
    result: Literal["pass", "fail"]
    reason: str
    details_safe: str = ""


class EscalationBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: EscalationPolicy
    provenance: Literal["none", "configured_escalated", "policy_triggered"]
    triggers_fired: list[str]
    mode_c_executed: bool
    rationale: str


class RigorBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effective_rigor: RigorMode
    resolution_explanation: str
    downgrade_attempted: bool
    requested_rigor: RigorMode | None = None


class AdvisoryEvaluation(BaseModel):
    """The advisory result returned in the envelope (FR-007 field set)."""

    model_config = ConfigDict(extra="forbid")

    # Mandatory advisory invariants — Literal[True]: unconstructible otherwise.
    decision_support_only: Literal[True]
    human_review_required: Literal[True]

    recommendation_label: RecommendationLabel
    criterion_evaluations: list[CriterionEvaluation]
    disagreements: list[Disagreement]
    fairness: FairnessBlock
    confidence: Confidence
    confidence_score: int = Field(ge=0, le=100)
    limitations: list[str]

    rigor: RigorBlock
    escalation: EscalationBlock
    triggers: list[TriggerResult]
    quality_gates: list[GateResult]

    ai_backend_type: AiBackendType
