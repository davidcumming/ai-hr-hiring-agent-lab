# Candidate Evaluation Council — Subsystem Architecture

Detail view of the council subsystem as implemented in
`src/hr_eval_lab/council/`, `rigor/`, `escalation/`, `gates/`, and
`evidence/`. Present tense; only what exists in code. Behavior-level
description: [`../product-current-state/candidate-evaluation-council.md`](../product-current-state/candidate-evaluation-council.md).

## 1. Composition — the 11-role registry

`council/composition.py` defines the source-controlled role registry in
pipeline order (role ids from `domain/schemas/council.py`):

| # | Role id | Kind |
|---|---|---|
| 1 | `request_normalizer` | code |
| 2 | `source_ingestion_versioning` | code |
| 3 | `evidence_extraction` | model |
| 4 | `deterministic_rules_validator` | code |
| 5 | `merit_advocate` | model |
| 6 | `risk_gaps_advocate` | model |
| 7 | `neutral_scoring_judge` | model (Mode B+) |
| 8 | `policy_fairness_auditor` | model (Mode B+) |
| 9 | `synthesis_judge` | model |
| 10 | `quality_gate_evaluators` | code |
| 11 | `persistence_review_queue` | code |

Mode C extension roles (run only via the escalation decision):
`second_synthesis_judge`, `rubric_calibration_judge`.

Judgment-role tables per effective rigor:

- `standard` → advocates + synthesis judge (**Mode A**).
- `high_impact` → advocates + neutral scoring judge + policy/fairness auditor
  + synthesis judge (**Mode B**).
- `escalated` → the Mode B base composition; the two extension roles are
  added by the escalation decision (**Mode C**, provenance
  `configured_escalated`).

`mode_letter()` derives the recorded `effective_mode`: `C` whenever the
extension roles executed, otherwise `A` for standard and `B` for
high-impact/escalated base.

## 2. Orchestrator flow (`council/orchestrator.py`)

A single synchronous pipeline per evaluation, with a mutable per-run state
(`_Run`) carrying the sequence counter, provider invocation counter, recorded
executions, and validated prior outputs:

1. **Role 1 (code)** — normalize the request; assign risk classification
   `hiring_candidate_evaluation`. Output is metadata-only.
2. **Rigor resolution** — `rigor/resolver.py` pure function over server
   default + risk classification + advisory `requested_rigor` (downgrade
   attempts recorded and ignored).
3. **Role 2 (code)** — build the evidence packet
   (`evidence/packet_builder.py`) from hash-verified sources; record the
   packet sequence index (proof that packet completion precedes provider
   calls; persisted as `packet_sequence_index`).
4. **Role 3 (model)** — Evidence Extraction: the **first** provider call.
5. **Role 4 (code)** — Deterministic Rules Validator, **before** any
   judgment role: required-document presence, D1 work-eligibility evidence
   presence/absence (absence = missing evidence, never disqualification),
   instruction-like-content scan over candidate segments and the
   `evaluation_question`. Its anomalous-segment list feeds the role context
   of subsequent model roles.
6. **Judgment roles for the mode** — invoked in table order.
7. **Triggers** — all six computed from base-mode outputs, always
   (`rigor/triggers.py`).
8. **Escalation decision** (`escalation/policy.py`) — may execute the two
   Mode C extension roles.
9. **Role 10 (code)** — the six quality gates (`gates/quality_gates.py`);
   any failure ⇒ status `blocked`, else `completed`.
10. **Result assembly** — `AdvisoryEvaluation` with rigor, escalation,
    fairness, trigger, and gate blocks.
11. **Role 11 (code)** — shapes the review-queue entry; the facade's store
    performs the actual append-only writes (persistence happens in the
    facade layer, not inside the orchestrator).

### Model-role invocation discipline

`_invoke_model_role()` wraps every provider call: invoke → validate payload
against the role's declared schema (`MODEL_ROLE_SCHEMAS`) → on failure,
exactly **one** corrective retry with a `corrective_hint` in the role context
→ on second failure, record the output as `schema_valid = false` (gate 1
fails the run; no coercion). Every invocation increments the run's provider
invocation counter, persisted as `provider_invocation_count`.

## 3. Code roles (`council/code_roles.py`)

Deterministic, facade-owned, zero provider calls; outputs recorded in the
audit record like every other role (schema version `1.0`,
`CODE_ROLE_SCHEMA_VERSION`). The instruction-like marker list is a
source-controlled constant (`INSTRUCTION_LIKE_MARKERS`).

## 4. Schema contracts (`domain/schemas/council.py`)

One pydantic schema per model-backed role output, all `extra="forbid"`, all
in a single source consumed by the orchestrator's validation map, the mock
provider, and the mock-parity tests (DT-013):

- `EvidenceExtractionOutput` — evidence items (id, criterion, artifact,
  segment, verbatim quote, supporting/contrary/contextual relation) +
  coverage notes. **Deliberately has no score or recommendation field** —
  evaluative drift is schema-impossible (DT-017).
- `MeritAdvocateOutput` / `RiskGapsAdvocateOutput` — stance-typed arguments +
  proposed scores (1–5, citations, missing-evidence flag).
- `NeutralScoringOutput` — proposed scores only.
- `PolicyFairnessOutput` — findings (severity, category, segment refs),
  overall severity, prohibited-factor violations, anomalous-content flag.
- `SynthesisOutput` — per-criterion evaluations (score, rationale,
  supporting/contrary citations, missing-evidence note), disagreements,
  closed advisory `recommendation_label`, confidence + 0–100 score,
  limitations.
- `SecondSynthesisOutput` (Mode C) — concurrence (`concur|partial|differ`),
  rationale, score deltas, confidence.
- `RubricCalibrationOutput` (Mode C) — per-criterion anchor-consistency
  notes + overall flag.

## 5. ORCHESTRATION_VERSION pinning

`domain/schemas/provider.py` pins:

- `ORCHESTRATION_VERSION = "council-composition-v1"` — the version of the
  source-controlled mode tables, stamped into the `ProviderMetadata` block of
  **every** model-role execution (so every persisted record carries which
  council composition produced it).
- `PROVIDER_CONTRACT_VERSION = "1.0"` — the seam schema version, recorded as
  `role_schema_version` per invocation and as the `schema_version` of every
  model-role execution row.

Together with `RECORD_SCHEMA_VERSION = "1.0"` (audit record), these make any
future contract drift visible in persisted data rather than silent.
