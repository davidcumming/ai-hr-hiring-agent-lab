"""Storage-boundary schemas (readiness pack).

``StorageArtifactRef`` — a reference to one persisted artifact (never the
content). ``RecordSummaryRow`` — the ``metadata/evaluations.jsonl`` summary
row: metadata-first by construction, with **no text-bearing field** (BR-010 —
no resume, cover-letter, prompt, or model I/O text can exist here).
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

#: Artifact types persisted per evaluation (local layout and the future
#: blob layout share these names).
ArtifactType = Literal[
    "record",
    "request",
    "source-documents",
    "evidence-packet",
    "council-role",
    "synthesis",
    "quality-gates",
    "provider-metadata",
    "human-review",
]


class StorageArtifactRef(BaseModel):
    """Reference to one persisted artifact — path/identity metadata only."""

    model_config = ConfigDict(extra="forbid")

    evaluation_id: str
    artifact_type: ArtifactType
    name: str  # file-relative name, e.g. "record.json" or "council/merit_advocate.json"
    sha256: str
    size_bytes: int


class RecordSummaryRow(BaseModel):
    """One row per evaluation in ``metadata/evaluations.jsonl``.

    Deliberately mirrors an Azure Table shape (PartitionKey/RowKey + typed
    properties). NO text-bearing fields: identifiers, enums, counts, hashes,
    and timestamps only.
    """

    model_config = ConfigDict(extra="forbid")

    PartitionKey: str  # evaluation_id
    RowKey: Literal["summary"] = "summary"
    status: Literal["completed", "blocked"]
    position_id: str
    candidate_ref: Optional[str] = None  # fixture id or None for inline submissions
    rubric_id: str
    rubric_version: str
    effective_rigor: str
    effective_mode: str
    escalation_policy: str
    triggers_fired: int
    gates_failed: int
    recommendation_label: Optional[str] = None
    human_review_required: bool
    decision_support_only: bool
    ai_backend_type: str
    provider_id: str
    artifact_count: int
    actor_id: str
    resolved_role: str
    correlation_id: str
    created_at: str
    completed_at: str
    source_hashes: list[str] = Field(default_factory=list)
