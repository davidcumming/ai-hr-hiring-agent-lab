"""Azure Blob storage backend for Slice E3 durable evaluation records.

Disabled by default and fail-closed by construction:

- **No Azure SDK import at module import time** (and none in default tests).
  SDK imports happen lazily only when ``azure_blob`` is explicitly selected,
  ``HRHA_ENABLE_AZURE_STORAGE=true`` is set, and no test client factory is
  installed.
- Selecting this backend without Blob account URL + container, or without the
  storage-specific live gate, raises :class:`StorageNotConfiguredError`.
- Auth is identity-based only. Hosted Azure prefers the user-assigned managed
  identity client id from ``HRHA_MANAGED_IDENTITY_CLIENT_ID``; local explicit
  smoke checks may fall back to ``DefaultAzureCredential``. Account keys,
  connection strings, SAS tokens, and SAS-in-URL query strings are rejected.

E3 mapping:

- ``write_evaluation_record`` / ``read_evaluation_record`` → block blobs under
  ``{container}/evaluations/{evaluation_id}/record.json``.
- ``write_artifact`` / ``list_artifacts`` → block blobs under the same
  evaluation prefix, matching the local layout in ``backend.py``.
- ``write_metadata_row`` / ``read_metadata_row`` use a Blob-only compatibility
  object under ``metadata/evaluations/{evaluation_id}.json`` so the current
  store contract can complete. Azure Table durability for summaries,
  idempotency, evidence rows, and review queue rows is deferred to a later
  slice.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from hr_eval_lab.config import (
    ENV_MANAGED_IDENTITY_CLIENT_ID,
    AzureStorageConfig,
    azure_storage_enabled,
)
from hr_eval_lab.domain.schemas.storage import ArtifactType, StorageArtifactRef
from hr_eval_lab.persistence.backend import (
    StorageBackend,
    StorageNotConfiguredError,
    canonical_json,
)

BlobContainerClientFactory = Callable[[AzureStorageConfig], Any]
_blob_container_client_factory: BlobContainerClientFactory | None = None

_SECRET_MARKERS = (
    "defaultendpointsprotocol=",
    "accountkey=",
    "sharedaccesssignature=",
)


def set_blob_container_client_factory_for_tests(
    factory: BlobContainerClientFactory | None,
) -> BlobContainerClientFactory | None:
    """Install a fake Blob client factory for deterministic tests.

    Returns the previous factory so callers can restore it. Production code
    should never call this.
    """

    global _blob_container_client_factory
    previous = _blob_container_client_factory
    _blob_container_client_factory = factory
    return previous


def _reject_secret_material(name: str, value: str) -> None:
    lowered = value.lower()
    if ";" in value or any(marker in lowered for marker in _SECRET_MARKERS):
        raise StorageNotConfiguredError(
            f"{name} appears to contain secret-bearing connection material; "
            "use account URL + managed identity only"
        )


def _validate_account_url(account_url: str) -> str:
    url = account_url.strip()
    _reject_secret_material("storage.azure.account_url", url)
    parsed = urlparse(url)
    if parsed.query or parsed.params or parsed.fragment:
        raise StorageNotConfiguredError(
            "storage.azure.account_url must not contain a SAS token or query string"
        )
    if parsed.scheme != "https" or not parsed.netloc:
        raise StorageNotConfiguredError(
            "storage.azure.account_url must be an https Blob service account URL"
        )
    if parsed.path not in ("", "/"):
        raise StorageNotConfiguredError(
            "storage.azure.account_url must be the account Blob service URL, "
            "not a container or blob URL"
        )
    return url.rstrip("/")


def _validate_container(container: str) -> str:
    name = container.strip()
    _reject_secret_material("storage.azure.container", name)
    if not name or any(char in name for char in ("/", "\\", "?", "#", ";")):
        raise StorageNotConfiguredError(
            "storage.azure.container must be a plain Blob container name"
        )
    return name


def _is_not_found(exc: Exception) -> bool:
    if exc.__class__.__name__ == "ResourceNotFoundError":
        return True
    return getattr(exc, "status_code", None) == 404


def _read_blob_bytes(blob_client: Any) -> bytes:
    raw = blob_client.download_blob().readall()
    if isinstance(raw, str):
        return raw.encode("utf-8")
    return bytes(raw)


def _build_container_client(azure: AzureStorageConfig) -> Any:
    """Build the real Azure Blob container client lazily."""

    account_url = _validate_account_url(azure.account_url)
    container = _validate_container(azure.container)
    client_id = os.environ.get(ENV_MANAGED_IDENTITY_CLIENT_ID, "").strip()
    if client_id:
        from azure.identity import ManagedIdentityCredential

        credential = ManagedIdentityCredential(client_id=client_id)
    elif os.environ.get("WEBSITE_SITE_NAME") or os.environ.get("FUNCTIONS_WORKER_RUNTIME"):
        from azure.identity import ManagedIdentityCredential

        credential = ManagedIdentityCredential()
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)

    from azure.storage.blob import BlobServiceClient

    service = BlobServiceClient(account_url=account_url, credential=credential)
    return service.get_container_client(container)


class AzureBlobBackend(StorageBackend):
    """Blob-backed record/artifact persistence for explicitly enabled Azure paths."""

    def __init__(self, azure: AzureStorageConfig, container_client: Any | None = None) -> None:
        missing = [
            key
            for key, value in (
                ("storage.azure.account_url", azure.account_url),
                ("storage.azure.container", azure.container),
            )
            if not value.strip()
        ]
        if missing:
            raise StorageNotConfiguredError(
                "azure_blob backend selected without configuration: "
                f"missing {', '.join(missing)}"
            )
        self.account_url = _validate_account_url(azure.account_url)
        self.container = _validate_container(azure.container)
        if azure.table_endpoint:
            _reject_secret_material("storage.azure.table_endpoint", azure.table_endpoint)
            parsed_table = urlparse(azure.table_endpoint.strip())
            if parsed_table.query or parsed_table.params or parsed_table.fragment:
                raise StorageNotConfiguredError(
                    "storage.azure.table_endpoint must not contain a SAS token or query string"
                )
        if not azure_storage_enabled():
            raise StorageNotConfiguredError(
                "azure_blob backend selected but Azure storage is disabled "
                "(HRHA_ENABLE_AZURE_STORAGE is not 'true')"
            )
        self._azure = azure
        factory = _blob_container_client_factory
        self._container_client = (
            container_client
            if container_client is not None
            else factory(azure)
            if factory is not None
            else _build_container_client(azure)
        )

    # -- paths -----------------------------------------------------------------

    def _blob_name(self, evaluation_id: str, artifact_name: str) -> str:
        return f"evaluations/{evaluation_id}/{artifact_name}"

    def _artifact_name(self, artifact_type: ArtifactType, role_or_name: str) -> str:
        if artifact_type == "council-role":
            return f"council/{role_or_name}.json"
        return f"{role_or_name}.json"

    def _blob_client(self, name: str) -> Any:
        return self._container_client.get_blob_client(name)

    def _write_json_blob(self, name: str, payload: Any) -> StorageArtifactRef | None:
        body = canonical_json(payload)
        raw = body.encode("utf-8")
        self._blob_client(name).upload_blob(raw, overwrite=True)
        if not name.startswith("evaluations/"):
            return None
        _, evaluation_id, rel = name.split("/", 2)
        return StorageArtifactRef(
            evaluation_id=evaluation_id,
            artifact_type=self._artifact_type_for_name(rel),
            name=rel,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
        )

    def _artifact_type_for_name(self, name: str) -> ArtifactType:
        if name.startswith("council/"):
            return "council-role"
        if name == "record.json":
            return "record"
        stem = name[: -len(".json")] if name.endswith(".json") else name
        if stem in (
            "request",
            "source-documents",
            "evidence-packet",
            "synthesis",
            "quality-gates",
            "provider-metadata",
            "human-review",
        ):
            return stem  # type: ignore[return-value]
        return "record"

    def write_evaluation_record(self, evaluation_id: str, record_payload: dict) -> None:
        self._write_json_blob(self._blob_name(evaluation_id, "record.json"), record_payload)

    def read_evaluation_record(self, evaluation_id: str) -> Optional[dict]:
        try:
            raw = _read_blob_bytes(self._blob_client(self._blob_name(evaluation_id, "record.json")))
        except Exception as exc:
            if _is_not_found(exc):
                return None
            raise
        return json.loads(raw.decode("utf-8"))

    def write_artifact(
        self,
        evaluation_id: str,
        artifact_type: ArtifactType,
        role_or_name: str,
        payload: Any,
    ) -> StorageArtifactRef:
        ref = self._write_json_blob(
            self._blob_name(evaluation_id, self._artifact_name(artifact_type, role_or_name)),
            payload,
        )
        assert ref is not None
        return ref

    def list_artifacts(self, evaluation_id: str) -> list[StorageArtifactRef]:
        prefix = f"evaluations/{evaluation_id}/"
        refs: list[StorageArtifactRef] = []
        for blob in sorted(
            self._container_client.list_blobs(name_starts_with=prefix),
            key=lambda item: item.name,
        ):
            rel = blob.name[len(prefix) :]
            if not rel.endswith(".json"):
                continue
            raw = _read_blob_bytes(self._blob_client(blob.name))
            refs.append(
                StorageArtifactRef(
                    evaluation_id=evaluation_id,
                    artifact_type=self._artifact_type_for_name(rel),
                    name=rel,
                    sha256=hashlib.sha256(raw).hexdigest(),
                    size_bytes=len(raw),
                )
            )
        return refs

    def write_metadata_row(self, record_summary: dict) -> None:
        evaluation_id = str(record_summary.get("PartitionKey", "")).strip()
        if not evaluation_id:
            raise StorageNotConfiguredError("metadata summary row is missing PartitionKey")
        self._write_json_blob(f"metadata/evaluations/{evaluation_id}.json", record_summary)

    def read_metadata_row(self, evaluation_id: str) -> Optional[dict]:
        try:
            raw = _read_blob_bytes(
                self._blob_client(f"metadata/evaluations/{evaluation_id}.json")
            )
        except Exception as exc:
            if _is_not_found(exc):
                return None
            raise
        return json.loads(raw.decode("utf-8"))
