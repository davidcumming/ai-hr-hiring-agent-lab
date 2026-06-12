"""RP-005..RP-008: Azure Blob scaffold, provider registry, kill switch, mock
contract conformance (readiness pack).

Pins the disabled-by-default posture: no Azure/Foundry import on the default
path, fail-closed configuration errors, guards enforced server-side.
"""

from __future__ import annotations

import sys

import pytest

from hr_eval_lab.config import (
    AzureStorageConfig,
    LabConfig,
    ProviderConfig,
    StorageConfig,
)
from hr_eval_lab.domain.schemas.provider import (
    ProviderNotConfiguredError,
    ProviderResult,
)
from hr_eval_lab.persistence.backend import StorageNotConfiguredError, select_backend
from hr_eval_lab.providers.registry import ProviderBlockedError, resolve_provider


def test_rp005_no_azure_import_on_default_path(make_client):
    """Default app construction + a full evaluation must not import any azure
    SDK module nor the scaffold modules."""
    client = make_client()
    from tests.conftest import post_evaluation

    assert post_evaluation(client, idempotency_key="rp005").status_code == 200
    assert not [m for m in sys.modules if m.startswith("azure")]
    assert "hr_eval_lab.persistence.azure_blob_backend" not in sys.modules


def test_rp005_azure_blob_selected_without_config_fails_closed():
    config = LabConfig(storage=StorageConfig(backend="azure_blob"))
    with pytest.raises(StorageNotConfiguredError) as excinfo:
        select_backend(config)
    assert "missing" in str(excinfo.value)


def test_rp005_azure_blob_configured_but_live_disabled_fails_closed(monkeypatch):
    monkeypatch.delenv("HRHA_ENABLE_LIVE_AZURE", raising=False)
    config = LabConfig(
        storage=StorageConfig(
            backend="azure_blob",
            azure=AzureStorageConfig(
                account_url="https://placeholder.blob.core.windows.net",
                container="placeholder",
                table_endpoint="https://placeholder.table.core.windows.net",
            ),
        )
    )
    with pytest.raises(StorageNotConfiguredError) as excinfo:
        select_backend(config)
    assert "HRHA_ENABLE_LIVE_AZURE" in str(excinfo.value)


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
