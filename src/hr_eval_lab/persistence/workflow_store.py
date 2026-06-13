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

    def upsert_table_entity(self, entity: WorkflowTableEntity) -> dict[str, Any]:
        row = entity.to_table_entity()
        path = self._table_path(entity.table_name)
        rows = [
            existing
            for existing in self._read_jsonl(path)
            if not (
                existing.get("PartitionKey") == row["PartitionKey"]
                and existing.get("RowKey") == row["RowKey"]
            )
        ]
        rows.append(row)
        self._write_jsonl_rows(path, rows)
        return row

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

    def delete_table_entity(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str,
        row_key: str,
    ) -> bool:
        path = self._table_path(model.table_name)
        rows = self._read_jsonl(path)
        kept = [
            row
            for row in rows
            if not (
                row.get("PartitionKey") == partition_key and row.get("RowKey") == row_key
            )
        ]
        if len(kept) == len(rows):
            return False
        self._write_jsonl_rows(path, kept)
        return True

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

    def delete_blob_artifact(self, blob_path: str) -> bool:
        path = self.blobs_root / validate_blob_path(blob_path)
        if not path.exists():
            return False
        path.unlink()
        return True

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

    def peek_queue_messages(
        self, queue_name: str = DEFAULT_QUEUE_NAME, max_messages: int = 1
    ) -> list[dict[str, Any]]:
        return self.list_queue_messages(queue_name)[:max_messages]

    def receive_queue_messages(
        self,
        queue_name: str = DEFAULT_QUEUE_NAME,
        max_messages: int = 1,
        visibility_timeout: int | None = None,
    ) -> list[Any]:
        del visibility_timeout
        from hr_eval_lab.persistence.workflow_storage import (
            WorkflowQueueReceivedMessage,
        )

        return [
            WorkflowQueueReceivedMessage(
                message_id=row["message_id"],
                queue_name=queue_name,
                payload=row["payload"],
                pop_receipt=f"local-pop-{row['message_id']}",
            )
            for row in self.list_queue_messages(queue_name)[:max_messages]
        ]

    def delete_queue_message(
        self,
        message: Any,
        pop_receipt: str | None = None,
        queue_name: str | None = None,
    ) -> bool:
        del pop_receipt
        message_id, effective_queue = self._queue_delete_args(message, queue_name)
        queue_path = self._queue_path(effective_queue)
        rows = self._read_jsonl(queue_path)
        kept = [row for row in rows if row.get("message_id") != message_id]
        if len(kept) == len(rows):
            return False
        self._write_jsonl_rows(queue_path, kept)
        return True

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

    def _write_jsonl_rows(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not rows:
            if path.exists():
                path.unlink()
            return
        body = "".join(canonical_table_json(row) + "\n" for row in rows)
        path.write_text(body, encoding="utf-8")

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

    def _queue_delete_args(self, message: Any, queue_name: str | None) -> tuple[str, str]:
        effective_queue = queue_name
        if isinstance(message, str):
            return message, effective_queue or self.DEFAULT_QUEUE_NAME
        if isinstance(message, dict):
            value = message.get("message_id") or message.get("id")
            if value:
                effective_queue = effective_queue or message.get("queue_name")
                return str(value), str(effective_queue or self.DEFAULT_QUEUE_NAME)
        value = getattr(message, "message_id", None) or getattr(message, "id", None)
        if value:
            effective_queue = effective_queue or getattr(message, "queue_name", None)
            return str(value), str(effective_queue or self.DEFAULT_QUEUE_NAME)
        raise ValueError("received queue message is missing message_id")

    def _validate_store_name(self, value: str, label: str) -> None:
        if not value or any(char in value for char in ("/", "\\", "?", "#", "..")):
            raise ValueError(f"{label} is not a safe local store name")
