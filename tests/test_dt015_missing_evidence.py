"""DT-015 — Missing-evidence path: surfaced, never fabricated.

Related: BR-013, AB-005, UFM-009, UFM-011.

A crafted inline fixture leaves criterion C6 (bilingual EN/FR) with zero
direct evidence: the record must carry an explicit missing-evidence note for
that criterion, the no-direct-evidence trigger must fire, no citation may be
fabricated anywhere, the score posture is the conservative floor with a
limitation recorded, and the D1 work-eligibility absence is handled as
missing evidence — never a disqualification.

NOTE: the candidate documents deliberately avoid the letter pair "fr" so the
substring keyword scan cannot credit C6.
"""

from __future__ import annotations

from tests.conftest import HR_HEADERS

# No D1 statement, no C6 (language) evidence anywhere.
RESUME_NO_C6 = """SYNTHETIC RESUME — test had no language section.

Project coordination across three concurrent workstreams: schedules,
deliverables, and weekly status reports.

Maintained the RAID log and risk register; ran escalation reviews with
ministry program leads and clinical advisors.

CAPM certification held.
"""

COVER_NO_C6 = """SYNTHETIC COVER LETTER — test variant.

I write briefing notes, meeting minutes, and decision logs used by
public-sector steering committees.
"""


def _run(client, key):
    response = client.post(
        "/api/evaluations",
        json={
            "position_id": "pos-sample-001",
            "resume_text": RESUME_NO_C6,
            "cover_letter_text": COVER_NO_C6,
            "idempotency_key": key,
        },
        headers=HR_HEADERS,
    )
    assert response.status_code == 200
    return response.json()


def test_missing_evidence_is_noted_never_fabricated(make_client):
    client = make_client()
    envelope = _run(client, "dt015-missing")
    assert envelope["status"] == "completed"
    result = envelope["result"]

    by_criterion = {e["criterion_id"]: e for e in result["criterion_evaluations"]}
    c6 = by_criterion["C6"]

    # Explicit missing-evidence note; conservative floor score; no citation.
    assert c6["missing_evidence_note"], "missing evidence must be surfaced"
    assert c6["supporting_evidence"] == []  # no fabricated citation
    assert c6["contrary_evidence"] == []
    assert c6["score"] == 1  # conservative floor posture
    assert "missing" in c6["missing_evidence_note"].lower()
    assert "disqualification" not in c6["rationale"].lower() or "never" in (
        c6["missing_evidence_note"] or ""
    )

    # The no-direct-evidence trigger fired with C6 in its computed value.
    trigger = next(
        t
        for t in result["triggers"]
        if t["trigger_id"] == "criterion_scored_with_no_direct_evidence"
    )
    assert trigger["fired"] is True
    assert "C6" in trigger["computed_value"]

    # A limitation is recorded (UFM-011 deterministic floor).
    assert any("C6" in lim or "Bilingual" in lim for lim in result["limitations"])

    # Gates confirm nothing was fabricated: evidence-per-score and
    # groundedness both pass WITH the missing-evidence note path.
    gates = {g["gate_id"]: g["result"] for g in result["quality_gates"]}
    assert gates["evidence_per_score"] == "pass"
    assert gates["groundedness_heuristic"] == "pass"

    # No fabricated citation anywhere: every cited id resolves.
    record = client.get(
        f"/api/evaluations/{envelope['evaluation_id']}", headers=HR_HEADERS
    ).json()["result"]
    extraction = next(
        r["output"]
        for r in record["role_executions"]
        if r["role_id"] == "evidence_extraction"
    )
    valid_ids = {i["evidence_id"] for i in extraction["evidence_items"]}
    valid_ids |= {s["segment_id"] for s in record["evidence_packet"]["segments"]}
    for e in result["criterion_evaluations"]:
        for cited in e["supporting_evidence"] + e["contrary_evidence"]:
            assert cited in valid_ids


def test_d1_absence_is_missing_evidence_never_disqualification(make_client):
    client = make_client()
    envelope = _run(client, "dt015-d1")
    record = client.get(
        f"/api/evaluations/{envelope['evaluation_id']}", headers=HR_HEADERS
    ).json()["result"]

    validator = next(
        r["output"]
        for r in record["role_executions"]
        if r["role_id"] == "deterministic_rules_validator"
    )
    d1 = validator["disqualifier_d1"]
    assert d1["evidence_present"] is False
    assert d1["segment_refs"] == []
    assert "missing" in d1["note"].lower()
    assert "never a disqualification" in d1["note"].lower()

    # The label is still driven by the evidenced required criteria — D1
    # absence did not disqualify.
    assert envelope["result"]["recommendation_label"] == "advance_to_interview"
    assert envelope["status"] == "completed"
