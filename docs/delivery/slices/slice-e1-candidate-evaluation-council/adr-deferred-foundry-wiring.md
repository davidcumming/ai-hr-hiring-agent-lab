# ADR (Deferred): Live Foundry Agents Wiring for the Candidate Evaluation Council

| Field | Value |
|---|---|
| Status | **Deferred — Draft. NOT APPROVED. Requires human approval before any live Foundry wiring begins.** |
| Date deferred | 2026-06-11 |
| Deferral authority | Product Owner decision 2026-06-11, recorded in slice spec §2.2.2 (BQ-001) and §2.2.3 (BQ-005) |
| Slice of record | `slice-e1-candidate-evaluation-council` (Stage 6 — [`architecture-check.md`](./architecture-check.md) §6, gap G-001 / plan flag AF-001) |
| Decision owner | Human release authority / Product Owner — **no agent may approve, advance, or act on this ADR** |
| Gates | This ADR must be approved by a human **before the live-wiring slice starts**. Until then it blocks: any live Foundry/Azure wiring, resource creation, model/agent calls, token spend, live evals LE-001…LE-007, Entra integration, and region adoption. |
| Does NOT block | Local deterministic implementation in slice E1 (deterministic mock provider + non-functional Foundry seam stub) — explicitly unblocked by PO §2.2.2 |

> This file is **draft input for the human ADR author** (per `adr-gap-detector` skill §7 step 4,
> produced on explicit orchestrator instruction). It records *what must be decided and why*, not
> the decision. When taken up, it should be moved/renumbered into the repo ADR sequence
> (`docs/architecture/adr/`) by its human author.

## Context

Slice E1 builds the Calibrated Evaluation Council against a deterministic mock provider behind a
provider seam (`CouncilProvider`) whose declared live target is **Foundry Agents behind the service
boundary** (slice spec §15). The Foundry companion document itself lists the wiring details as open
decisions (`foundry-agent-framework-architecture.md` §11, items 1–2), and the repo has no ADRs
(greenfield). The Product Owner decided on 2026-06-11 that pinning these details must not block
local deterministic coding; the ADR is therefore **deferred, not skipped**, and this stub is the
durable record of that deferral.

Interim seam-contract authority while deferred (PO §2.2.2): the Foundry companion §8 required
trace/eval metadata **plus** slice E1's versioned provider schemas
(`src/hr_eval_lab/domain/schemas/provider.py`, `role_schema_version`). The wiring slice must
reconcile what was built against what this ADR decides; schema versioning exists to make any drift
visible.

## Decision questions this ADR must answer (scope)

1. **Agent Service vs Agent Framework.** Should the live council roles run as Foundry Agent
   Service agents, as an Agent Framework workflow, or a combination — per the companion §5
   backend-choice decision table — and which roles map to which construct?
2. **Backend-type enumeration.** What is the final enumeration of supported
   `provider.ai_backend_type` values (slice E1 ships `none | foundry_agents`; `foundry_agents` is a
   non-functional stub)? Does the live target need finer-grained values (e.g. agent-service vs
   agent-framework-workflow), and what does each select?
3. **Live trace/eval metadata contract.** The exact field schema for the companion §8 set — AI
   backend type, model/agent identifier, workflow version, trace ID, evaluation-run ID, token and
   latency metrics, validated-output confirmation — including field names/types, which fields are
   placeholders vs mandatory live values, and where each lives (safe telemetry vs the
   evidence/audit record; companion §11 item 2). Slice E1's placeholders
   (`ai_backend_type`, `trace_id`, `agent_run_id`, `model_deployment`, `prompt_version`,
   `token_usage`, `latency_ms`, plus the `eval_run_id` placeholder added per architecture-check
   condition C-COND-2) are the reconciliation baseline.
4. **Region / data residency.** The approved Canadian region and approved model deployments for
   any live call (BQ-005; companion §9: an unapproved region or deployment is never introduced
   silently). This is a mandatory human gate in its own right before any live eval.

## Options sketch (balanced; no recommendation — the human decides)

- **Foundry Agent Service** — managed agent hosting per role. Pros: managed runtime, built-in
  tracing identifiers. Cons/risks: per-role cost and lifecycle management; mapping 6–8 council
  roles to hosted agents may be heavier than needed.
- **Agent Framework workflow** — one orchestrated workflow implementing the council. Pros: matches
  the council's single-pipeline shape and the companion's multi-step workflow row; one workflow
  version to record. Cons/risks: workflow-versioning discipline becomes load-bearing; less
  isolation between roles.
- **Hybrid / phased** — model-endpoint or minimal-agent start for low-complexity roles, workflow
  for the council pipeline later. Pros: smallest live footprint first. Cons/risks: two backend
  shapes to keep in seam parity; risks re-opening this ADR.

## Consequences if left undecided

No impact on slice E1 (all-local, mock-backed, stub raises on use). The live-wiring slice cannot
start: live evals LE-001…LE-007 remain deferred, the seam contract cannot be finalized beyond
placeholders, and region/residency remains unapproved.

## Adjacent decisions explicitly NOT pinned here

- Facade hosting shape at wiring time (e.g. Azure Functions per canonical architecture vs the lab's
  local FastAPI facade) — note for the wiring slice's planning, separate decision.
- Admin rigor-config surface and config-change audit subsystem (slice spec §16 gap 2 / plan
  AF-006) — separate follow-up slice and its own ADR check.
- Evidence retention policy for live records (slice spec §14) — deferred, non-blocking.
