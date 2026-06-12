#!/usr/bin/env python3
"""FUTURE Foundry configuration smoke test — DISABLED BY DEFAULT (target 7.2).

This scaffold exists so that, on the day live wiring is approved (human-gated
deferred ADR), a config sanity check already exists. Today it:

- performs NO network I/O and imports NO Azure/Foundry SDK unless BOTH
  ``HRHA_ENABLE_LIVE_AZURE=true`` AND ``--live`` are supplied;
- in the default (disabled) path, only reports which guards/placeholders are
  set, then exits 0 with a "skipped" message;
- fails safely (clear config error, no stack trace, exit 2) if the live path
  is requested but configuration is incomplete — which it always is in this
  batch, because live wiring is deferred.

No secrets are read or printed; placeholder names only.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

PLACEHOLDER_SETTINGS = (
    "HRHA_FOUNDRY_PROJECT_ENDPOINT",
    "HRHA_FOUNDRY_MODEL_DEPLOYMENT",
    "HRHA_FOUNDRY_AGENT_ID_PREFIX",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="explicitly request the live config check (also requires HRHA_ENABLE_LIVE_AZURE=true)",
    )
    args = parser.parse_args()

    from hr_eval_lab.config import (
        live_azure_enabled,
        load_config,
        provider_kill_switch_active,
    )

    config = load_config(REPO_ROOT / "config" / "lab-config.toml")
    print("=== Foundry config smoke (scaffold) ===")
    print(f"provider_id                : {config.provider.provider_id}")
    print(f"HRHA_ENABLE_LIVE_AZURE     : {live_azure_enabled()}")
    print(f"HRHA_PROVIDER_KILL_SWITCH  : {provider_kill_switch_active()}")
    for name in PLACEHOLDER_SETTINGS:
        print(f"{name:<27}: {'set' if os.environ.get(name) else 'unset (placeholder)'}")

    if not (args.live and live_azure_enabled()):
        print(
            "SKIPPED: live Foundry checks are disabled by default. Enable with "
            "HRHA_ENABLE_LIVE_AZURE=true AND --live — only after the deferred "
            "Foundry-wiring ADR is human-approved."
        )
        return 0

    if provider_kill_switch_active():
        print("BLOCKED: HRHA_PROVIDER_KILL_SWITCH is active; refusing live checks.")
        return 2

    missing = [name for name in PLACEHOLDER_SETTINGS if not os.environ.get(name)]
    if missing:
        print(f"CONFIG ERROR (safe failure): missing settings: {', '.join(missing)}")
        print("Live Foundry wiring is deferred in this batch; this is expected.")
        return 2

    # Live path intentionally unimplemented in this batch (deferred ADR).
    print(
        "CONFIG ERROR (safe failure): live Foundry connectivity checks are not "
        "implemented in this batch — live wiring is deferred and human-gated."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
