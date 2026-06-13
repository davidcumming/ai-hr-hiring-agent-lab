"""E7 deterministic local workflow store adapter."""

from __future__ import annotations

from hr_eval_lab.domain.schemas.workflow import CandidatePackage
from hr_eval_lab.domain.schemas.workflow_artifacts import candidate_package_path
from hr_eval_lab.domain.schemas.workflow_queue import RunModelCandidateAssessmentMessage
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore


def _candidate_package() -> CandidatePackage:
    return CandidatePackage(
        PartitionKey="case-001",
        RowKey="package#cand-001#v1",
        created_at="2026-06-13T00:00:00Z",
        correlation_id="corr-001",
        case_id="case-001",
        candidate_id="cand-001",
        package_version="v1",
        rubric_version="v1",
        document_ids=["doc-001"],
        required_document_status={"resume": "present"},
        package_status="complete",
        blob_path=candidate_package_path("case-001", "cand-001", "v1"),
        sha256="0" * 64,
    )


def test_e7_local_workflow_store_round_trips_table_entities(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    package = _candidate_package()

    row = store.write_table_entity(package)

    assert row["document_ids"] == '["doc-001"]'
    rows = store.list_table_rows("CandidatePackages", partition_key="case-001")
    assert len(rows) == 1
    restored = store.get_table_entity(
        CandidatePackage, "case-001", "package#cand-001#v1"
    )
    assert isinstance(restored, CandidatePackage)
    assert restored.required_document_status == {"resume": "present"}


def test_e7_local_workflow_store_writes_blob_artifacts_with_hashes(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    path = candidate_package_path("case-001", "cand-001", "v1")

    ref = store.write_blob_artifact(path, {"candidate_id": "cand-001", "version": "v1"})

    assert ref.container == "case-artifacts"
    assert ref.blob_path == path
    assert len(ref.sha256) == 64
    assert ref.size_bytes > 0
    assert store.read_blob_json(path) == {"candidate_id": "cand-001", "version": "v1"}


def test_e7_local_workflow_store_appends_queue_messages_deterministically(tmp_path):
    store = LocalWorkflowStore(tmp_path)
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

    first = store.enqueue_message(message)
    second = store.enqueue_message(message.to_queue_payload())

    assert first["message_id"].startswith("msg-")
    assert first["sequence"] == 0
    assert second["sequence"] == 1
    assert first["payload"]["message_type"] == "run-model-candidate-assessment"
    assert [row["sequence"] for row in store.list_queue_messages()] == [0, 1]
