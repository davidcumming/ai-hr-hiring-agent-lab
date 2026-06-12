"""Full audit record (blob-equivalent) + table-equivalent metadata row shapes.

The full record is the ONLY artifact allowed to carry document/evidence text
(the controlled channel). The table-equivalent row schema deliberately has no
text-bearing field — references, hashes, sizes, counters, and flags only
(BR-010, enforced by shape; storage-doc metadata-first rule).
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from hr_eval_lab.config import RigorMode
from hr_eval_lab.domain.schemas.evaluation import (
    AdvisoryEvaluation,
    GateResult,
    TriggerResult,
)
from hr_eval_lab.domain.schemas.provider import ProviderMetadata

RECORD_SCHEMA_VERSION = "1.0"


class ActorContext(BaseModel):
    """Authenticated simulated-lab actor — persisted on every record (UFM-012)."""

    model_config = ConfigDict(extra="forbid")

    actor_id: str
    display: Optional[str] = None
    roles: list[str]
    resolved_role: str  # the role that authorized this request ("hr")


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    version: str
    sha256: str
    origin: Literal["fixture", "inline"]
    synthetic: bool = True


class PacketSegment(BaseModel):
    """Stably addressed source segment (e.g. ``resume:s04``) so citations are
    mechanically resolvable. Text is allowed here: the packet lives only
    inside the controlled full record."""

    model_config = ConfigDict(extra="forbid")

    segment_id: str
    artifact_id: str
    text: str


class RubricCriterionView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str
    name: str
    kind: Literal["required", "preferred"]
    definition: str
    keywords: list[str]


class RubricView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rubric_id: str
    version: str
    sha256: str
    scale_min: int
    scale_max: int
    anchors: dict[str, str]
    criteria: list[RubricCriterionView]
    disqualifier_note: str
    prohibited_factors_note: str


class EvidencePacket(BaseModel):
    """The controlled evidence packet — code-built BEFORE any provider call."""

    model_config = ConfigDict(extra="forbid")

    sources: list[SourceRef]
    rubric: RubricView
    segments: list[PacketSegment]
    evaluation_question: Optional[str] = None


class RoleExecution(BaseModel):
    """One council role's recorded execution (every intermediate output)."""

    model_config = ConfigDict(extra="forbid")

    sequence_index: int
    role_id: str
    role_kind: Literal["code", "model"]
    schema_version: str
    output: dict[str, Any]
    provider_metadata: Optional[ProviderMetadata] = None  # model-backed only
    retry_count: int = Field(ge=0, le=1, default=0)
    schema_valid: bool = True


class RigorResolution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    server_default: RigorMode
    risk_classification: str
    requested_rigor: Optional[RigorMode] = None
    effective_rigor: RigorMode
    explanation: str
    downgrade_attempted: bool = False
    downgrade_detail: Optional[str] = None


class EscalationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: Literal["record_only", "auto_escalate"]
    provenance: Literal["none", "configured_escalated", "policy_triggered"]
    triggers_fired: list[str]
    mode_c_executed: bool
    rationale: str
    human_review_mandatory_reason: Optional[str] = None


class HumanReviewBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    human_review_required: Literal[True]
    reasons: list[str]


class EvaluationRecord(BaseModel):
    """Blob-equivalent full audit record, persisted per evaluation_id and
    serialized as canonical JSON (sorted keys, fixed separators, UTF-8)."""

    model_config = ConfigDict(extra="forbid")

    record_schema_version: str = RECORD_SCHEMA_VERSION
    evaluation_id: str
    correlation_id: str
    created_at: str
    completed_at: str
    status: Literal["completed", "blocked"]
    actor: ActorContext
    request: dict[str, Any]  # as received, incl. advisory requested_rigor
    sources: list[SourceRef]
    evidence_packet: EvidencePacket
    packet_sequence_index: int  # proves packet completion precedes provider calls
    role_executions: list[RoleExecution]
    rigor_resolution: RigorResolution
    triggers: list[TriggerResult]
    escalation: EscalationRecord
    gate_results: list[GateResult]
    provider_invocation_count: int
    effective_mode: Literal["A", "B", "C"]
    result: Optional[AdvisoryEvaluation] = None  # None only if assembly failed
    human_review: HumanReviewBlock


# ---------------------------------------------------------------------------
# Table-equivalent row shapes (metadata-first; NO text fields by construction)
# ---------------------------------------------------------------------------


class EvidenceRow(BaseModel):
    """One EvaluationEvidence row. References, hashes, sizes, counters, and
    flags ONLY — the schema has no field able to carry document text, prompt
    text, or model I/O (BR-010). Carries actor/role/correlation properties for
    storage-doc §4.4 parity (architecture-check §8 recommendation)."""

    model_config = ConfigDict(extra="forbid")

    PartitionKey: str  # evaluation_id (case-less analogue of case_id)
    RowKey: str  # zero-padded sequence index (ordered partition scan)
    event_type: str
    role_id: str
    role_kind: Literal["code", "model"]
    schema_version: str
    artifact_refs: list[str]
    segment_count: int = 0
    citation_count: int = 0
    output_size_bytes: int = 0
    retry_count: int = 0
    ai_backend_type: str = "none"
    flags: list[str] = Field(default_factory=list)
    actor_id: str = ""
    resolved_role: str = ""
    correlation_id: str = ""
    created_at: str = ""


class IdempotencyRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    PartitionKey: str  # idempotency_key
    RowKey: str  # constant "key"
    evaluation_id: str
    request_fingerprint: str  # sha256 of canonical request JSON — never content
    created_at: str


class ReviewQueueRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    PartitionKey: str  # evaluation_id
    RowKey: str
    status: str
    mandatory_reasons: list[str]
    actor_id: str
    created_at: str
