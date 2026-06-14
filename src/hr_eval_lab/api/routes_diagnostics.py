"""Guarded troubleshooting diagnostics for workflow storage.

Diagnostics are hidden from OpenAPI and disabled unless
``HRHA_ENABLE_DIAGNOSTICS=true``. They operate only through the existing
workflow storage seam and return redacted, troubleshooting-oriented facts.
"""

from __future__ import annotations

import os
import re
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from hr_eval_lab.api.auth import authenticate_and_authorize
from hr_eval_lab.config import (
    ENV_ENABLE_DIAGNOSTICS,
    ENV_MANAGED_IDENTITY_CLIENT_ID,
    azure_workflow_storage_enabled,
    diagnostics_enabled,
)
from hr_eval_lab.domain.schemas.cases import CaseEnvelope
from hr_eval_lab.domain.schemas.workflow import RecruitmentCase
from hr_eval_lab.domain.schemas.workflow_artifacts import role_intake_artifact_path
from hr_eval_lab.domain.schemas.workflow_queue import WriteNotificationMessage
from hr_eval_lab.persistence.workflow_storage import (
    WorkflowQueueReceivedMessage,
    WorkflowStorageBackend,
)

router = APIRouter()

DIAG_CASE_ID = "case-diag-workflow-storage"
DIAG_CORRELATION_ID = "corr-diag-workflow-storage"
DIAG_ACTOR_ID = "diag-workflow-storage"
DIAG_ROLE = "hr_specialist"
DIAG_BLOB_VERSION = "diag-workflow-storage"

_MAX_SAFE_ERROR_CHARS = 320
_SECRET_PATTERNS = (
    re.compile(r"(?i)(DefaultEndpointsProtocol=)[^;\s]+"),
    re.compile(r"(?i)(AccountKey=)[^;\s]+"),
    re.compile(r"(?i)(SharedAccessSignature=)[^;\s]+"),
    re.compile(r"(?i)(x-functions-key\s*[:=]\s*)[^\s;]+"),
    re.compile(r"(?i)(authorization\s*[:=]\s*Bearer\s+)[^\s;]+"),
    re.compile(r"(?i)(sig=)[^&\s;]+"),
    re.compile(r"(?i)(client_secret\s*[:=]\s*)[^\s;]+"),
    re.compile(r"(?i)(connection\s*string\s*[:=]\s*)[^\s;]+"),
    re.compile(r"https?://[^\s,;]+"),
)


def _env_true(value: str | None) -> bool:
    return (value or "").strip().lower() == "true"


def _is_set(value: str | None) -> bool:
    return bool((value or "").strip())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_error_message(exc: Exception) -> str:
    text = str(exc) or exc.__class__.__name__
    text = re.sub(r"(?is)\bTraceback\b.*", "[redacted traceback]", text)
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[redacted]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > _MAX_SAFE_ERROR_CHARS:
        text = text[: _MAX_SAFE_ERROR_CHARS - 3].rstrip() + "..."
    return text


def _ok(**details: Any) -> dict[str, Any]:
    return {"status": "ok", **details}


def _skipped(reason: str) -> dict[str, Any]:
    return {"status": "skipped", "reason": reason}


def _failed(exc: Exception) -> dict[str, Any]:
    return {
        "status": "failed",
        "error_class": exc.__class__.__name__,
        "safe_error_message": _safe_error_message(exc),
    }


def _diagnostic_case() -> RecruitmentCase:
    now = _utc_now()
    return RecruitmentCase(
        PartitionKey=DIAG_CASE_ID,
        RowKey="case",
        case_id=DIAG_CASE_ID,
        case_title="Workflow storage diagnostic case",
        role_title="Workflow storage diagnostic",
        department="Diagnostics",
        recruitment_type="diagnostic",
        case_status="intake_pending",
        current_stage="diagnostic",
        current_gate="diagnostic",
        hr_owner_actor_id=DIAG_ACTOR_ID,
        entity_type="RecruitmentCases",
        created_at=now,
        updated_at=now,
        created_by_actor_id=DIAG_ACTOR_ID,
        created_by_role=DIAG_ROLE,
        updated_by_actor_id=DIAG_ACTOR_ID,
        updated_by_role=DIAG_ROLE,
        correlation_id=DIAG_CORRELATION_ID,
        synthetic=True,
    )


def _diagnostic_blob_path() -> str:
    return role_intake_artifact_path(DIAG_CASE_ID, DIAG_BLOB_VERSION)


def _diagnostic_queue_message() -> WriteNotificationMessage:
    return WriteNotificationMessage(
        case_id=DIAG_CASE_ID,
        correlation_id=DIAG_CORRELATION_ID,
        recipient_actor_ids=[DIAG_ACTOR_ID],
        notification_type="gate_blocked",
        source_job_id="job-diag-workflow-storage",
    )


def _payload_matches(message: dict[str, Any] | WorkflowQueueReceivedMessage) -> bool:
    payload = message.payload if isinstance(message, WorkflowQueueReceivedMessage) else (
        message.get("payload") or {}
    )
    return payload == _diagnostic_queue_message().to_queue_payload()


