#!/usr/bin/env python3
"""Regenerate (or drift-check) the committed OpenAPI document (FR-010, DT-014).

Usage:
    python3 scripts/export_openapi.py            # regenerate openapi/evaluations-api.json
    python3 scripts/export_openapi.py --check    # regenerate-and-diff; exit 1 on drift

The document is generated from the live app factory so contract and
implementation cannot silently diverge (RF-005).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

OUTPUT_PATH = REPO_ROOT / "openapi" / "evaluations-api.json"


def generate() -> str:
    from hr_eval_lab.api.app import create_app
    from hr_eval_lab.config import LabConfig, PersistenceConfig

    # Generation must not touch the real persistence root or require fixtures
    # beyond the committed ones.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        config = LabConfig(persistence=PersistenceConfig(root=tmp))
        app = create_app(config=config, fixtures_root=REPO_ROOT / "fixtures")
        spec = app.openapi()
    return json.dumps(spec, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="diff the regenerated document against the committed file (no write)",
    )
    args = parser.parse_args()

    document = generate()
    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"DRIFT: {OUTPUT_PATH} does not exist", file=sys.stderr)
            return 1
        committed = OUTPUT_PATH.read_text(encoding="utf-8")
        if committed != document:
            print(
                "DRIFT: regenerated OpenAPI differs from committed "
                f"{OUTPUT_PATH.relative_to(REPO_ROOT)} — run "
                "scripts/export_openapi.py and commit the result",
                file=sys.stderr,
            )
            return 1
        print("OpenAPI document matches the committed file (no drift).")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(document, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
