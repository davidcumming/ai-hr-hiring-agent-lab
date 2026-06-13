"""E7 Azure Queue-shaped message contracts."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from hr_eval_lab.domain.schemas.workflow_queue import (
    RunModelAssessmentBatchMessage,
    RunModelCandidateAssessmentMessage,
    WriteNotificationMessage,
    validate_queue_message,
)


FORBIDDEN_QUEUE_MARKERS = (
    "resume_text",
    "cover_letter_text",
    "DefaultEndpointsProtocol=",
    "AccountKey=",
    "SharedAccessSignature=",
    "x-functions-key",
    "tenant_id",
    "subscription_id",
)


def test_e7_run_model_candidate_assessment_message_contract():
    message = RunModelCandidateAssessmentMessage(
        case_id="case-001",
        candidate_id="cand-001",
        candidate_package_version="v1",
        rubric_version="v1",
        job_id="job-001",
        requested_by_actor_id="actor-hr",
        requested_by_role="hr_specialist",
        correlation_id="corr-001",
    )

    assert message.to_queue_payload() == {
        "message_type": "run-model-candidate-assessment",
        "schema_version": "1.0",
        "case_id": "case-001",
        "candidate_id": "cand-001",
        "candidate_package_version": "v1",
        "rubric_version": "v1",
        "job_id": "job-001",
        "requested_by_actor_id": "actor-hr",
        "requested_by_role": "hr_specialist",
        "correlation_id": "corr-001",
        "retry_count": 0,
    }


def test_e7_batch_and_notification_messages_validate_by_message_type():
    batch = validate_queue_message(
        {
            "message_type": "run-model-assessment-batch",
            "schema_version": "1.0",
            "case_id": "case-001",
            "candidate_ids": ["cand-001", "cand-002"],
            "rubric_version": "v1",
            "job_id": "job-002",
            "requested_by_actor_id": "actor-hr",
            "correlation_id": "corr-002",
            "retry_count": 1,
        }
    )
    assert isinstance(batch, RunModelAssessmentBatchMessage)
    assert batch.retry_count == 1

    notification = validate_queue_message(
        {
            "message_type": "write-notification",
            "schema_version": "1.0",
            "case_id": "case-001",
            "recipient_actor_ids": ["actor-hr", "actor-hm"],
            "notification_type": "assessment_completed",
            "source_job_id": "job-002",
            "candidate_id": "cand-001",
            "assessment_id": "ma-001",
            "correlation_id": "corr-003",
        }
    )
    assert isinstance(notification, WriteNotificationMessage)
    assert notification.retry_count == 0


def test_e7_queue_messages_forbid_extra_raw_content_and_bad_retry_count():
    with pytest.raises(ValidationError):
        RunModelCandidateAssessmentMessage(
            case_id="case-001",
            candidate_id="cand-001",
            candidate_package_version="v1",
            rubric_version="v1",
            job_id="job-001",
            requested_by_actor_id="actor-hr",
            requested_by_role="hr_specialist",
            correlation_id="corr-001",
            retry_count=-1,
        )

    with pytest.raises(ValidationError):
        RunModelCandidateAssessmentMessage(
            case_id="case-001",
            candidate_id="cand-001",
            candidate_package_version="v1",
            rubric_version="v1",
            job_id="job-001",
            requested_by_actor_id="actor-hr",
            requested_by_role="hr_specialist",
            correlation_id="corr-001",
            resume_text="raw candidate text must not be queued",
        )

    with pytest.raises(ValueError):
        validate_queue_message({"message_type": "unknown", "case_id": "case-001"})


def _candidate_assessment_payload():
    return {
        "case_id": "case-001",
        "candidate_id": "cand-001",
        "candidate_package_version": "v1",
        "rubric_version": "v1",
        "job_id": "job-001",
        "requested_by_actor_id": "actor-hr",
        "requested_by_role": "hr_specialist",
        "correlation_id": "corr-001",
    }


@pytest.mark.parametrize(
    ("field_name", "marker"),
    [
        ("case_id", "resume_text"),
        ("correlation_id", "cover_letter_text"),
        ("candidate_id", "DefaultEndpointsProtocol="),
        ("requested_by_actor_id", "AccountKey="),
        ("job_id", "SharedAccessSignature="),
        ("candidate_package_version", "x-functions-key"),
        ("rubric_version", "tenant_id"),
        ("requested_by_role", "subscription_id"),
    ],
)
def test_e7_queue_messages_reject_forbidden_markers_in_allowed_string_fields(
    field_name, marker
):
    payload = _candidate_assessment_payload()
    payload[field_name] = f"synthetic-{marker}-marker"

    with pytest.raises(ValidationError, match="forbidden raw-content"):
        RunModelCandidateAssessmentMessage(**payload)


@pytest.mark.parametrize(
    ("payload", "field_name", "marker"),
    [
        (
            {
                "case_id": "case-001",
                "candidate_ids": ["cand-001"],
                "rubric_version": "v1",
                "job_id": "job-002",
                "requested_by_actor_id": "actor-hr",
                "correlation_id": "corr-002",
            },
            "candidate_ids",
            "tenant_id",
        ),
        (
            {
                "case_id": "case-001",
                "recipient_actor_ids": ["actor-hr"],
                "notification_type": "assessment_completed",
                "source_job_id": "job-001",
                "correlation_id": "corr-003",
            },
            "recipient_actor_ids",
            "x-functions-key",
        ),
    ],
)
def test_e7_queue_messages_reject_forbidden_markers_in_allowed_list_fields(
    payload, field_name, marker
):
    payload[field_name] = [f"synthetic-{marker}-marker"]
    message_type = (
        RunModelAssessmentBatchMessage
        if field_name == "candidate_ids"
        else WriteNotificationMessage
    )

    with pytest.raises(ValidationError, match="forbidden raw-content"):
        message_type(**payload)


def test_e7_queue_payloads_are_identifier_only_and_secret_free():
    payloads = [
        RunModelCandidateAssessmentMessage(
            case_id="case-001",
            candidate_id="cand-001",
            candidate_package_version="v1",
            rubric_version="v1",
            job_id="job-001",
            requested_by_actor_id="actor-hr",
            requested_by_role="hr_specialist",
            correlation_id="corr-001",
        ).to_queue_payload(),
        RunModelAssessmentBatchMessage(
            case_id="case-001",
            candidate_ids=["cand-001"],
            rubric_version="v1",
            job_id="job-002",
            requested_by_actor_id="actor-hr",
            correlation_id="corr-002",
        ).to_queue_payload(),
        WriteNotificationMessage(
            case_id="case-001",
            recipient_actor_ids=["actor-hr"],
            notification_type="assessment_completed",
            source_job_id="job-001",
            correlation_id="corr-003",
        ).to_queue_payload(),
    ]

    raw = json.dumps(payloads, sort_keys=True)
    for marker in FORBIDDEN_QUEUE_MARKERS:
        assert marker not in raw
