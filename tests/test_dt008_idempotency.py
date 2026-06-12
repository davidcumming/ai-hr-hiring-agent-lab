"""DT-008 — Idempotency replay: same key -> original result, council NOT re-run.

Related: AC-012, FR-004, UFM-013.
"""

from __future__ import annotations

from tests.conftest import CountingProvider, post_evaluation


def test_replay_returns_original_result_without_rerunning_council(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)

    first = post_evaluation(client, idempotency_key="dt008-replay")
    assert first.status_code == 200
    first_envelope = first.json()
    assert first_envelope["status"] == "completed"
    calls_after_first = list(provider.calls)
    assert calls_after_first  # the first run did execute the council

    second = post_evaluation(client, idempotency_key="dt008-replay")
    assert second.status_code == 200
    second_envelope = second.json()

    # Same evaluation_id, identical result payload.
    assert second_envelope["evaluation_id"] == first_envelope["evaluation_id"]
    assert second_envelope["status"] == first_envelope["status"]
    assert second_envelope["result"] == first_envelope["result"]
    assert "replay" in second_envelope["user_message"].lower()

    # Provider invocation count unchanged: ZERO new council role executions.
    assert provider.calls == calls_after_first

    # No duplicate record persisted.
    store = client.app.state.store
    blobs = list((store.root / "evaluations").iterdir())
    assert len(blobs) == 1
    rows = store.read_table("IdempotencyRecords.jsonl")
    assert len([r for r in rows if r["PartitionKey"] == "dt008-replay"]) == 1


def test_same_key_different_payload_is_validation_failed(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)

    first = post_evaluation(client, idempotency_key="dt008-conflict")
    assert first.json()["status"] == "completed"
    calls_after_first = list(provider.calls)

    conflicting = post_evaluation(
        client,
        idempotency_key="dt008-conflict",
        evaluation_question="A different payload under the same key.",
    )
    assert conflicting.status_code == 200
    envelope = conflicting.json()
    assert envelope["status"] == "validation_failed"
    assert "idempotency_key_conflict" in envelope["errors"]
    assert provider.calls == calls_after_first  # still no re-run


def test_different_keys_run_independently(make_client):
    provider = CountingProvider()
    client = make_client(provider=provider)

    a = post_evaluation(client, idempotency_key="dt008-a").json()
    calls_after_first = len(provider.calls)
    b = post_evaluation(client, idempotency_key="dt008-b").json()

    assert a["evaluation_id"] != b["evaluation_id"]
    assert len(provider.calls) == calls_after_first * 2  # second full council run
