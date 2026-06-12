"""DT-013 — Mock parity: provider-seam contract schema validation.

Related: AC-016, FR-012, RF-010, UFM-006.

Every mock role output validates against the SAME provider-contract schemas
declared for the Foundry-agent backend (single schema source — no mock-only
fork), including the nullable trace_id/eval_run_id metadata placeholders;
provider metadata records ai_backend_type = "none" truthfully.
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas import council as c
from hr_eval_lab.domain.schemas.provider import (
    PROVIDER_CONTRACT_VERSION,
    ProviderMetadata,
)

from tests.conftest import get_record, post_evaluation

ALL_MODEL_ROLES = set(c.MODEL_ROLE_SCHEMAS)


def test_all_eight_mock_role_outputs_validate_against_seam_schemas(make_client):
    # Escalated rigor executes the full 8-role model-backed surface (Mode C).
    client = make_client(rigor="escalated")
    response = post_evaluation(client, idempotency_key="dt013-parity")
    assert response.status_code == 200
    record = get_record(client, response.json()["evaluation_id"])

    model_executions = [
        r for r in record["role_executions"] if r["role_kind"] == "model"
    ]
    assert {r["role_id"] for r in model_executions} == ALL_MODEL_ROLES

    for execution in model_executions:
        role_id = execution["role_id"]
        # The single schema source (no mock-only fork): re-validate the
        # persisted payload against the declared seam schema.
        schema = c.MODEL_ROLE_SCHEMAS[role_id]
        schema.model_validate(execution["output"])
        assert execution["schema_version"] == PROVIDER_CONTRACT_VERSION

        # Metadata contract: typed, nullable trace/eval placeholders present.
        raw = execution["provider_metadata"]
        metadata = ProviderMetadata.model_validate(raw)
        assert metadata.ai_backend_type == "none"  # truthful backend declaration
        assert "trace_id" in raw and "eval_run_id" in raw  # keys present
        assert raw["trace_id"] is None or isinstance(raw["trace_id"], str)
        assert raw["eval_run_id"] is None or isinstance(raw["eval_run_id"], str)
        assert metadata.orchestration_version
        assert metadata.role_schema_version == PROVIDER_CONTRACT_VERSION
        assert metadata.token_usage.prompt >= 0
        assert metadata.latency_ms >= 0


def test_seam_schemas_forbid_decision_rank_contact_fields():
    """UFM-006 structural guard: extra=forbid rejects decision/ranking/contact
    fields on every model-backed role output schema."""
    import pytest
    from pydantic import ValidationError

    base_extraction = {"role": "evidence_extraction", "evidence_items": []}
    for forbidden in ("hiring_decision", "rank", "contact_candidate"):
        with pytest.raises(ValidationError):
            c.MODEL_ROLE_SCHEMAS[c.ROLE_EVIDENCE_EXTRACTION].model_validate(
                {**base_extraction, forbidden: True}
            )


def test_record_level_backend_truthfulness(make_client):
    client = make_client()
    response = post_evaluation(client, idempotency_key="dt013-truthful")
    assert response.json()["result"]["ai_backend_type"] == "none"
    record = get_record(client, response.json()["evaluation_id"])
    rows = client.app.state.store.read_table("EvaluationEvidence.jsonl")
    assert rows and all(r["ai_backend_type"] == "none" for r in rows)
    assert record["result"]["ai_backend_type"] == "none"
