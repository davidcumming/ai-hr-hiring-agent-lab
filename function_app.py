"""Azure Functions ASGI host wrapper for the HR evaluation facade.

The FastAPI business app remains owned by ``hr_eval_lab.api.app.create_app``.
This module only adapts it to the Azure Functions Python worker. It keeps the
repo TOML defaults local, then applies Azure Functions app-setting overlays
for hosted storage explicitly in this wrapper path.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import azure.functions as func

from hr_eval_lab.api.app import create_app
from hr_eval_lab.config import (
    ENV_STORAGE_ACCOUNT_URL,
    ENV_STORAGE_BACKEND,
    ENV_STORAGE_CONTAINER,
    ENV_STORAGE_TABLE_ENDPOINT,
    AzureStorageConfig,
    PersistenceConfig,
    StorageConfig,
    load_config,
)

HRHA_PERSISTENCE_ROOT = "HRHA_PERSISTENCE_ROOT"
REPO_ROOT = Path(__file__).resolve().parent


def _function_persistence_root() -> str:
    configured = os.environ.get(HRHA_PERSISTENCE_ROOT)
    if configured:
        return configured
    return str(Path(tempfile.gettempdir()) / "hrha-lab-data")


def _load_function_config():
    config = load_config(REPO_ROOT / "config" / "lab-config.toml")
    updates = {"persistence": PersistenceConfig(root=_function_persistence_root())}
    storage_backend = os.environ.get(ENV_STORAGE_BACKEND, "").strip()
    if storage_backend:
        if storage_backend != "azure_blob":
            raise ValueError(
                f"unsupported {ENV_STORAGE_BACKEND}={storage_backend!r}; "
                "expected 'azure_blob'"
            )
        updates["storage"] = StorageConfig(
            backend="azure_blob",
            azure=AzureStorageConfig(
                account_url=os.environ.get(ENV_STORAGE_ACCOUNT_URL, ""),
                container=os.environ.get(ENV_STORAGE_CONTAINER, ""),
                table_endpoint=os.environ.get(ENV_STORAGE_TABLE_ENDPOINT, ""),
            ),
        )
    return config.model_copy(update=updates)


fastapi_app = create_app(
    config=_load_function_config(),
    fixtures_root=REPO_ROOT / "fixtures",
)
app = func.AsgiFunctionApp(
    app=fastapi_app,
    http_auth_level=func.AuthLevel.FUNCTION,
)