def _run_table_diagnostic(storage: WorkflowStorageBackend) -> dict[str, Any]:
    try:
        entity = _diagnostic_case()
        storage.upsert_table_entity(entity)
        retrieved = storage.get_table_entity(RecruitmentCase, DIAG_CASE_ID, "case")
        if retrieved is None:
            raise RuntimeError("diagnostic table read did not return the synthetic row")
        if retrieved.case_id != DIAG_CASE_ID:
            raise RuntimeError("diagnostic table read returned an unexpected row")
        deleted = storage.delete_table_entity(RecruitmentCase, DIAG_CASE_ID, "case")
        if not deleted:
            raise RuntimeError("diagnostic table delete did not remove the synthetic row")
        return _ok(row_written=True, row_read=True, row_deleted=True)
    except Exception as exc:
        return _failed(exc)
    finally:
        with suppress(Exception):
            storage.delete_table_entity(RecruitmentCase, DIAG_CASE_ID, "case")


def _run_blob_diagnostic(storage: WorkflowStorageBackend) -> dict[str, Any]:
    blob_path = _diagnostic_blob_path()
    payload = {
        "diagnostic": "workflow_storage",
        "case_id": DIAG_CASE_ID,
        "correlation_id": DIAG_CORRELATION_ID,
        "synthetic": True,
    }
    try:
        storage.write_blob_artifact(blob_path, payload)
        read_payload = storage.read_blob_json(blob_path)
        if read_payload != payload:
            raise RuntimeError("diagnostic blob read did not match the synthetic payload")
        deleted = storage.delete_blob_artifact(blob_path)
        if not deleted:
            raise RuntimeError("diagnostic blob delete did not remove the synthetic blob")
        return _ok(blob_written=True, blob_read=True, blob_deleted=True)
    except Exception as exc:
        return _failed(exc)
    finally:
        with suppress(Exception):
            storage.delete_blob_artifact(blob_path)


def _run_queue_diagnostic(
    storage: WorkflowStorageBackend, queue_name: str | None
) -> dict[str, Any]:
    if not _is_set(queue_name):
        return _skipped("workflow queue name is not configured")

    received_message: WorkflowQueueReceivedMessage | None = None
    try:
        existing = storage.peek_queue_messages(queue_name=queue_name, max_messages=1)
        if existing:
            return _skipped(
                "configured workflow queue is not empty; receive/delete probe skipped"
            )

        message = _diagnostic_queue_message()
        storage.enqueue_message(message, queue_name=queue_name)
        peeked = storage.peek_queue_messages(queue_name=queue_name, max_messages=1)
        if not peeked or not _payload_matches(peeked[0]):
            raise RuntimeError("diagnostic queue peek did not return the synthetic message")

        received = storage.receive_queue_messages(
            queue_name=queue_name,
            max_messages=1,
            visibility_timeout=30,
        )
        if not received:
            raise RuntimeError("diagnostic queue receive returned no message")
        received_message = received[0]
        if not _payload_matches(received_message):
            received_message = None
            raise RuntimeError(
                "diagnostic queue receive returned a non-diagnostic message"
            )

        deleted = storage.delete_queue_message(
            received_message,
            queue_name=queue_name,
        )
        if not deleted:
            raise RuntimeError("diagnostic queue delete did not remove the message")
        received_message = None
        return _ok(message_enqueued=True, message_peeked=True, message_deleted=True)
    except Exception as exc:
        return _failed(exc)
    finally:
        if received_message is not None:
            with suppress(Exception):
                storage.delete_queue_message(received_message, queue_name=queue_name)


def _safe_config_facts(request: Request) -> dict[str, Any]:
    config = request.app.state.config
    workflow = config.workflow_storage
    azure = config.storage.azure
    return {
        "selected_workflow_storage_class": type(
            request.app.state.workflow_storage
        ).__name__,
        "config_workflow_backend": workflow.backend,
        "azure_workflow_storage_guard_enabled": azure_workflow_storage_enabled(),
        "storage_account_url_set": _is_set(azure.account_url),
        "storage_table_endpoint_set": _is_set(azure.table_endpoint),
        "storage_queue_endpoint_set": _is_set(azure.queue_endpoint),
        "workflow_blob_container_set": _is_set(
            workflow.blob_container or azure.container
        ),
        "workflow_queue_name_set": _is_set(workflow.queue_name),
        "managed_identity_client_id_set": _is_set(
            os.environ.get(ENV_MANAGED_IDENTITY_CLIENT_ID)
        ),
    }


@router.get("/api/diagnostics/workflow-storage", include_in_schema=False)
async def get_workflow_storage_diagnostics(request: Request) -> CaseEnvelope:
    """Run guarded, synthetic workflow storage diagnostics."""

    if not diagnostics_enabled():
        raise HTTPException(status_code=404, detail="Not Found")

    authenticate_and_authorize(request)
    storage = request.app.state.workflow_storage
    config = request.app.state.config
    result = {
        "diagnostics_enabled": _env_true(os.environ.get(ENV_ENABLE_DIAGNOSTICS)),
        "config": _safe_config_facts(request),
        "operations": {
            "table": _run_table_diagnostic(storage),
            "blob": _run_blob_diagnostic(storage),
            "queue": _run_queue_diagnostic(storage, config.workflow_storage.queue_name),
        },
    }
    return CaseEnvelope(
        status="completed",
        user_message="Workflow storage diagnostics completed.",
        safe_details="Guarded troubleshooting-only diagnostic; no secret values returned.",
        result=result,
    )
