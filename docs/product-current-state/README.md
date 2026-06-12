# Product Current-State Documentation

This folder describes **what the application currently does** — present tense,
implementation-verified, slice-agnostic (Process Doc §7.1). Every claim here
traces to code, configuration, fixtures, or tests in this repository. Where a
claim is inferred from code rather than verified by a test, the doc says so
inline.

## What the application is, at a glance

The repository contains a working, fully local **Candidate Evaluation Council
lab**: a FastAPI service (`src/hr_eval_lab/`) that accepts a single synthetic
candidate evaluation request, runs an 11-role "Calibrated Evaluation Council"
pipeline against an evidence packet built from hash-verified fixture (or
inline synthetic) documents, applies deterministic quality gates, and persists
a complete audit record — plus per-artifact projections (request, source
documents, evidence packet, per-role council transcripts, synthesis, gates,
provider metadata, human review) and a text-free summary row — locally
through a formal storage-backend seam. All AI-role outputs come from a
**deterministic mock provider** (provider id `deterministic_mock`); no live
model call is involved anywhere in the runtime path. The normal local app
uses local filesystem persistence. The Azure Functions wrapper can explicitly
overlay Azure Blob persistence for evaluation audit records/artifacts when
`HRHA_STORAGE_BACKEND=azure_blob` and `HRHA_ENABLE_AZURE_STORAGE=true`.

Foundry-facing surfaces exist only as **fail-closed, non-functional
scaffolds**: the three Foundry provider scaffolds raise safe configuration
errors on any use (selection is additionally blocked by
`HRHA_ENABLE_LIVE_AZURE` and `HRHA_PROVIDER_KILL_SWITCH`). Storage smoke
checks remain disabled by default; the explicit storage config path uses the
narrow `HRHA_ENABLE_AZURE_STORAGE` gate. The `infra/` skeleton is placeholder
documentation only and executes nothing. Live model wiring remains deferred
and human-gated. A versioned, source-controlled prompt registry
(`src/hr_eval_lab/prompts/`) records prompt provenance into every audit
record; templates are never executed.

Every result is advisory decision support: `decision_support_only = true` and
`human_review_required = true` are structurally enforced (`Literal[True]`
fields in `src/hr_eval_lab/domain/schemas/evaluation.py`), and every
evaluation produces a human-review queue entry.

A deterministic test suite (`tests/`, DT-001…DT-018 plus RP and smoke
coverage) covers the behavior described here: 176 tests pass, 7 live-eval
stubs skip with a documented deferral rationale, 0 fail (verified run,
2026-06-12).

## Documents in this folder

| Document | Contents |
|---|---|
| [`candidate-evaluation-council.md`](./candidate-evaluation-council.md) | The full behavior reference: API endpoints (operation IDs, idempotency/correlation headers), envelope and error model, simulated auth, council orchestration and modes, rigor and escalation, quality gates, evidence packet, persistence (artifact tree, summary rows, storage-backend seam) and audit record, idempotency, review queue, CLI and local scripts, configuration surface and environment guards, prompt registry, fixtures, logging guarantees, and limitations. |

## How these docs relate to other documentation

- **Architecture (what is physically built):**
  [`../architecture/actual-technical-architecture.md`](../architecture/actual-technical-architecture.md)
  and companions describe the implemented structure. There are currently **no
  architecture guideline documents and no approved ADRs** in this repo's
  `docs/architecture/` tree; the vendored standards under
  `standards/azure-development-standards/` define process, not this
  application's architecture.
- **Slice delivery artifacts (intent and history, NOT current-state truth):**
  `docs/delivery/slices/<slice-id>/` holds specs, plans, eval contracts,
  deviation logs, and state files for individual delivery slices. Per the
  source-of-truth hierarchy (AGENTS.md, Process Doc §7), those artifacts
  record intent and delivery history; when they disagree with code, tests, or
  these current-state docs, the code and tests win.
- **Integration:** [`../integration/README.md`](../integration/README.md)
  records that **no live integration exists** — only in-code seams,
  fail-closed scaffolds, and a deferred, unapproved ADR draft.
  [`../integration/copilot-studio-tool-readiness.md`](../integration/copilot-studio-tool-readiness.md)
  records what the implemented API contract already provides for a future
  Copilot Studio tool registration (documentation only; no portal
  configuration exists).

## Maintenance rule

Update these docs at documentation-reconciliation time (Process Doc §25),
from the full working tree — never from individual commits, and never by
copying aspirational text from planning documents.
