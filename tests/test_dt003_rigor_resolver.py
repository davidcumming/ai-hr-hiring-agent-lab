"""DT-003 — Rigor resolver unit matrix.

Related: AC-004, AC-005, BR-001, BR-002, BR-003, UFM-002.

Unit-level (pure function) coverage of ``resolve_rigor``: default hiring
classification resolves to high_impact; explicit server ``escalated`` and
``standard`` config states each win; a request-body downgrade attempt is
recorded AND ignored (the effective rigor never lowers); plus an integration
check that the downgrade evidence reaches the persisted record.
"""

from __future__ import annotations

from hr_eval_lab.rigor.resolver import HIRING_CLASSIFICATION, resolve_rigor

from tests.conftest import get_record, post_evaluation


def test_default_hiring_classification_resolves_high_impact():
    resolution = resolve_rigor(
        server_default="high_impact",
        risk_classification=HIRING_CLASSIFICATION,
        requested_rigor=None,
    )
    assert resolution.effective_rigor == "high_impact"
    assert resolution.downgrade_attempted is False
    assert resolution.downgrade_detail is None
    assert "high_impact" in resolution.explanation
    assert HIRING_CLASSIFICATION in resolution.explanation


def test_explicit_server_escalated_wins():
    resolution = resolve_rigor(
        server_default="escalated",
        risk_classification=HIRING_CLASSIFICATION,
        requested_rigor=None,
    )
    assert resolution.effective_rigor == "escalated"
    assert "escalated" in resolution.explanation


def test_explicit_server_standard_is_server_winning():
    """An explicit server ``standard`` IS the server winning (BR-001 note)."""
    resolution = resolve_rigor(
        server_default="standard",
        risk_classification=HIRING_CLASSIFICATION,
        requested_rigor=None,
    )
    assert resolution.effective_rigor == "standard"
    assert "server config wins" in resolution.explanation.lower()


def test_downgrade_attempt_recorded_and_ignored():
    """The request body can NEVER lower rigor; the attempt is auditable."""
    resolution = resolve_rigor(
        server_default="high_impact",
        risk_classification=HIRING_CLASSIFICATION,
        requested_rigor="standard",
    )
    assert resolution.effective_rigor == "high_impact"  # ignored
    assert resolution.downgrade_attempted is True  # recorded
    assert resolution.requested_rigor == "standard"
    assert resolution.downgrade_detail
    assert "never" in resolution.downgrade_detail.lower()


def test_downgrade_attempt_against_escalated_config():
    resolution = resolve_rigor(
        server_default="escalated",
        risk_classification=HIRING_CLASSIFICATION,
        requested_rigor="high_impact",
    )
    assert resolution.effective_rigor == "escalated"
    assert resolution.downgrade_attempted is True


def test_non_downgrade_request_is_advisory_only():
    """An equal-or-higher requested_rigor is recorded as advisory, with no
    downgrade flag — server config remains authoritative."""
    resolution = resolve_rigor(
        server_default="high_impact",
        risk_classification=HIRING_CLASSIFICATION,
        requested_rigor="high_impact",
    )
    assert resolution.effective_rigor == "high_impact"
    assert resolution.downgrade_attempted is False
    assert "advisory" in resolution.explanation.lower()


def test_each_config_state_drives_the_pipeline(make_client):
    """Integration: each rigor.default_mode value flows to effective rigor."""
    for mode in ("standard", "high_impact", "escalated"):
        client = make_client(rigor=mode)
        response = post_evaluation(client, idempotency_key=f"dt003-{mode}")
        assert response.status_code == 200
        assert response.json()["result"]["rigor"]["effective_rigor"] == mode


def test_downgrade_attempt_persisted_in_record(make_client):
    client = make_client()  # high_impact default
    response = post_evaluation(
        client, idempotency_key="dt003-downgrade", requested_rigor="standard"
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["rigor"]["effective_rigor"] == "high_impact"
    assert result["rigor"]["downgrade_attempted"] is True
    assert result["rigor"]["requested_rigor"] == "standard"

    record = get_record(client, response.json()["evaluation_id"])
    assert record["rigor_resolution"]["downgrade_attempted"] is True
    assert record["rigor_resolution"]["downgrade_detail"]
    assert record["request"]["requested_rigor"] == "standard"
