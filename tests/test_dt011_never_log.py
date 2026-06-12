"""DT-011 — Never-log scrub (BR-010).

Related: AC-014, BR-010, UFM-007.

All log/telemetry output is captured during a full integration run (caplog
plus a root-logger capture handler, so propagated records are seen even if a
handler is attached elsewhere); zero occurrences of sentinel substrings drawn
from the fixture resume/cover-letter bodies are allowed. The defense-in-depth
redaction registry is deliberately left EMPTY so redaction cannot mask a
violating call site. All JSONL table rows (the metadata-first telemetry
surface) are scanned for the same sentinels.
"""

from __future__ import annotations

import logging

from hr_eval_lab.logging_setup import clear_sentinels

from tests.conftest import FIXTURES_ROOT, post_evaluation
from tests.sentinels import ALL_SENTINELS, COVER_LETTER_SENTINELS, RESUME_SENTINELS


class _CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def test_sentinels_really_exist_in_fixture_bodies():
    """Guard against fixture drift making the scrub vacuous."""
    resume = (FIXTURES_ROOT / "candidates" / "cand-sample-001" / "resume.md").read_text(
        encoding="utf-8"
    )
    cover = (
        FIXTURES_ROOT / "candidates" / "cand-sample-001" / "cover-letter.md"
    ).read_text(encoding="utf-8")
    for sentinel in RESUME_SENTINELS:
        assert sentinel in resume, f"stale resume sentinel: {sentinel!r}"
    for sentinel in COVER_LETTER_SENTINELS:
        assert sentinel in cover, f"stale cover-letter sentinel: {sentinel!r}"


def test_no_sentinel_in_any_log_output_during_full_run(make_client, caplog):
    clear_sentinels()  # redaction must NOT be what saves us
    handler = _CaptureHandler()
    root = logging.getLogger()
    previous_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    try:
        with caplog.at_level(logging.DEBUG):
            client = make_client()
            response = post_evaluation(client, idempotency_key="dt011-scrub")
            assert response.status_code == 200
            evaluation_id = response.json()["evaluation_id"]
            get_response = client.get(
                f"/api/evaluations/{evaluation_id}",
                headers={"X-Lab-Actor-Id": "u-hr-001", "X-Lab-Roles": "hr"},
            )
            assert get_response.status_code == 200
            # Replay + a validation failure too, for log-path coverage.
            post_evaluation(client, idempotency_key="dt011-scrub")
            post_evaluation(client, idempotency_key="dt011-bad", position_id="pos-x")
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)

    captured = handler.messages + [r.getMessage() for r in caplog.records]
    assert captured, "expected log output from the integration run"
    for message in captured:
        for sentinel in ALL_SENTINELS:
            assert sentinel not in message, (
                f"never-log violation: sentinel {sentinel!r} reached a log line"
            )


def test_no_sentinel_in_any_table_row(make_client):
    """Evidence-metadata rows carry references/hashes/counters only — scan
    every JSONL table row (raw text) for document-body sentinels."""
    client = make_client()
    assert post_evaluation(client, idempotency_key="dt011-rows").status_code == 200

    store = client.app.state.store
    tables_dir = store.root / "tables"
    table_files = list(tables_dir.glob("*.jsonl"))
    assert table_files, "expected table-equivalent rows to exist"
    for table_file in table_files:
        raw = table_file.read_text(encoding="utf-8")
        for sentinel in ALL_SENTINELS:
            assert sentinel not in raw, (
                f"document text leaked into {table_file.name}: {sentinel!r}"
            )

    # Structural check: the evidence-row schema has no text-bearing field.
    for row in store.read_table("EvaluationEvidence.jsonl"):
        assert set(row) <= {
            "PartitionKey",
            "RowKey",
            "event_type",
            "role_id",
            "role_kind",
            "schema_version",
            "artifact_refs",
            "segment_count",
            "citation_count",
            "output_size_bytes",
            "retry_count",
            "ai_backend_type",
            "flags",
            "actor_id",
            "resolved_role",
            "correlation_id",
            "created_at",
        }
