"""Azure Table-shaped workflow entities for the HR Hiring MVP foundation.

These schemas define the logical E7 data model without adding public API
surface or live Azure SDK calls. They serialize to Table-compatible rows:
primitive properties stay primitive, and list/dict properties are canonical
JSON strings at the adapter boundary.
"""

from __future__ import annotations

import json
import types
from typing import Any, ClassVar, Literal, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, model_validator


def canonical_table_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _non_empty(value: str, label: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{label} must not be empty")
    return text


def _expects_json_property(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin in (list, dict):
        return True
    if origin in (Union, types.UnionType):
        return any(_expects_json_property(arg) for arg in get_args(annotation))
    return False


WorkflowEntityT = TypeVar("WorkflowEntityT", bound="WorkflowTableEntity")


class WorkflowTableEntity(BaseModel):
    """Base for logical Table entities.

    ``table_name`` is a class-level routing value, not a Table property. The
    persisted row contains ``PartitionKey`` / ``RowKey`` plus entity fields.
    """

    model_config = ConfigDict(extra="forbid")

    table_name: ClassVar[str]
    case_partition_key_field: ClassVar[str | None] = None
    row_key_prefix: ClassVar[str | None] = None

    PartitionKey: str
    RowKey: str
    entity_type: str
    schema_version: Literal["1.0"] = "1.0"
    created_at: str
    updated_at: str | None = None
    created_by_actor_id: str | None = None
    created_by_role: str | None = None
    updated_by_actor_id: str | None = None
    updated_by_role: str | None = None
    correlation_id: str
    synthetic: bool = True
    etag: str | None = None

    @model_validator(mode="after")
    def _validate_common_fields(self) -> "WorkflowTableEntity":
        _non_empty(self.PartitionKey, "PartitionKey")
        _non_empty(self.RowKey, "RowKey")
        _non_empty(self.entity_type, "entity_type")
        _non_empty(self.schema_version, "schema_version")
        _non_empty(self.created_at, "created_at")
        _non_empty(self.correlation_id, "correlation_id")
        if self.case_partition_key_field is not None:
            expected_partition = getattr(self, self.case_partition_key_field, None)
            if not isinstance(expected_partition, str):
                raise ValueError(
                    f"{self.entity_type} requires "
                    f"{self.case_partition_key_field} for PartitionKey validation"
                )
            if self.PartitionKey != _non_empty(
                expected_partition, self.case_partition_key_field
            ):
                raise ValueError(
                    f"{self.entity_type} PartitionKey must equal "
                    f"{self.case_partition_key_field}"
                )
        if self.row_key_prefix is not None and not self.RowKey.startswith(
            self.row_key_prefix
        ):
            raise ValueError(
                f"{self.entity_type} RowKey must start with {self.row_key_prefix!r}"
            )
        return self

    def to_table_entity(self) -> dict[str, Any]:
        row: dict[str, Any] = {}
        for key, value in self.model_dump(mode="json").items():
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                row[key] = canonical_table_json(value)
            else:
                row[key] = value
        return row

    @classmethod
    def from_table_entity(
        cls: type[WorkflowEntityT], row: dict[str, Any]
    ) -> WorkflowEntityT:
        decoded = dict(row)
        for name, field in cls.model_fields.items():
            if name not in decoded:
                continue
            value = decoded[name]
            if isinstance(value, str) and _expects_json_property(field.annotation):
                decoded[name] = json.loads(value)
        return cls.model_validate(decoded)


class CasePartitionedWorkflowEntity(WorkflowTableEntity):
    """Workflow entity whose Azure Table partition is the owning case id."""

    case_partition_key_field: ClassVar[str | None] = "case_id"


CaseStatus = Literal[
    "intake_pending",
    "posting_draft",
    "rubric_pending",
    "applicants_pending",
    "assessment_ready",
    "assessment_running",
    "review_pending",
    "shortlist_pending",
    "interview_pending",
    "final_pending",
    "completed",
    "cancelled",
]

CaseRole = Literal[
    "hr_specialist",
    "hiring_manager",
    "interviewer",
    "reviewer",
    "auditor",
    "admin",
]

TaskStatus = Literal["open", "blocked", "completed", "cancelled"]
GateStatus = Literal["locked", "unlocked", "blocked", "satisfied", "waived"]
NotificationStatus = Literal["unread", "read", "dismissed", "actioned"]
NotificationType = Literal[
    "assessment_completed",
    "assessment_failed",
    "review_required",
    "approval_required",
    "gate_blocked",
    "export_ready",
]
SourceDocumentStatus = Literal["registered", "queued", "processed", "failed", "excluded"]
ArtifactVersionStatus = Literal[
    "draft",
    "under_review",
    "approved",
    "superseded",
    "rejected",
    "exported",
]
ApprovalDecision = Literal["approved", "rejected", "changes_requested", "abstained"]
ApplicantImportStatus = Literal[
    "imported",
    "incomplete",
    "duplicate_pending",
    "confirmed",
    "excluded",
]
CandidatePackageStatus = Literal["draft", "complete", "blocked", "stale", "assessed"]
ModelAssessmentJobStatus = Literal[
    "queued",
    "running",
    "completed",
    "partially_completed",
    "failed",
    "cancelled",
]
ModelAssessmentStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
    "stale",
    "superseded",
]
HumanReviewStatus = Literal[
    "not_started",
    "in_progress",
    "completed",
    "returned_for_changes",
    "withdrawn",
]
FinalEvaluationStatus = Literal["draft", "ready_for_shortlist", "superseded"]
ReviewCoverageStatus = Literal["complete", "incomplete", "waived"]
CalculationMethod = Literal[
    "model_only_all_agree",
    "model_plus_single_override_average",
    "human_overrides_average",
]


class RecruitmentCase(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "RecruitmentCases"

    entity_type: Literal["RecruitmentCases"] = "RecruitmentCases"
    RowKey: Literal["case"] = "case"
    case_id: str
    case_title: str
    role_title: str
    department: str
    recruitment_type: str
    case_status: CaseStatus
    current_stage: str
    current_gate: str
    hr_owner_actor_id: str
    primary_hiring_manager_actor_id: str
    target_start_date: str | None = None
    posting_period_start: str | None = None
    posting_period_end: str | None = None
    active_intake_version: str | None = None
    active_posting_version: str | None = None
    active_rubric_version: str | None = None
    applicant_set_version: str | None = None
    cancel_reason: str | None = None
    cancelled_at: str | None = None
    cancelled_by_actor_id: str | None = None


class CaseParticipant(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "CaseParticipants"

    entity_type: Literal["CaseParticipants"] = "CaseParticipants"
    case_id: str
    actor_id: str
    display_name: str | None = None
    case_role: CaseRole
    required_for_review: bool = False
    required_for_approval: bool = False
    scope: dict[str, Any] = Field(default_factory=dict)
    status: Literal["active", "inactive", "removed"] = "active"


class CaseTask(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "CaseTasks"
    row_key_prefix: ClassVar[str | None] = "task#"

    entity_type: Literal["CaseTasks"] = "CaseTasks"
    case_id: str
    task_id: str
    task_type: str
    assigned_role: CaseRole
    assigned_actor_id: str | None = None
    candidate_id: str | None = None
    artifact_id: str | None = None
    artifact_version: str | None = None
    status: TaskStatus = "open"
    due_at: str | None = None
    blocking_gate: str | None = None
    completion_event_id: str | None = None


class CaseEvent(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "CaseEvents"

    entity_type: Literal["CaseEvents"] = "CaseEvents"
    case_id: str
    event_id: str
    event_type: str
    actor_id: str
    actor_role: CaseRole
    candidate_id: str | None = None
    artifact_id: str | None = None
    artifact_version: str | None = None
    assessment_id: str | None = None
    review_id: str | None = None
    job_id: str | None = None
    summary: str
    safe_details: dict[str, Any] = Field(default_factory=dict)
    evidence_id: str | None = None


class WorkflowGate(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "WorkflowGates"
    row_key_prefix: ClassVar[str | None] = "gate#"

    entity_type: Literal["WorkflowGates"] = "WorkflowGates"
    case_id: str
    gate_id: str
    gate_status: GateStatus
    required_inputs: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    last_checked_at: str
    satisfied_by_event_id: str | None = None
    waiver_reason: str | None = None
    waived_by_actor_id: str | None = None


class Notification(WorkflowTableEntity):
    table_name: ClassVar[str] = "Notifications"

    entity_type: Literal["Notifications"] = "Notifications"
    notification_id: str
    case_id: str
    candidate_id: str | None = None
    job_id: str | None = None
    assessment_id: str | None = None
    artifact_id: str | None = None
    notification_type: NotificationType
    recipient_actor_id: str
    recipient_role: CaseRole
    title: str
    message: str
    status: NotificationStatus = "unread"
    action_tool: str | None = None
    action_payload: dict[str, Any] = Field(default_factory=dict)
    channel: Literal["copilot_inbox", "teams", "email", "power_automate"] = (
        "copilot_inbox"
    )

    @model_validator(mode="after")
    def _validate_notification_partition(self) -> "Notification":
        case_id = _non_empty(self.case_id, "case_id")
        recipient_actor_id = _non_empty(self.recipient_actor_id, "recipient_actor_id")
        allowed_partitions = {recipient_actor_id, f"case#{case_id}"}
        if self.PartitionKey not in allowed_partitions:
            raise ValueError(
                "Notifications PartitionKey must equal recipient_actor_id "
                "or case#{case_id}"
            )
        return self


class SourceDocument(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "SourceDocuments"
    row_key_prefix: ClassVar[str | None] = "doc#"

    entity_type: Literal["SourceDocuments"] = "SourceDocuments"
    case_id: str
    document_id: str
    candidate_id: str | None = None
    document_type: str
    source_origin: Literal[
        "manual_upload",
        "fixture",
        "adp_export",
        "generated",
        "external_reference",
    ]
    blob_path: str
    normalized_text_blob_path: str | None = None
    mime_type: str | None = None
    file_name: str | None = None
    size_bytes: int | None = None
    sha256: str
    processing_status: SourceDocumentStatus = "registered"
    version: str


class ArtifactVersion(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "ArtifactVersions"
    row_key_prefix: ClassVar[str | None] = "artifact#"

    entity_type: Literal["ArtifactVersions"] = "ArtifactVersions"
    case_id: str
    artifact_id: str
    artifact_type: str
    version: str
    status: ArtifactVersionStatus
    blob_path: str
    source_document_ids: list[str] = Field(default_factory=list)
    sha256: str
    approved_version_required: bool = False


class Approval(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "Approvals"
    row_key_prefix: ClassVar[str | None] = "approval#"

    entity_type: Literal["Approvals"] = "Approvals"
    case_id: str
    approval_id: str
    artifact_id: str
    artifact_type: str
    artifact_version: str
    actor_id: str
    actor_role: CaseRole
    decision: ApprovalDecision
    comments: str | None = None
    decided_at: str
    superseded_by_version: str | None = None


class Applicant(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "Applicants"
    row_key_prefix: ClassVar[str | None] = "candidate#"

    entity_type: Literal["Applicants"] = "Applicants"
    case_id: str
    candidate_id: str
    candidate_ref: str
    display_label: str
    import_status: ApplicantImportStatus
    applicant_set_version: str
    duplicate_group_id: str | None = None
    blocking_findings: list[str] = Field(default_factory=list)


class CandidatePackage(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "CandidatePackages"
    row_key_prefix: ClassVar[str | None] = "package#"

    entity_type: Literal["CandidatePackages"] = "CandidatePackages"
    case_id: str
    candidate_id: str
    package_version: str
    rubric_version: str
    document_ids: list[str] = Field(default_factory=list)
    required_document_status: dict[str, str] = Field(default_factory=dict)
    package_status: CandidatePackageStatus
    blob_path: str
    sha256: str


class ModelAssessmentJob(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "ModelAssessmentJobs"
    row_key_prefix: ClassVar[str | None] = "job#"

    entity_type: Literal["ModelAssessmentJobs"] = "ModelAssessmentJobs"
    case_id: str
    job_id: str
    job_type: Literal[
        "single_candidate_model_assessment",
        "batch_model_assessment",
        "regenerate_stale_assessment",
    ]
    candidate_ids: list[str] = Field(default_factory=list)
    rubric_version: str
    requested_by_actor_id: str
    requested_by_role: CaseRole
    status: ModelAssessmentJobStatus = "queued"
    queued_at: str
    started_at: str | None = None
    completed_at: str | None = None
    total_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    queue_message_id: str | None = None
    retry_count: int = 0
    error_summary: str | None = None


class ModelCandidateAssessment(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "ModelCandidateAssessments"
    row_key_prefix: ClassVar[str | None] = "modelAssessment#"

    entity_type: Literal["ModelCandidateAssessments"] = "ModelCandidateAssessments"
    case_id: str
    assessment_id: str
    evaluation_id: str | None = None
    candidate_id: str
    candidate_ref: str
    package_version: str
    rubric_version: str
    rubric_sha256: str
    assessment_status: ModelAssessmentStatus = "queued"
    recommendation_label: str | None = None
    confidence: str | None = None
    confidence_score: int | None = None
    flags: list[str] = Field(default_factory=list)
    foundry_run_id: str | None = None
    record_blob_path: str
    summary_blob_path: str | None = None
    completed_at: str | None = None
    human_review_required: bool = True


class ModelCriterionRating(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "ModelCriterionRatings"
    row_key_prefix: ClassVar[str | None] = "modelCriterion#"

    entity_type: Literal["ModelCriterionRatings"] = "ModelCriterionRatings"
    case_id: str
    assessment_id: str
    candidate_id: str
    criterion_id: str
    criterion_name: str
    model_score: float
    model_score_normalized_10: float | None = None
    model_rationale: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contrary_evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence_note: str | None = None


class HumanCandidateReview(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "HumanCandidateReviews"
    row_key_prefix: ClassVar[str | None] = "humanReview#"

    entity_type: Literal["HumanCandidateReviews"] = "HumanCandidateReviews"
    case_id: str
    review_id: str
    assessment_id: str
    candidate_id: str
    reviewer_actor_id: str
    reviewer_role: CaseRole
    review_status: HumanReviewStatus = "not_started"
    required_review: bool = True
    started_at: str | None = None
    completed_at: str | None = None
    overall_comment: str | None = None
    follow_up_flags: list[str] = Field(default_factory=list)
    review_blob_path: str | None = None


class HumanCriterionReviewItem(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "HumanCriterionReviewItems"
    row_key_prefix: ClassVar[str | None] = "humanCriterion#"

    entity_type: Literal["HumanCriterionReviewItems"] = "HumanCriterionReviewItems"
    case_id: str
    review_id: str
    assessment_id: str
    candidate_id: str
    criterion_id: str
    model_score_snapshot: float
    model_rationale_snapshot: str
    agree_with_model: bool
    override_score: float | None = None
    override_score_normalized_10: float | None = None
    override_rationale: str | None = None
    agreement_comment: str | None = None
    reviewed_at: str


class FinalCandidateEvaluation(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "FinalCandidateEvaluations"
    row_key_prefix: ClassVar[str | None] = "finalEvaluation#"

    entity_type: Literal["FinalCandidateEvaluations"] = "FinalCandidateEvaluations"
    case_id: str
    final_evaluation_id: str
    candidate_id: str
    assessment_id: str
    source_model_assessment_id: str
    required_review_coverage_status: ReviewCoverageStatus
    final_status: FinalEvaluationStatus = "draft"
    final_overall_score: float | None = None
    score_scale: str = "rubric_native"
    aggregation_policy_version: str
    report_blob_path: str


class FinalCriterionRating(CasePartitionedWorkflowEntity):
    table_name: ClassVar[str] = "FinalCriterionRatings"
    row_key_prefix: ClassVar[str | None] = "finalCriterion#"

    entity_type: Literal["FinalCriterionRatings"] = "FinalCriterionRatings"
    case_id: str
    final_evaluation_id: str
    candidate_id: str
    criterion_id: str
    model_score: float
    human_override_count: int
    human_agreement_count: int
    final_score: float
    calculation_method: CalculationMethod
    calculation_explanation: str
    model_rationale: str
    human_rationales: list[dict[str, Any]] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


WORKFLOW_TABLE_MODELS: tuple[type[WorkflowTableEntity], ...] = (
    RecruitmentCase,
    CaseParticipant,
    CaseTask,
    CaseEvent,
    WorkflowGate,
    Notification,
    SourceDocument,
    ArtifactVersion,
    Approval,
    Applicant,
    CandidatePackage,
    ModelAssessmentJob,
    ModelCandidateAssessment,
    ModelCriterionRating,
    HumanCandidateReview,
    HumanCriterionReviewItem,
    FinalCandidateEvaluation,
    FinalCriterionRating,
)

WORKFLOW_TABLES: tuple[str, ...] = tuple(model.table_name for model in WORKFLOW_TABLE_MODELS)
