"""RP-005..RP-008: Azure Blob backend, provider registry, kill switch, mock
contract conformance.

Pins the disabled-by-default posture: no Azure/Foundry import on the default
path, fail-closed configuration errors, guards enforced server-side.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from hr_eval_lab.config import (
    AzureStorageConfig,
    LabConfig,
    PersistenceConfig,
    ProviderConfig,
    StorageConfig,
)
from hr_eval_lab.domain.schemas.provider import (
    ProviderNotConfiguredError,
    ProviderResult,
)
from hr_eval_lab.persistence.backend import StorageNotConfiguredError, select_backend
from hr_eval_lab.providers.registry import ProviderBlockedError, resolve_provider
from tests.conftest import REPO_ROOT
from tests.fake_blob import FakeBlobContainerClient


def test_rp005_clean_default_app_does_not_import_azure_modules():
    """A clean local app process must not import Azure modules on construction."""
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
        "hr_eval_lab.persistence.azure_blob_backend",
        "hr_eval_lab.persistence.azure_workflow_storage",
    )
}))
"""
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    for name in (
        "HRHA_STORAGE_BACKEND",
        "HRHA_ENABLE_AZURE_STORAGE",
        "HRHA_STORAGE_ACCOUNT_URL",
        "HRHA_STORAGE_CONTAINER",
        "HRHA_STORAGE_TABLE_ENDPOINT",
        "HRHA_STORAGE_QUEUE_ENDPOINT",
        "HRHA_WORKFLOW_STORAGE_BACKEND",
        "HRHA_ENABLE_AZURE_WORKFLOW_STORAGE",
        "HRHA_WORKFLOW_BLOB_CONTAINER",
        "HRHA_WORKFLOW_TABLE_PREFIX",
        "HRHA_WORKFLOW_QUEUE_NAME",
        "HRHA_MANAGED_IDENTITY_CLIENT_ID",
    ):
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
        "hr_eval_lab.persistence.azure_blob_backend": False,
        "hr_eval_lab.persistence.azure_workflow_storage": False,
    }


def test_rp005_no_azure_import_on_default_path(make_client):
    """Default app construction + evaluation must not import Azure storage SDKs."""
    sys.modules.pop("hr_eval_lab.persistence.azure_blob_backend", None)
    sys.modules.pop("hr_eval_lab.persistence.azure_workflow_storage", None)
    client = make_client()
    from tests.conftest import post_evaluation

    assert post_evaluation(client, idempotency_key="rp005").status_code == 200
    assert not [
        m
        for m in sys.modules
        if m == "azure.identity"
        or m.startswith("azure.identity.")
        or m == "azure.storage"
        or m.startswith("azure.storage.")
        or m == "azure.data"
        or m.startswith("azure.data.")
    ]
    assert "hr_eval_lab.persistence.azure_blob_backend" not in sys.modules
    assert "hr_eval_lab.persistence.azure_workflow_storage" not in sys.modules


def test_rp005_local_app_ignores_ambient_storage_env(make_client, monkeypatch):
    monkeypatch.setenv("HRHA_STORAGE_BACKEND", "azure_blob")
    monkeypatch.setenv("HRHA_ENABLE_AZURE_STORAGE", "true")
    monkeypatch.setenv(
        "HRHA_STORAGE_ACCOUNT_URL", "https://placeholder.blob.core.windows.net"
    )
    monkeypatch.setenv("HRHA_STORAGE_CONTAINER", "placeholder")

    client = make_client()

    assert type(client.app.state.store.backend).__name__ == "LocalFilesystemBackend"
    assert client.app.state.config.storage.backend == "local_filesystem"


def test_rp005_azure_blob_selected_without_config_fails_closed():
    config = LabConfig(storage=StorageConfig(backend="azure_blob"))
    with pytest.raises(StorageNotConfiguredError) as excinfo:
        select_backend(config)
    assert "missing" in str(excinfo.value)


def test_rp005_azure_blob_configured_but_storage_disabled_fails_closed(monkeypatch):
    monkeypatch.delenv("HRHA_ENABLE_AZURE_STORAGE", raising=False)
    config = LabConfig(
        storage=StorageConfig(
            backend="azure_blob",
            azure=AzureStorageConfig(
                account_url="https://placeholder.blob.core.windows.net",
                container="placeholder",
            ),
        )
    )
    with pytest.raises(StorageNotConfiguredError) as excinfo:
        select_backend(config)
    assert "HRHA_ENABLE_AZURE_STORAGE" in str(excinfo.value)


