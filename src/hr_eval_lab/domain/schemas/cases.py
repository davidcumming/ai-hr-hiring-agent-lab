"""Recruitment case API schemas for the E9 case-state foundation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from hr_eval_lab.domain.schemas.workflow import (
    CaseRole,
    CaseStatus,
    GateStatus,
    SourceDocumentStatus,
    TaskStatus,
)


CaseEnvelopeStatus = Literal[
    "completed",
    "blocked",
    "validation_failed",
    "unauthorized",
    "needs_input",
    "error",
]


def _strip_required(value: str, label: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{label} must not be empty")
    return text


SourceDocumentRequestType = Literal[
    "job_description",
    "adp_export",
    "posting_source",
    "org_context",
    "business_note",
    "other_role_source",
]
SourceDocumentRequestOrigin = Literal[
    "manual_upload",
    "fixture",
    "adp_export",
    "external_reference",
]
SourceDocumentMimeType = Literal["text/plain", "text/markdown"]


class HiringManagerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: str = Field(min_length=1)
    display_name: str | None = None
    confirmed: bool = False

    @field_validator("actor_id", "display_name")
    @classmethod
    def _strip_strings(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return _strip_required(value, info.field_name)


class RecruitmentCaseCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_title: str = Field(min_length=1)
    department: str = Field(min_length=1)
    recruitment_type: str = Field(min_length=1)
    case_title: str | None = None
    hiring_manager: HiringManagerInput | None = None

    @field_validator("role_title", "department", "recruitment_type", "case_title")
    @classmethod
    def _strip_strings(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return _strip_required(value, info.field_name)

    @property
    def resolved_case_title(self) -> str:
        return self.case_title or f"{self.role_title} - {self.department}"


class SourceDocumentRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: SourceDocumentRequestType
    source_origin: SourceDocumentRequestOrigin
    source_label: str | None = None
    file_name: str | None = None
    mime_type: SourceDocumentMimeType = "text/plain"
    synthetic: bool
    content_text: str = Field(min_length=1, max_length=20_000)

    @field_validator("source_label", "file_name", "content_text")
    @classmethod
    def _strip_strings(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return _strip_required(value, info.field_name)

    @field_validator("synthetic")
    @classmethod
    def _require_synthetic_true(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("synthetic must be true")
        return value


class CaseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    case_title: str
    role_title: str
    department: str
    recruitment_type: str
    case_status: CaseStatus
    current_stage: str
    current_gate: str
    hr_owner_actor_id: str
    primary_hiring_manager_actor_id: str | None = None
    created_at: str
    updated_at: str | None = None
    correlation_id: str
    synthetic: bool = True


class CaseParticipantSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: str
    display_name: str | None = None
    case_role: CaseRole
    required_for_review: bool = False
    required_for_approval: bool = False
    scope: dict[str, Any] = Field(default_factory=dict)
    status: Literal["active", "inactive", "removed"] = "active"


class CaseTaskSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    task_type: str
    assigned_role: CaseRole
    assigned_actor_id: str | None = None
    status: TaskStatus
    blocking_gate: str | None = None


class WorkflowGateSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_id: str
    gate_status: GateStatus
    required_inputs: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    last_checked_at: str


class CaseEventSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_type: str
    actor_id: str
    actor_role: CaseRole
    summary: str
    safe_details: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class CaseNextAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    task_id: str | None = None
    label: str
    description: str
    assigned_role: CaseRole | None = None
    assigned_actor_id: str | None = None
    blocker_ids: list[str] = Field(default_factory=list)


class SourceDocumentSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    document_type: str
    source_origin: str
    source_label: str | None = None
    blob_path: str
    mime_type: str | None = None
    file_name: str | None = None
    size_bytes: int
    sha256: str
    processing_status: SourceDocumentStatus
    version: str
    created_at: str
    synthetic: bool = True


class RecruitmentCaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    participants: list[CaseParticipantSummary] = Field(default_factory=list)
    open_tasks: list[CaseTaskSummary] = Field(default_factory=list)
    gates: list[WorkflowGateSummary] = Field(default_factory=list)
    events: list[CaseEventSummary] = Field(default_factory=list)
    next_actions: list[CaseNextAction] = Field(default_factory=list)


class CaseNextActionsResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    open_tasks: list[CaseTaskSummary] = Field(default_factory=list)
    blocked_tasks: list[CaseTaskSummary] = Field(default_factory=list)
    active_gate_blockers: list[WorkflowGateSummary] = Field(default_factory=list)
    next_actions: list[CaseNextAction] = Field(default_factory=list)


class SourceDocumentRegistrationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    document: SourceDocumentSummary
    documents_count: int


class SourceDocumentListResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    documents: list[SourceDocumentSummary] = Field(default_factory=list)


class SourceDocumentGetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    document: SourceDocumentSummary


class CaseEnvelope(BaseModel):
    """Case-specific standard envelope.

    The existing evaluation ``Envelope`` intentionally remains unchanged so
    the E9 case surface does not alter the established evaluation API schema.
    """

    model_config = ConfigDict(extra="forbid")

    status: CaseEnvelopeStatus
    evaluation_id: None = None
    case_id: str | None = None
    correlation_id: str | None = None
    user_message: str = ""
    safe_details: str | None = None
    result: Any | None = None
    next_actions: list[CaseNextAction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
