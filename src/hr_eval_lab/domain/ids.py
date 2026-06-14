"""Run-identity generation: evaluation/case ids, correlation ids, timestamps.

These are the only non-deterministic values in evaluation and case flows;
deterministic tests normalize or inject them before byte-comparison.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


def new_evaluation_id() -> str:
    return "eval-" + uuid.uuid4().hex[:20]


def new_case_id() -> str:
    return "case-" + uuid.uuid4().hex[:20]


def new_event_id() -> str:
    return "evt-" + uuid.uuid4().hex[:20]


def correlation_id_for(evaluation_id: str) -> str:
    """Correlation id is derived from the evaluation id so that normalizing
    the evaluation id in determinism tests normalizes correlation too."""
    return "corr-" + evaluation_id.removeprefix("eval-")


def correlation_id_for_case(case_id: str) -> str:
    return "corr-" + case_id.removeprefix("case-")


def utc_now_iso() -> str:
    """Canonical timestamp source (UTC, second precision, ISO-8601 Z)."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
