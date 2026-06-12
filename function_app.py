"""Azure Functions ASGI host wrapper for the HR evaluation facade.

The FastAPI business app remains owned by ``hr_eval_lab.api.app.create_app``.
This module only adapts it to the Azure Functions Python worker and moves the
local filesystem persistence root to a writable runtime path for hosted smoke
tests.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import azure.functions as func

from hr_eval_lab.api.app import create_app
from hr_eval_lab.config import PersistenceConfig, load_config

HRHA_PERSISTENCE_ROOT = "HRHA_PERSISTENCE_ROOT"
REPO_ROOT = Path(__file__).resolve().parent


def _function_persistence_root() -> str:
    configured = os.environ.get(HRHA_PERSISTENCE_ROOT)
    if configured:
        return configured
    return str(Path(tempfile.gettempdir()) / "hrha-lab-data")


def _load_function_config():
    config = load_config(REPO_ROOT / "config" / "lab-config.toml")
    return config.model_copy(
        update={"persistence": PersistenceConfig(root=_function_persistence_root())}
    )


fastapi_app = create_app(
    config=_load_function_config(),
    fixtures_root=REPO_ROOT / "fixtures",
)
app = func.AsgiFunctionApp(
    app=fastapi_app,
    http_auth_level=func.AuthLevel.FUNCTION,
)
