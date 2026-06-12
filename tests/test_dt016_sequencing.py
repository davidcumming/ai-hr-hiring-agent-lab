"""DT-016 — Evidence packet creation precedes any model-role invocation.

Related: FR-005, AB-001, UFM-003, UFM-009.

The ordered audit record's sequence indices prove the controlled evidence
packet (Source Ingestion/Versioning code role) completes BEFORE the first
provider call, and that Evidence Extraction is the first model-backed role,
followed by the Deterministic Rules Validator before any judgment role.
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas import council as c

from tests.conftest import get_record, post_evaluation


def _indices(record, role_id):
    return [
        r["sequence_index"] for r in record["role_executions"] if r["role_id"] == role_id
    ]


def test_packet_precedes_first_model_invocation(make_client):
    client = make_client()
    response = post_evaluation(client, idempotency_key="dt016-order")
    assert response.status_code == 200
    record = get_record(client, response.json()["evaluation_id"])

    executions = record["role_executions"]
    # Sequence indices are unique and strictly ordered as recorded.
    indices = [r["sequence_index"] for r in executions]
    assert indices == sorted(indices) and len(set(indices)) == len(indices)

    model_indices = [
        r["sequence_index"] for r in executions if r["role_kind"] == "model"
    ]
    assert model_indices, "expected model-backed executions"

    # The packet-building code role completed before EVERY provider call.
    packet_index = record["packet_sequence_index"]
    assert packet_index == _indices(record, c.ROLE_SOURCE_INGESTION)[0]
    assert packet_index < min(model_indices)

    # Evidence Extraction is the FIRST model-backed role...
    extraction_index = _indices(record, c.ROLE_EVIDENCE_EXTRACTION)[0]
    assert extraction_index == min(model_indices)

    # ...and the Rules Validator (code) runs before every judgment role.
    validator_index = _indices(record, c.ROLE_RULES_VALIDATOR)[0]
    judgment_indices = [
        r["sequence_index"]
        for r in executions
        if r["role_kind"] == "model" and r["role_id"] != c.ROLE_EVIDENCE_EXTRACTION
    ]
    assert judgment_indices and validator_index < min(judgment_indices)

    # The Synthesis Judge runs after both advocates (evidence before judgment,
    # arguments before synthesis).
    synthesis_index = _indices(record, c.ROLE_SYNTHESIS_JUDGE)[0]
    assert synthesis_index > _indices(record, c.ROLE_MERIT_ADVOCATE)[0]
    assert synthesis_index > _indices(record, c.ROLE_RISK_GAPS_ADVOCATE)[0]


def test_ordering_holds_in_escalated_mode_c(make_client):
    client = make_client(rigor="escalated")
    response = post_evaluation(client, idempotency_key="dt016-mode-c")
    record = get_record(client, response.json()["evaluation_id"])

    packet_index = record["packet_sequence_index"]
    model_indices = [
        r["sequence_index"]
        for r in record["role_executions"]
        if r["role_kind"] == "model"
    ]
    assert packet_index < min(model_indices)

    # Mode C extension roles run after the base synthesis.
    synthesis_index = _indices(record, c.ROLE_SYNTHESIS_JUDGE)[0]
    assert _indices(record, c.ROLE_SECOND_SYNTHESIS_JUDGE)[0] > synthesis_index
    assert _indices(record, c.ROLE_RUBRIC_CALIBRATION_JUDGE)[0] > synthesis_index
