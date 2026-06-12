"""Human-review queue entries (council role 11 — Persistence/Review Queue).

Every evaluation gets a queue entry (review is always required, BR-007);
``mandatory_reasons`` is enriched for escalated runs, gate failures, and
anomalous-content flags. Rows are metadata-only (no content).
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas.audit import EvaluationRecord, ReviewQueueRow


def build_review_queue_row(record: EvaluationRecord) -> ReviewQueueRow:
    return ReviewQueueRow(
        PartitionKey=record.evaluation_id,
        RowKey="0000",
        status=record.status,
        mandatory_reasons=list(record.human_review.reasons),
        actor_id=record.actor.actor_id,
        created_at=record.created_at,
    )
