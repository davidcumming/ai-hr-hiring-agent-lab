"""Local persistence — blob-equivalent + table-equivalent shapes (FR-009).

Mirrors the storage-doc shapes so future Azure wiring is configuration, not
restructuring (AF-002 confirmed faithful at Stage 6). Readiness pack: the
physical layout is owned by the :class:`StorageBackend` seam
(``persistence/backend.py``); ``LocalStore`` keeps its facade API and
projects the audit record into discrete artifacts at persistence time:

- ``<root>/evaluations/{evaluation_id}/record.json`` — the full audit record,
  CANONICAL JSON (sorted keys, fixed separators, UTF-8) so DT-002
  byte-identity holds — plus per-artifact projections (request,
  source-documents, evidence-packet, council/{role}, synthesis,
  quality-gates, provider-metadata, human-review).
- ``<root>/metadata/evaluations.jsonl`` — one text-free summary row per
  evaluation (``RecordSummaryRow``).
- Table-equivalent: ``<root>/tables/EvaluationEvidence.jsonl`` — one
  metadata-first row per role output/evidence event. The row schema has NO
  text-bearing fields (BR-010): no resume text, prompt text, or model I/O
  exists anywhere outside the full record and its artifact projections.
- ``<root>/tables/ReviewQueue.jsonl`` — human-review queue entries.

All writers are append-only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from hr_eval_lab.domain.schemas.audit import EvaluationRecord, EvidenceRow
from hr_eval_lab.domain.schemas.storage import RecordSummaryRow
from hr_eval_lab.domain.schemas.transcript import build_role_invocation
from hr_eval_lab.logging_setup import get_logger
from hr_eval_lab.persistence.backend import LocalFilesystemBackend, StorageBackend
from hr_eval_lab.review_queue import build_review_queue_row

logger = get_logger("persistence")

EVIDENCE_TABLE = "EvaluationEvidence.jsonl"
IDEMPOTENCY_TABLE = "IdempotencyRecords.jsonl"
REVIEW_QUEUE_TABLE = "ReviewQueue.jsonl"


def canonical_json(payload: Any) -> str:
    """Canonical JSON: sorted keys, fixed separators, UTF-8, no float drift."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class LocalStore:
    def __init__(
        self, root: str | Path, backend: StorageBackend | None = None
    ) -> None:
        self.root = Path(root)
        (self.root / "evaluations").mkdir(parents=True, exist_ok=True)
        (self.root / "tables").mkdir(parents=True, exist_ok=True)
        self.backend: StorageBackend = backend or LocalFilesystemBackend(self.root)

    # -- blob-equivalent (via the storage backend seam) -------------------------

    def save_record(self, record: EvaluationRecord) -> None:
        """Persist the full record + artifact projections + metadata rows."""
        evaluation_id = record.evaluation_id
        payload = record.model_dump(mode="json")
        self.backend.write_evaluation_record(evaluation_id, payload)

        # Artifact projections (single source of truth = the record).
        self.backend.write_artifact(evaluation_id, "request", "request", payload["request"])
        self.backend.write_artifact(
            evaluation_id, "source-documents", "source-documents", payload["sources"]
        )
        self.backend.write_artifact(
            evaluation_id, "evidence-packet", "evidence-packet", payload["evidence_packet"]
        )
        provider_metadata: list[dict] = []
        for execution in record.role_executions:
            invocation = build_role_invocation(record, execution)
            self.backend.write_artifact(
                evaluation_id,
                "council-role",
                execution.role_id,
                invocation.model_dump(mode="json"),
            )
            if execution.provider_metadata is not None:
                provider_metadata.append(
                    {
                        "role_id": execution.role_id,
                        "sequence_index": execution.sequence_index,
                        **execution.provider_metadata.model_dump(mode="json"),
                    }
                )
        self.backend.write_artifact(
            evaluation_id,
            "synthesis",
            "synthesis",
            payload.get("result"),
        )
        self.backend.write_artifact(
            evaluation_id, "quality-gates", "quality-gates", payload["gate_results"]
        )
        self.backend.write_artifact(
            evaluation_id, "provider-metadata", "provider-metadata", provider_metadata
        )
        self.backend.write_artifact(
            evaluation_id,
            "human-review",
            "human-review",
            {
                "human_review": payload["human_review"],
                "decision_support_only": True,
            },
        )

        # Legacy table-equivalents (storage-doc shapes; unchanged).
        for row in self._evidence_rows(record):
            self._append(EVIDENCE_TABLE, row.model_dump(mode="json"))
        review_row = build_review_queue_row(record)
        self._append(REVIEW_QUEUE_TABLE, review_row.model_dump(mode="json"))

        # Text-free summary row (metadata/evaluations.jsonl).
        self.backend.write_metadata_row(
            self._summary_row(record).model_dump(mode="json")
        )
        logger.info(
            "persisted evaluation_id=%s rows=%d status=%s",
            record.evaluation_id,
            len(record.role_executions),
            record.status,
        )

    def load_record(self, evaluation_id: str) -> Optional[dict]:
        return self.backend.read_evaluation_record(evaluation_id)

    def _summary_row(self, record: EvaluationRecord) -> RecordSummaryRow:
        """Metadata-first summary: identifiers/enums/counts/hashes only —
        the schema has no text-bearing field (BR-010)."""
        result = record.result
        rubric = record.evidence_packet.rubric
        return RecordSummaryRow(
            PartitionKey=record.evaluation_id,
            status=record.status,
            position_id=str(record.request.get("position_id", "")),
            candidate_ref=record.request.get("candidate_ref"),
            rubric_id=rubric.rubric_id,
            rubric_version=rubric.version,
            effective_rigor=record.rigor_resolution.effective_rigor,
            effective_mode=record.effective_mode,
            escalation_policy=record.escalation.policy,
            triggers_fired=sum(1 for t in record.triggers if t.fired),
            gates_failed=sum(1 for g in record.gate_results if g.result == "fail"),
            recommendation_label=(result.recommendation_label if result else None),
            human_review_required=record.human_review.human_review_required,
            decision_support_only=True,
            ai_backend_type=(result.ai_backend_type if result else "none"),
            provider_id="deterministic_mock" if (result is None or result.ai_backend_type == "none") else "foundry_unresolved",
            artifact_count=len(self.backend.list_artifacts(record.evaluation_id)),
            actor_id=record.actor.actor_id,
            resolved_role=record.actor.resolved_role,
            correlation_id=record.correlation_id,
            created_at=record.created_at,
            completed_at=record.completed_at,
            source_hashes=[s.sha256 for s in record.sources],
        )

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
