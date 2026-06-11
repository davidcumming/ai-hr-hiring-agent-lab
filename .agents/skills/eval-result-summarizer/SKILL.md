---
name: eval-result-summarizer
description: Produces a concise, repo-safe eval summary from a live eval run record and artifact references. Use when summarizing eval results for the repo and closeout package (Stage 11).
context: fork
---
# Skill: Eval Result Summarizer

**Used at:** Stage 11 — Eval results & failure classification (Orchestration Map §3 stage table)
**Execution model:** `recommended-subagent`
**Supports:** Process Doc §19 Live-Model Eval Rules, §29 Slice Closeout Package

---

## 1. Purpose

Produce a concise, repo-safe eval summary from the live eval run record and external artifact references. The summary is the primary human-readable record of what the eval found and enters the code repo and closeout package. This skill surfaces what happened so that `eval-failure-classifier` and human release authority can decide; it does not classify failures or judge blocking vs. non-blocking, and it does not adjust the run record's pass/fail results.

**Non-agentic carve-out:** when the eval contract documents the carve-out (Stage 10 skipped), produce the same summary artifact with the deterministic-only rationale recorded instead of a run record. The rationale must explicitly state no model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency; mark version and threshold fields `N/A — non-agentic carve-out`. This is the only place the carve-out is handled — treat it uniformly throughout the summary.

---

## 3. Do Not Use This Skill For

- Classifying failures as blocking/non-blocking/ambiguous/flaky (`eval-failure-classifier`), or accepting/rejecting them (human release authority).
- Packaging high-risk results for human review (`high-risk-human-review-packager`) or recommending regression promotion (`regression-promotion-recommender`).
- Writing full outputs or sensitive responses into the repo, or modifying run-record results.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Live eval run record | If live evals ran | Completed record, not an in-progress draft. |
| 2 | Non-agentic skip rationale | If evals did not run | From eval contract / Stage 10 decision; see §1. |
| 3 | External artifact references | If live evals ran | URIs/paths to full transcripts (run record §6). |
| 4 | Eval contract | Yes | Context on what was required, expected rubric, and threshold. |
| 5 | Risk tier | Yes | From `eval-risk-profiler` or eval contract; sets the threshold comparison. |
| 6 | Reviewer notes | Optional | Notes captured during the run. |

If the run record is incomplete (partial/blocked), produce a partial summary and flag it clearly.

---

## 7. Process Steps

### Step 1 — Review the run record (or confirm the carve-out)

Read the entire run record: run status, version values, scenario results, threshold summary, cost/latency (if tracked), artifact references, errors/skips. If live evals are not applicable, confirm the carve-out rationale per §1.

### Step 2 — Compare against the eval contract

1. Confirm all required scenarios appear in the run record (or the carve-out is explicit).
2. Confirm the threshold comparison uses the correct risk tier (Process Doc §19.1), or mark it `N/A — non-agentic carve-out`.
3. For skipped scenarios, determine whether they were optional (regression extras), required, or N/A under the carve-out.
4. Flag any contract requirement not satisfied — do not resolve discrepancies silently.

### Step 3 — Produce the summary

Populate the template: header metadata; version block (all §19.2 fields); compact scenario results table; threshold summary; carve-out rationale when applicable; failure summary (scenario IDs + brief observed behaviour, no outputs, no classification); cost/latency if tracked; artifact reference table; gap/discrepancy flags; reviewer notes if provided; handoff notes.

### Step 4 — Verify repo-safe

No raw outputs in the body; no PHI/PII reproduced even paraphrased; sensitive detail as external references only; length suitable for a repo document.

### Step 5 — Hand off

Pass the summary to the orchestrator, which dispatches `eval-failure-classifier` if failures exist.

---

## 9. Output Format

Use `templates/eval-summary-template.md`. Place at `docs/delivery/slices/<slice-id>/eval-summary.md`, or `eval-summary-rerun-<date>.md` for a drift-triggered re-eval. Reference raw eval artifacts by external location; never paste full transcripts; no PHI/PII in the body. Artifact references must match the run record exactly.

---

## 10. Quality Bar

Before handoff, confirm:

- All Process Doc §19.2 version fields present (or marked `N/A — non-agentic carve-out` with rationale complete).
- Every scenario in the contract is accounted for (passed/failed/skipped/error); pass/fail matches the run record exactly — no adjustment or softening.
- Threshold comparison uses the correct §19.1 risk tier; required vs. actual rate shown; zero-critical-failure check noted for high-risk and safety/privacy/evidence-critical tiers.
- Every failed scenario has a failure-summary entry described by observed behaviour only — no classification terms.
- No full outputs, no PHI/PII inline; all sensitive detail is external references; each failure row carries its artifact reference.
- Cost/latency section complete if the contract set thresholds (Process Doc §20), else "Not tracked" with reason.
- All artifact references match the run record and are locatable.
- Contract/run-record discrepancies listed in the gap table with action required — not silently omitted.
- Summary is complete enough for the closeout package.
- The summary does not classify, accept, recommend merge, or modify results.

See AGENTS.md cross-cutting rules (Authority and human gates; Evidence, privacy, context).

---

## 11. Failure Modes to Avoid

- Including full outputs or sensitive transcripts in the body; reproducing PHI/PII even paraphrased.
- Adjusting or softening run-record pass/fail; classifying a failure (that is `eval-failure-classifier`).
- Silently omitting errored or skipped scenarios; using the wrong risk-tier threshold.
- Producing a summary too brief to support the closeout package; omitting cost/latency when the contract set thresholds.

---

## 13. Handoff to Next Skill

If any failures exist, pass the summary to **`eval-failure-classifier`** (isolated-verification), which classifies each failure against its taxonomy. If no failures and the threshold is met, the orchestrator proceeds to Stage 12 (`current-state-reconciler`). For high-risk tier, the orchestrator also dispatches **`high-risk-human-review-packager`** (conditional per Orchestration Map §5).

Return with: summary status (`complete`/`partial`/`blocked`/`not applicable — non-agentic`); scenario counts (total/passed/failed/skipped-error); threshold result; failure count with brief description (no outputs); artifact reference count; recommended next skill. Do not classify, recommend merge, or accept risk.
