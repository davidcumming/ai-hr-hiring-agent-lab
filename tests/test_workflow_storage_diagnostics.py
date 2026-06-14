"""Guarded workflow storage diagnostics coverage."""

from __future__ import annotations

import json
from typing import Any

from hr_eval_lab.domain.schemas.workflow import RecruitmentCase
from hr_eval_lab.domain.schemas.workflow_artifacts import role_intake_artifact_path
from tests.conftest import HR_HEADERS, identity_headers

DIAG_PATH = "/api/diagnostics/workflow-storage"
DIAG_CASE_ID = "case-diag-workflow-storage"
DIAG_BLOB_PATH = role_intake_artifact_path(
    DIAG_CASE_ID,
    "diag-workflow-storage",
)


def test_workflow_storage_diagnostics_disabled_by_default(client, monkeypatch):
    monkeypatch.delenv("HRHA_ENABLE_DIAGNOSTICS", raising=False)

    response = client.get(DIAG_PATH, headers=HR_HEADERS)

    assert response.status_code == 404
    assert DIAG_PATH not in client.app.openapi()["paths"]


def test_workflow_storage_diagnostics_requires_hr_auth_when_enabled(client, monkeypatch):
    monkeypatch.setenv("HRHA_ENABLE_DIAGNOSTICS", "true")

    missing_identity = client.get(DIAG_PATH)
    wrong_role = client.get(
        DIAG_PATH,
        headers=identity_headers(actor_id="u-reviewer-diag", roles="reviewer"),
    )

    assert missing_identity.status_code == 401
    assert missing_identity.json()["status"] == "unauthorized"
    assert wrong_role.status_code == 403
    assert wrong_role.json()["status"] == "unauthorized"


def test_workflow_storage_diagnostics_local_backend_succeeds(client, monkeypatch):
    monkeypatch.setenv("HRHA_ENABLE_DIAGNOSTICS", "true")

    response = client.get(DIAG_PATH, headers=HR_HEADERS)

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"
    result = envelope["result"]
    assert result["diagnostics_enabled"] is True
    assert result["config"] == {
        "selected_workflow_storage_class": "LocalWorkflowStore",
        "config_workflow_backend": "local",
        "azure_workflow_storage_guard_enabled": False,
        "storage_account_url_set": False,
        "storage_table_endpoint_set": False,
        "storage_queue_endpoint_set": False,
        "workflow_blob_container_set": False,
        "workflow_queue_name_set": True,
        "managed_identity_client_id_set": False,
    }
    assert result["operations"]["table"]["status"] == "ok"
    assert result["operations"]["blob"]["status"] == "ok"
    assert result["operations"]["queue"]["status"] == "ok"

    store = client.app.state.workflow_storage
    queue_name = client.app.state.config.workflow_storage.queue_name
    assert store.get_table_entity(RecruitmentCase, DIAG_CASE_ID, "case") is None
    assert store.read_blob_json(DIAG_BLOB_PATH) is None
    assert store.peek_queue_messages(queue_name=queue_name) == []


class SecretFailure(RuntimeError):
    pass


class FailingWorkflowStorage:
    def upsert_table_entity(self, entity: Any) -> dict[str, Any]:
        del entity
        raise SecretFailure(
            "table failure AccountKey=super-secret-key\n"
            "Traceback (most recent call last): raw stack should not leak"
        )

    def get_table_entity(
        self,
        model: type[Any],
        partition_key: str,
        row_key: str,
    ) -> Any:
        del model, partition_key, row_key
        return None

    def list_table_entities(
        self,
        model: type[Any],
        partition_key: str | None = None,
    ) -> list[Any]:
        del model, partition_key
        return []

    def delete_table_entity(
        self,
        model: type[Any],
        partition_key: str,
        row_key: str,
    ) -> bool:
        del model, partition_key, row_key
        return False

    def write_blob_artifact(self, blob_path: str, payload: Any) -> Any:
        del blob_path, payload
        raise SecretFailure(
            "blob failure SharedAccessSignature=hidden-sas "
            "https://storage.example/container?sig=hidden-signature"
        )

    def read_blob_bytes(self, blob_path: str) -> bytes | None:
        del blob_path
        return None

    def read_blob_json(self, blob_path: str) -> Any:
        del blob_path
        return None

    def delete_blob_artifact(self, blob_path: str) -> bool:
        del blob_path
        return False

    def enqueue_message(
        self,
        message: Any,
        queue_name: str = "workflow-jobs",
    ) -> dict[str, Any]:
        del message, queue_name
        return {}

    def peek_queue_messages(
        self,
        queue_name: str = "workflow-jobs",
        max_messages: int = 1,
    ) -> list[dict[str, Any]]:
        del queue_name, max_messages
        raise SecretFailure(
            "queue failure DefaultEndpointsProtocol=https;AccountKey=hidden "
            "x-functions-key=hidden-function-key"
        )

    def receive_queue_messages(
        self,
        queue_name: str = "workflow-jobs",
        max_messages: int = 1,
        visibility_timeout: int | None = None,
    ) -> list[Any]:
        del queue_name, max_messages, visibility_timeout
        return []

    def delete_queue_message(
        self,
        message: Any,
        pop_receipt: str | None = None,
        queue_name: str = "workflow-jobs",
    ) -> bool:
        del message, pop_receipt, queue_name
        return False


def test_workflow_storage_diagnostics_failure_redacts_safe_error(
    client, monkeypatch
):
    monkeypatch.setenv("HRHA_ENABLE_DIAGNOSTICS", "true")
    client.app.state.workflow_storage = FailingWorkflowStorage()

    response = client.get(DIAG_PATH, headers=HR_HEADERS)

    assert response.status_code == 200
    operations = response.json()["result"]["operations"]
    assert operations["table"]["status"] == "failed"
    assert operations["table"]["error_class"] == "SecretFailure"
    assert operations["blob"]["status"] == "failed"
    assert operations["queue"]["status"] == "failed"

    serialized = json.dumps(response.json())
    for forbidden in (
        "super-secret-key",
        "hidden-sas",
        "hidden-signature",
        "hidden-function-key",
        "Traceback",
        "AccountKey",
        "SharedAccessSignature",
        "DefaultEndpointsProtocol",
        "x-functions-key",
        "https://storage.example",
    ):
        assert forbidden not in serialized
