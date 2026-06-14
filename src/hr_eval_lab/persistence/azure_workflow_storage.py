"""Guarded Azure SDK-backed workflow storage adapter for E8.

This module imports no Azure SDKs at import time. Real SDK clients are created
only after the workflow Azure backend is explicitly selected and all guards
pass. Tests can inject fake clients to verify adapter behaviour without Azure
packages or network I/O.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote, unquote

from pydantic import BaseModel

from hr_eval_lab.config import (
    AzureStorageConfig,
    WorkflowStorageConfig,
    azure_workflow_storage_enabled,
)
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
from hr_eval_lab.persistence.azure_storage_guards import (
    build_identity_credential,
    reject_secret_material,
    validate_container_name,
    validate_queue_name,
    validate_service_url,
    validate_table_name,
    validate_table_prefix,
)
from hr_eval_lab.persistence.backend import StorageNotConfiguredError
from hr_eval_lab.persistence.workflow_storage import (
    WorkflowQueueReceivedMessage,
    WorkflowStorageNotConfiguredError,
)


def _is_not_found(exc: Exception) -> bool:
    if exc.__class__.__name__ == "ResourceNotFoundError":
        return True
    return getattr(exc, "status_code", None) == 404


def _payload_to_bytes(payload: Any) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    if isinstance(payload, BaseModel):
        payload = payload.model_dump(mode="json")
    return canonical_table_json(payload).encode("utf-8")


def _read_blob_bytes(blob_client: Any) -> bytes:
    raw = blob_client.download_blob().readall()
    if isinstance(raw, str):
        return raw.encode("utf-8")
    return bytes(raw)


def _message_content(message: Any) -> str:
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    if content is None:
        raise ValueError("queue message is missing content")
    if isinstance(content, bytes):
        return content.decode("utf-8")
    return str(content)


def _encode_table_key(value: str) -> str:
    """Encode logical workflow Table keys for Azure Table Storage.

    Domain RowKey conventions intentionally use values such as
    ``task#complete_role_intake``. Azure Table Storage rejects ``#``, ``/``,
    ``\\``, ``?``, and control characters in PartitionKey/RowKey, so the
    Azure adapter percent-encodes keys at the physical boundary only.
    """

    return quote(value, safe="-._~")


def _decode_table_key(value: str) -> str:
    return unquote(value)


def _build_real_clients(
    azure: AzureStorageConfig,
    blob_container: str,
) -> tuple[Any, Any, Any, Any]:
    credential = build_identity_credential()

    from azure.data.tables import TableServiceClient, UpdateMode
    from azure.storage.blob import BlobServiceClient
    from azure.storage.queue import QueueServiceClient

    table_service = TableServiceClient(
        endpoint=azure.table_endpoint.strip().rstrip("/"),
        credential=credential,
    )
    blob_service = BlobServiceClient(
        account_url=azure.account_url.strip().rstrip("/"),
        credential=credential,
    )
    queue_service = QueueServiceClient(
        account_url=azure.queue_endpoint.strip().rstrip("/"),
        credential=credential,
    )
    return (
        table_service,
        blob_service.get_container_client(blob_container),
        queue_service,
        UpdateMode.REPLACE,
    )


class AzureWorkflowStorageBackend:
    """Azure Table/Blob/Queue adapter behind the E7 workflow contracts."""

    def __init__(
        self,
        azure: AzureStorageConfig,
        workflow: WorkflowStorageConfig,
        *,
        table_service_client: Any | None = None,
        blob_container_client: Any | None = None,
        queue_service_client: Any | None = None,
        queue_client: Any | None = None,
        table_replace_mode: Any | None = None,
    ) -> None:
        missing = [
            name
            for name, value in (
                ("storage.azure.account_url", azure.account_url),
                ("storage.azure.table_endpoint", azure.table_endpoint),
                ("storage.azure.queue_endpoint", azure.queue_endpoint),
                ("workflow_storage.queue_name", workflow.queue_name),
            )
            if not value.strip()
        ]
        blob_container = (workflow.blob_container or azure.container).strip()
        if not blob_container:
            missing.append("workflow_storage.blob_container or storage.azure.container")
        if missing:
            raise WorkflowStorageNotConfiguredError(
                "azure workflow storage selected without configuration: "
                f"missing {', '.join(missing)}"
            )

        try:
            self.account_url = validate_service_url(
                "storage.azure.account_url", azure.account_url
            )
            self.table_endpoint = validate_service_url(
                "storage.azure.table_endpoint", azure.table_endpoint
            )
            self.queue_endpoint = validate_service_url(
                "storage.azure.queue_endpoint", azure.queue_endpoint
            )
            self.blob_container = validate_container_name(
                "workflow_storage.blob_container", blob_container
            )
            self.table_prefix = validate_table_prefix(workflow.table_prefix)
            self.queue_name = validate_queue_name(workflow.queue_name)
            for name, value in (
                ("storage.azure.container", azure.container),
                ("workflow_storage.blob_container", workflow.blob_container),
            ):
                if value:
                    reject_secret_material(name, value)
        except StorageNotConfiguredError as exc:
            raise WorkflowStorageNotConfiguredError(str(exc)) from exc

        if not azure_workflow_storage_enabled():
            raise WorkflowStorageNotConfiguredError(
                "azure workflow storage selected but disabled "
                "(HRHA_ENABLE_AZURE_WORKFLOW_STORAGE is not 'true')"
            )

        if (
            table_service_client is None
            or blob_container_client is None
            or queue_service_client is None
        ):
            (
                table_service_client,
                blob_container_client,
                queue_service_client,
                table_replace_mode,
            ) = _build_real_clients(azure, self.blob_container)

        self._table_service_client = table_service_client
        self._blob_container_client = blob_container_client
        self._queue_service_client = queue_service_client
        self._queue_client_override = queue_client
        self._table_replace_mode = table_replace_mode or "REPLACE"

    # -- Table-backed rows -----------------------------------------------------

    def upsert_table_entity(self, entity: WorkflowTableEntity) -> dict[str, Any]:
        row = entity.to_table_entity()
        response = self._table_client(entity.table_name).upsert_entity(
            entity=self._azure_table_row(row),
            mode=self._table_replace_mode,
        )
        etag = self._etag_from_response(response)
        if etag:
            row["etag"] = etag
        return row

    def get_table_entity(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str,
        row_key: str,
    ) -> WorkflowTableEntity | None:
        try:
            raw = self._table_client(model.table_name).get_entity(
                partition_key=_encode_table_key(partition_key),
                row_key=_encode_table_key(row_key),
            )
        except Exception as exc:
            if _is_not_found(exc):
                return None
            raise
        return model.from_table_entity(self._logical_table_row(raw))

    def list_table_entities(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str | None = None,
    ) -> list[WorkflowTableEntity]:
        table = self._table_client(model.table_name)
        if partition_key is None:
            rows = table.list_entities()
        else:
            escaped = _encode_table_key(partition_key).replace("'", "''")
            rows = table.query_entities(query_filter=f"PartitionKey eq '{escaped}'")
        return [model.from_table_entity(self._logical_table_row(row)) for row in rows]

    def delete_table_entity(
        self,
        model: type[WorkflowTableEntity],
        partition_key: str,
        row_key: str,
    ) -> bool:
        try:
            self._table_client(model.table_name).delete_entity(
                partition_key=_encode_table_key(partition_key),
                row_key=_encode_table_key(row_key),
            )
        except Exception as exc:
            if _is_not_found(exc):
                return False
            raise
        return True

    # -- Blob-backed artifacts -------------------------------------------------

    def write_blob_artifact(self, blob_path: str, payload: Any) -> WorkflowBlobArtifactRef:
        safe_path = validate_blob_path(blob_path)
        raw = _payload_to_bytes(payload)
        self._blob_client(safe_path).upload_blob(raw, overwrite=True)
        return WorkflowBlobArtifactRef.from_bytes(safe_path, raw)

    def read_blob_bytes(self, blob_path: str) -> bytes | None:
        safe_path = validate_blob_path(blob_path)
        try:
            return _read_blob_bytes(self._blob_client(safe_path))
        except Exception as exc:
            if _is_not_found(exc):
                return None
            raise

    def read_blob_json(self, blob_path: str) -> Any | None:
        raw = self.read_blob_bytes(blob_path)
        if raw is None:
            return None
        return json.loads(raw.decode("utf-8"))

    def delete_blob_artifact(self, blob_path: str) -> bool:
        safe_path = validate_blob_path(blob_path)
        try:
            self._blob_client(safe_path).delete_blob()
        except Exception as exc:
            if _is_not_found(exc):
                return False
            raise
        return True

    # -- Queue-backed messages -------------------------------------------------

    def enqueue_message(
        self,
        message: WorkflowQueueMessageBase | dict[str, Any],
        queue_name: str | None = None,
    ) -> dict[str, Any]:
        queue = self._queue_client(queue_name)
        payload = self._message_payload(message)
        body = canonical_table_json(payload)
        result = queue.send_message(body)
        message_id = getattr(result, "id", None) or getattr(result, "message_id", None)
        return {
            "message_id": str(message_id) if message_id else "",
            "queue_name": self._queue_name(queue_name),
            "payload": payload,
        }

    def peek_queue_messages(
        self, queue_name: str | None = None, max_messages: int = 1
    ) -> list[dict[str, Any]]:
        queue = self._queue_client(queue_name)
        return [
            {
                "message_id": str(getattr(message, "id", "")),
                "queue_name": self._queue_name(queue_name),
                "payload": self._message_payload(json.loads(_message_content(message))),
            }
            for message in queue.peek_messages(max_messages=max_messages)
        ]

    def receive_queue_messages(
        self,
        queue_name: str | None = None,
        max_messages: int = 1,
        visibility_timeout: int | None = None,
    ) -> list[WorkflowQueueReceivedMessage]:
        queue = self._queue_client(queue_name)
        kwargs: dict[str, Any] = {"max_messages": max_messages}
        if visibility_timeout is not None:
            kwargs["visibility_timeout"] = visibility_timeout
        return [
            WorkflowQueueReceivedMessage(
                message_id=str(getattr(message, "id", "")),
                queue_name=self._queue_name(queue_name),
                payload=self._message_payload(json.loads(_message_content(message))),
                pop_receipt=getattr(message, "pop_receipt", None),
                dequeue_count=getattr(message, "dequeue_count", None),
            )
            for message in queue.receive_messages(**kwargs)
        ]

    def delete_queue_message(
        self,
        message: WorkflowQueueReceivedMessage | dict[str, Any] | str,
        pop_receipt: str | None = None,
        queue_name: str | None = None,
    ) -> bool:
        message_id, receipt, effective_queue = self._queue_delete_args(
            message, pop_receipt, queue_name
        )
        if not receipt:
            raise WorkflowStorageNotConfiguredError(
                "Azure Queue delete requires a pop receipt from receive_messages"
            )
        try:
            self._queue_client(effective_queue).delete_message(message_id, receipt)
        except Exception as exc:
            if _is_not_found(exc):
                return False
            raise
        return True

    # -- internals -------------------------------------------------------------

    def _effective_table_name(self, table_name: str) -> str:
        return validate_table_name(f"{self.table_prefix}{table_name}")

    def _table_client(self, table_name: str) -> Any:
        return self._table_service_client.get_table_client(
            self._effective_table_name(table_name)
        )

    def _blob_client(self, blob_path: str) -> Any:
        return self._blob_container_client.get_blob_client(blob_path)

    def _queue_name(self, queue_name: str | None) -> str:
        return validate_queue_name(queue_name or self.queue_name)

    def _queue_client(self, queue_name: str | None = None) -> Any:
        effective = self._queue_name(queue_name)
        if self._queue_client_override is not None and effective == self.queue_name:
            return self._queue_client_override
        return self._queue_service_client.get_queue_client(effective)

    def _message_payload(
        self, message: WorkflowQueueMessageBase | dict[str, Any]
    ) -> dict[str, Any]:
        if isinstance(message, WorkflowQueueMessageBase):
            return message.to_queue_payload()
        return validate_queue_message(message).to_queue_payload()

    def _queue_delete_args(
        self,
        message: WorkflowQueueReceivedMessage | dict[str, Any] | str,
        pop_receipt: str | None,
        queue_name: str | None,
    ) -> tuple[str, str | None, str | None]:
        if isinstance(message, str):
            return message, pop_receipt, queue_name
        if isinstance(message, dict):
            message_id = str(message.get("message_id") or message.get("id") or "")
            receipt = pop_receipt or message.get("pop_receipt")
            return message_id, receipt, queue_name
        return message.message_id, pop_receipt or message.pop_receipt, message.queue_name

    def _etag_from_response(self, response: Any) -> str | None:
        if not response:
            return None
        if isinstance(response, dict):
            value = response.get("etag") or response.get("ETag")
            return str(value) if value else None
        value = getattr(response, "etag", None)
        return str(value) if value else None

    def _azure_table_row(self, row: dict[str, Any]) -> dict[str, Any]:
        encoded = dict(row)
        encoded["PartitionKey"] = _encode_table_key(str(row["PartitionKey"]))
        encoded["RowKey"] = _encode_table_key(str(row["RowKey"]))
        return encoded

    def _logical_table_row(self, raw: Any) -> dict[str, Any]:
        row = self._row_with_etag(raw)
        row["PartitionKey"] = _decode_table_key(str(row["PartitionKey"]))
        row["RowKey"] = _decode_table_key(str(row["RowKey"]))
        return row

    def _row_with_etag(self, raw: Any) -> dict[str, Any]:
        row = dict(raw)
        etag = (
            row.pop("odata.etag", None)
            or row.get("etag")
            or getattr(raw, "metadata", {}).get("etag")
        )
        if etag and "etag" not in row:
            row["etag"] = str(etag)
        return row
