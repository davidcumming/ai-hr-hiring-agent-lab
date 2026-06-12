"""Council role invocation transcript (readiness pack, coding target 5).

``CouncilRoleInvocation`` is the per-role artifact persisted at
``evaluations/{evaluation_id}/council/{role}.json``. It is a **projection of
the audit record** (the single source of truth), shaped to the readiness-pack
provider output contract: role, prompt template id/version, input artifact
refs, structured output JSON, validation status, provider trace metadata,
token usage, latency, warnings, and safe error. It never contains raw
prompts, hidden instructions, raw provider errors, secrets, or stack traces.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from hr_eval_lab.domain.schemas.audit import EvaluationRecord, RoleExecution
from hr_eval_lab.domain.schemas.provider import TokenUsage


class CouncilRoleInvocation(BaseModel):
    """Provider-contract view of one council role execution."""

    model_config = ConfigDict(extra="forbid")

    evaluation_id: str
    sequence_index: int
    role: str
    role_kind: Literal["code", "model"]
    prompt_template_id: Optional[str] = None  # null for code roles
    prompt_template_version: Optional[str] = None
    input_artifact_refs: list[str] = Field(default_factory=list)
    output_json: dict[str, Any]
    validation_status: Literal["valid", "valid_after_retry", "invalid"]
    model_or_agent_ref: Optional[str] = None  # null under the deterministic mock
    provider_trace_id: Optional[str] = None  # null/local placeholder under the mock
    token_usage: Optional[TokenUsage] = None  # null for code roles
    latency_ms: int = 0
    warnings: list[str] = Field(default_factory=list)
    safe_error: Optional[str] = None  # safe category only; never raw provider errors


def _validation_status(execution: RoleExecution) -> str:
    if not execution.schema_valid:
        return "invalid"
    if execution.retry_count:
        return "valid_after_retry"
    return "valid"


def build_role_invocation(
    record: EvaluationRecord, execution: RoleExecution
) -> CouncilRoleInvocation:
    """Project one RoleExecution from the audit record into the transcript view."""
    meta = execution.provider_metadata
    return CouncilRoleInvocation(
        evaluation_id=record.evaluation_id,
        sequence_index=execution.sequence_index,
        role=execution.role_id,
        role_kind=execution.role_kind,
        prompt_template_id=meta.prompt_template_id if meta else None,
        prompt_template_version=meta.prompt_template_version if meta else None,
        input_artifact_refs=[s.artifact_id for s in record.sources],
        output_json=execution.output,
        validation_status=_validation_status(execution),  # type: ignore[arg-type]
        model_or_agent_ref=meta.model_or_agent_ref if meta else None,
        provider_trace_id=meta.trace_id if meta else None,
        token_usage=meta.token_usage if meta else None,
        latency_ms=meta.latency_ms if meta else 0,
        warnings=list(meta.warnings) if meta else [],
        safe_error=meta.safe_error if meta else None,
    )
