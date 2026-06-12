"""DT-006 — The six deterministic quality gates, pass and fail per gate,
including the schema-retry bound (exactly one corrective retry, then fail).

Related: AC-007, AC-008, FR-008, AB-008, UFM-001, UFM-003, UFM-005.
"""

from __future__ import annotations

import json

from hr_eval_lab.domain.schemas import council as c
from hr_eval_lab.evidence.packet_builder import build_packet
from hr_eval_lab.gates.quality_gates import GATE_IDS, run_gates
from hr_eval_lab.sources.fixture_store import inline_source

from tests.conftest import (
    FIXTURES_ROOT,
    CountingProvider,
    post_evaluation,
    scripted_provider,
)

# ---------------------------------------------------------------------------
# Unit harness: a minimal real packet + well-formed synthesis/extraction
# ---------------------------------------------------------------------------

RESUME = "Project coordination of schedules and status reports.\n\nRAID log and risk register owner."
COVER = "I write briefings and minutes for ministry and clinical stakeholders.\n\nCAPM certified; bilingual French."


def _packet():
    rubric_json = json.loads(
        (FIXTURES_ROOT / "positions" / "pos-sample-001" / "rubric.v1.json").read_text(
            encoding="utf-8"
        )
    )
    return build_packet(
        resume=inline_source("inline:resume", RESUME),
        cover_letter=inline_source("inline:cover_letter", COVER),
        job_description=inline_source("inline:job_description", "Synthetic JD."),
        rubric_json=rubric_json,
        rubric_source=inline_source("rub-sample-001", json.dumps(rubric_json)),
    )


def _evidence_items(packet):
    seg = packet.segments[0]
    return [
        {
            "evidence_id": "ev-001",
            "criterion_id": "C1",
            "artifact_id": seg.artifact_id,
            "segment_id": seg.segment_id,
            "quote": seg.text[:40],
            "relation": "supporting",
        }
    ]


def _synthesis(packet):
    evaluations = []
    for criterion in packet.rubric.criteria:
        cid = criterion.criterion_id
        evaluations.append(
            {
                "criterion_id": cid,
                "criterion_name": criterion.name,
                "score": 4 if cid == "C1" else 1,
                "rationale": "Anchored to the scale from cited evidence.",
                "supporting_evidence": ["ev-001"] if cid == "C1" else [],
                "contrary_evidence": [],
                "missing_evidence_note": None if cid == "C1" else "No direct evidence found.",
            }
        )
    return {"criterion_evaluations": evaluations}


def _gates(packet, evidence_items, synthesis, fairness=None, flags_present=True):
    results = run_gates(
        packet=packet,
        role_executions=[],
        evidence_items=evidence_items,
        synthesis=synthesis,
        fairness=fairness,
        flags_present=flags_present,
    )
    assert [g.gate_id for g in results] == GATE_IDS  # fixed order, always all six
    return {g.gate_id: g for g in results}


def test_all_six_gates_pass_on_well_formed_inputs():
    packet = _packet()
    gates = _gates(packet, _evidence_items(packet), _synthesis(packet))
    assert all(g.result == "pass" for g in gates.values())


def test_gate2_all_criteria_scored_fails_on_missing_criterion():
    packet = _packet()
    synthesis = _synthesis(packet)
    synthesis["criterion_evaluations"] = synthesis["criterion_evaluations"][:-1]
    gates = _gates(packet, _evidence_items(packet), synthesis)
    assert gates["all_criteria_scored"].result == "fail"
    assert "C6" in gates["all_criteria_scored"].reason


def test_gate2_fails_on_out_of_range_score():
    packet = _packet()
    synthesis = _synthesis(packet)
    synthesis["criterion_evaluations"][0]["score"] = 7
    gates = _gates(packet, _evidence_items(packet), synthesis)
    assert gates["all_criteria_scored"].result == "fail"


def test_gate3_evidence_per_score_fails_on_fabricated_citation():
    """A citation that resolves to nothing is the UFM-003 blocking fail."""
    packet = _packet()
    synthesis = _synthesis(packet)
    synthesis["criterion_evaluations"][0]["supporting_evidence"] = ["ev-fabricated-999"]
    gates = _gates(packet, _evidence_items(packet), synthesis)
    assert gates["evidence_per_score"].result == "fail"
    assert "ev-fabricated-999" in gates["evidence_per_score"].reason


def test_gate3_fails_on_unevidenced_score_without_missing_note():
    packet = _packet()
    synthesis = _synthesis(packet)
    synthesis["criterion_evaluations"][1]["missing_evidence_note"] = None
    gates = _gates(packet, _evidence_items(packet), synthesis)
    assert gates["evidence_per_score"].result == "fail"


