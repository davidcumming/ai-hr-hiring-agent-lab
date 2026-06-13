"""E7 workflow Table schemas: Azure-shaped, local deterministic contracts."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from hr_eval_lab.domain.schemas.workflow import (
    WORKFLOW_TABLES,
    Applicant,
    Approval,
    ArtifactVersion,
    CandidatePackage,
    CaseEvent,
    CaseParticipant,
    CaseTask,
    FinalCandidateEvaluation,
    FinalCriterionRating,
    HumanCandidateReview,
    HumanCriterionReviewItem,
    ModelAssessmentJob,
    ModelCandidateAssessment,
    ModelCriterionRating,
    Notification,
    RecruitmentCase,
    SourceDocument,
    WorkflowGate,
)

TS = "2026-06-13T00:00:00Z"
CASE_ID = "case-e7-001"
CORR = "corr-e7-001"


def common(row_key: str, partition_key: str = CASE_ID):
    return {
        "PartitionKey": partition_key,
        "RowKey": row_key,
        "created_at": TS,
        "correlation_id": CORR,
        "created_by_actor_id": "actor-hr",
        "created_by_role": "hr_specialist",
    }


def sample_entities():
    return [
        RecruitmentCase(
            **common("case"),
            case_id=CASE_ID,
            case_title="Synthetic E7 hiring case",
            role_title="Analyst",
            department="Synthetic Lab",
            recruitment_type="permanent",
            case_status="intake_pending",
            current_stage="case_intake",
            current_gate="role_source_required",
            hr_owner_actor_id="actor-hr",
            primary_hiring_manager_actor_id="actor-hm",
        ),
        CaseParticipant(
            **common("hr_specialist#actor-hr"),
            case_id=CASE_ID,
            actor_id="actor-hr",
            case_role="hr_specialist",
            scope={"case": CASE_ID},
        ),
        CaseTask(
            **common("task#task-001"),
            case_id=CASE_ID,
            task_id="task-001",
            task_type="complete_intake",
            assigned_role="hr_specialist",
        ),
        CaseEvent(
            **common(f"{TS}#event-001"),
            case_id=CASE_ID,
            event_id="event-001",
            event_type="case_created",
            actor_id="actor-hr",
            actor_role="hr_specialist",
            summary="Synthetic case created.",
            safe_details={"source": "test"},
        ),
        WorkflowGate(
            **common("gate#rubric_approved"),
            case_id=CASE_ID,
            gate_id="rubric_approved",
            gate_status="locked",
            required_inputs=["active_rubric_version"],
            blocking_reasons=["Rubric is not approved."],
            last_checked_at=TS,
        ),
        Notification(
            **common(f"{TS}#notif-001", partition_key="actor-hr"),
            notification_id="notif-001",
            case_id=CASE_ID,
            notification_type="assessment_completed",
            recipient_actor_id="actor-hr",
            recipient_role="hr_specialist",
            title="Assessment complete",
            message="Synthetic assessment is ready for review.",
            action_payload={"case_id": CASE_ID},
        ),
        SourceDocument(
            **common("doc#doc-role-001"),
            case_id=CASE_ID,
            document_id="doc-role-001",
            document_type="job_description",
            source_origin="fixture",
            blob_path="case-documents/cases/case-e7-001/role-source/doc-role-001/raw",
            sha256="0" * 64,
            version="v1",
        ),
        ArtifactVersion(
            **common("artifact#screening_rubric#rubric-001#v1"),
            case_id=CASE_ID,
            artifact_id="rubric-001",
            artifact_type="screening_rubric",
            version="v1",
            status="approved",
            blob_path="case-artifacts/cases/case-e7-001/rubric/v1/rubric.json",
            source_document_ids=["doc-role-001"],
            sha256="1" * 64,
            approved_version_required=True,
        ),
        Approval(
            **common("approval#rubric-001#v1#hiring_manager#actor-hm"),
            case_id=CASE_ID,
            approval_id="approval-001",
            artifact_id="rubric-001",
            artifact_type="screening_rubric",
            artifact_version="v1",
            actor_id="actor-hm",
            actor_role="hiring_manager",
            decision="approved",
            decided_at=TS,
        ),
        Applicant(
            **common("candidate#cand-001"),
            case_id=CASE_ID,
            candidate_id="cand-001",
            candidate_ref="cand-synthetic-001",
            display_label="Synthetic candidate 001",
            import_status="confirmed",
            applicant_set_version="v1",
            blocking_findings=[],
        ),
        CandidatePackage(
            **common("package#cand-001#v1"),
            case_id=CASE_ID,
            candidate_id="cand-001",
            package_version="v1",
            rubric_version="v1",
            document_ids=["doc-cand-001"],
            required_document_status={"resume": "present"},
            package_status="complete",
            blob_path="case-artifacts/cases/case-e7-001/candidate-packages/cand-001/v1/package.json",
            sha256="2" * 64,
        ),
        ModelAssessmentJob(
            **common("job#job-001"),
            case_id=CASE_ID,
            job_id="job-001",
            job_type="single_candidate_model_assessment",
            candidate_ids=["cand-001"],
            rubric_version="v1",
            requested_by_actor_id="actor-hr",
            requested_by_role="hr_specialist",
            queued_at=TS,
            total_count=1,
        ),
        ModelCandidateAssessment(
            **common("modelAssessment#cand-001#ma-001"),
            case_id=CASE_ID,
            assessment_id="ma-001",
            evaluation_id="eval-synthetic-001",
            candidate_id="cand-001",
            candidate_ref="cand-synthetic-001",
            package_version="v1",
            rubric_version="v1",
            rubric_sha256="3" * 64,
            record_blob_path="evaluations/cases/case-e7-001/candidates/cand-001/model-assessments/ma-001/record.json",
        ),
        ModelCriterionRating(
            **common("modelCriterion#ma-001#crit-001"),
            case_id=CASE_ID,
            assessment_id="ma-001",
            candidate_id="cand-001",
            criterion_id="crit-001",
            criterion_name="Synthetic criterion",
            model_score=7.0,
            model_rationale="Synthetic summary rationale.",
            supporting_evidence_ids=["ev-001"],
        ),
        HumanCandidateReview(
            **common("humanReview#cand-001#ma-001#hiring_manager#actor-hm"),
            case_id=CASE_ID,
            review_id="hrv-001",
            assessment_id="ma-001",
            candidate_id="cand-001",
            reviewer_actor_id="actor-hm",
            reviewer_role="hiring_manager",
        ),
        HumanCriterionReviewItem(
            **common("humanCriterion#hrv-001#crit-001"),
            case_id=CASE_ID,
            review_id="hrv-001",
            assessment_id="ma-001",
            candidate_id="cand-001",
            criterion_id="crit-001",
            model_score_snapshot=7.0,
            model_rationale_snapshot="Synthetic snapshot rationale.",
            agree_with_model=True,
            reviewed_at=TS,
        ),
        FinalCandidateEvaluation(
            **common("finalEvaluation#cand-001#final-001"),
            case_id=CASE_ID,
            final_evaluation_id="final-001",
            candidate_id="cand-001",
            assessment_id="ma-001",
            source_model_assessment_id="ma-001",
            required_review_coverage_status="complete",
            aggregation_policy_version="final-rating-aggregation-v1",
            report_blob_path="evaluations/cases/case-e7-001/candidates/cand-001/final-evaluations/final-001/report.json",
        ),
        FinalCriterionRating(
            **common("finalCriterion#final-001#crit-001"),
            case_id=CASE_ID,
            final_evaluation_id="final-001",
            candidate_id="cand-001",
            criterion_id="crit-001",
            model_score=7.0,
            human_override_count=0,
            human_agreement_count=1,
            final_score=7.0,
            calculation_method="model_only_all_agree",
            calculation_explanation="All required reviewers agreed with the model.",
            model_rationale="Synthetic model rationale.",
            human_rationales=[{"review_id": "hrv-001", "comment": "Agreed."}],
            evidence_refs=["ev-001"],
        ),
    ]


def test_e7_all_expected_table_names_are_declared():
    assert WORKFLOW_TABLES == (
        "RecruitmentCases",
        "CaseParticipants",
        "CaseTasks",
        "CaseEvents",
        "WorkflowGates",
        "Notifications",
        "SourceDocuments",
        "ArtifactVersions",
        "Approvals",
        "Applicants",
        "CandidatePackages",
        "ModelAssessmentJobs",
        "ModelCandidateAssessments",
        "ModelCriterionRatings",
        "HumanCandidateReviews",
        "HumanCriterionReviewItems",
        "FinalCandidateEvaluations",
        "FinalCriterionRatings",
    )


def test_e7_workflow_entities_have_table_keys_type_marker_and_schema_version():
    for entity in sample_entities():
        row = entity.to_table_entity()
        assert row["PartitionKey"]
        assert row["RowKey"]
        assert row["entity_type"] == entity.table_name
        assert row["schema_version"] == "1.0"
        assert row["synthetic"] is True
        assert row["correlation_id"] == CORR


def test_e7_table_json_properties_serialize_as_canonical_strings():
    package = next(e for e in sample_entities() if isinstance(e, CandidatePackage))
    row = package.to_table_entity()

    assert row["document_ids"] == '["doc-cand-001"]'
    assert row["required_document_status"] == '{"resume":"present"}'

    restored = CandidatePackage.from_table_entity(row)
    assert restored.document_ids == ["doc-cand-001"]
    assert restored.required_document_status == {"resume": "present"}


def test_e7_table_schemas_forbid_extra_fields_and_invalid_status_values():
    with pytest.raises(ValidationError):
        RecruitmentCase(
            **common("case"),
            case_id=CASE_ID,
            case_title="Synthetic E7 hiring case",
            role_title="Analyst",
            department="Synthetic Lab",
            recruitment_type="permanent",
            case_status="not_a_status",
            current_stage="case_intake",
            current_gate="role_source_required",
            hr_owner_actor_id="actor-hr",
            primary_hiring_manager_actor_id="actor-hm",
        )

    with pytest.raises(ValidationError):
        CaseParticipant(
            **common("hr_specialist#actor-hr"),
            case_id=CASE_ID,
            actor_id="actor-hr",
            case_role="hr_specialist",
            unexpected="not allowed",
        )


def test_e7_recruitment_case_partition_key_is_case_id():
    with pytest.raises(ValidationError):
        RecruitmentCase(
            **common("case", partition_key="wrong-case"),
            case_id=CASE_ID,
            case_title="Synthetic E7 hiring case",
            role_title="Analyst",
            department="Synthetic Lab",
            recruitment_type="permanent",
            case_status="intake_pending",
            current_stage="case_intake",
            current_gate="role_source_required",
            hr_owner_actor_id="actor-hr",
            primary_hiring_manager_actor_id="actor-hm",
        )


def test_e7_case_partitioned_entities_require_partition_key_to_equal_case_id():
    for entity in sample_entities():
        if isinstance(entity, Notification):
            continue

        payload = entity.model_dump(mode="json")
        payload["PartitionKey"] = "wrong-case"

        with pytest.raises(ValidationError, match="PartitionKey"):
            type(entity).model_validate(payload)


def test_e7_notification_supports_actor_inbox_and_case_inbox_partitions():
    notification = next(e for e in sample_entities() if isinstance(e, Notification))
    payload = notification.model_dump(mode="json")

    actor_partition = Notification.model_validate(
        {**payload, "PartitionKey": "actor-hr"}
    )
    case_partition = Notification.model_validate(
        {**payload, "PartitionKey": f"case#{CASE_ID}"}
    )

    assert actor_partition.PartitionKey == "actor-hr"
    assert case_partition.PartitionKey == f"case#{CASE_ID}"

    with pytest.raises(ValidationError, match="Notifications PartitionKey"):
        Notification.model_validate({**payload, "PartitionKey": CASE_ID})


@pytest.mark.parametrize(
    ("model_type", "required_prefix"),
    [
        (CaseTask, "task#"),
        (WorkflowGate, "gate#"),
        (SourceDocument, "doc#"),
        (ArtifactVersion, "artifact#"),
        (Approval, "approval#"),
        (Applicant, "candidate#"),
        (CandidatePackage, "package#"),
        (ModelAssessmentJob, "job#"),
        (ModelCandidateAssessment, "modelAssessment#"),
        (ModelCriterionRating, "modelCriterion#"),
        (HumanCandidateReview, "humanReview#"),
        (HumanCriterionReviewItem, "humanCriterion#"),
        (FinalCandidateEvaluation, "finalEvaluation#"),
        (FinalCriterionRating, "finalCriterion#"),
    ],
)
def test_e7_critical_table_entities_require_row_key_prefix(
    model_type, required_prefix
):
    entity = next(e for e in sample_entities() if isinstance(e, model_type))
    payload = entity.model_dump(mode="json")
    payload["RowKey"] = f"wrong#{required_prefix.rstrip('#')}"

    with pytest.raises(ValidationError, match="RowKey"):
        model_type.model_validate(payload)


def test_e7_table_rows_do_not_need_non_table_json_types():
    for entity in sample_entities():
        row = entity.to_table_entity()
        json.dumps(row)
        for value in row.values():
            assert not isinstance(value, (list, dict))
