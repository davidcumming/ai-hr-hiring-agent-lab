"""Queue message contracts for the E7 workflow foundation.

Messages are async work requests only. They carry identifiers and retry
metadata; they never carry source document text, prompt text, model output, or
secret-bearing connection material.
"""

from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


QueueMessageType = Literal[
    "run-model-candidate-assessment",
    "run-model-assessment-batch",
    "write-notification",
]

NotificationType = Literal[
    "assessment_completed",
    "assessment_failed",
    "review_required",
    "approval_required",
    "gate_blocked",
    "export_ready",
]


FORBIDDEN_QUEUE_CONTENT_MARKERS = (
    "resume_text",
    "cover_letter_text",
    "DefaultEndpointsProtocol=",
    "AccountKey=",
    "SharedAccessSignature=",
    "x-functions-key",
    "tenant_id",
    "subscription_id",
)


def _non_empty(value: str, label: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{label} must not be empty")
    return text


def _reject_forbidden_queue_content(value: Any, label: str) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        for marker in FORBIDDEN_QUEUE_CONTENT_MARKERS:
            if marker.lower() in lowered:
                raise ValueError(
                    f"{label} contains forbidden raw-content or secret marker"
                )
        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_queue_content(item, f"{label}[{index}]")
        return

    if isinstance(value, dict):
        for key, item in value.items():
            _reject_forbidden_queue_content(item, f"{label}.{key}")


class WorkflowQueueMessageBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_type: QueueMessageType
    schema_version: Literal["1.0"] = "1.0"
    case_id: str
    correlation_id: str
    retry_count: int = 0

    @field_validator("case_id", "correlation_id")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        return _non_empty(value, "queue message field")

    @field_validator("retry_count")
    @classmethod
    def _validate_retry_count(cls, value: int) -> int:
        if value < 0:
            raise ValueError("retry_count must be non-negative")
        return value

    @model_validator(mode="after")
    def _validate_identifier_only_payload(self) -> "WorkflowQueueMessageBase":
        for field_name, value in self.model_dump(mode="json").items():
            _reject_forbidden_queue_content(value, field_name)
        return self

    def to_queue_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class RunModelCandidateAssessmentMessage(WorkflowQueueMessageBase):
    message_type: Literal["run-model-candidate-assessment"] = (
        "run-model-candidate-assessment"
    )
    candidate_id: str
    candidate_package_version: str
    rubric_version: str
    job_id: str
    requested_by_actor_id: str
    requested_by_role: str

    @field_validator(
        "candidate_id",
        "candidate_package_version",
        "rubric_version",
        "job_id",
        "requested_by_actor_id",
        "requested_by_role",
    )
    @classmethod
    def _validate_text(cls, value: str) -> str:
        return _non_empty(value, "run-model-candidate-assessment field")


class RunModelAssessmentBatchMessage(WorkflowQueueMessageBase):
    message_type: Literal["run-model-assessment-batch"] = "run-model-assessment-batch"
    candidate_ids: list[str]
    rubric_version: str
    job_id: str
    requested_by_actor_id: str

    @field_validator("candidate_ids")
    @classmethod
    def _validate_candidate_ids(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("candidate_ids must not be empty")
        return [_non_empty(candidate_id, "candidate_id") for candidate_id in value]

    @field_validator("rubric_version", "job_id", "requested_by_actor_id")
    @classmethod
    def _validate_text(cls, value: str) -> str:
        return _non_empty(value, "run-model-assessment-batch field")


class WriteNotificationMessage(WorkflowQueueMessageBase):
    message_type: Literal["write-notification"] = "write-notification"
    recipient_actor_ids: list[str]
    notification_type: NotificationType
    source_job_id: str
    candidate_id: str | None = None
    assessment_id: str | None = None

    @field_validator("recipient_actor_ids")
    @classmethod
    def _validate_recipients(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("recipient_actor_ids must not be empty")
        return [_non_empty(actor_id, "recipient_actor_id") for actor_id in value]

    @field_validator("source_job_id")
    @classmethod
    def _validate_source_job(cls, value: str) -> str:
        return _non_empty(value, "source_job_id")

    @field_validator("candidate_id", "assessment_id")
    @classmethod
    def _validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _non_empty(value, "optional queue message field")


WorkflowQueueMessage = Union[
    RunModelCandidateAssessmentMessage,
    RunModelAssessmentBatchMessage,
    WriteNotificationMessage,
]

QUEUE_MESSAGE_MODELS: dict[str, type[WorkflowQueueMessageBase]] = {
    "run-model-candidate-assessment": RunModelCandidateAssessmentMessage,
    "run-model-assessment-batch": RunModelAssessmentBatchMessage,
    "write-notification": WriteNotificationMessage,
}


def validate_queue_message(payload: dict[str, Any]) -> WorkflowQueueMessageBase:
    message_type = payload.get("message_type")
    model = QUEUE_MESSAGE_MODELS.get(str(message_type))
    if model is None:
        raise ValueError(f"unknown queue message_type: {message_type!r}")
    return model.model_validate(payload)
