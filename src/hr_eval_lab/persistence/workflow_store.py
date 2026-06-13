"""Deterministic local workflow storage adapter for E7.

This is an Azure-shaped local adapter only:

- Table-like entities are appended as canonical JSONL rows.
- Blob-like artifacts are written under a local root using canonical paths.
- Queue-like work requests are appended as canonical JSONL messages.

No Azure SDK is imported and no network I/O is performed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from hr_eval_lab.domain.schemas.workflow import (
    WorkflowTableEntity,
    canonical_table_json,
)
from hr_eval_lab.domain.schemas.workflow_artifacts import (
    WorkflowBlobArtifactRef,
    validate_blob_path,
)
from hr_eval_lab.domain.schemas.workflow_queue import (
    WorkflowQueueMessageBase,
    validate_queue_message,
)


class LocalWorkflowStore:
    """Local deterministic adapter mirroring Table, Blob, and Queue roles."""

    DEFAULT_QUEUE_NAME = "workflow-jobs"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.tables_root = self.root / "workflow" / "tables"
        self.blobs_root = self.root / "workflow" / "blobs"
        self.queues_root = self.root / "workflow" / "queues"
        self.tables_root.mkdir(parents=True, exist_ok=True)
        self.blobs_root.mkdir(parents=True, exist_ok=True)
        self.queues_root.mkdir(parents=True, exist_ok=True)

    # -- Table-shaped rows -----------------------------------------------------

    def write_table_entity(self, entity: WorkflowTableEntity) -> dict[str, Any]:
        row = entity.to_table_entity()
        self._append_jsonl(self._table_path(entity.table_name), row)
        return row

    def list_table_rows(
        self, table_name: str, partition_key: str | None = None
    ) -> list[dict[str, Any]]:
        rows = self._read_jsonl(self._table_path(table_name))
        if partition_key is None:
            return rows
        return [row for row in rows if row.get("PartitionKey") == partition_key]

    def list_table_entities(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str | None = None,
    ) -> list[WorkflowTableEntity]:
        return [
            model.from_table_entity(row)
            for row in self.list_table_rows(model.table_name, partition_key)
        ]

    def get_table_entity(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str,
        row_key: str,
    ) -> WorkflowTableEntity | None:
        for row in reversed(self.list_table_rows(model.table_name, partition_key)):
            if row.get("PartitionKey") == partition_key and row.get("RowKey") == row_key:
                return model.from_table_entity(row)
        return None

    # -- Blob-shaped artifacts -------------------------------------------------

    def write_blob_artifact(self, blob_path: str, payload: Any) -> WorkflowBlobArtifactRef:
        safe_path = validate_blob_path(blob_path)
        raw = self._payload_to_bytes(payload)
        path = self.blobs_root / safe_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return WorkflowBlobArtifactRef.from_bytes(safe_path, raw)

    def read_blob_bytes(self, blob_path: str) -> bytes | None:
        path = self.blobs_root / validate_blob_path(blob_path)
        if not path.exists():
            return None
        return path.read_bytes()

    def read_blob_json(self, blob_path: str) -> Any | None:
        raw = self.read_blob_bytes(blob_path)
        if raw is None:
            return None
        return json.loads(raw.decode("utf-8"))

    # -- Queue-shaped messages -------------------------------------------------

    def enqueue_message(
        self,
        message: WorkflowQueueMessageBase | dict[str, Any],
        queue_name: str = DEFAULT_QUEUE_NAME,
    ) -> dict[str, Any]:
        payload = self._message_payload(message)
        queue_path = self._queue_path(queue_name)
        sequence = len(self._read_jsonl(queue_path))
        message_id = self._message_id(queue_name, sequence, payload)
        row = {
            "message_id": message_id,
            "queue_name": queue_name,
            "sequence": sequence,
            "payload": payload,
        }
        self._append_jsonl(queue_path, row)
        return row

    def list_queue_messages(
        self, queue_name: str = DEFAULT_QUEUE_NAME
    ) -> list[dict[str, Any]]:
        return self._read_jsonl(self._queue_path(queue_name))

    # -- internals -------------------------------------------------------------

    def _table_path(self, table_name: str) -> Path:
        self._validate_store_name(table_name, "table_name")
        return self.tables_root / f"{table_name}.jsonl"

    def _queue_path(self, queue_name: str) -> Path:
        self._validate_store_name(queue_name, "queue_name")
        return self.queues_root / f"{queue_name}.jsonl"

    def _append_jsonl(self, path: Path, row: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(canonical_table_json(row) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _payload_to_bytes(self, payload: Any) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode("utf-8")
        if isinstance(payload, BaseModel):
            payload = payload.model_dump(mode="json")
        return canonical_table_json(payload).encode("utf-8")

    def _message_payload(
        self, message: WorkflowQueueMessageBase | dict[str, Any]
    ) -> dict[str, Any]:
        if isinstance(message, WorkflowQueueMessageBase):
            return message.to_queue_payload()
        return validate_queue_message(message).to_queue_payload()

    def _message_id(
        self, queue_name: str, sequence: int, payload: dict[str, Any]
    ) -> str:
        import hashlib

        body = canonical_table_json(
            {"queue_name": queue_name, "sequence": sequence, "payload": payload}
        )
        return "msg-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:24]

    def _validate_store_name(self, value: str, label: str) -> None:
        if not value or any(char in value for char in ("/", "\\", "?", "#", "..")):
            raise ValueError(f"{label} is not a safe local store name")
