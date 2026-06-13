"""E8 local workflow storage protocol behaviour."""

from __future__ import annotations

from hr_eval_lab.domain.schemas.workflow import CandidatePackage
from hr_eval_lab.domain.schemas.workflow_artifacts import candidate_package_path
from hr_eval_lab.domain.schemas.workflow_queue import RunModelCandidateAssessmentMessage
from hr_eval_lab.persistence.workflow_storage import (
    WorkflowBlobStore,
    WorkflowQueueStore,
    WorkflowStorageBackend,
    WorkflowTableStore,
)
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore


def _candidate_package(status: str = "complete") -> CandidatePackage:
    return CandidatePackage(
        PartitionKey="case-e8-001",
        RowKey="package#cand-e8-001#v1",
        created_at="2026-06-13T00:00:00Z",
        correlation_id="corr-e8-001",
        case_id="case-e8-001",
        candidate_id="cand-e8-001",
        package_version="v1",
        rubric_version="v1",
        document_ids=["doc-e8-001"],
        required_document_status={"resume": "present"},
        package_status=status,  # type: ignore[arg-type]
        blob_path=candidate_package_path("case-e8-001", "cand-e8-001", "v1"),
        sha256="8" * 64,
    )


def _message() -> RunModelCandidateAssessmentMessage:
    return RunModelCandidateAssessmentMessage(
        case_id="case-e8-001",
        candidate_id="cand-e8-001",
        candidate_package_version="v1",
        rubric_version="v1",
        job_id="job-e8-001",
        requested_by_actor_id="actor-hr",
        requested_by_role="hr_specialist",
        correlation_id="corr-e8-001",
    )


def test_e8_local_workflow_store_satisfies_protocols(tmp_path):
    store = LocalWorkflowStore(tmp_path)

    assert isinstance(store, WorkflowTableStore)
    assert isinstance(store, WorkflowBlobStore)
    assert isinstance(store, WorkflowQueueStore)
    assert isinstance(store, WorkflowStorageBackend)


def test_e8_local_upsert_get_list_and_delete_table_entity(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    package = _candidate_package()
    changed = _candidate_package(status="stale")

    first = store.upsert_table_entity(package)
    second = store.upsert_table_entity(changed)

    assert first["document_ids"] == '["doc-e8-001"]'
    assert second["package_status"] == "stale"
    rows = store.list_table_rows("CandidatePackages", partition_key="case-e8-001")
    assert len(rows) == 1
    restored = store.get_table_entity(
        CandidatePackage, "case-e8-001", "package#cand-e8-001#v1"
    )
    assert isinstance(restored, CandidatePackage)
    assert restored.package_status == "stale"

    assert store.delete_table_entity(
        CandidatePackage, "case-e8-001", "package#cand-e8-001#v1"
    )
    assert (
        store.get_table_entity(
            CandidatePackage, "case-e8-001", "package#cand-e8-001#v1"
        )
        is None
    )


def test_e8_local_blob_delete_and_queue_receive_delete(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    blob_path = candidate_package_path("case-e8-001", "cand-e8-001", "v1")

    ref = store.write_blob_artifact(blob_path, {"candidate_id": "cand-e8-001"})
    assert ref.blob_path == blob_path
    assert store.read_blob_json(blob_path) == {"candidate_id": "cand-e8-001"}
    assert store.delete_blob_artifact(blob_path)
    assert store.read_blob_bytes(blob_path) is None

    sent = store.enqueue_message(_message())
    peeked = store.peek_queue_messages(max_messages=1)
    received = store.receive_queue_messages(max_messages=1)

    assert sent["message_id"].startswith("msg-")
    assert peeked[0]["payload"]["message_type"] == "run-model-candidate-assessment"
    assert received[0].pop_receipt is not None
    assert received[0].payload["job_id"] == "job-e8-001"
    assert store.delete_queue_message(received[0])
    assert store.peek_queue_messages() == []


def test_e8_local_queue_delete_uses_received_queue_name(tmp_path):
    store = LocalWorkflowStore(tmp_path)

    store.enqueue_message(_message(), queue_name="workflow-jobs-custom")
    received = store.receive_queue_messages(queue_name="workflow-jobs-custom")

    assert store.delete_queue_message(received[0])
    assert store.peek_queue_messages(queue_name="workflow-jobs-custom") == []
