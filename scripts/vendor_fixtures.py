#!/usr/bin/env python3
"""Vendor the SYNTHETIC slice-e1 fixtures from the read-only source-doc repo.

One-time/dev script (output is committed). Copies the four fixture files
byte-identical from the source repo into ``fixtures/`` and writes
``fixtures/manifest.json`` carrying ``artifact_id``, ``version``, ``path``,
``sha256`` (computed over file bytes), ``synthetic: true``, and provenance.
The manifest is the hash authority (the source rubric carries no hash field —
source-document-inventory.md #12). The source repo is never edited.

Usage:
    python3 scripts/vendor_fixtures.py --source /path/to/hr-hiring [--copy]

Without ``--copy`` it only (re)computes hashes for the already-vendored files
and rewrites the manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_ROOT = REPO_ROOT / "fixtures"

# (artifact_id, version, source-repo relative path, vendored relative path)
ARTIFACTS = [
    (
        "pos-sample-001",
        "v1",
        "fixtures/sample-position/job-description.md",
        "positions/pos-sample-001/job-description.md",
    ),
    (
        "rub-sample-001",
        "v1",
        "fixtures/sample-position/rubric.v1.json",
        "positions/pos-sample-001/rubric.v1.json",
    ),
    (
        "cand-sample-001:resume",
        "v1",
        "fixtures/candidates/jordan-rivera/resume.md",
        "candidates/cand-sample-001/resume.md",
    ),
    (
        "cand-sample-001:cover_letter",
        "v1",
        "fixtures/candidates/jordan-rivera/cover-letter.md",
        "candidates/cand-sample-001/cover-letter.md",
    ),
]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Path to the read-only hr-hiring source repo")
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy fixture files from --source before hashing (byte-identical)",
    )
    args = parser.parse_args()

    if args.copy:
        if not args.source:
            print("--copy requires --source", file=sys.stderr)
            return 2
        source_root = Path(args.source)
        for _, _, src_rel, dst_rel in ARTIFACTS:
            src = source_root / src_rel
            dst = FIXTURES_ROOT / dst_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)  # content only; source repo never modified
            print(f"vendored {src_rel} -> fixtures/{dst_rel}")

    manifest = {
        "manifest_version": "1",
        "synthetic_notice": (
            "All fixtures are SYNTHETIC lab data (BR-011). No real applicant "
            "data exists or is permitted in this repository."
        ),
        "artifacts": [],
    }
    for artifact_id, version, src_rel, dst_rel in ARTIFACTS:
        path = FIXTURES_ROOT / dst_rel
        if not path.exists():
            print(f"missing vendored fixture: {path}", file=sys.stderr)
            return 1
        manifest["artifacts"].append(
            {
                "artifact_id": artifact_id,
                "version": version,
                "path": f"fixtures/{dst_rel}",
                "sha256": sha256_of(path),
                "synthetic": True,
                "provenance": {
                    "source_repo": "hr-hiring (read-only source documentation repo)",
                    "source_path": src_rel,
                    "vendored_date": str(date.today()),
                },
            }
        )

    manifest_path = FIXTURES_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
