"""Thin CLI runner — strictly an HTTP client of the facade (FR-013, DT-018).

IMPORT-GRAPH CONSTRAINT: this module imports stdlib + httpx ONLY. It never
imports application modules, storage, or fixtures — there is no privileged
side door. It prints the API response envelope (the controlled channel) to
stdout and nothing else.

Usage:
    python3 -m hr_eval_lab.cli submit --base-url http://127.0.0.1:8000 \
        --actor-id u-hr-001 --roles hr --position-id pos-sample-001 \
        --candidate-ref cand-sample-001 --idempotency-key demo-001
    python3 -m hr_eval_lab.cli get <evaluation_id> --base-url ... --actor-id ... --roles hr
"""

from __future__ import annotations

import argparse
import json
import sys

import httpx


def _headers(args: argparse.Namespace) -> dict[str, str]:
    headers = {"X-Lab-Actor-Id": args.actor_id, "X-Lab-Roles": args.roles}
    if args.actor_display:
        headers["X-Lab-Actor-Display"] = args.actor_display
    return headers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hr-eval-lab-cli", description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--actor-display", default=None)
    parser.add_argument("--roles", default="hr", help="comma-separated lab roles")
    sub = parser.add_subparsers(dest="command", required=True)

    submit = sub.add_parser("submit", help="POST /api/evaluations")
    submit.add_argument("--position-id", required=True)
    submit.add_argument("--candidate-ref", default=None)
    submit.add_argument("--resume-text", default=None)
    submit.add_argument("--cover-letter-text", default=None)
    submit.add_argument("--idempotency-key", required=True)
    submit.add_argument("--evaluation-question", default=None)
    submit.add_argument("--requested-rigor", default=None)

    get = sub.add_parser("get", help="GET /api/evaluations/{evaluation_id}")
    get.add_argument("evaluation_id")

    args = parser.parse_args(argv)

    with httpx.Client(base_url=args.base_url, timeout=60.0) as client:
        if args.command == "submit":
            body: dict = {
                "position_id": args.position_id,
                "idempotency_key": args.idempotency_key,
            }
            if args.candidate_ref:
                body["candidate_ref"] = args.candidate_ref
            if args.resume_text is not None:
                body["resume_text"] = args.resume_text
            if args.cover_letter_text is not None:
                body["cover_letter_text"] = args.cover_letter_text
            if args.evaluation_question:
                body["evaluation_question"] = args.evaluation_question
            if args.requested_rigor:
                body["requested_rigor"] = args.requested_rigor
            response = client.post("/api/evaluations", json=body, headers=_headers(args))
        else:
            response = client.get(
                f"/api/evaluations/{args.evaluation_id}", headers=_headers(args)
            )

    print(json.dumps(response.json(), indent=2, sort_keys=True))
    return 0 if response.status_code < 500 else 1


if __name__ == "__main__":
    sys.exit(main())
