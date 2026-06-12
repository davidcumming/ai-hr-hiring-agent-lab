"""Run-identity generation: evaluation ids, correlation ids, timestamps.

These are the only non-deterministic values in a run; DT-002 normalizes
exactly these (evaluation_id-derived ids + timestamps) before byte-comparison.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


def new_evaluation_id() -> str:
    return "eval-" + uuid.uuid4().hex[:20]


def correlation_id_for(evaluation_id: str) -> str:
    """Correlation id is derived from the evaluation id so that normalizing
    the evaluation id in determinism tests normalizes correlation too."""
    return "corr-" + evaluation_id.removeprefix("eval-")


def utc_now_iso() -> str:
    """Canonical timestamp source (UTC, second precision, ISO-8601 Z)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
