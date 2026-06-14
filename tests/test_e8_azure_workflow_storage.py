"""E8 guarded Azure workflow storage adapter with fake clients."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from hr_eval_lab.config import AzureStorageConfig, WorkflowStorageConfig
from hr_eval_lab.domain.schemas.workflow import CandidatePackage, CaseParticipant
from hr_eval_lab.domain.schemas.workflow_artifacts import candidate_package_path
from hr_eval_lab.domain.schemas.workflow_queue import RunModelCandidateAssessmentMessage
from hr_eval_lab.persistence.azure_workflow_storage import AzureWorkflowStorageBackend
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore
from hr_eval_lab.persistence.workflow_storage import WorkflowStorageNotConfiguredError
from tests.fake_blob import FakeBlobContainerClient, ResourceNotFoundError


class FakeTableClient:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], dict] = {}
        self.upsert_modes: list[object] = []

    def upsert_entity(self, entity: dict, mode: object) -> dict:
        self.upsert_modes.append(mode)
        key = (entity["PartitionKey"], entity["RowKey"])
        self.rows[key] = dict(entity)
        return {"etag": "etag-e8"}

    def get_entity(self, partition_key: str, row_key: str) -> dict:
        key = (partition_key, row_key)
        if key not in self.rows:
            raise ResourceNotFoundError(key)
        return {**self.rows[key], "odata.etag": "etag-read-e8"}

    def query_entities(self, query_filter: str):
        partition = query_filter.split("'", 2)[1]
        return [
            row
            for (partition_key, _), row in self.rows.items()
            if partition_key == partition
        ]

    def list_entities(self):
        return list(self.rows.values())

    def delete_entity(self, partition_key: str, row_key: str) -> None:
        key = (partition_key, row_key)
        if key not in self.rows:
            raise ResourceNotFoundError(key)
        del self.rows[key]


class FakeTableServiceClient:
    def __init__(self) -> None:
        self.tables: dict[str, FakeTableClient] = {}

    def get_table_client(self, table_name: str) -> FakeTableClient:
        self.tables.setdefault(table_name, FakeTableClient())
        return self.tables[table_name]


class FakeQueueClient:
    def __init__(self) -> None:
        self.messages: list[dict] = []
        self.deleted: list[tuple[str, str]] = []

    def send_message(self, content: str):
        message_id = f"queue-msg-{len(self.messages)}"
        self.messages.append({"id": message_id, "content": content})
        return SimpleNamespace(id=message_id)

    def peek_messages(self, max_messages: int):
        return [
            SimpleNamespace(id=row["id"], content=row["content"])
            for row in self.messages[:max_messages]
        ]

    def receive_messages(self, max_messages: int, **kwargs):
        del kwargs
        return [
            SimpleNamespace(
                id=row["id"],
                content=row["content"],
                pop_receipt=f"receipt-{row['id']}",
                dequeue_count=1,
            )
            for row in self.messages[:max_messages]
        ]

    def delete_message(self, message_id: str, pop_receipt: str) -> None:
        for index, row in enumerate(self.messages):
            if row["id"] == message_id:
                del self.messages[index]
                self.deleted.append((message_id, pop_receipt))
                return
        raise ResourceNotFoundError(message_id)


class FakeQueueServiceClient:
    def __init__(self) -> None:
        self.queues: dict[str, FakeQueueClient] = {}

    def get_queue_client(self, queue_name: str) -> FakeQueueClient:
        self.queues.setdefault(queue_name, FakeQueueClient())
        return self.queues[queue_name]


def _azure_config(**overrides) -> AzureStorageConfig:
    data = {
        "account_url": "https://placeholder.blob.core.windows.net",
        "container": "hrha-evaluations",
        "table_endpoint": "https://placeholder.table.core.windows.net",
        "queue_endpoint": "https://placeholder.queue.core.windows.net",
    }
    data.update(overrides)
    return AzureStorageConfig(**data)


def _workflow_config(**overrides) -> WorkflowStorageConfig:
    data = {
        "backend": "azure",
        "blob_container": "hrha-evaluations",
        "table_prefix": "E8",
        "queue_name": "hrha-workflow-smoke",
    }
    data.update(overrides)
    return WorkflowStorageConfig(**data)


def _backend(monkeypatch):
    monkeypatch.setenv("HRHA_ENABLE_AZURE_WORKFLOW_STORAGE", "true")
    table_service = FakeTableServiceClient()
    blob_container = FakeBlobContainerClient()
    queue_service = FakeQueueServiceClient()
    backend = AzureWorkflowStorageBackend(
        azure=_azure_config(),
        workflow=_workflow_config(),
        table_service_client=table_service,
        blob_container_client=blob_container,
        queue_service_client=queue_service,
    )
    return backend, table_service, blob_container, queue_service


def _candidate_package() -> CandidatePackage:
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
        package_status="complete",
        blob_path=candidate_package_path("case-e8-001", "cand-e8-001", "v1"),
        sha256="8" * 64,
    )


def _case_participant() -> CaseParticipant:
    return CaseParticipant(
        PartitionKey="case-e8#keys",
        RowKey="hr_specialist#u-hr",
        created_at="2026-06-13T00:00:00Z",
        correlation_id="corr-e8-keys",
        case_id="case-e8#keys",
        actor_id="u-hr",
        display_name="Synthetic HR",
        case_role="hr_specialist",
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


def test_e8_azure_workflow_storage_fails_closed_without_guard(monkeypatch):
    monkeypatch.delenv("HRHA_ENABLE_AZURE_WORKFLOW_STORAGE", raising=False)

    with pytest.raises(WorkflowStorageNotConfiguredError) as excinfo:
        AzureWorkflowStorageBackend(
            azure=_azure_config(),
            workflow=_workflow_config(),
            table_service_client=FakeTableServiceClient(),
            blob_container_client=FakeBlobContainerClient(),
            queue_service_client=FakeQueueServiceClient(),
        )

    assert "HRHA_ENABLE_AZURE_WORKFLOW_STORAGE" in str(excinfo.value)


def test_e8_azure_workflow_storage_fails_closed_without_required_config(monkeypatch):
    monkeypatch.setenv("HRHA_ENABLE_AZURE_WORKFLOW_STORAGE", "true")

    with pytest.raises(WorkflowStorageNotConfiguredError) as excinfo:
        AzureWorkflowStorageBackend(
            azure=AzureStorageConfig(),
            workflow=WorkflowStorageConfig(backend="azure"),
            table_service_client=FakeTableServiceClient(),
            blob_container_client=FakeBlobContainerClient(),
            queue_service_client=FakeQueueServiceClient(),
        )

    assert "missing" in str(excinfo.value)


@pytest.mark.parametrize(
    ("azure", "workflow"),
    [
        (_azure_config(account_url="DefaultEndpointsProtocol=https;AccountKey=secret"), _workflow_config()),
        (_azure_config(table_endpoint="https://placeholder.table.core.windows.net?sig=secret"), _workflow_config()),
        (_azure_config(queue_endpoint="https://placeholder.queue.core.windows.net/q"), _workflow_config()),
        (_azure_config(), _workflow_config(table_prefix="bad-prefix")),
        (_azure_config(), _workflow_config(queue_name="BadQueueName")),
    ],
)
def test_e8_azure_workflow_storage_rejects_secret_or_invalid_config(
    monkeypatch, azure, workflow
):
    monkeypatch.setenv("HRHA_ENABLE_AZURE_WORKFLOW_STORAGE", "true")

    with pytest.raises(WorkflowStorageNotConfiguredError):
        AzureWorkflowStorageBackend(
            azure=azure,
            workflow=workflow,
            table_service_client=FakeTableServiceClient(),
            blob_container_client=FakeBlobContainerClient(),
            queue_service_client=FakeQueueServiceClient(),
        )


def test_e8_azure_table_upsert_uses_replace_and_decodes_json_fields(monkeypatch):
    backend, table_service, _, _ = _backend(monkeypatch)
    package = _candidate_package()

    row = backend.upsert_table_entity(package)
    restored = backend.get_table_entity(
        CandidatePackage, "case-e8-001", "package#cand-e8-001#v1"
    )
    listed = backend.list_table_entities(CandidatePackage, partition_key="case-e8-001")

    table = table_service.tables["E8CandidatePackages"]
    assert table.upsert_modes == ["REPLACE"]
    assert row["document_ids"] == '["doc-e8-001"]'
    assert row["etag"] == "etag-e8"
    assert isinstance(restored, CandidatePackage)
    assert restored.etag == "etag-read-e8"
    assert restored.required_document_status == {"resume": "present"}
    assert len(listed) == 1
    assert listed[0].required_document_status == {"resume": "present"}
    assert listed[0].etag is None

    assert backend.delete_table_entity(
        CandidatePackage, "case-e8-001", "package#cand-e8-001#v1"
    )
    assert (
        backend.get_table_entity(
            CandidatePackage, "case-e8-001", "package#cand-e8-001#v1"
        )
        is None
    )


def test_e8_azure_table_keys_are_encoded_only_at_adapter_boundary(monkeypatch):
    backend, table_service, _, _ = _backend(monkeypatch)
    participant = _case_participant()

    row = backend.upsert_table_entity(participant)
    table = table_service.tables["E8CaseParticipants"]

    assert row["PartitionKey"] == "case-e8#keys"
    assert row["RowKey"] == "hr_specialist#u-hr"
    assert ("case-e8%23keys", "hr_specialist%23u-hr") in table.rows
    assert ("case-e8#keys", "hr_specialist#u-hr") not in table.rows

    restored = backend.get_table_entity(
        CaseParticipant,
        "case-e8#keys",
        "hr_specialist#u-hr",
    )
    listed = backend.list_table_entities(
        CaseParticipant,
        partition_key="case-e8#keys",
    )

    assert restored is not None
    assert restored.PartitionKey == "case-e8#keys"
    assert restored.RowKey == "hr_specialist#u-hr"
    assert restored.case_id == "case-e8#keys"
    assert listed[0].PartitionKey == "case-e8#keys"
    assert listed[0].RowKey == "hr_specialist#u-hr"
    assert "%23" not in restored.RowKey
    assert "%23" not in listed[0].PartitionKey

    assert backend.delete_table_entity(
        CaseParticipant,
        "case-e8#keys",
        "hr_specialist#u-hr",
    )
    assert ("case-e8%23keys", "hr_specialist%23u-hr") not in table.rows


def test_e8_local_workflow_store_keeps_logical_table_keys(tmp_path):
    store = LocalWorkflowStore(tmp_path)
    participant = _case_participant()

    row = store.upsert_table_entity(participant)
    stored_rows = store.list_table_rows("CaseParticipants", partition_key="case-e8#keys")
    restored = store.get_table_entity(
        CaseParticipant,
        "case-e8#keys",
        "hr_specialist#u-hr",
    )

    assert row["PartitionKey"] == "case-e8#keys"
    assert row["RowKey"] == "hr_specialist#u-hr"
    assert stored_rows[0]["PartitionKey"] == "case-e8#keys"
    assert stored_rows[0]["RowKey"] == "hr_specialist#u-hr"
    assert restored is not None
    assert restored.RowKey == "hr_specialist#u-hr"


def test_e8_azure_blob_uses_canonical_path_as_blob_name(monkeypatch):
    backend, _, blob_container, _ = _backend(monkeypatch)
    path = candidate_package_path("case-e8-001", "cand-e8-001", "v1")

    ref = backend.write_blob_artifact(path, {"candidate_id": "cand-e8-001"})

    assert ref.blob_path == path
    assert path in blob_container.blobs
    assert backend.read_blob_json(path) == {"candidate_id": "cand-e8-001"}
    assert backend.delete_blob_artifact(path)
    assert backend.read_blob_bytes(path) is None


def test_e8_azure_queue_uses_canonical_json_and_pop_receipt_delete(monkeypatch):
    backend, _, _, queue_service = _backend(monkeypatch)

    sent = backend.enqueue_message(_message())
    queue = queue_service.queues["hrha-workflow-smoke"]
    peeked = backend.peek_queue_messages(max_messages=1)
    received = backend.receive_queue_messages(max_messages=1)

    assert sent["message_id"] == "queue-msg-0"
    assert sent["payload"]["message_type"] == "run-model-candidate-assessment"
    assert '"job_id":"job-e8-001"' in queue.messages[0]["content"]
    assert peeked[0]["payload"]["candidate_id"] == "cand-e8-001"
    assert received[0].pop_receipt == "receipt-queue-msg-0"

    assert backend.delete_queue_message(received[0])
    assert queue.deleted == [("queue-msg-0", "receipt-queue-msg-0")]
    assert queue.messages == []


def test_e8_azure_queue_rejects_unvalidated_raw_content_payload(monkeypatch):
    backend, _, _, queue_service = _backend(monkeypatch)

    with pytest.raises(ValidationError):
        backend.enqueue_message(
            {
                "message_type": "run-model-candidate-assessment",
                "case_id": "case-e8-001",
                "candidate_id": "cand-e8-001",
                "candidate_package_version": "v1",
                "rubric_version": "v1",
                "job_id": "job-e8-001",
                "requested_by_actor_id": "actor-hr",
                "requested_by_role": "hr_specialist",
                "correlation_id": "corr-e8-001",
                "resume_text": "raw candidate text must not be queued",
            }
        )

    assert queue_service.queues["hrha-workflow-smoke"].messages == []


def test_e8_azure_queue_delete_requires_pop_receipt(monkeypatch):
    backend, _, _, _ = _backend(monkeypatch)

    with pytest.raises(WorkflowStorageNotConfiguredError):
        backend.delete_queue_message("queue-msg-1")