@pytest.mark.parametrize(
    "account_url",
    [
        "DefaultEndpointsProtocol=https;AccountName=acct;AccountKey=secret",
        "https://placeholder.blob.core.windows.net?sv=2024-01-01&sig=secret",
        "https://placeholder.blob.core.windows.net/container",
    ],
)
def test_rp005_azure_blob_rejects_secret_or_blob_urls(monkeypatch, account_url):
    monkeypatch.setenv("HRHA_ENABLE_AZURE_STORAGE", "true")
    config = LabConfig(
        storage=StorageConfig(
            backend="azure_blob",
            azure=AzureStorageConfig(account_url=account_url, container="placeholder"),
        )
    )
    with pytest.raises(StorageNotConfiguredError):
        select_backend(config)


def test_rp005_azure_blob_storage_enabled_does_not_require_live_azure(monkeypatch):
    from hr_eval_lab.persistence import azure_blob_backend

    monkeypatch.setenv("HRHA_ENABLE_AZURE_STORAGE", "true")
    monkeypatch.setenv("HRHA_ENABLE_LIVE_AZURE", "false")
    monkeypatch.setenv("HRHA_PROVIDER_KILL_SWITCH", "true")
    fake = FakeBlobContainerClient()
    monkeypatch.setattr(
        azure_blob_backend, "_blob_container_client_factory", lambda azure: fake
    )
    config = LabConfig(
        storage=StorageConfig(
            backend="azure_blob",
            azure=AzureStorageConfig(
                account_url="https://placeholder.blob.core.windows.net",
                container="placeholder",
            ),
        )
    )

    backend = select_backend(config)

    assert type(backend).__name__ == "AzureBlobBackend"
    provider = resolve_provider(LabConfig())
    assert type(provider).__name__ == "DeterministicMockProvider"


def test_rp005_app_factory_fails_closed_when_azure_blob_selected(tmp_path):
    """BM-001 pin: create_app consults [storage] backend and fails closed at
    construction when azure_blob is selected without configuration."""
    from hr_eval_lab.api.app import create_app
    from hr_eval_lab.config import PersistenceConfig

    config = LabConfig(
        persistence=PersistenceConfig(root=str(tmp_path / "lab-data")),
        storage=StorageConfig(backend="azure_blob"),
    )
    with pytest.raises(StorageNotConfiguredError):
        create_app(config=config)


