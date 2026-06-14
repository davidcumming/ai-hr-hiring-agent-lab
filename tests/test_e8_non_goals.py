"""E8 non-goal pins updated after E10's narrow document API foundation."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from tests.conftest import REPO_ROOT


WORKFLOW_ENV_NAMES = (
    "HRHA_WORKFLOW_STORAGE_BACKEND",
    "HRHA_ENABLE_AZURE_WORKFLOW_STORAGE",
    "HRHA_STORAGE_ACCOUNT_URL",
    "HRHA_STORAGE_CONTAINER",
    "HRHA_STORAGE_TABLE_ENDPOINT",
    "HRHA_STORAGE_QUEUE_ENDPOINT",
    "HRHA_WORKFLOW_BLOB_CONTAINER",
    "HRHA_WORKFLOW_TABLE_PREFIX",
    "HRHA_WORKFLOW_QUEUE_NAME",
    "HRHA_MANAGED_IDENTITY_CLIENT_ID",
)

CASE_PATHS = {
    "/api/cases",
    "/api/cases/{case_id}",
    "/api/cases/{case_id}/next-actions",
    "/api/cases/{case_id}/source-documents",
    "/api/cases/{case_id}/source-documents/{document_id}",
}


def test_e8_default_app_selects_local_workflow_storage_with_expected_case_routes(
    make_client,
):
    client = make_client()
    paths = set(client.app.openapi()["paths"])

    assert type(client.app.state.workflow_storage).__name__ == "LocalWorkflowStore"
    assert client.app.state.config.workflow_storage.backend == "local"
    assert {path for path in paths if path.startswith("/api/cases")} == CASE_PATHS
    assert not any("notifications" in path for path in paths)
    assert not any("workflow" in path for path in paths)


def test_e8_local_app_ignores_ambient_workflow_storage_env(make_client, monkeypatch):
    monkeypatch.setenv("HRHA_WORKFLOW_STORAGE_BACKEND", "azure")
    monkeypatch.setenv("HRHA_ENABLE_AZURE_WORKFLOW_STORAGE", "true")
    monkeypatch.setenv(
        "HRHA_STORAGE_ACCOUNT_URL", "https://placeholder.blob.core.windows.net"
    )
    monkeypatch.setenv(
        "HRHA_STORAGE_TABLE_ENDPOINT", "https://placeholder.table.core.windows.net"
    )
    monkeypatch.setenv(
        "HRHA_STORAGE_QUEUE_ENDPOINT", "https://placeholder.queue.core.windows.net"
    )
    monkeypatch.setenv("HRHA_WORKFLOW_BLOB_CONTAINER", "hrha-evaluations")
    monkeypatch.setenv("HRHA_WORKFLOW_QUEUE_NAME", "hrha-workflow-smoke")

    client = make_client()

    assert type(client.app.state.workflow_storage).__name__ == "LocalWorkflowStore"
    assert client.app.state.config.workflow_storage.backend == "local"


def test_e8_clean_default_app_does_not_import_azure_workflow_modules():
    script = """
import json
import sys
import tempfile

from hr_eval_lab.api.app import create_app
from hr_eval_lab.config import LabConfig, PersistenceConfig

create_app(config=LabConfig(persistence=PersistenceConfig(root=tempfile.mkdtemp())))
print(json.dumps({
    name: name in sys.modules
    for name in (
        "azure",
        "azure.identity",
        "azure.storage",
        "azure.storage.blob",
        "azure.storage.queue",
        "azure.data",
        "azure.data.tables",
        "hr_eval_lab.persistence.azure_workflow_storage",
    )
}))
"""
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    for name in WORKFLOW_ENV_NAMES:
        env.pop(name, None)
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    loaded = json.loads(result.stdout.splitlines()[-1])
    assert loaded == {
        "azure": False,
        "azure.identity": False,
        "azure.storage": False,
        "azure.storage.blob": False,
        "azure.storage.queue": False,
        "azure.data": False,
        "azure.data.tables": False,
        "hr_eval_lab.persistence.azure_workflow_storage": False,
    }
