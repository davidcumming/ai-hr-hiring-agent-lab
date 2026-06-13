"""Shared validation helpers for guarded Azure storage paths."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

from hr_eval_lab.config import ENV_MANAGED_IDENTITY_CLIENT_ID
from hr_eval_lab.persistence.backend import StorageNotConfiguredError

_SECRET_MARKERS = (
    "defaultendpointsprotocol=",
    "accountkey=",
    "sharedaccesssignature=",
    "x-functions-key",
    "tenant_id",
    "subscription_id",
)

_TABLE_PREFIX_RE = re.compile(r"^[A-Za-z0-9]*$")
_TABLE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{2,62}$")
_CONTAINER_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$")
_QUEUE_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$")


def reject_secret_material(name: str, value: str) -> None:
    text = value.strip()
    lowered = text.lower()
    if ";" in text or any(marker in lowered for marker in _SECRET_MARKERS):
        raise StorageNotConfiguredError(
            f"{name} appears to contain secret-bearing connection material; "
            "use service URLs plus managed identity only"
        )


def validate_service_url(name: str, value: str) -> str:
    url = value.strip()
    reject_secret_material(name, url)
    parsed = urlparse(url)
    if parsed.query or parsed.params or parsed.fragment:
        raise StorageNotConfiguredError(
            f"{name} must not contain a SAS token, query string, params, or fragment"
        )
    if parsed.scheme != "https" or not parsed.netloc:
        raise StorageNotConfiguredError(f"{name} must be an https service URL")
    if parsed.path not in ("", "/"):
        raise StorageNotConfiguredError(
            f"{name} must be the account service URL, not a container, table, queue, or object URL"
        )
    return url.rstrip("/")


def validate_container_name(name: str, value: str) -> str:
    container = value.strip()
    reject_secret_material(name, container)
    if not _CONTAINER_RE.fullmatch(container) or "--" in container:
        raise StorageNotConfiguredError(f"{name} must be a plain Azure Blob container name")
    return container


def validate_table_prefix(value: str) -> str:
    prefix = value.strip()
    reject_secret_material("workflow_storage.table_prefix", prefix)
    if not _TABLE_PREFIX_RE.fullmatch(prefix):
        raise StorageNotConfiguredError(
            "workflow_storage.table_prefix must be alphanumeric only"
        )
    return prefix


def validate_table_name(value: str) -> str:
    table_name = value.strip()
    reject_secret_material("workflow table name", table_name)
    if not _TABLE_NAME_RE.fullmatch(table_name):
        raise StorageNotConfiguredError(
            "workflow table name must be 3-63 alphanumeric characters and start with a letter"
        )
    return table_name


def validate_queue_name(value: str) -> str:
    queue_name = value.strip()
    reject_secret_material("workflow_storage.queue_name", queue_name)
    if not _QUEUE_RE.fullmatch(queue_name) or "--" in queue_name:
        raise StorageNotConfiguredError(
            "workflow_storage.queue_name must be a plain Azure Queue name"
        )
    return queue_name


def build_identity_credential():
    """Build an identity-only Azure credential after all guards pass."""

    client_id = os.environ.get(ENV_MANAGED_IDENTITY_CLIENT_ID, "").strip()
    if client_id:
        from azure.identity import ManagedIdentityCredential

        return ManagedIdentityCredential(client_id=client_id)
    if os.environ.get("WEBSITE_SITE_NAME") or os.environ.get("FUNCTIONS_WORKER_RUNTIME"):
        from azure.identity import ManagedIdentityCredential

        return ManagedIdentityCredential()
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential(exclude_interactive_browser_credential=True)
