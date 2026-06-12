"""Per-role output schemas for all council roles (single schema source).

Model-backed role outputs (Evidence Extraction, the two Advocates, Neutral
Scoring Judge, Policy/Fairness Auditor, Synthesis Judge, plus the Mode C
extension roles) are validated against these models immediately after every
provider invocation, with exactly one bounded corrective retry on failure
(AB-008, gate 1). ``extra="forbid"`` everywhere keeps role discipline
mechanical: e.g. the Evidence Extraction schema has no score or recommendation
field, so evaluative drift is unconstructible (AB-002, DT-016).
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Role ids
# ---------------------------------------------------------------------------

ROLE_REQUEST_NORMALIZER = "request_normalizer"
ROLE_SOURCE_INGESTION = "source_ingestion_versioning"
ROLE_EVIDENCE_EXTRACTION = "evidence_extraction"
ROLE_RULES_VALIDATOR = "deterministic_rules_validator"
ROLE_MERIT_ADVOCATE = "merit_advocate"
ROLE_RISK_GAPS_ADVOCATE = "risk_gaps_advocate"
ROLE_NEUTRAL_SCORING_JUDGE = "neutral_scoring_judge"
ROLE_POLICY_FAIRNESS_AUDITOR = "policy_fairness_auditor"
ROLE_SYNTHESIS_JUDGE = "synthesis_judge"
ROLE_QUALITY_GATES = "quality_gate_evaluators"
ROLE_PERSISTENCE_REVIEW_QUEUE = "persistence_review_queue"
# Mode C extension roles
ROLE_SECOND_SYNTHESIS_JUDGE = "second_synthesis_judge"
ROLE_RUBRIC_CALIBRATION_JUDGE = "rubric_calibration_judge"

Severity = Literal["info", "low", "medium", "high"]
Confidence = Literal["low", "medium", "high"]


# ---------------------------------------------------------------------------
# Evidence Extraction (model-backed, neutral — AB-002)
# ---------------------------------------------------------------------------


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    criterion_id: str
    artifact_id: str
    segment_id: str  # must mechanically resolve to a packet segment
    quote: str  # verbatim span from the referenced segment (gate 6)
    relation: Literal["supporting", "contrary", "contextual"]


class EvidenceExtractionOutput(BaseModel):
    """Neutral evidence inventory. Deliberately has NO score/recommendation
    field of any kind — evaluative output is schema-impossible here."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["evidence_extraction"]
    evidence_items: list[EvidenceItem]
    coverage_notes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Advocates and Neutral Scoring Judge
# ---------------------------------------------------------------------------


class ProposedScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str
    score: int = Field(ge=1, le=5)
    rationale: str
    citations: list[str] = Field(default_factory=list)  # evidence/segment ids
    missing_evidence: bool = False


class AdvocateArgument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str
    claim: str
    citations: list[str]


class MeritAdvocateOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["merit_advocate"]
    stance: Literal["merit"]
    arguments: list[AdvocateArgument]
    proposed_scores: list[ProposedScore]


class RiskGapsAdvocateOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["risk_gaps_advocate"]
    stance: Literal["risk_gaps"]
    arguments: list[AdvocateArgument]
    proposed_scores: list[ProposedScore]


class NeutralScoringOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["neutral_scoring_judge"]
    scores: list[ProposedScore]


# ---------------------------------------------------------------------------
# Policy/Fairness Auditor
# ---------------------------------------------------------------------------


class FairnessFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    severity: Severity
    category: Literal[
        "prohibited_factor",
        "unsupported_inference",
        "anomalous_content",
        "other",
    ]
    description: str
    segment_refs: list[str] = Field(default_factory=list)


class PolicyFairnessOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["policy_fairness_auditor"]
    findings: list[FairnessFinding]
    overall_severity: Severity
    prohibited_factor_violations: list[str] = Field(default_factory=list)
    anomalous_content_flagged: bool = False


# ---------------------------------------------------------------------------
# Synthesis Judge (+ Mode C extension roles)
# ---------------------------------------------------------------------------


class CriterionEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str
    criterion_name: str
    score: int = Field(ge=1, le=5)
    rationale: str
    supporting_evidence: list[str] = Field(default_factory=list)
    contrary_evidence: list[str] = Field(default_factory=list)
    missing_evidence_note: Optional[str] = None


class Disagreement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str
    positions: list[str]  # safe textual positions, e.g. "merit_advocate: 5"
    resolution_rationale: str


class SynthesisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["synthesis_judge"]
    criterion_evaluations: list[CriterionEvaluation]
    disagreements: list[Disagreement]
    recommendation_label: Literal[
        "advance_to_interview",
        "do_not_advance",
        "hold_for_review",
        "insufficient_evidence",
    ]
    confidence: Confidence
    confidence_score: int = Field(ge=0, le=100)
    limitations: list[str]


class SecondSynthesisOutput(BaseModel):
    """Mode C extension: independent second synthesis pass."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["second_synthesis_judge"]
    concurrence: Literal["concur", "partial", "differ"]
    rationale: str
    criterion_score_deltas: list[ProposedScore] = Field(default_factory=list)
    confidence: Confidence


class CalibrationNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str
    anchor_consistent: bool
    note: str


class RubricCalibrationOutput(BaseModel):
    """Mode C extension: rubric anchor-consistency check."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["rubric_calibration_judge"]
    calibration_notes: list[CalibrationNote]
    overall_consistent: bool


#: Role id -> output schema for every MODEL-BACKED role (gate 1 validation map).
MODEL_ROLE_SCHEMAS = {
    ROLE_EVIDENCE_EXTRACTION: EvidenceExtractionOutput,
    ROLE_MERIT_ADVOCATE: MeritAdvocateOutput,
    ROLE_RISK_GAPS_ADVOCATE: RiskGapsAdvocateOutput,
    ROLE_NEUTRAL_SCORING_JUDGE: NeutralScoringOutput,
    ROLE_POLICY_FAIRNESS_AUDITOR: PolicyFairnessOutput,
    ROLE_SYNTHESIS_JUDGE: SynthesisOutput,
    ROLE_SECOND_SYNTHESIS_JUDGE: SecondSynthesisOutput,
    ROLE_RUBRIC_CALIBRATION_JUDGE: RubricCalibrationOutput,
}