def test_rp005_azure_blob_round_trips_record_across_app_instances(
    make_client, monkeypatch, tmp_path
):
    """POST in one app instance, GET in another, using shared fake Blob storage."""
    from tests.conftest import HR_HEADERS, post_evaluation
    from hr_eval_lab.persistence import azure_blob_backend

    monkeypatch.setenv("HRHA_ENABLE_AZURE_STORAGE", "true")
    fake = FakeBlobContainerClient()
    monkeypatch.setattr(
        azure_blob_backend, "_blob_container_client_factory", lambda azure: fake
    )
    storage = StorageConfig(
        backend="azure_blob",
        azure=AzureStorageConfig(
            account_url="https://placeholder.blob.core.windows.net",
            container="placeholder",
        ),
    )
    config1 = LabConfig(
        persistence=PersistenceConfig(root=str(tmp_path / "app1")),
        storage=storage,
    )
    client1 = make_client(config=config1)
    post = post_evaluation(client1, idempotency_key="rp005-blob").json()
    evaluation_id = post["evaluation_id"]

    config2 = LabConfig(
        persistence=PersistenceConfig(root=str(tmp_path / "app2")),
        storage=storage,
    )
    client2 = make_client(config=config2)
    response = client2.get(f"/api/evaluations/{evaluation_id}", headers=HR_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["result"]["evaluation_id"] == evaluation_id
    assert body["result"]["result"]["ai_backend_type"] == "none"

    body_response = client2.post(
        "/api/evaluations/retrieve",
        json={"evaluation_id": evaluation_id},
        headers=HR_HEADERS,
    )
    assert body_response.status_code == 200
    body_retrieve = body_response.json()
    assert body_retrieve["status"] == "completed"
    assert body_retrieve["result"]["evaluation_id"] == evaluation_id
    assert body_retrieve["result"] == body["result"]

    assert f"evaluations/{evaluation_id}/record.json" in fake.blobs
    assert not (tmp_path / "app2" / "evaluations" / evaluation_id / "record.json").exists()


def test_rp006_default_provider_is_mock_without_foundry_imports():
    provider = resolve_provider(LabConfig())
    assert type(provider).__name__ == "DeterministicMockProvider"
    assert not [m for m in sys.modules if m.startswith("hr_eval_lab.providers.foundry.")]


def test_rp006_unknown_provider_fails_safely():
    """Unknown provider ids cannot pass config validation (closed enum)."""
    with pytest.raises(Exception) as excinfo:
        ProviderConfig(provider_id="totally_unknown")  # type: ignore[arg-type]
    assert "provider_id" in str(excinfo.value)


def test_rp006_inconsistent_backend_family_rejected():
    with pytest.raises(Exception):
        ProviderConfig(provider_id="foundry_prompt_agent", ai_backend_type="none")


@pytest.mark.parametrize(
    "provider_id",
    ["foundry_project_responses", "foundry_prompt_agent", "foundry_hosted_agent"],
)
def test_rp006_foundry_ids_blocked_while_live_disabled(monkeypatch, provider_id):
    monkeypatch.delenv("HRHA_ENABLE_LIVE_AZURE", raising=False)
    monkeypatch.delenv("HRHA_PROVIDER_KILL_SWITCH", raising=False)
    config = LabConfig(
        provider=ProviderConfig(provider_id=provider_id, ai_backend_type="foundry_agents")
    )
    with pytest.raises(ProviderBlockedError) as excinfo:
        resolve_provider(config)
    assert "HRHA_ENABLE_LIVE_AZURE" in str(excinfo.value)


def test_rp007_kill_switch_blocks_foundry_even_with_live_enabled(monkeypatch):
    monkeypatch.setenv("HRHA_ENABLE_LIVE_AZURE", "true")
    monkeypatch.setenv("HRHA_PROVIDER_KILL_SWITCH", "true")
    config = LabConfig(
        provider=ProviderConfig(
            provider_id="foundry_prompt_agent", ai_backend_type="foundry_agents"
        )
    )
    with pytest.raises(ProviderBlockedError) as excinfo:
        resolve_provider(config)
    assert "KILL_SWITCH" in str(excinfo.value)


@pytest.mark.parametrize(
    "provider_id",
    ["foundry_project_responses", "foundry_prompt_agent", "foundry_hosted_agent"],
)
def test_rp007_scaffolds_fail_closed_on_use(monkeypatch, provider_id):
    """Even with both guards opened, the scaffolds cannot execute a role."""
    monkeypatch.setenv("HRHA_ENABLE_LIVE_AZURE", "true")
    monkeypatch.setenv("HRHA_PROVIDER_KILL_SWITCH", "false")
    config = LabConfig(
        provider=ProviderConfig(provider_id=provider_id, ai_backend_type="foundry_agents")
    )
    provider = resolve_provider(config)
    with pytest.raises(ProviderNotConfiguredError):
        provider.invoke_role("merit_advocate", None, {})  # type: ignore[arg-type]


def test_rp008_mock_conforms_to_extended_provider_contract(make_client):
    """The mock stamps prompt template provenance and the new contract fields."""
    from tests.conftest import get_record, post_evaluation

    client = make_client()
    response = post_evaluation(client, idempotency_key="rp008")
    record = get_record(client, response.json()["evaluation_id"])
    model_executions = [
        e for e in record["role_executions"] if e["role_kind"] == "model"
    ]
    assert model_executions
    for execution in model_executions:
        metadata = execution["provider_metadata"]
        assert metadata["ai_backend_type"] == "none"
        assert metadata["prompt_template_id"] == f"prompt-{execution['role_id']}"
        assert metadata["prompt_template_version"] == "v1"
        assert metadata["model_or_agent_ref"] is None
        assert metadata["warnings"] == []
        assert metadata["safe_error"] is None
        # ProviderResult contract remains constructible from the metadata.
        ProviderResult.model_validate(
            {"role_id": execution["role_id"], "payload": {}, "metadata": metadata}
        )
