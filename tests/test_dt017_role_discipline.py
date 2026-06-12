"""DT-017 — Per-role output discipline across all 11 council roles.

Related: FR-006, AB-002, AB-008, UFM-003, UFM-006.

All role outputs are schema-valid; every citation mechanically resolves to a
packet segment id (or extraction evidence id); the Evidence Extraction output
carries NO evaluative field of any kind — evaluative drift is structurally
unconstructible at the schema level.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from hr_eval_lab.domain.schemas import council as c

from tests.conftest import get_record, post_evaluation

EVALUATIVE_KEYS = {
    "score",
    "scores",
    "proposed_scores",
    "recommendation",
    "recommendation_label",
    "rank",
    "ranking",
    "decision",
    "verdict",
}

ALL_11_ROLES = {
    c.ROLE_REQUEST_NORMALIZER,
    c.ROLE_SOURCE_INGESTION,
    c.ROLE_EVIDENCE_EXTRACTION,
    c.ROLE_RULES_VALIDATOR,
    c.ROLE_MERIT_ADVOCATE,
    c.ROLE_RISK_GAPS_ADVOCATE,
    c.ROLE_NEUTRAL_SCORING_JUDGE,
    c.ROLE_POLICY_FAIRNESS_AUDITOR,
    c.ROLE_SYNTHESIS_JUDGE,
    c.ROLE_QUALITY_GATES,
    c.ROLE_PERSISTENCE_REVIEW_QUEUE,
}


def _all_keys(obj):
    """Recursively collect every dict key in a nested payload."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            keys |= _all_keys(v)
    elif isinstance(obj, list):
        for item in obj:
            keys |= _all_keys(item)
    return keys


@pytest.fixture(scope="module")
def escalated_record(tmp_path_factory):
    """One escalated (Mode C) run: all 11 base roles + 2 extension roles."""
    from fastapi.testclient import TestClient

    from hr_eval_lab.api.app import create_app

    from tests.conftest import FIXTURES_ROOT, make_config

    tmp_path = tmp_path_factory.mktemp("dt017")
    config = make_config(tmp_path, rigor="escalated")
    client = TestClient(create_app(config=config, fixtures_root=FIXTURES_ROOT))
    response = post_evaluation(client, idempotency_key="dt017-discipline")
    assert response.status_code == 200
    return get_record(client, response.json()["evaluation_id"])


def test_all_eleven_roles_plus_extensions_executed(escalated_record):
    executed = {r["role_id"] for r in escalated_record["role_executions"]}
    assert ALL_11_ROLES <= executed
    assert {c.ROLE_SECOND_SYNTHESIS_JUDGE, c.ROLE_RUBRIC_CALIBRATION_JUDGE} <= executed


def test_every_role_output_schema_valid(escalated_record):
    for execution in escalated_record["role_executions"]:
        assert execution["schema_valid"] is True, execution["role_id"]
        assert execution["retry_count"] == 0
        if execution["role_kind"] == "model":
            # Re-validate the persisted payload against the declared schema.
            c.MODEL_ROLE_SCHEMAS[execution["role_id"]].model_validate(
                execution["output"]
            )


def test_citations_resolve_to_packet_segment_ids(escalated_record):
    record = escalated_record
    segment_ids = {s["segment_id"] for s in record["evidence_packet"]["segments"]}
    outputs = {r["role_id"]: r["output"] for r in record["role_executions"]}

    extraction = outputs[c.ROLE_EVIDENCE_EXTRACTION]
    assert extraction["evidence_items"], "expected extracted evidence"
    segments_by_id = {
        s["segment_id"]: s["text"] for s in record["evidence_packet"]["segments"]
    }
    for item in extraction["evidence_items"]:
        assert item["segment_id"] in segment_ids  # mechanical resolution
        assert item["quote"] in segments_by_id[item["segment_id"]]  # verbatim span

    evidence_ids = {i["evidence_id"] for i in extraction["evidence_items"]}
    resolvable = segment_ids | evidence_ids

    for role_id, field in [
        (c.ROLE_MERIT_ADVOCATE, "proposed_scores"),
        (c.ROLE_RISK_GAPS_ADVOCATE, "proposed_scores"),
        (c.ROLE_NEUTRAL_SCORING_JUDGE, "scores"),
    ]:
        for proposal in outputs[role_id][field]:
            for cited in proposal["citations"]:
                assert cited in resolvable, f"{role_id} cited unresolvable {cited}"
        for argument in outputs[role_id].get("arguments", []):
            for cited in argument["citations"]:
                assert cited in resolvable

    for evaluation in outputs[c.ROLE_SYNTHESIS_JUDGE]["criterion_evaluations"]:
        for cited in evaluation["supporting_evidence"] + evaluation["contrary_evidence"]:
            assert cited in resolvable

    for finding in outputs[c.ROLE_POLICY_FAIRNESS_AUDITOR]["findings"]:
        for ref in finding["segment_refs"]:
            assert ref in segment_ids


def test_extraction_output_has_no_evaluative_fields(escalated_record):
    extraction = next(
        r["output"]
        for r in escalated_record["role_executions"]
        if r["role_id"] == c.ROLE_EVIDENCE_EXTRACTION
    )
    assert _all_keys(extraction).isdisjoint(EVALUATIVE_KEYS)
    # And the schema makes evaluative output unconstructible (extra=forbid).
    with pytest.raises(ValidationError):
        c.MODEL_ROLE_SCHEMAS[c.ROLE_EVIDENCE_EXTRACTION].model_validate(
            {**extraction, "score": 5}
        )
    with pytest.raises(ValidationError):
        c.MODEL_ROLE_SCHEMAS[c.ROLE_EVIDENCE_EXTRACTION].model_validate(
            {**extraction, "recommendation_label": "advance_to_interview"}
        )
