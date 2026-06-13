"""E7 non-goal pins: no public API, no cloud SDK path, no live model work."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from tests.conftest import REPO_ROOT


def test_e7_default_app_still_has_no_case_or_notification_api(make_client):
    client = make_client()
    paths = set(client.app.openapi()["paths"])

    assert "/api/evaluations" in paths
    assert "/api/evaluations/retrieve" in paths
    assert "/api/evaluations/{evaluation_id}" in paths
    assert not any(path.startswith("/api/cases") for path in paths)
    assert not any("notifications" in path for path in paths)


def test_e7_workflow_store_import_does_not_import_azure_sdks():
    script = """
import json
import sys
from hr_eval_lab.persistence.workflow_store import LocalWorkflowStore

LocalWorkflowStore("/tmp/hrha-e7-import-check")
print(json.dumps({
    name: name in sys.modules
    for name in (
        "azure",
        "azure.identity",
        "azure.storage",
        "azure.storage.blob",
        "azure.data.tables",
        "azure.storage.queue",
    )
}))
"""
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
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
        "azure.data.tables": False,
        "azure.storage.queue": False,
    }


def test_e7_default_app_remains_local_deterministic_and_mock_backed(make_client):
    client = make_client()
    config = client.app.state.config

    assert config.storage.backend == "local_filesystem"
    assert config.provider.provider_id == "deterministic_mock"
    assert config.provider.ai_backend_type == "none"
