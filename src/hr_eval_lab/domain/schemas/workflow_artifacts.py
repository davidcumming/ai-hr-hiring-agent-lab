"""Blob path contracts for the HR Hiring MVP workflow foundation.

E7 defines the canonical Azure-shaped artifact paths, but keeps all execution
local and deterministic. The helpers return repo-safe relative paths that can
be used unchanged by the local adapter or a future Blob-backed adapter.
"""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict


class InvalidWorkflowPathError(ValueError):
    """Raised when a workflow artifact id would create an unsafe Blob path."""


def _safe_segment(value: str, label: str) -> str:
    segment = value.strip()
    if not segment:
        raise InvalidWorkflowPathError(f"{label} must not be empty")
    if segment.startswith(("/", "\\")):
        raise InvalidWorkflowPathError(f"{label} must not start with a slash")
    if any(marker in segment for marker in ("..", "/", "\\", "?", "#")):
        raise InvalidWorkflowPathError(f"{label} contains an unsafe path marker")
    return segment


def validate_blob_path(path: str) -> str:
    """Validate an already-built workflow Blob path."""

    blob_path = path.strip()
    if not blob_path:
        raise InvalidWorkflowPathError("blob path must not be empty")
    if blob_path.startswith(("/", "\\")):
        raise InvalidWorkflowPathError("blob path must be relative")
    if "\\" in blob_path or "?" in blob_path or "#" in blob_path:
        raise InvalidWorkflowPathError("blob path contains an unsafe marker")
    parts = PurePosixPath(blob_path).parts
    if any(part in ("", ".", "..") for part in parts):
        raise InvalidWorkflowPathError("blob path contains traversal")
    if blob_path != PurePosixPath(*parts).as_posix():
        raise InvalidWorkflowPathError("blob path is not normalized")
    if parts[0] not in {"case-documents", "case-artifacts", "evaluations"}:
        raise InvalidWorkflowPathError("blob path uses an unknown container prefix")
    return blob_path


def _join(*segments: str) -> str:
    return validate_blob_path(PurePosixPath(*segments).as_posix())


def role_source_raw_path(case_id: str, document_id: str) -> str:
    return _join(
        "case-documents",
        "cases",
        _safe_segment(case_id, "case_id"),
        "role-source",
        _safe_segment(document_id, "document_id"),
        "raw",
    )


def candidate_document_raw_path(
    case_id: str, candidate_id: str, document_id: str
) -> str:
    return _join(
        "case-documents",
        "cases",
        _safe_segment(case_id, "case_id"),
        "candidates",
        _safe_segment(candidate_id, "candidate_id"),
        _safe_segment(document_id, "document_id"),
        "raw",
    )


def rubric_artifact_path(case_id: str, version: str) -> str:
    return _join(
        "case-artifacts",
        "cases",
        _safe_segment(case_id, "case_id"),
        "rubric",
        _safe_segment(version, "version"),
        "rubric.json",
    )


def role_intake_artifact_path(case_id: str, version: str) -> str:
    return _join(
        "case-artifacts",
        "cases",
        _safe_segment(case_id, "case_id"),
        "intake",
        _safe_segment(version, "version"),
        "intake.json",
    )


def candidate_package_path(case_id: str, candidate_id: str, version: str) -> str:
    return _join(
        "case-artifacts",
        "cases",
        _safe_segment(case_id, "case_id"),
        "candidate-packages",
        _safe_segment(candidate_id, "candidate_id"),
        _safe_segment(version, "version"),
        "package.json",
    )


def model_assessment_record_path(
    case_id: str, candidate_id: str, assessment_id: str
) -> str:
    return _join(
        "evaluations",
        "cases",
        _safe_segment(case_id, "case_id"),
        "candidates",
        _safe_segment(candidate_id, "candidate_id"),
        "model-assessments",
        _safe_segment(assessment_id, "assessment_id"),
        "record.json",
    )


def human_review_path(case_id: str, candidate_id: str, review_id: str) -> str:
    return _join(
        "evaluations",
        "cases",
        _safe_segment(case_id, "case_id"),
        "candidates",
        _safe_segment(candidate_id, "candidate_id"),
        "human-reviews",
        _safe_segment(review_id, "review_id"),
        "review.json",
    )


def final_evaluation_report_path(
    case_id: str, candidate_id: str, final_evaluation_id: str
) -> str:
    return _join(
        "evaluations",
        "cases",
        _safe_segment(case_id, "case_id"),
        "candidates",
        _safe_segment(candidate_id, "candidate_id"),
        "final-evaluations",
        _safe_segment(final_evaluation_id, "final_evaluation_id"),
        "report.json",
    )


WorkflowBlobContainer = Literal["case-documents", "case-artifacts", "evaluations"]


class WorkflowBlobArtifactRef(BaseModel):
    """Metadata-only reference to a workflow Blob artifact."""

    model_config = ConfigDict(extra="forbid")

    container: WorkflowBlobContainer
    blob_path: str
    sha256: str
    size_bytes: int
    synthetic: bool = True

    @classmethod
    def from_bytes(cls, blob_path: str, raw: bytes) -> "WorkflowBlobArtifactRef":
        safe_path = validate_blob_path(blob_path)
        container = safe_path.split("/", 1)[0]
        return cls(
            container=container,  # type: ignore[arg-type]
            blob_path=safe_path,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
        )