def test_gate4_no_prohibited_factors_fails_on_prohibited_rationale():
    packet = _packet()
    synthesis = _synthesis(packet)
    synthesis["criterion_evaluations"][0]["rationale"] = (
        "Strong because the candidate is married and settled."
    )
    gates = _gates(packet, _evidence_items(packet), synthesis)
    assert gates["no_prohibited_factors"].result == "fail"
    assert "married" in gates["no_prohibited_factors"].reason


def test_gate4_fails_when_auditor_findings_dropped():
    packet = _packet()
    fairness = {"findings": [], "prohibited_factor_violations": ["years old"]}
    gates = _gates(packet, _evidence_items(packet), _synthesis(packet), fairness=fairness)
    assert gates["no_prohibited_factors"].result == "fail"
    assert "dropped" in gates["no_prohibited_factors"].reason


def test_gate5_human_review_flag_fails_when_flags_absent():
    packet = _packet()
    gates = _gates(packet, _evidence_items(packet), _synthesis(packet), flags_present=False)
    assert gates["human_review_flag_present"].result == "fail"


def test_gate6_groundedness_fails_on_non_verbatim_quote():
    packet = _packet()
    items = _evidence_items(packet)
    items[0]["quote"] = "This text appears nowhere in the referenced segment."
    gates = _gates(packet, items, _synthesis(packet))
    assert gates["groundedness_heuristic"].result == "fail"
    assert "ev-001" in gates["groundedness_heuristic"].reason


# ---------------------------------------------------------------------------
# Gate 1 + bounded retry: integration through the provider seam (AB-008)
# ---------------------------------------------------------------------------


def _invalid_once(role_id, packet, role_context, payload):
    if "corrective_hint" in role_context:
        return payload  # corrected on the single bounded retry
    return {"bogus": "schema-invalid output"}


def _invalid_always(role_id, packet, role_context, payload):
    return {"bogus": "schema-invalid output"}


def test_gate1_schema_retry_recovers_with_exactly_one_retry(make_client):
    provider = CountingProvider(
        scripted_provider({c.ROLE_MERIT_ADVOCATE: _invalid_once})
    )
    client = make_client(provider=provider)
    response = post_evaluation(client, idempotency_key="dt006-retry-recover")
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["status"] == "completed"
    gates = {g["gate_id"]: g for g in envelope["result"]["quality_gates"]}
    assert gates["schema_validity"]["result"] == "pass"

    record = client.get(
        f"/api/evaluations/{envelope['evaluation_id']}",
        headers={"X-Lab-Actor-Id": "u-hr-001", "X-Lab-Roles": "hr"},
    ).json()["result"]
    merit = next(
        r for r in record["role_executions"] if r["role_id"] == c.ROLE_MERIT_ADVOCATE
    )
    assert merit["retry_count"] == 1
    assert merit["schema_valid"] is True
    assert provider.calls.count(c.ROLE_MERIT_ADVOCATE) == 2  # original + 1 retry


def test_gate1_fails_run_after_exactly_one_corrective_retry(make_client):
    provider = CountingProvider(
        scripted_provider({c.ROLE_MERIT_ADVOCATE: _invalid_always})
    )
    client = make_client(provider=provider)
    response = post_evaluation(client, idempotency_key="dt006-retry-bounded")
    assert response.status_code == 200  # business outcome carried in envelope
    envelope = response.json()
    assert envelope["status"] == "blocked"
    assert "schema_validity" in (envelope["safe_details"] or "")

    gates = {g["gate_id"]: g for g in envelope["result"]["quality_gates"]}
    assert gates["schema_validity"]["result"] == "fail"
    assert c.ROLE_MERIT_ADVOCATE in gates["schema_validity"]["reason"]

    # Exactly one corrective retry — never a second.
    assert provider.calls.count(c.ROLE_MERIT_ADVOCATE) == 2

    record = client.get(
        f"/api/evaluations/{envelope['evaluation_id']}",
        headers={"X-Lab-Actor-Id": "u-hr-001", "X-Lab-Roles": "hr"},
    ).json()["result"]
    merit = next(
        r for r in record["role_executions"] if r["role_id"] == c.ROLE_MERIT_ADVOCATE
    )
    assert merit["retry_count"] == 1
    assert merit["schema_valid"] is False
    assert record["status"] == "blocked"
    assert "quality_gate_failure" in record["human_review"]["reasons"]
