"""Provider-contract envelope (single schema source for mock AND Foundry seam).

This is the in-slice seam-contract authority alongside the Foundry companion §8
required trace/eval metadata (PO §2.2.2). The same schema serves the
deterministic mock and the Foundry stub — "no mock-only schema fork" (DT-013).

C-COND-2 (architecture-check §8) applied: a typed, NULLABLE ``eval_run_id``
placeholder is present alongside the nullable ``trace_id``, and the
orchestration/workflow version is carried in the metadata block.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from hr_eval_lab.config import AiBackendType

#: Version of this provider contract (seam schema), recorded per invocation.
PROVIDER_CONTRACT_VERSION = "1.0"

#: Source-controlled orchestration/workflow version (council mode tables).
ORCHESTRATION_VERSION = "council-composition-v1"


class TokenUsage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: int = 0
    completion: int = 0


class ProviderMetadata(BaseModel):
    """Trace/eval metadata per Foundry companion §8 (placeholders typed).

    Under the mock backend the identifiers are deterministic local
    placeholders; ``trace_id`` and ``eval_run_id`` are nullable by contract
    (C-COND-2). The exact live schema is pinned later by the deferred ADR.
    """

    model_config = ConfigDict(extra="forbid")

    ai_backend_type: AiBackendType
    trace_id: Optional[str] = None
    eval_run_id: Optional[str] = None  # C-COND-2: nullable evaluation-run identifier
    agent_run_id: Optional[str] = None
    model_deployment: Optional[str] = None
    prompt_version: Optional[str] = None
    # Readiness-pack provider output contract additions (all deterministic /
    # nullable under the mock; live semantics remain owned by the deferred ADR):
    prompt_template_id: Optional[str] = None  # versioned prompt registry id
    prompt_template_version: Optional[str] = None
    model_or_agent_ref: Optional[str] = None  # null for mock
    warnings: list[str] = Field(default_factory=list)
    safe_error: Optional[str] = None  # safe category only; never raw provider errors
    orchestration_version: str = ORCHESTRATION_VERSION
    role_schema_version: str = PROVIDER_CONTRACT_VERSION
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: int = 0


class ProviderResult(BaseModel):
    """What every provider returns for one role invocation."""

    model_config = ConfigDict(extra="forbid")

    role_id: str
    payload: dict[str, Any]
    metadata: ProviderMetadata


class ProviderNotConfiguredError(RuntimeError):
    """Raised by the Foundry seam stub on any invocation (live wiring deferred)."""
