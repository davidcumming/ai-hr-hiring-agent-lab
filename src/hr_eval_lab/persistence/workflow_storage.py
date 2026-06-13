"""Workflow storage protocol boundary for E8.

The default implementation is still :class:`LocalWorkflowStore`. The Azure
implementation is imported lazily only when explicitly selected so ordinary
local app construction imports no Azure SDK modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from hr_eval_lab.config import LabConfig
from hr_eval_lab.domain.schemas.workflow import WorkflowTableEntity
from hr_eval_lab.domain.schemas.workflow_artifacts import WorkflowBlobArtifactRef
from hr_eval_lab.domain.schemas.workflow_queue import WorkflowQueueMessageBase
from hr_eval_lab.persistence.backend import StorageNotConfiguredError
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore


class WorkflowStorageNotConfiguredError(StorageNotConfiguredError):
    """Workflow storage was explicitly selected without safe configuration."""


@dataclass(frozen=True)
class WorkflowQueueReceivedMessage:
    """A queue message plus the receipt needed to delete it after receive."""

    message_id: str
    queue_name: str
    payload: dict[str, Any]
    pop_receipt: str | None = None
    dequeue_count: int | None = None


@runtime_checkable
class WorkflowTableStore(Protocol):
    def upsert_table_entity(self, entity: WorkflowTableEntity) -> dict[str, Any]:
        """Insert or replace one Workflow Table entity."""

    def get_table_entity(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str,
        row_key: str,
    ) -> WorkflowTableEntity | None:
        """Return one Workflow Table entity or None."""

    def list_table_entities(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str | None = None,
    ) -> list[WorkflowTableEntity]:
        """List Workflow Table entities for a model."""

    def delete_table_entity(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str,
        row_key: str,
    ) -> bool:
        """Delete one Workflow Table entity. Returns True when deleted."""


@runtime_checkable
class WorkflowBlobStore(Protocol):
    def write_blob_artifact(self, blob_path: str, payload: Any) -> WorkflowBlobArtifactRef:
        """Write one workflow artifact at a canonical E7 Blob path."""

    def read_blob_bytes(self, blob_path: str) -> bytes | None:
        """Read one workflow artifact as bytes, or None if absent."""

    def read_blob_json(self, blob_path: str) -> Any | None:
        """Read and decode one JSON workflow artifact, or None if absent."""

    def delete_blob_artifact(self, blob_path: str) -> bool:
        """Delete one workflow artifact. Returns True when deleted."""


@runtime_checkable
class WorkflowQueueStore(Protocol):
    def enqueue_message(
        self,
        message: WorkflowQueueMessageBase | dict[str, Any],
        queue_name: str = LocalWorkflowStore.DEFAULT_QUEUE_NAME,
    ) -> dict[str, Any]:
        """Enqueue one validated workflow message."""

    def peek_queue_messages(
        self,
        queue_name: str = LocalWorkflowStore.DEFAULT_QUEUE_NAME,
        max_messages: int = 1,
    ) -> list[dict[str, Any]]:
        """Peek visible workflow messages without deleting them."""

    def receive_queue_messages(
        self,
        queue_name: str = LocalWorkflowStore.DEFAULT_QUEUE_NAME,
        max_messages: int = 1,
        visibility_timeout: int | None = None,
    ) -> list[WorkflowQueueReceivedMessage]:
        """Receive messages and return receipts required for deletion."""

    def delete_queue_message(
        self,
        message: WorkflowQueueReceivedMessage | dict[str, Any] | str,
        pop_receipt: str | None = None,
        queue_name: str = LocalWorkflowStore.DEFAULT_QUEUE_NAME,
    ) -> bool:
        """Delete one received workflow message."""


@runtime_checkable
class WorkflowStorageBackend(WorkflowTableStore, WorkflowBlobStore, WorkflowQueueStore, Protocol):
    """Composed workflow storage backend for future case APIs and workers."""


def select_workflow_storage(config: LabConfig) -> WorkflowStorageBackend:
    """Resolve the configured workflow storage backend.

    Lazy: the Azure workflow module is imported only when the explicit
    workflow backend is ``azure``.
    """

    backend_id = config.workflow_storage.backend
    if backend_id == "local":
        return LocalWorkflowStore(config.persistence.root)
    if backend_id == "azure":
        from hr_eval_lab.persistence.azure_workflow_storage import (
            AzureWorkflowStorageBackend,
        )

        return AzureWorkflowStorageBackend(
            azure=config.storage.azure,
            workflow=config.workflow_storage,
        )
    raise WorkflowStorageNotConfiguredError(
        f"unknown workflow storage backend: {backend_id!r}"
    )
