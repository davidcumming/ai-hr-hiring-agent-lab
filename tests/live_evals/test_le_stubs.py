"""LE-001…LE-007 — live (model-backed) evaluation stubs, DEFERRED.

Per the eval contract, all live evals are deferred until live Foundry wiring
lands under the deferred provider ADR: this slice ships only the deterministic
mock backend (``ai_backend_type = none``), so no live model behaviour exists
to evaluate. Each stub skips with the contract's deferral rationale and pins
the LE id so the deferred scope stays visible in every test run.
"""

from __future__ import annotations

import pytest

_DEFERRAL = "live eval not applicable until Foundry wiring — deferred per eval contract"


def test_le_001_grounded_advisory_output():
    """LE-001 — grounded, advisory-only end-to-end output quality (FR-001)."""
    pytest.skip(_DEFERRAL)


def test_le_002_confidence_calibration_and_decision_language():
    """LE-002 — confidence calibration / no decision language (UFM-006/011)."""
    pytest.skip(_DEFERRAL)


def test_le_003_fairness_trap_resistance():
    """LE-003 — prohibited-factor fairness traps never influence scores (UFM-001)."""
    pytest.skip(_DEFERRAL)


def test_le_004_prompt_injection_resistance_live():
    """LE-004 — live injection resistance (UFM-004; deterministic analogue DT-012)."""
    pytest.skip(_DEFERRAL)


def test_le_005_missing_evidence_discipline_live():
    """LE-005 — live missing-evidence discipline, no fabricated citations (UFM-003/009)."""
    pytest.skip(_DEFERRAL)


def test_le_006_council_role_adherence_live():
    """LE-006 — live per-role council adherence across modes (FR-006)."""
    pytest.skip(_DEFERRAL)


def test_le_007_adversarial_rigor_downgrade_live():
    """LE-007 — live adversarial rigor/escalation manipulation attempts (UFM-002)."""
    pytest.skip(_DEFERRAL)
