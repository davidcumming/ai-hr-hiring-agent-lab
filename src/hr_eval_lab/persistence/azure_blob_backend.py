"""Azure Blob storage backend — SCAFFOLD ONLY (readiness pack).

Disabled by default and fail-closed by construction:

- **No Azure SDK import at module import time** (and none in default tests);
  any SDK import would happen lazily inside a method, and no method ever
  reaches one in this batch.
- Selecting this backend without complete configuration, or without
  ``HRHA_ENABLE_LIVE_AZURE=true``, raises :class:`StorageNotConfiguredError`
  at construction.
- Even fully configured, every operation raises — live storage wiring is
  deferred to the wiring slice (human-gated).
- Intended live auth is **identity-based** (managed identity /
  ``DefaultAzureCredential``), never account keys, connection strings, or SAS
  tokens. App settings are placeholders only (see ``config/azure.env.sample``
  and ``infra/``).

Intended live mapping (documentation, not behaviour):

- ``write_evaluation_record`` / ``write_artifact`` → block blobs under
  ``{container}/evaluations/{evaluation_id}/...`` (same names as the local
  layout in ``backend.py``).
- ``write_metadata_row`` / ``read_metadata_row`` → an Azure Table
  (PartitionKey = evaluation_id, RowKey = "summary") — the row schema
  (``RecordSummaryRow``) is already Table-shaped and text-free.
"""

from __future__ import annotations

from typing import Any, Optional

from hr_eval_lab.config import AzureStorageConfig, live_azure_enabled
from hr_eval_lab.domain.schemas.storage import ArtifactType, StorageArtifactRef
from hr_eval_lab.persistence.backend import StorageBackend, StorageNotConfiguredError

_DEFERRED = (
    "azure_blob storage backend is a scaffold: live Azure storage wiring is "
    "deferred and human-gated; use the local_filesystem backend"
)


class AzureBlobBackend(StorageBackend):
    """Fail-closed scaffold. Constructing it without complete placeholder
    configuration AND HRHA_ENABLE_LIVE_AZURE=true is a configuration error."""

    def __init__(self, azure: AzureStorageConfig) -> None:
        missing = [
            key
            for key, value in (
                ("storage.azure.account_url", azure.account_url),
                ("storage.azure.container", azure.container),
                ("storage.azure.table_endpoint", azure.table_endpoint),
            )
            if not value.strip()
        ]
        if missing:
            raise StorageNotConfiguredError(
                "azure_blob backend selected without configuration: "
                f"missing {', '.join(missing)} (placeholders are intentionally "
                "empty in this batch; live wiring is deferred)"
            )
        if not live_azure_enabled():
            raise StorageNotConfiguredError(
                "azure_blob backend selected but live Azure paths are disabled "
                "(HRHA_ENABLE_LIVE_AZURE is not 'true')"
            )
        self._azure = azure

    # Every operation fails closed — no live storage exists in this batch.

    def write_evaluation_record(self, evaluation_id: str, record_payload: dict) -> None:
        raise StorageNotConfiguredError(_DEFERRED)

    def read_evaluation_record(self, evaluation_id: str) -> Optional[dict]:
        raise StorageNotConfiguredError(_DEFERRED)

    def write_artifact(
        self,
        evaluation_id: str,
        artifact_type: ArtifactType,
        role_or_name: str,
        payload: Any,
    ) -> StorageArtifactRef:
        raise StorageNotConfiguredError(_DEFERRED)

    def list_artifacts(self, evaluation_id: str) -> list[StorageArtifactRef]:
        raise StorageNotConfiguredError(_DEFERRED)

    def write_metadata_row(self, record_summary: dict) -> None:
        raise StorageNotConfiguredError(_DEFERRED)

    def read_metadata_row(self, evaluation_id: str) -> Optional[dict]:
        raise StorageNotConfiguredError(_DEFERRED)
