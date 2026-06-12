"""IdempotencyRecords-equivalent (FR-004, DT-008).

Replay with the same key + same request fingerprint returns the original
result with ZERO council execution; the same key with a different fingerprint
is ``validation_failed`` with safe detail (the fingerprint is a sha256 of the
canonical request JSON — never content).
"""

from __future__ import annotations

import hashlib
import json
from typing import Optional

from hr_eval_lab.domain.schemas.audit import IdempotencyRow
from hr_eval_lab.persistence.store import IDEMPOTENCY_TABLE, LocalStore


def request_fingerprint(body: dict) -> str:
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def lookup(store: LocalStore, idempotency_key: str) -> Optional[IdempotencyRow]:
    for raw in store.read_table(IDEMPOTENCY_TABLE):
        if raw["PartitionKey"] == idempotency_key:
            return IdempotencyRow.model_validate(raw)
    return None


def record(
    store: LocalStore,
    idempotency_key: str,
    evaluation_id: str,
    fingerprint: str,
    created_at: str,
) -> None:
    row = IdempotencyRow(
        PartitionKey=idempotency_key,
        RowKey="key",
        evaluation_id=evaluation_id,
        request_fingerprint=fingerprint,
        created_at=created_at,
    )
    store._append(IDEMPOTENCY_TABLE, row.model_dump(mode="json"))
