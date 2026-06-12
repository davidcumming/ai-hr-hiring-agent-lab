"""Council orchestrator — single synchronous pipeline (plan §3.7).

Sequence (sequence indices recorded for DT-016):
  1. Code roles 1-2 (normalize; ingest/version/build packet).
  2. Evidence Extraction — the FIRST provider call, only after packet completion.
  3. Code role 4 (Deterministic Rules Validator) — before judgment roles.
  4. Judgment roles for the mode (advocates, then scoring/fairness where in
     mode, then the Synthesis Judge).
  5. Trigger computation — always, from the base-mode outputs.
  6. Escalation decision — may invoke the Mode C extension roles.
  7. Quality gates.
  8. Record assembly (persistence + review queue happen in the facade layer).

Every model-backed invocation goes through the provider seam, is validated
against its declared schema immediately, with exactly one bounded corrective
retry on schema failure (AB-008), and is recorded with provider metadata,
retry count, and the run's provider invocation counter.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from hr_eval_lab.config import LabConfig
from hr_eval_lab.council import code_roles, composition
from hr_eval_lab.domain.schemas import council as c
from hr_eval_lab.domain.schemas.audit import (
    ActorContext,
    EvaluationRecord,
    EvidencePacket,
    HumanReviewBlock,
    RoleExecution,
)
from hr_eval_lab.domain.schemas.evaluation import (
    AdvisoryEvaluation,
    EscalationBlock,
    FairnessBlock,
    RigorBlock,
)
from hr_eval_lab.domain.schemas.provider import PROVIDER_CONTRACT_VERSION
from hr_eval_lab.domain.schemas.request import EvaluationRequest
from hr_eval_lab.escalation.policy import decide_escalation
from hr_eval_lab.evidence.packet_builder import build_packet
from hr_eval_lab.gates.quality_gates import run_gates
from hr_eval_lab.logging_setup import get_logger
from hr_eval_lab.providers.base import CouncilProvider
from hr_eval_lab.rigor.resolver import resolve_rigor
from hr_eval_lab.rigor.triggers import compute_triggers
from hr_eval_lab.sources.fixture_store import ResolvedSource

logger = get_logger("orchestrator")

CODE_ROLE_SCHEMA_VERSION = "1.0"


class _Run:
    """Mutable per-run state: sequence indices + provider invocation counter."""

    def __init__(self) -> None:
        self.sequence = 0
        self.invocations = 0
        self.executions: list[RoleExecution] = []
        self.prior_outputs: dict[str, dict] = {}

    def next_index(self) -> int:
        index = self.sequence
        self.sequence += 1
        return index

    def record_code_role(self, role_id: str, output: dict) -> int:
        index = self.next_index()
        self.executions.append(
            RoleExecution(
                sequence_index=index,
                role_id=role_id,
                role_kind="code",
                schema_version=CODE_ROLE_SCHEMA_VERSION,
                output=output,
                provider_metadata=None,
                retry_count=0,
                schema_valid=True,
            )
        )
        self.prior_outputs[role_id] = output
        return index


def _invoke_model_role(
    run: _Run,
    provider: CouncilProvider,
    role_id: str,
    packet: EvidencePacket,
    role_context: dict[str, Any],
) -> dict | None:
    """One model-backed role: provider call, immediate schema validation,
    exactly one bounded corrective retry, full recording."""
    schema = c.MODEL_ROLE_SCHEMAS[role_id]
    retry_count = 0
    run.invocations += 1
    result = provider.invoke_role(role_id, packet, role_context)
    valid = True
    try:
        schema.model_validate(result.payload)
    except ValidationError:
        retry_count = 1
        run.invocations += 1
        corrective_context = {
            **role_context,
            "corrective_hint": (
                f"Previous output failed validation against the declared "
                f"'{role_id}' output schema; return schema-valid JSON only."
            ),
        }
        result = provider.invoke_role(role_id, packet, corrective_context)
        try:
            schema.model_validate(result.payload)
            valid = True
        except ValidationError:
            valid = False  # gate 1 fails the run; no coercion, no further retries

    run.executions.append(
        RoleExecution(
            sequence_index=run.next_index(),
            role_id=role_id,
            role_kind="model",
            schema_version=PROVIDER_CONTRACT_VERSION,
            output=result.payload,
            provider_metadata=result.metadata,
            retry_count=retry_count,
            schema_valid=valid,
        )
    )
    logger.info(
        "role=%s schema_valid=%s retry_count=%d invocation_count=%d",
        role_id,
        valid,
        retry_count,
        run.invocations,
    )
    if valid:
        run.prior_outputs[role_id] = result.payload
        return result.payload
    return None


def run_council(
    config: LabConfig,
    provider: CouncilProvider,
    request: EvaluationRequest,
    actor: ActorContext,
    resume: ResolvedSource,
    cover_letter: ResolvedSource,
    job_description: ResolvedSource,
    rubric_json: dict,
    rubric_source: ResolvedSource,
    evaluation_id: str,
    correlation_id: str,
    created_at: str,
    completed_at_fn,
) -> EvaluationRecord:
    """Execute the full council pipeline and assemble the audit record."""
    run = _Run()

    # -- Role 1: Request Normalizer (code) ------------------------------------
    normalizer_output = code_roles.request_normalizer(request)
    run.record_code_role(c.ROLE_REQUEST_NORMALIZER, normalizer_output)

    rigor_resolution = resolve_rigor(
        server_default=config.rigor.default_mode,
        risk_classification=normalizer_output["risk_classification"],
        requested_rigor=request.requested_rigor,
    )
    effective_rigor = rigor_resolution.effective_rigor

    # -- Role 2: Source Ingestion/Versioning (code) — builds the packet -------
    packet = build_packet(
        resume=resume,
        cover_letter=cover_letter,
        job_description=job_description,
        rubric_json=rubric_json,
        rubric_source=rubric_source,
        evaluation_question=request.evaluation_question,
    )
    packet_sequence_index = run.record_code_role(
        c.ROLE_SOURCE_INGESTION, code_roles.source_ingestion_output(packet)
    )

    base_context: dict[str, Any] = {
        "effective_rigor": effective_rigor,
        "prior_outputs": run.prior_outputs,
        "anomalous_segments": [],
    }

    # -- Role 3: Evidence Extraction (model) — first provider call ------------
    _invoke_model_role(run, provider, c.ROLE_EVIDENCE_EXTRACTION, packet, base_context)

    # -- Role 4: Deterministic Rules Validator (code) — before judgment -------
    rules_output = code_roles.deterministic_rules_validator(packet, request)
    run.record_code_role(c.ROLE_RULES_VALIDATOR, rules_output)
    base_context["anomalous_segments"] = rules_output["anomalous_segments"]

    # -- Judgment roles for the mode -------------------------------------------
    for role_id in composition.judgment_roles_for(effective_rigor):
        _invoke_model_role(run, provider, role_id, packet, base_context)

    # -- Triggers: always computed from base-mode outputs (FR-011) ------------
    required_criteria = [
        cr.criterion_id for cr in packet.rubric.criteria if cr.kind == "required"
    ]
    triggers = compute_triggers(
        prior_outputs=run.prior_outputs,
        required_criteria=required_criteria,
        roles_in_mode=composition.model_roles_in_mode(effective_rigor),
        rubric_criteria=[cr.criterion_id for cr in packet.rubric.criteria],
    )

    # -- Escalation decision (may execute the Mode C extension roles) ---------
    decision = decide_escalation(effective_rigor, config.escalation.policy, triggers)
    if decision.run_mode_c:
        for role_id in composition.MODE_C_EXTENSION_ROLES:
            _invoke_model_role(run, provider, role_id, packet, base_context)

    # -- Quality gates (code role 10) ------------------------------------------
    synthesis = run.prior_outputs.get(c.ROLE_SYNTHESIS_JUDGE)
    auditor = run.prior_outputs.get(c.ROLE_POLICY_FAIRNESS_AUDITOR)
    extraction = run.prior_outputs.get(c.ROLE_EVIDENCE_EXTRACTION, {})
    evidence_items = extraction.get("evidence_items", [])

    # flags_present is True by construction: the only result type is the
    # Literal[True] AdvisoryEvaluation model (gate 5 is belt-and-braces; the
    # parameter exists so unit tests can exercise the failing branch).
    gate_results = run_gates(
        packet=packet,
        role_executions=run.executions,
        evidence_items=evidence_items,
        synthesis=synthesis,
        fairness=auditor,
        flags_present=True,
    )
    run.record_code_role(
        c.ROLE_QUALITY_GATES,
        {
            "role": "quality_gate_evaluators",
            "gate_results": [g.model_dump(mode="json") for g in gate_results],
        },
    )

    gates_passed = all(g.result == "pass" for g in gate_results)
    status = "completed" if gates_passed else "blocked"

    # -- Assemble the advisory result -------------------------------------------
    result: AdvisoryEvaluation | None = None
    if synthesis is not None:
        fairness = FairnessBlock(
            reviewed=auditor is not None,
            findings=(auditor or {}).get("findings", []),
            overall_severity=(auditor or {}).get("overall_severity", "info"),
            prohibited_factor_violations=(auditor or {}).get(
                "prohibited_factor_violations", []
            ),
            anomalous_content_flags=rules_output["anomalous_segments"],
        )
        result = AdvisoryEvaluation(
            decision_support_only=True,
            human_review_required=True,
            recommendation_label=synthesis["recommendation_label"],
            criterion_evaluations=synthesis["criterion_evaluations"],
            disagreements=synthesis["disagreements"],
            fairness=fairness,
            confidence=synthesis["confidence"],
            confidence_score=synthesis["confidence_score"],
            limitations=synthesis["limitations"],
            rigor=RigorBlock(
                effective_rigor=effective_rigor,
                resolution_explanation=rigor_resolution.explanation,
                downgrade_attempted=rigor_resolution.downgrade_attempted,
                requested_rigor=rigor_resolution.requested_rigor,
            ),
            escalation=EscalationBlock(
                policy=decision.policy,
                provenance=decision.provenance,  # type: ignore[arg-type]
                triggers_fired=decision.triggers_fired,
                mode_c_executed=decision.run_mode_c,
                rationale=decision.rationale,
            ),
            triggers=triggers,
            quality_gates=gate_results,
            ai_backend_type=provider.ai_backend_type,  # type: ignore[arg-type]
        )

    # -- Human review block (review always required) ----------------------------
    review_reasons = ["advisory_only_policy: every evaluation requires human review"]
    if decision.human_review_mandatory_reason:
        review_reasons.append(decision.human_review_mandatory_reason)
    if not gates_passed:
        review_reasons.append("quality_gate_failure")
    if rules_output["anomalous_content_detected"]:
        review_reasons.append("anomalous_content_flagged")

    # -- Role 11: Persistence/Review Queue (code) — entry shaped here; the
    # facade's store performs the actual append-only writes.
    run.record_code_role(
        c.ROLE_PERSISTENCE_REVIEW_QUEUE,
        {
            "role": "persistence_review_queue",
            "review_queue_entry": {"mandatory_reasons": review_reasons},
            "status": status,
        },
    )

    record = EvaluationRecord(
        evaluation_id=evaluation_id,
        correlation_id=correlation_id,
        created_at=created_at,
        completed_at=completed_at_fn(),
        status=status,  # type: ignore[arg-type]
        actor=actor,
        request=request.model_dump(mode="json"),
        sources=packet.sources,
        evidence_packet=packet,
        packet_sequence_index=packet_sequence_index,
        role_executions=run.executions,
        rigor_resolution=rigor_resolution,
        triggers=triggers,
        escalation={
            "policy": decision.policy,
            "provenance": decision.provenance,
            "triggers_fired": decision.triggers_fired,
            "mode_c_executed": decision.run_mode_c,
            "rationale": decision.rationale,
            "human_review_mandatory_reason": decision.human_review_mandatory_reason,
        },
        gate_results=gate_results,
        provider_invocation_count=run.invocations,
        effective_mode=composition.mode_letter(effective_rigor, decision.run_mode_c),  # type: ignore[arg-type]
        result=result,
        human_review=HumanReviewBlock(
            human_review_required=True, reasons=review_reasons
        ),
    )
    logger.info(
        "evaluation_id=%s status=%s mode=%s invocations=%d gates_passed=%s",
        evaluation_id,
        status,
        record.effective_mode,
        run.invocations,
        gates_passed,
    )
    return record
