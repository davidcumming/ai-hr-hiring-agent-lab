#!/usr/bin/env python3
"""Local deterministic council demo (readiness pack, coding target 7.1).

Runs ONE synthetic candidate (cand-sample-001 / pos-sample-001 / rub-sample-001
v1) strictly through the HTTP facade in-process — no privileged side door —
writes the local artifact tree, and prints a SAFE summary only: identifiers,
statuses, counts. Never resume text, never prompts, never model I/O.

Usage:
    python3 scripts/run_council_local.py [--data-root var/lab-data-demo]

Entirely local and deterministic: no Azure, no Foundry, no network, no secrets.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        default=str(REPO_ROOT / "var" / "lab-data-demo"),
        help="local persistence root for this demo run (gitignored)",
    )
    args = parser.parse_args()

    from fastapi.testclient import TestClient

    from hr_eval_lab.api.app import create_app
    from hr_eval_lab.config import LabConfig, PersistenceConfig

    config = LabConfig(persistence=PersistenceConfig(root=args.data_root))
    app = create_app(config=config, fixtures_root=REPO_ROOT / "fixtures")
    headers = {"X-Lab-Actor-Id": "u-hr-demo", "X-Lab-Roles": "hr"}

    with TestClient(app) as client:
        submit = client.post(
            "/api/evaluations",
            json={
                "position_id": "pos-sample-001",
                "candidate_ref": "cand-sample-001",
                "idempotency_key": f"local-demo-{uuid.uuid4().hex[:12]}",
            },
            headers=headers,
        )
        envelope = submit.json()
        evaluation_id = envelope.get("evaluation_id")
        retrieve = client.get(f"/api/evaluations/{evaluation_id}", headers=headers)

    store = app.state.store
    artifacts = store.backend.list_artifacts(evaluation_id)
    record = retrieve.json()["result"]
    result = record.get("result") or {}

    # SAFE summary only — identifiers, enums, counts. No document text.
    print("=== local deterministic council run (advisory; synthetic data only) ===")
    print(f"evaluation_id       : {evaluation_id}")
    print(f"status              : {envelope.get('status')}")
    print(f"correlation_id      : {submit.headers.get('X-Correlation-Id')}")
    print(f"effective_rigor     : {record['rigor_resolution']['effective_rigor']}")
    print(f"effective_mode      : {record['effective_mode']}")
    print(f"escalation_policy   : {record['escalation']['policy']}")
    print(f"triggers_fired      : {sum(1 for t in record['triggers'] if t['fired'])}/{len(record['triggers'])}")
    print(f"gates               : {sum(1 for g in record['gate_results'] if g['result']=='pass')} pass / {sum(1 for g in record['gate_results'] if g['result']=='fail')} fail")
    print(f"recommendation      : {result.get('recommendation_label')}")
    print(f"decision_support_only: {result.get('decision_support_only')}")
    print(f"human_review_required: {result.get('human_review_required')}")
    print(f"artifacts written   : {len(artifacts)} under {args.data_root}/evaluations/{evaluation_id}/")
    for ref in artifacts:
        print(f"  - {ref.name} ({ref.size_bytes} bytes, sha256 {ref.sha256[:12]}…)")
    print("This output is decision support for a human reviewer — never a hiring decision.")
    return 0 if envelope.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
