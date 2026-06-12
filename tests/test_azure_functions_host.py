"""Azure Functions host wrapper tests.

These assertions pin the bridge layer only: importability, route-prefix
configuration, deterministic defaults, and deployment ignore hygiene. They do
not call Azure or enable any live backend.
"""

from __future__ import annotations

import fnmatch
import importlib
import json
import sys
from pathlib import Path

import pytest

from tests.conftest import REPO_ROOT
from tests.fake_blob import FakeBlobContainerClient

HOST_PATH = REPO_ROOT / "host.json"
FUNCIGNORE_PATH = REPO_ROOT / ".funcignore"

REQUIRED_EXCLUDES = {
    ".git/",
    ".venv/",
    "venv/",
    ".pytest_cache/",
    "__pycache__/",
    "**/__pycache__/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".local/",
    "var/",
    ".deploy/",
    ".coverage",
    ".coverage.*",
    "coverage.xml",
    "*.log",
    "*.tmp",
    "local.settings.json",
    ".env",
    ".env.*",
}

REQUIRED_RUNTIME_PATHS = {
    "src/hr_eval_lab/api/app.py",
    "config/lab-config.toml",
    "fixtures/manifest.json",
    "pyproject.toml",
    "requirements.txt",
    "function_app.py",
    "host.json",
    "openapi/evaluations-api.json",
}

STORAGE_ENV_NAMES = (
    "HRHA_STORAGE_BACKEND",
    "HRHA_ENABLE_AZURE_STORAGE",
    "HRHA_STORAGE_ACCOUNT_URL",
    "HRHA_STORAGE_CONTAINER",
    "HRHA_STORAGE_TABLE_ENDPOINT",
    "HRHA_MANAGED_IDENTITY_CLIENT_ID",
)


def _clear_function_app_modules() -> None:
    for name in list(sys.modules):
        if name == "function_app" or name == "azure" or name.startswith("azure."):
            sys.modules.pop(name, None)


def _load_function_app_module():
    _clear_function_app_modules()
    return importlib.import_module("function_app")


@pytest.fixture()
def function_app_module(monkeypatch):
    for name in STORAGE_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    module = _load_function_app_module()
    try:
        yield module
    finally:
        _clear_function_app_modules()


def _funcignore_patterns() -> list[str]:
    return [
        line.strip()
        for line in FUNCIGNORE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _matches_funcignore(path: str, pattern: str) -> bool:
    pattern = pattern.strip()
    if pattern.endswith("/"):
        directory = pattern.rstrip("/")
        return path == directory or path.startswith(f"{directory}/")
    if "/" not in pattern:
        return fnmatch.fnmatch(Path(path).name, pattern)
    return fnmatch.fnmatch(path, pattern)


def test_function_app_imports_and_exports_asgi_app(function_app_module):
    assert function_app_module.app.__class__.__name__ == "AsgiFunctionApp"
    assert function_app_module.fastapi_app is not None


def test_host_json_preserves_fastapi_api_routes():
    host = json.loads(HOST_PATH.read_text(encoding="utf-8"))

    assert host["extensions"]["http"]["routePrefix"] == ""


def test_function_app_openapi_operation_ids_are_stable(function_app_module):
    spec = function_app_module.fastapi_app.openapi()

    assert spec["paths"]["/api/evaluations"]["post"]["operationId"] == "submitEvaluation"
    assert (
        spec["paths"]["/api/evaluations/{evaluation_id}"]["get"]["operationId"]
        == "getEvaluation"
    )


def test_function_app_defaults_remain_deterministic_and_non_live(function_app_module):
    config = function_app_module.fastapi_app.state.config

    assert config.provider.provider_id == "deterministic_mock"
    assert config.provider.ai_backend_type == "none"
    assert config.storage.backend == "local_filesystem"
    assert config.persistence.root != "var/lab-data"


def test_function_app_applies_storage_env_overlay_only_in_wrapper(monkeypatch):
    from hr_eval_lab.persistence import azure_blob_backend

    fake = FakeBlobContainerClient()
    monkeypatch.setattr(
        azure_blob_backend, "_blob_container_client_factory", lambda azure: fake
    )
    monkeypatch.setenv("HRHA_STORAGE_BACKEND", "azure_blob")
    monkeypatch.setenv("HRHA_ENABLE_AZURE_STORAGE", "true")
    monkeypatch.setenv(
        "HRHA_STORAGE_ACCOUNT_URL", "https://placeholder.blob.core.windows.net"
    )
    monkeypatch.setenv("HRHA_STORAGE_CONTAINER", "placeholder")
    monkeypatch.delenv("HRHA_STORAGE_TABLE_ENDPOINT", raising=False)

    module = _load_function_app_module()
    try:
        config = module.fastapi_app.state.config
        assert config.provider.provider_id == "deterministic_mock"
        assert config.provider.ai_backend_type == "none"
        assert config.storage.backend == "azure_blob"
        assert config.storage.azure.container == "placeholder"
        assert config.storage.azure.table_endpoint == ""
        assert type(module.fastapi_app.state.store.backend).__name__ == "AzureBlobBackend"
    finally:
        _clear_function_app_modules()


def test_funcignore_excludes_local_state_but_keeps_runtime_paths():
    patterns = _funcignore_patterns()

    assert REQUIRED_EXCLUDES <= set(patterns)
    for required_path in REQUIRED_RUNTIME_PATHS:
        assert not any(
            _matches_funcignore(required_path, pattern) for pattern in patterns
        ), f"{required_path} must remain deployable"
