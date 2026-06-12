"""Local persistence — blob-equivalent + table-equivalent shapes (FR-009).

Mirrors the storage-doc shapes so future Azure wiring is configuration, not
restructuring (AF-002 confirmed faithful at Stage 6):

- Blob-equivalent: ``<root>/evaluations/{evaluation_id}.json`` — the full
  audit record, serialized as CANONICAL JSON (sorted keys, fixed separators,
  UTF-8) so DT-002 byte-identity holds.
- Table-equivalent: ``<root>/tables/EvaluationEvidence.jsonl`` — one
  metadata-first row per role output/evidence event. The row schema has NO
  text-bearing fields (BR-010): no resume text, prompt text, or model I/O
  exists anywhere outside the full record.
- ``<root>/tables/ReviewQueue.jsonl`` — human-review queue entries.

All writers are append-only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from hr_eval_lab.domain.schemas.audit import EvaluationRecord, EvidenceRow
from hr_eval_lab.logging_setup import get_logger
from hr_eval_lab.review_queue import build_review_queue_row

logger = get_logger("persistence")

EVIDENCE_TABLE = "EvaluationEvidence.jsonl"
IDEMPOTENCY_TABLE = "IdempotencyRecords.jsonl"
REVIEW_QUEUE_TABLE = "ReviewQueue.jsonl"


def canonical_json(payload: Any) -> str:
    """Canonical JSON: sorted keys, fixed separators, UTF-8, no float drift."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class LocalStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        (self.root / "evaluations").mkdir(parents=True, exist_ok=True)
        (self.root / "tables").mkdir(parents=True, exist_ok=True)

    # -- blob-equivalent -------------------------------------------------------

    def save_record(self, record: EvaluationRecord) -> None:
        """Persist the full record + metadata rows + review-queue entry."""
        blob_path = self.root / "evaluations" / f"{record.evaluation_id}.json"
        blob_path.write_text(
            canonical_json(record.model_dump(mode="json")), encoding="utf-8"
        )
        for row in self._evidence_rows(record):
            self._append(EVIDENCE_TABLE, row.model_dump(mode="json"))
        review_row = build_review_queue_row(record)
        self._append(REVIEW_QUEUE_TABLE, review_row.model_dump(mode="json"))
        logger.info(
            "persisted evaluation_id=%s rows=%d status=%s",
            record.evaluation_id,
            len(record.role_executions),
            record.status,
        )

    def load_record(self, evaluation_id: str) -> Optional[dict]:
        blob_path = self.root / "evaluations" / f"{evaluation_id}.json"
        if not blob_path.exists():
            return None
        return json.loads(blob_path.read_text(encoding="utf-8"))

    # -- table-equivalent ------------------------------------------------------

    def _append(self, table: str, row: dict) -> None:
        path = self.root / "tables" / table
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(canonical_json(row) + "\n")

    def read_table(self, table: str) -> list[dict]:
        path = self.root / "tables" / table
        if not path.exists():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _evidence_rows(self, record: EvaluationRecord) -> list[EvidenceRow]:
        """Metadata-first rows: one per role execution. No text, by schema."""
        rows: list[EvidenceRow] = []
        artifact_ids = [s.artifact_id for s in record.sources]
        for execution in record.role_executions:
            output = execution.output
            citation_count = 0
            for key in ("evidence_items", "scores", "proposed_scores", "criterion_evaluations"):
                items = output.get(key)
                if isinstance(items, list):
                    citation_count += len(items)
            flags: list[str] = []
            if output.get("anomalous_content_detected"):
                flags.append("anomalous_content")
            if execution.retry_count:
                flags.append("schema_retry")
            if not execution.schema_valid:
                flags.append("schema_invalid")
            rows.append(
                EvidenceRow(
                    PartitionKey=record.evaluation_id,
                    RowKey=f"{execution.sequence_index:04d}",
                    event_type="role_output",
                    role_id=execution.role_id,
                    role_kind=execution.role_kind,
                    schema_version=execution.schema_version,
                    artifact_refs=artifact_ids,
                    segment_count=len(record.evidence_packet.segments),
                    citation_count=citation_count,
                    output_size_bytes=len(canonical_json(output).encode("utf-8")),
                    retry_count=execution.retry_count,
                    ai_backend_type=(
                        execution.provider_metadata.ai_backend_type
                        if execution.provider_metadata
                        else "none"
                    ),
                    flags=flags,
                    actor_id=record.actor.actor_id,
                    resolved_role=record.actor.resolved_role,
                    correlation_id=record.correlation_id,
                    created_at=record.created_at,
                )
            )
        return rows
