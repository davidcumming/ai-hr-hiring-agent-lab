#!/usr/bin/env python3
"""FUTURE Azure storage configuration smoke test — DISABLED BY DEFAULT (target 7.3).

Scaffold for the live-wiring slice. Today it:

- performs NO network I/O and imports NO Azure SDK unless BOTH
  ``HRHA_ENABLE_LIVE_AZURE=true`` AND ``--live`` are supplied;
- in the default (disabled) path, validates only that the local filesystem
  backend works (write/read/list a throwaway artifact in a temp dir) and
  reports placeholder status, exiting 0;
- fails safely (clear config error, no stack trace, exit 2) if the live path
  is requested while configuration is incomplete — always true in this batch.

No secrets are read or printed. Intended live auth is identity-based
(managed identity / DefaultAzureCredential); never keys or connection strings.
"""

from __future__ import annotations

import argparse
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
        help="explicitly request the live storage check (also requires HRHA_ENABLE_LIVE_AZURE=true)",
    )
    args = parser.parse_args()

    from hr_eval_lab.config import live_azure_enabled, load_config
    from hr_eval_lab.persistence.backend import LocalFilesystemBackend

    config = load_config(REPO_ROOT / "config" / "lab-config.toml")
    azure = config.storage.azure
    print("=== Storage config smoke (scaffold) ===")
    print(f"storage.backend            : {config.storage.backend}")
    print(f"HRHA_ENABLE_LIVE_AZURE     : {live_azure_enabled()}")
    print(f"azure.account_url          : {'set' if azure.account_url else 'unset (placeholder)'}")
    print(f"azure.container            : {'set' if azure.container else 'unset (placeholder)'}")
    print(f"azure.table_endpoint       : {'set' if azure.table_endpoint else 'unset (placeholder)'}")

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

    if not (args.live and live_azure_enabled()):
        print(
            "SKIPPED: live Azure storage checks are disabled by default. Enable "
            "with HRHA_ENABLE_LIVE_AZURE=true AND --live — only after live "
            "wiring is human-approved."
        )
        return 0 if ok else 2

    missing = [
        name
        for name, value in (
            ("storage.azure.account_url", azure.account_url),
            ("storage.azure.container", azure.container),
            ("storage.azure.table_endpoint", azure.table_endpoint),
        )
        if not value.strip()
    ]
    if missing:
        print(f"CONFIG ERROR (safe failure): missing settings: {', '.join(missing)}")
        print("Live storage wiring is deferred in this batch; this is expected.")
        return 2

    print(
        "CONFIG ERROR (safe failure): live Azure storage connectivity checks are "
        "not implemented in this batch — wiring is deferred and human-gated."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
