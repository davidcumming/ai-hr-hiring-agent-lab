"""Server-side lab configuration: load + validate config/lab-config.toml.

The config file is source-controlled and is the only runtime configuration
surface this slice (slice spec §17; AF-006 defers the admin surface). Tests
exercise non-default states by constructing :class:`LabConfig` directly.

Readiness-pack additions (all local/deterministic by default):

- ``[provider] provider_id`` — readiness provider registry selector
  (``deterministic_mock`` default; the three ``foundry_*`` IDs are
  scaffold-only and fail closed). The legacy ``ai_backend_type`` key is kept
  for audit-record compatibility and must agree with ``provider_id``.
- ``[storage]`` — storage backend selector (``local_filesystem`` default).
  ``azure_blob`` is real for Blob-backed audit records only when an explicit
  config object selects it and ``HRHA_ENABLE_AZURE_STORAGE=true`` is set.
  Ordinary local app construction never overlays storage env vars.
- Env guards (read at resolution time, never stored in records):
  ``HRHA_ENABLE_LIVE_AZURE`` and ``HRHA_PROVIDER_KILL_SWITCH`` govern
  Foundry/provider paths; ``HRHA_ENABLE_AZURE_STORAGE`` is the narrower gate
  for the Azure Blob storage backend. ``HRHA_ENABLE_AZURE_WORKFLOW_STORAGE``
  is the E8 storage-only gate for Workflow Table/Blob/Queue adapters.

PLAN DEVIATION (recorded): the implementation plan assumed stdlib ``tomllib``
(Python 3.11+). This environment runs Python 3.10, so we fall back to the
``tomli`` package, which is API-compatible.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

try:  # Python 3.11+
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # Python 3.10 fallback (see module docstring)
    import tomli as tomllib  # type: ignore[no-redef]

RigorMode = Literal["standard", "high_impact", "escalated"]
EscalationPolicy = Literal["record_only", "auto_escalate"]
AiBackendType = Literal["none", "foundry_agents"]

#: Readiness-pack provider identifiers. ``deterministic_mock`` is the only
#: functional provider; the three ``foundry_*`` IDs select scaffold-only
#: providers that fail closed (live wiring is human-gated by the deferred ADR;
#: the final enumeration is ADR question 2 — these IDs decide nothing).
ProviderId = Literal[
    "deterministic_mock",
    "foundry_project_responses",
    "foundry_prompt_agent",
    "foundry_hosted_agent",
]

FOUNDRY_PROVIDER_IDS = frozenset(
    {"foundry_project_responses", "foundry_prompt_agent", "foundry_hosted_agent"}
)

#: provider_id -> legacy ai_backend_type family (recorded in audit records).
PROVIDER_BACKEND_FAMILY: dict[str, AiBackendType] = {
    "deterministic_mock": "none",
    "foundry_project_responses": "foundry_agents",
    "foundry_prompt_agent": "foundry_agents",
    "foundry_hosted_agent": "foundry_agents",
}

#: Storage backend selector. ``local_filesystem`` is the default; ``azure_blob``
#: is guarded and limited to evaluation record/artifact persistence.
StorageBackendId = Literal["local_filesystem", "azure_blob"]

#: Workflow storage backend selector. ``local`` is the deterministic default;
#: ``azure`` is guarded and limited to E7 workflow Table/Blob/Queue contracts.
WorkflowStorageBackendId = Literal["local", "azure"]

#: Foundry live-path switch. Unset/anything-but-"true" keeps live AI paths
#: disabled (the lab default). Azure Blob storage has its own narrower gate.
ENV_ENABLE_LIVE_AZURE = "HRHA_ENABLE_LIVE_AZURE"
#: Hard block on Foundry providers, independent of all other configuration.
ENV_PROVIDER_KILL_SWITCH = "HRHA_PROVIDER_KILL_SWITCH"
#: Narrow live-storage gate. Read only when azure_blob is explicitly selected.
ENV_ENABLE_AZURE_STORAGE = "HRHA_ENABLE_AZURE_STORAGE"
#: E8 guarded workflow storage gate. Read only when workflow backend is azure.
ENV_ENABLE_AZURE_WORKFLOW_STORAGE = "HRHA_ENABLE_AZURE_WORKFLOW_STORAGE"
#: Azure Functions wrapper-only storage backend overlay.
ENV_STORAGE_BACKEND = "HRHA_STORAGE_BACKEND"
ENV_STORAGE_ACCOUNT_URL = "HRHA_STORAGE_ACCOUNT_URL"
ENV_STORAGE_CONTAINER = "HRHA_STORAGE_CONTAINER"
ENV_STORAGE_TABLE_ENDPOINT = "HRHA_STORAGE_TABLE_ENDPOINT"
ENV_STORAGE_QUEUE_ENDPOINT = "HRHA_STORAGE_QUEUE_ENDPOINT"
ENV_WORKFLOW_STORAGE_BACKEND = "HRHA_WORKFLOW_STORAGE_BACKEND"
ENV_WORKFLOW_BLOB_CONTAINER = "HRHA_WORKFLOW_BLOB_CONTAINER"
ENV_WORKFLOW_TABLE_PREFIX = "HRHA_WORKFLOW_TABLE_PREFIX"
ENV_WORKFLOW_QUEUE_NAME = "HRHA_WORKFLOW_QUEUE_NAME"
ENV_MANAGED_IDENTITY_CLIENT_ID = "HRHA_MANAGED_IDENTITY_CLIENT_ID"

DEFAULT_CONFIG_PATH = Path("config") / "lab-config.toml"


def live_azure_enabled() -> bool:
    """True only when HRHA_ENABLE_LIVE_AZURE is explicitly 'true' (lab default: false)."""
    return os.environ.get(ENV_ENABLE_LIVE_AZURE, "false").strip().lower() == "true"


def provider_kill_switch_active() -> bool:
    """True when HRHA_PROVIDER_KILL_SWITCH=true — blocks all Foundry providers."""
    return os.environ.get(ENV_PROVIDER_KILL_SWITCH, "false").strip().lower() == "true"


def azure_storage_enabled() -> bool:
    """True only when HRHA_ENABLE_AZURE_STORAGE is explicitly 'true'."""
    return os.environ.get(ENV_ENABLE_AZURE_STORAGE, "false").strip().lower() == "true"


def azure_workflow_storage_enabled() -> bool:
    """True only when HRHA_ENABLE_AZURE_WORKFLOW_STORAGE is explicitly 'true'."""
    return (
        os.environ.get(ENV_ENABLE_AZURE_WORKFLOW_STORAGE, "false").strip().lower()
        == "true"
    )


class RigorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    default_mode: RigorMode = "high_impact"


class EscalationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy: EscalationPolicy = "record_only"


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ai_backend_type: AiBackendType = "none"
    provider_id: ProviderId = "deterministic_mock"

    @model_validator(mode="after")
    def _family_consistency(self) -> "ProviderConfig":
        expected = PROVIDER_BACKEND_FAMILY[self.provider_id]
        if self.ai_backend_type != expected:
            raise ValueError(
                f"provider.ai_backend_type '{self.ai_backend_type}' is inconsistent "
                f"with provider.provider_id '{self.provider_id}' "
                f"(expected '{expected}')"
            )
        return self


class PersistenceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    root: str = "var/lab-data"


class AzureStorageConfig(BaseModel):
    """Blob storage settings. Empty by default; no secrets ever.

    ``table_endpoint`` and ``queue_endpoint`` are used only by explicit E8
    workflow-storage paths. They remain empty in committed local defaults.
    """

    model_config = ConfigDict(extra="forbid")
    account_url: str = ""  # e.g. https://<storage-account>.blob.core.windows.net (placeholder)
    container: str = ""  # e.g. hrha-evaluations (placeholder)
    table_endpoint: str = ""  # e.g. https://<storage-account>.table.core.windows.net (placeholder)
    queue_endpoint: str = ""  # e.g. https://<storage-account>.queue.core.windows.net (placeholder)


class StorageConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    backend: StorageBackendId = "local_filesystem"
    azure: AzureStorageConfig = AzureStorageConfig()


class WorkflowStorageConfig(BaseModel):
    """E8 workflow Table/Blob/Queue storage selector.

    ``backend = "local"`` is the default deterministic path. ``azure`` is
    selected only by explicit config objects or the Azure Functions overlay.
    """

    model_config = ConfigDict(extra="forbid")
    backend: WorkflowStorageBackendId = "local"
    blob_container: str = ""  # optional override; defaults to storage.azure.container
    table_prefix: str = ""  # optional alphanumeric prefix for all workflow tables
    queue_name: str = "workflow-jobs"


class LabConfig(BaseModel):
    """Typed, validated view of config/lab-config.toml."""

    model_config = ConfigDict(extra="forbid")

    rigor: RigorConfig = RigorConfig()
    escalation: EscalationConfig = EscalationConfig()
    provider: ProviderConfig = ProviderConfig()
    persistence: PersistenceConfig = PersistenceConfig()
    storage: StorageConfig = StorageConfig()
    workflow_storage: WorkflowStorageConfig = WorkflowStorageConfig()


def load_config(path: str | Path | None = None) -> LabConfig:
    """Read and validate the server-side config file (read once at app start)."""
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    with open(config_path, "rb") as fh:
        raw = tomllib.load(fh)
    return LabConfig.model_validate(raw)
