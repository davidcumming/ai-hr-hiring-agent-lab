"""Recruitment case API schemas for the case workflow facade."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from hr_eval_lab.domain.schemas.workflow import (
    CaseRole,
    CaseStatus,
    CandidatePackageStatus,
    GateStatus,
    ApplicantImportStatus,
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
WorkflowArtifactStatus = Literal[
    "draft",
    "under_review",
    "approved",
    "superseded",
    "rejected",
    "exported",
]
ImportFindingSeverity = Literal["blocking", "warning"]


def _strip_string_list(values: list[str], label: str) -> list[str]:
    stripped = [_strip_required(value, label) for value in values]
    if len(set(stripped)) != len(stripped):
        raise ValueError(f"{label} must not contain duplicates")
    return stripped


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


class ApplicantCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    synthetic: bool
    candidate_ref: str = Field(min_length=1, max_length=120)
    display_label: str | None = Field(default=None, max_length=160)

    @field_validator("candidate_ref", "display_label")
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


class CandidateDocumentRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = Field(min_length=1, max_length=80)
    source_origin: SourceDocumentRequestOrigin
    source_label: str | None = Field(default=None, max_length=160)
    file_name: str | None = Field(default=None, max_length=240)
    mime_type: SourceDocumentMimeType = "text/plain"
    synthetic: bool
    content_text: str = Field(min_length=1, max_length=20_000)

    @field_validator("document_type", "source_label", "file_name", "content_text")
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


class ApplicantImportCandidateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_ref: str = Field(min_length=1, max_length=120)
    display_label: str | None = Field(default=None, max_length=160)
    documents: list[CandidateDocumentRegisterRequest] = Field(
        default_factory=list,
        max_length=10,
    )

    @field_validator("candidate_ref", "display_label")
    @classmethod
    def _strip_strings(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return _strip_required(value, info.field_name)


class ApplicantImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    synthetic: bool
    candidates: list[ApplicantImportCandidateInput] = Field(min_length=1)

    @field_validator("synthetic")
    @classmethod
    def _require_synthetic_true(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("synthetic must be true")
        return value


class ApplicantSetConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    synthetic: bool
    applicant_set_version: str = Field(
        default="v1",
        pattern=r"^v[0-9][A-Za-z0-9._-]{0,31}$",
    )

    @field_validator("applicant_set_version")
    @classmethod
    def _strip_strings(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)

    @field_validator("synthetic")
    @classmethod
    def _require_synthetic_true(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("synthetic must be true")
        return value


class RoleIntakeCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    synthetic: bool
    intake_title: str = Field(min_length=1, max_length=160)
    role_purpose: str = Field(min_length=1, max_length=2_000)
    responsibilities: list[str] = Field(min_length=1, max_length=20)
    required_qualifications: list[str] = Field(min_length=1, max_length=20)
    intake_version: str = Field(default="v1", pattern=r"^v[0-9][A-Za-z0-9._-]{0,31}$")
    preferred_qualifications: list[str] = Field(default_factory=list, max_length=20)
    business_context: str | None = Field(default=None, max_length=2_000)
    role_risks: list[str] = Field(default_factory=list, max_length=20)
    open_questions: list[str] = Field(default_factory=list, max_length=20)
    source_document_ids: list[str] = Field(default_factory=list, max_length=20)

    @field_validator(
        "intake_title",
        "role_purpose",
        "business_context",
        "intake_version",
    )
    @classmethod
    def _strip_strings(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return _strip_required(value, info.field_name)

    @field_validator(
        "responsibilities",
        "required_qualifications",
        "preferred_qualifications",
        "role_risks",
        "open_questions",
        "source_document_ids",
    )
    @classmethod
    def _strip_lists(cls, value: list[str], info) -> list[str]:
        return _strip_string_list(value, info.field_name)

    @field_validator("synthetic")
    @classmethod
    def _require_synthetic_true(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("synthetic must be true")
        return value


class RubricRatingAnchorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=10)
    label: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)

    @field_validator("label", "description")
    @classmethod
    def _strip_strings(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)


class RubricCriterionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._-]+$")
    label: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1_000)
    weight: float = Field(gt=0, le=100)
    rating_scale: list[RubricRatingAnchorInput] = Field(min_length=2, max_length=10)
    evidence_expectations: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("criterion_id", "label", "description")
    @classmethod
    def _strip_strings(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)

    @field_validator("evidence_expectations")
    @classmethod
    def _strip_lists(cls, value: list[str], info) -> list[str]:
        return _strip_string_list(value, info.field_name)


class ApprovedRubricRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    synthetic: bool
    rubric_title: str = Field(min_length=1, max_length=160)
    criteria: list[RubricCriterionInput] = Field(min_length=1, max_length=10)
    rubric_version: str = Field(default="v1", pattern=r"^v[0-9][A-Za-z0-9._-]{0,31}$")
    approved_by_actor_id: str | None = Field(default=None, min_length=1, max_length=120)

    @field_validator("rubric_title", "rubric_version", "approved_by_actor_id")
    @classmethod
    def _strip_strings(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return _strip_required(value, info.field_name)

    @field_validator("criteria")
    @classmethod
    def _require_unique_criteria(
        cls, value: list[RubricCriterionInput]
    ) -> list[RubricCriterionInput]:
        criterion_ids = [criterion.criterion_id for criterion in value]
        if len(set(criterion_ids)) != len(criterion_ids):
            raise ValueError("criteria must have unique criterion_id values")
        return value

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
    active_intake_version: str | None = None
    active_rubric_version: str | None = None
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


class CandidateDocumentSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    candidate_id: str
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


class ApplicantSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    candidate_ref: str
    display_label: str
    import_status: ApplicantImportStatus
    applicant_set_version: str
    duplicate_group_id: str | None = None
    blocking_findings: list[str] = Field(default_factory=list)
    created_at: str
    synthetic: bool = True


class CandidatePackageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    package_version: str
    rubric_version: str
    document_ids: list[str] = Field(default_factory=list)
    required_document_status: dict[str, str] = Field(default_factory=dict)
    package_status: CandidatePackageStatus
    blob_path: str
    sha256: str
    created_at: str
    synthetic: bool = True


class ImportFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    severity: ImportFindingSeverity
    finding_type: str
    message: str
    candidate_id: str | None = None
    candidate_ref: str | None = None


class WorkflowArtifactSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: str
    version: str
    status: WorkflowArtifactStatus
    blob_path: str
    sha256: str
    source_document_ids: list[str] = Field(default_factory=list)
    created_at: str
    synthetic: bool = True


class RoleIntakeArtifactResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    artifact: WorkflowArtifactSummary
    role_intake: dict[str, Any]


class RoleIntakeGetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    artifact: WorkflowArtifactSummary
    role_intake: dict[str, Any]


class RubricArtifactResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    artifact: WorkflowArtifactSummary
    approval_id: str
    rubric: dict[str, Any]


class RubricListResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    active_rubric_version: str | None = None
    rubrics: list[WorkflowArtifactSummary] = Field(default_factory=list)


class RubricGetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    artifact: WorkflowArtifactSummary
    rubric: dict[str, Any]


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


class ApplicantRegistrationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    applicant: ApplicantSummary
    package: CandidatePackageSummary
    findings: list[ImportFinding] = Field(default_factory=list)


class ApplicantListResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    applicants: list[ApplicantSummary] = Field(default_factory=list)
    packages: list[CandidatePackageSummary] = Field(default_factory=list)
    findings: list[ImportFinding] = Field(default_factory=list)
    can_confirm: bool = False


class ApplicantDetailResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    applicant: ApplicantSummary
    documents: list[CandidateDocumentSummary] = Field(default_factory=list)
    package: CandidatePackageSummary | None = None
    findings: list[ImportFinding] = Field(default_factory=list)


class CandidateDocumentRegistrationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    applicant: ApplicantSummary
    document: CandidateDocumentSummary
    package: CandidatePackageSummary
    findings: list[ImportFinding] = Field(default_factory=list)


class ApplicantImportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    applicants: list[ApplicantSummary] = Field(default_factory=list)
    packages: list[CandidatePackageSummary] = Field(default_factory=list)
    findings: list[ImportFinding] = Field(default_factory=list)
    imported_count: int
    document_count: int
    can_confirm: bool = False


class ImportFindingsResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    findings: list[ImportFinding] = Field(default_factory=list)
    packages: list[CandidatePackageSummary] = Field(default_factory=list)
    can_confirm: bool = False


class ApplicantSetConfirmationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case: CaseSummary
    confirmed_applicant_set_version: str
    confirmed_candidate_ids: list[str] = Field(default_factory=list)
    packages: list[CandidatePackageSummary] = Field(default_factory=list)
    assessment_unlocked: Literal["locked"] = "locked"


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
