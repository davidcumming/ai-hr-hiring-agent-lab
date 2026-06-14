"""E7 canonical workflow Blob path contracts."""

from __future__ import annotations

import pytest

from hr_eval_lab.domain.schemas.workflow_artifacts import (
    InvalidWorkflowPathError,
    candidate_document_raw_path,
    candidate_package_path,
    final_evaluation_report_path,
    human_review_path,
    model_assessment_record_path,
    role_intake_artifact_path,
    role_source_raw_path,
    rubric_artifact_path,
    validate_blob_path,
)


def test_e7_blob_path_builders_return_exact_contract_paths():
    assert (
        role_source_raw_path("case-001", "doc-role-001")
        == "case-documents/cases/case-001/role-source/doc-role-001/raw"
    )
    assert (
        candidate_document_raw_path("case-001", "cand-001", "doc-resume-001")
        == "case-documents/cases/case-001/candidates/cand-001/doc-resume-001/raw"
    )
    assert (
        rubric_artifact_path("case-001", "v1")
        == "case-artifacts/cases/case-001/rubric/v1/rubric.json"
    )
    assert (
        role_intake_artifact_path("case-001", "v1")
        == "case-artifacts/cases/case-001/intake/v1/intake.json"
    )
    assert (
        candidate_package_path("case-001", "cand-001", "v1")
        == "case-artifacts/cases/case-001/candidate-packages/cand-001/v1/package.json"
    )
    assert (
        model_assessment_record_path("case-001", "cand-001", "ma-001")
        == "evaluations/cases/case-001/candidates/cand-001/model-assessments/ma-001/record.json"
    )
    assert (
        human_review_path("case-001", "cand-001", "hrv-001")
        == "evaluations/cases/case-001/candidates/cand-001/human-reviews/hrv-001/review.json"
    )
    assert (
        final_evaluation_report_path("case-001", "cand-001", "final-001")
        == "evaluations/cases/case-001/candidates/cand-001/final-evaluations/final-001/report.json"
    )


@pytest.mark.parametrize(
    "bad_segment",
    ["", "   ", "/case-001", "case/001", "case\\001", "../case-001", "case?x=1", "case#frag"],
)
def test_e7_blob_path_builders_reject_unsafe_segments(bad_segment):
    with pytest.raises(InvalidWorkflowPathError):
        role_source_raw_path(bad_segment, "doc-001")


@pytest.mark.parametrize(
    "bad_path",
    [
        "",
        "/case-documents/cases/case-001/role-source/doc-001/raw",
        "case-documents//cases/case-001/role-source/doc-001/raw",
        "case-documents/cases/./case-001/role-source/doc-001/raw",
        "case-documents/cases/case-001/../doc-001/raw",
        "case-documents\\cases\\case-001",
        "case-documents/cases/case-001?sig=secret",
        "unknown/cases/case-001/doc",
    ],
)
def test_e7_validate_blob_path_rejects_traversal_and_unknown_containers(bad_path):
    with pytest.raises(InvalidWorkflowPathError):
        validate_blob_path(bad_path)
