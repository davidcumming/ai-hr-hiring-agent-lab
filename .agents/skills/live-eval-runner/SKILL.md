---
name: live-eval-runner
description: Executes approved live-model eval scenarios against a real deployed model with full version tracking, producing a run record. Use when running live evals (Stage 10); records evidence only.
context: fork
---
# Skill: Live Eval Runner

**Used at:** Stage 10 — Live eval execution (Orchestration Map §3 stage table)
**Execution model:** `recommended-subagent`
**Supports:** Process Doc §19 Live-Model Eval Rules, §21 Mandatory Re-Eval Triggers

---

## 1. Purpose

Execute approved live-model eval scenarios against a real deployed model with full version tracking, and produce a run record holding artifact references, per-scenario pass/fail results, and run metadata. This skill runs exactly what the approved eval contract specifies and records exactly what happened — it does not invent or change scenarios, interpret or classify failures, or decide whether failures are acceptable. It records evidence; classification and accept/reject decisions belong to Stage 11 and human release authority.

---

## 3. Do Not Use This Skill For

- Inventing or changing scenarios or pass/fail rubrics — the eval contract is fixed before this skill runs.
- Interpreting or classifying failures (`eval-failure-classifier`) or summarizing for the repo (`eval-result-summarizer`).
- Slices whose eval contract documents the non-agentic carve-out — Stage 10 records a skip and `eval-result-summarizer` captures the rationale.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Approved eval contract | Yes | Approved version, not a draft. |
| 2 | Eval scenario files | Yes | Complete definitions with expected behaviour and pass/fail rubrics. |
| 3 | Model name + deployment endpoint + API version | Yes | From deployment config or policy doc. |
| 4 | Version manifests | Yes | Model, prompt, tool schema, orchestration, workflow/state. Read the manifest files; do not infer from filenames or commits. |
| 5 | Eval-data governance approval | Yes | Must cover the scenario set; surface a blocker if it cannot be located. |
| 6 | Runtime/environment configuration | Yes | Azure region, endpoint, model tier, rate-limit settings. |
| 7 | Required runs per scenario | Yes | From the eval contract threshold table (Process Doc §19.1 risk tiers). |
| 8 | Prior run records | If re-eval | For comparison or threshold verification. |

If any required input is missing or ambiguous, surface a blocker and do not begin execution.

---

## 7. Process Steps

### Step 1 — Pre-run verification

1. Confirm eval contract status is `approved` (not `draft`).
2. Confirm governance approval exists and covers the scenario set. Do not proceed past a missing approval.
3. Confirm all version manifests are readable; record every version value in the run record before the first scenario runs.
4. Confirm the deployment target (endpoint, region, tier) matches the contract's environment.
5. Confirm the required run count per scenario for the slice's risk tier (Process Doc §19.1).

If any check fails, stop and produce a pre-run blocker report.

### Step 2 — Execute scenarios

For each scenario, repeating for the required run count:

1. Submit scenario inputs to the model; capture the full response and tool-call traces.
2. Apply the eval contract's pass/fail rubric unchanged; record result and rubric score per run.
3. Capture token usage and latency (and cost if the contract sets cost/latency thresholds, Process Doc §20).
4. Store full response artifacts to the external artifact store (never the code repo); record the reference (path, blob URL, or ID) in the run record.

Do not stop early on individual failures — run the full count unless a catastrophic error prevents continuation.

### Step 3 — Capture errors and skipped scenarios

Record the reason (API error, quota, governance hold, missing input) and mark `error` or `skipped`. Never mark an incomplete scenario as `passed`.

### Step 4 — Produce the run record

Populate the template with run metadata (all versions, date, executor, environment), per-scenario results, threshold summary (pass rate vs. required threshold per tier), external artifact references, and errors/skips. References only — no full outputs or sensitive responses in the record.

### Step 5 — Hand off

Pass the completed run record to the orchestrator, which dispatches `eval-result-summarizer` and, if failures exist, `eval-failure-classifier`.

---

## 9. Output Format

Use `templates/live-eval-run-record-template.md`. Place the record at `docs/delivery/slices/<slice-id>/live-eval-run-record-<run-date>.md`. Store full artifacts externally per Process Doc §23.3 durable audit archive requirements; the record holds resolvable references only — never full transcripts, and no PHI/PII in the body.

---

## 10. Quality Bar

Before handoff, confirm:

- Every scenario in the contract was attempted; the full required run count completed, or the shortfall is logged as `error`/`skipped`.
- No scenario stopped early because individual runs failed.
- Pass/fail applied using the eval contract's rubric, not an improvised one; skipped/errored scenarios are not marked `passed`.
- All version values (model, prompt, tool schema, orchestration, workflow state) were read from manifests and appear in the record.
- Token usage and latency captured per scenario; cost captured if the contract set thresholds.
- No real PHI/PII in eval payloads without documented governance approval; data classification (synthetic / de-identified / approved production) recorded; Canadian residency considered where applicable.
- Full outputs stored externally; every external artifact has a resolvable reference.
- Threshold summary complete; aggregate pass rate calculated and compared against the §19.1 required threshold.
- Failure detail rows present for every failed scenario; errors/skips documented with reasons.
- Run status stated (`complete`, `partial`, or `blocked`); the record neither classifies nor accepts/rejects failures.

See AGENTS.md cross-cutting rules (Authority and human gates; Evidence, privacy, context).

---

## 11. Failure Modes to Avoid

- Running against a model version not specified in the contract, or recording versions from memory/filenames instead of manifests.
- Stopping early when some scenarios fail; applying a different rubric than the contract's.
- Marking skipped or errored scenarios as passed.
- Writing full outputs or sensitive transcripts into the code repo, or using real PHI/PII without governance approval.

---

## 13. Handoff to Next Skill

Pass the completed run record to **`eval-result-summarizer`** for a concise, repo-safe summary. If failures exist, the orchestrator also dispatches **`eval-failure-classifier`** (isolated-verification) using the run record and eval contract.

Return with: run status (`complete`/`partial`/`blocked` with reason); scenario counts (run/pass/fail/error-skip); whether aggregate pass rate met the tier threshold; external artifact reference count; recommended next skill `eval-result-summarizer`. Surface evidence only — do not accept/reject failures or recommend merge.
