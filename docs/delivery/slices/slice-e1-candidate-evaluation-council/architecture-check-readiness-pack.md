# Architecture Guideline Compliance Report — Azure/Foundry Readiness Pack

> Stage 6 — Architecture compliance & ADR check for the readiness-pack coding batch.
> Produced with `architecture-guideline-checker`; `adr-gap-detector` consulted only for the
> flags raised in [`implementation-plan-readiness-pack.md`](./implementation-plan-readiness-pack.md) §5
> (conditional trigger satisfied; not run speculatively).
> Plan reviewed: implementation-plan-readiness-pack.md (Stage 5 final, 2026-06-11).
> Guidelines: slice spec §15 adopted constraints; baseline architecture-check.md (2026-06-11)
> findings and conditions C-COND-1/C-COND-2 remain in force. Actual-architecture doc:
> `docs/architecture/actual-technical-architecture.md` (exists; used for drift detection only).

## Findings

| # | Plan area | Finding | Notes |
|---|---|---|---|
| 1 | T1 domain hardening (additive schemas, no rename churn) | **Compliant** | Single schema source preserved; canonical JSON unchanged; deterministic serialization retained |
| 2 | T2 storage backend boundary + local FS layout | **Compliant** | Formalizes the storage-doc-shaped seam already adopted (§15 row 4); artifact-per-evaluation layout mirrors blob design (`{container}/{id}/...`); metadata-first never-log rows preserved |
| 3 | T2 Azure Blob scaffold, disabled by default, lazy import, fail-closed | **Compliant** | Matches documented live storage intent; no resource creation, no network, no secrets; identity-first auth documented as future path (per identity design) |
| 4 | T3 provider registry with 4 provider IDs, mock default | **Compliant — ADR boundary respected** | Widens the seam enumeration to keep all live runtime options open; **chooses none** — the live runtime choice stays inside the deferred ADR's scope (G-001). The enumeration question is question 2 of `adr-deferred-foundry-wiring.md`; this batch records the candidate IDs there as reconciliation input rather than deciding |
| 5 | T3 kill switch + live-enable env guards | **Compliant** | Server-side only; request body still cannot influence provider selection (test-pinned) |
| 6 | T3 ProviderMetadata extension (template id/version, model_or_agent_ref, warnings, safe_error) | **Compliant** | Additive, nullable, deterministic under mock; stays within the C-COND-2 placeholder discipline; live field semantics still owned by the deferred ADR |
| 7 | T4 versioned prompt registry | **Compliant — previously "not covered", now resolved as config** | Current-state docs record "no prompt seam exists"; adding one was checked against §15 row 7 (server-side, source-controlled configuration) and the quality-controls doc (template id/version per invocation). It is source-controlled configuration, not a new architecture pattern → **no new ADR required**. Stage 12 must update the stale current-state statement |
| 8 | T5 per-role transcript artifacts derived from the record | **Compliant** | Single source of truth (the record) projected to artifacts at persistence time; no second truth; safe-response boundary unchanged |
| 9 | T6 OpenAPI: operation IDs, X-Correlation-Id, optional Idempotency-Key header | **Compliant** | Additive within the adopted envelope/status vocabulary; body idempotency_key remains canonical; mismatch → HTTP 400 (consistent with C-COND-1 mapping) |
| 10 | T7 CLI demo via in-process HTTP facade; smoke scaffolds disabled by default | **Compliant** | Facade-only access preserved (DT-018 discipline); smoke scripts honour the live-enable guard and perform no network by default |
| 11 | T8 infra skeleton, placeholders only | **Compliant** | IaC-as-documentation; no deploy commands, no real identifiers; consistent with repo-first preference in AGENTS.md |
| 12 | T9 config samples | **Compliant** | Source-controlled, no secrets; git history is the change record |

## Drift check (actual architecture vs plan)

The plan deliberately *changes* two statements in the current-state/architecture docs:
"no prompt seam exists" and "LocalStore is a concrete class, not an abstract interface."
Both changes are forward-compatible refinements of the documented seams, not contradictions
of any guideline. They are recorded here so Stage 12 reconciliation updates the docs —
not as violations.

## ADR gap disposition

- **G-001 (live Foundry runtime choice)** — unchanged: **deferred, NOT approved**, human
  gate before any live wiring. This batch adds no live behaviour and selects no runtime.
  The provider-ID enumeration (`deterministic_mock | foundry_project_responses |
  foundry_prompt_agent | foundry_hosted_agent`) is scaffolding kept deliberately
  option-neutral; the final enumeration remains ADR question 2.
- **Azure Blob/Table live storage** — documented intent since the baseline batch;
  scaffold-only here; ADR only if implementation must deviate from the documented shapes
  (it does not).
- **No new ADR is required before local deterministic implementation.** No blocking gaps.

## Verdict

**Clear** (for local deterministic implementation of the readiness pack), with the
standing conditions: C-COND-1 (HTTP-code mapping per API-contracts §4) and C-COND-2
(nullable trace/eval placeholders) continue to apply; G-001 remains a human-gated
deferred ADR blocking only the live-wiring slice.

→ Proceed to Stage 7.
