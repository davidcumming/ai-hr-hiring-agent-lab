#!/usr/bin/env python3
"""Azure storage configuration smoke test — DISABLED BY DEFAULT.

Default path:

- performs NO network I/O and imports NO Azure SDK;
- validates only that the local filesystem backend works in a temp dir;
- exits 0 with a SKIPPED message.

Explicit live-storage config path:

- requires ``--live`` and ``HRHA_ENABLE_AZURE_STORAGE=true``;
- validates that ``HRHA_STORAGE_BACKEND=azure_blob`` plus Blob account URL and
  container are present;
- does not require Table Storage because Slice E3 is Blob-only record
  durability.

No secrets are read or printed. Intended live auth is identity-based
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="explicitly request the live storage config check (also requires HRHA_ENABLE_AZURE_STORAGE=true)",
    )
    args = parser.parse_args()

    from hr_eval_lab.config import (
        ENV_ENABLE_AZURE_STORAGE,
        ENV_STORAGE_ACCOUNT_URL,
        ENV_STORAGE_BACKEND,
        ENV_STORAGE_CONTAINER,
        ENV_STORAGE_TABLE_ENDPOINT,
        azure_storage_enabled,
        load_config,
    )
    from hr_eval_lab.persistence.backend import LocalFilesystemBackend

    config = load_config(REPO_ROOT / "config" / "lab-config.toml")
    print("=== Storage config smoke ===")
    print(f"storage.backend            : {config.storage.backend}")
    print(f"{ENV_STORAGE_BACKEND:<27}: {os.environ.get(ENV_STORAGE_BACKEND, 'unset')}")
    print(f"{ENV_ENABLE_AZURE_STORAGE:<27}: {azure_storage_enabled()}")
    print(f"{ENV_STORAGE_ACCOUNT_URL:<27}: {'set' if os.environ.get(ENV_STORAGE_ACCOUNT_URL) else 'unset'}")
    print(f"{ENV_STORAGE_CONTAINER:<27}: {'set' if os.environ.get(ENV_STORAGE_CONTAINER) else 'unset'}")
    print(f"{ENV_STORAGE_TABLE_ENDPOINT:<27}: {'set (optional for E3)' if os.environ.get(ENV_STORAGE_TABLE_ENDPOINT) else 'unset (optional for E3)'}")

    # Local backend sanity (no network, throwaway temp dir).
    with tempfile.TemporaryDirectory() as tmp:
        backend = LocalFilesystemBackend(tmp)
        backend.write_evaluation_record("smoke-eval", {"smoke": True})
        ref = backend.write_artifact("smoke-eval", "quality-gates", "quality-gates", [])
        ok = (
            backend.read_evaluation_record("smoke-eval") == {"smoke": True}
            and any(a.name == ref.name for a in backend.list_artifacts("smoke-eval"))
        )
    print(f"local_filesystem backend   : {'OK' if ok else 'FAILED'}")

    if not (args.live and azure_storage_enabled()):
        print(
            "SKIPPED: Azure storage checks are disabled by default. Enable "
            "with HRHA_ENABLE_AZURE_STORAGE=true AND --live for the explicit "
            "storage smoke path."
        )
        return 0 if ok else 2

    if os.environ.get(ENV_STORAGE_BACKEND, "").strip() != "azure_blob":
        print("CONFIG ERROR (safe failure): HRHA_STORAGE_BACKEND must be azure_blob")
        return 2

    missing = [
        name
        for name, value in (
            (ENV_STORAGE_ACCOUNT_URL, os.environ.get(ENV_STORAGE_ACCOUNT_URL, "")),
            (ENV_STORAGE_CONTAINER, os.environ.get(ENV_STORAGE_CONTAINER, "")),
        )
        if not value.strip()
    ]
    if missing:
        print(f"CONFIG ERROR (safe failure): missing settings: {', '.join(missing)}")
        return 2

    print(
        "OK: Azure Blob storage config is present for E3. Connectivity is "
        "validated by the hosted POST/GET smoke test, not this offline check."
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
