#!/usr/bin/env python3
"""Workflow storage configuration smoke test — DISABLED BY DEFAULT.

Default path:

- performs NO network I/O and imports NO Azure SDK;
- validates the local workflow Table/Blob/Queue store in a temp dir;
- exits 0 with a SKIPPED message for live checks.

Explicit live workflow-storage path:

- requires ``--live`` and ``HRHA_ENABLE_AZURE_WORKFLOW_STORAGE=true``;
- requires ``HRHA_WORKFLOW_STORAGE_BACKEND=azure`` and service URLs for Blob,
  Table, and Queue;
- writes and deletes one synthetic Table row, Blob artifact, and Queue
  message using the E7 contracts.

No secrets are read or printed. Intended auth is identity-based
(managed identity / DefaultAzureCredential); never keys, connection strings,
or SAS tokens.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

TS = "2026-06-13T00:00:00Z"


def _sample_case():
    from hr_eval_lab.domain.schemas.workflow import RecruitmentCase

    return RecruitmentCase(
        PartitionKey="case-e8-smoke",
        RowKey="case",
        created_at=TS,
        correlation_id="corr-e8-smoke",
        created_by_actor_id="actor-e8-smoke",
        created_by_role="hr_specialist",
        case_id="case-e8-smoke",
        case_title="Synthetic E8 smoke case",
        role_title="Storage Adapter Smoke",
        department="Synthetic Lab",
        recruitment_type="permanent",
        case_status="intake_pending",
        current_stage="case_intake",
        current_gate="role_source_required",
        hr_owner_actor_id="actor-e8-smoke",
        primary_hiring_manager_actor_id="actor-e8-manager",
    )


def _sample_message():
    from hr_eval_lab.domain.schemas.workflow_queue import (
        RunModelCandidateAssessmentMessage,
    )

    return RunModelCandidateAssessmentMessage(
        case_id="case-e8-smoke",
        candidate_id="cand-e8-smoke",
        candidate_package_version="v1",
        rubric_version="v1",
        job_id="job-e8-smoke",
        requested_by_actor_id="actor-e8-smoke",
        requested_by_role="hr_specialist",
        correlation_id="corr-e8-smoke",
    )


def _sample_blob_path() -> str:
    from hr_eval_lab.domain.schemas.workflow_artifacts import candidate_package_path

    return candidate_package_path("case-e8-smoke", "cand-e8-smoke", "v1")


def _exercise_backend(backend, queue_name: str) -> bool:
    case = _sample_case()
    blob_path = _sample_blob_path()
    message = _sample_message()

    backend.upsert_table_entity(case)
    restored = backend.get_table_entity(type(case), case.PartitionKey, case.RowKey)
    table_ok = restored is not None and restored.case_id == case.case_id

    ref = backend.write_blob_artifact(
        blob_path, {"case_id": case.case_id, "candidate_id": "cand-e8-smoke"}
    )
    blob_ok = (
        ref.blob_path == blob_path
        and backend.read_blob_json(blob_path) == {"case_id": case.case_id, "candidate_id": "cand-e8-smoke"}
    )

    before = backend.peek_queue_messages(queue_name=queue_name, max_messages=1)
    if before:
        print(
            "CONFIG ERROR (safe failure): workflow smoke queue is not empty; "
            "use a dedicated empty queue"
        )
        return False
    sent = backend.enqueue_message(message, queue_name=queue_name)
    peeked = backend.peek_queue_messages(queue_name=queue_name, max_messages=1)
    received = backend.receive_queue_messages(queue_name=queue_name, max_messages=1)
    queue_ok = (
        sent["payload"]["message_type"] == "run-model-candidate-assessment"
        and len(peeked) == 1
        and len(received) == 1
        and received[0].payload["job_id"] == "job-e8-smoke"
    )

    queue_deleted = backend.delete_queue_message(received[0])
    blob_deleted = backend.delete_blob_artifact(blob_path)
    table_deleted = backend.delete_table_entity(type(case), case.PartitionKey, case.RowKey)
    return table_ok and blob_ok and queue_ok and table_deleted and blob_deleted and queue_deleted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="explicitly request the live workflow storage check",
    )
    args = parser.parse_args()

    from hr_eval_lab.config import (
        ENV_ENABLE_AZURE_WORKFLOW_STORAGE,
        ENV_STORAGE_ACCOUNT_URL,
        ENV_STORAGE_QUEUE_ENDPOINT,
        ENV_STORAGE_TABLE_ENDPOINT,
        ENV_WORKFLOW_BLOB_CONTAINER,
        ENV_WORKFLOW_QUEUE_NAME,
        ENV_WORKFLOW_STORAGE_BACKEND,
        ENV_WORKFLOW_TABLE_PREFIX,
        AzureStorageConfig,
        LabConfig,
        StorageConfig,
        WorkflowStorageConfig,
        azure_workflow_storage_enabled,
        load_config,
    )
    from hr_eval_lab.persistence.workflow_storage import select_workflow_storage

    config = load_config(REPO_ROOT / "config" / "lab-config.toml")
    print("=== Workflow storage config smoke ===")
    print(f"workflow_storage.backend      : {config.workflow_storage.backend}")
    print(f"{ENV_WORKFLOW_STORAGE_BACKEND:<31}: {os.environ.get(ENV_WORKFLOW_STORAGE_BACKEND, 'unset')}")
    print(f"{ENV_ENABLE_AZURE_WORKFLOW_STORAGE:<31}: {azure_workflow_storage_enabled()}")
    print(f"{ENV_STORAGE_ACCOUNT_URL:<31}: {'set' if os.environ.get(ENV_STORAGE_ACCOUNT_URL) else 'unset'}")
    print(f"{ENV_STORAGE_TABLE_ENDPOINT:<31}: {'set' if os.environ.get(ENV_STORAGE_TABLE_ENDPOINT) else 'unset'}")
    print(f"{ENV_STORAGE_QUEUE_ENDPOINT:<31}: {'set' if os.environ.get(ENV_STORAGE_QUEUE_ENDPOINT) else 'unset'}")
    print(f"{ENV_WORKFLOW_BLOB_CONTAINER:<31}: {'set' if os.environ.get(ENV_WORKFLOW_BLOB_CONTAINER) else 'unset'}")
    print(f"{ENV_WORKFLOW_TABLE_PREFIX:<31}: {'set' if os.environ.get(ENV_WORKFLOW_TABLE_PREFIX) else 'unset'}")
    print(f"{ENV_WORKFLOW_QUEUE_NAME:<31}: {'set' if os.environ.get(ENV_WORKFLOW_QUEUE_NAME) else 'unset'}")

    with tempfile.TemporaryDirectory() as tmp:
        local_config = LabConfig(
            storage=config.storage,
            workflow_storage=config.workflow_storage,
        ).model_copy(update={"persistence": config.persistence.model_copy(update={"root": tmp})})
        local_backend = select_workflow_storage(local_config)
        local_ok = _exercise_backend(local_backend, queue_name="workflow-jobs")
    print(f"local workflow storage       : {'OK' if local_ok else 'FAILED'}")

    if not (args.live and azure_workflow_storage_enabled()):
        print(
            "SKIPPED: Azure workflow storage checks are disabled by default. "
            "Enable with HRHA_ENABLE_AZURE_WORKFLOW_STORAGE=true AND --live "
            "for the explicit workflow storage smoke path."
        )
        return 0 if local_ok else 2

    if os.environ.get(ENV_WORKFLOW_STORAGE_BACKEND, "").strip() != "azure":
        print("CONFIG ERROR (safe failure): HRHA_WORKFLOW_STORAGE_BACKEND must be azure")
        return 2

    queue_name = os.environ.get(ENV_WORKFLOW_QUEUE_NAME, "").strip()
    missing = [
        name
        for name, value in (
            (ENV_STORAGE_ACCOUNT_URL, os.environ.get(ENV_STORAGE_ACCOUNT_URL, "")),
            (ENV_STORAGE_TABLE_ENDPOINT, os.environ.get(ENV_STORAGE_TABLE_ENDPOINT, "")),
            (ENV_STORAGE_QUEUE_ENDPOINT, os.environ.get(ENV_STORAGE_QUEUE_ENDPOINT, "")),
            (ENV_WORKFLOW_BLOB_CONTAINER, os.environ.get(ENV_WORKFLOW_BLOB_CONTAINER, "")),
            (ENV_WORKFLOW_QUEUE_NAME, queue_name),
        )
        if not value.strip()
    ]
    if missing:
        print(f"CONFIG ERROR (safe failure): missing settings: {', '.join(missing)}")
        return 2

    live_config = LabConfig(
        storage=StorageConfig(
            azure=AzureStorageConfig(
                account_url=os.environ.get(ENV_STORAGE_ACCOUNT_URL, ""),
                container=os.environ.get(ENV_WORKFLOW_BLOB_CONTAINER, ""),
                table_endpoint=os.environ.get(ENV_STORAGE_TABLE_ENDPOINT, ""),
                queue_endpoint=os.environ.get(ENV_STORAGE_QUEUE_ENDPOINT, ""),
            )
        ),
        workflow_storage=WorkflowStorageConfig(
            backend="azure",
            blob_container=os.environ.get(ENV_WORKFLOW_BLOB_CONTAINER, ""),
            table_prefix=os.environ.get(ENV_WORKFLOW_TABLE_PREFIX, ""),
            queue_name=queue_name,
        ),
    )
    try:
        live_backend = select_workflow_storage(live_config)
        live_ok = _exercise_backend(live_backend, queue_name=queue_name)
    except Exception as exc:
        print(f"CONFIG ERROR (safe failure): {exc}")
        return 2

    print(f"Azure workflow storage       : {'OK' if live_ok else 'FAILED'}")
    return 0 if local_ok and live_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
