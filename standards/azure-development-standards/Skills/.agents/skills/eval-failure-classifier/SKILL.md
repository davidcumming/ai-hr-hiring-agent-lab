---
name: eval-failure-classifier
description: "Independently classifies each eval failure into one canonical category and recommends a treatment path. Use at Stage 11 to route failures to fix, clarification, or acceptance."
context: fork
---

# Skill: Eval Failure Classifier

**Used at:** Stage 11 — Eval results & failure classification (Orchestration Map §3 stage table)
**Execution model:** `isolated-verification`
**Supports:** Process Doc §22 Handling Eval Failures, §27 GitHub Issues

---

## 1. Purpose

Independently classify each eval failure from the eval summary and recommend the appropriate treatment path. Each failure receives exactly one primary category from the canonical taxonomy, which determines what happens next: fix loop, human clarification pause, human approval for non-blocking acceptance, or regression-promotion consideration. This skill recommends and does not approve; it never weakens evals to make failures pass. Human release authority decides whether non-blocking failures are acceptable (Process Doc §22.2).

Run isolated: this skill must execute in an agent context that did not produce the eval summary or run record, so the eval runner cannot rationalize its own failures.

---

## 3. Do Not Use This Skill For

- Approving non-blocking failures or accepting residual risk (human gate, §22.2); recommending merge (human gate, Stage 16).
- Weakening rubrics to reclassify failures as passes; classifying in the same context that produced the summary.
- Drafting GitHub Issues (`github-issue-drafter`); running evals (`live-eval-runner`); deciding regression-suite entry (`regression-promotion-recommender`).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Eval summary | Yes | Completed summary, not the raw run record. |
| 2 | Eval contract | Yes | Scenario intent, expected behaviour, rubric, threshold. |
| 3 | Risk tier | Yes | Applies the correct §22 severity rules. |
| 4 | Unsafe failure-mode register | Yes | A failure matching a known unsafe mode is automatically `BLOCK`. |
| 5 | Raw artifact references | Optional | Consult externally for ambiguous failures; never paste into the output. |
| 6 | Prior failure classifications | If re-run | For comparison and delta analysis. |
| 7 | Human clarification notes | If available | For previously ambiguous failures now clarified. |

---

## 7. Process Steps

### 7.1 Failure Category Taxonomy

Assign each failure exactly one primary category. For detailed decision criteria and edge-case boundaries, use `rubrics/eval-failure-severity-rubric.md` — do not restate it here.

| Category | Code | When to use |
|---|---|---|
| **Blocking** | `BLOCK` | Affects safety, privacy, evidence integrity, approval logic, user trust, workflow state correctness, incorrect authoritative claims, core agent behaviour, or any scenario designated high-risk in the contract or unsafe-mode register. Prevents merge (§22.1). |
| **Non-blocking candidate** | `NBC` | Low-risk scenario, none of the blocking areas, observed behaviour is quality degradation rather than correctness failure, trackable as residual risk with human approval and a GitHub Issue (§22.2). |
| **Ambiguous requirement** | `AMB` | Failure stems from unclear requirement, poorly defined rubric, or under-specified expected output. Slice pauses; no agent resolves silently (§22.3). |
| **Flaky / nondeterministic** | `FLAKY` | Inconsistent across runs (e.g., 1–2 of 8+), low rate, varying failure content — nondeterminism, not a systematic defect. Still needs documentation and human approval if accepted. |
| **Eval-design defect** | `EDD` | Scenario, rubric, or expected-output spec is wrong (tests the wrong thing, too strict/loose, unrealistic data) — not the model. |
| **Implementation defect** | `IMP` | Clear, consistent defect in implementation (wrong logic, missing tool call, bad prompt, broken state); expected behaviour and rubric are correct, model is wrong. |
| **Model limitation** | `MLM` | Consistent, systematic limitation of the underlying model not fixable by prompt/tool changes. Human decides accept/change model/reduce scope. |
| **Fixture defect** | `FIX` | Caused by eval data, synthetic setup, mock service, or environment — not model or implementation. |

Note secondary contributing factors in the classification; the primary category drives the treatment path.

### 7.2 Classification Steps

1. **Review each failure** — read expected behaviour (contract) and observed behaviour (summary); check the unsafe failure-mode register (listed → `BLOCK` regardless of other factors); assess consistency across runs, clarity of expected behaviour, and whether the failure is a correctness error, quality degradation, interpretation disagreement, or environment issue.
2. **Assign one primary category** using the rubric for edge cases. Apply the blocking rule strictly: any unsafe-mode or blocking-area failure is `BLOCK`; do not downgrade to `NBC` without explicit human instruction and documented rationale.
3. **Determine the treatment path:**

| Category | Treatment |
|---|---|
| `BLOCK` | Fix required before proceeding; orchestrator routes to the relevant fix loop (Stage 7 / 4 / 2 by cause). |
| `NBC` | Human release authority approval required; GitHub Issue (via `github-issue-drafter`); re-test criteria defined. |
| `AMB` | Slice pauses; orchestrator surfaces ambiguity to human; no agent proceeds until clarified. |
| `FLAKY` | Document and assess frequency. < 10% and not high-risk may be treated as `NBC` with human approval; > 10% escalate to `BLOCK` or re-investigate as `IMP`/`FIX`. |
| `EDD` | Revise eval contract; route to `eval-contract-designer` before re-running. |
| `IMP` | Implementation fix; route to Stage 7 fix loop. |
| `MLM` | Human decision; surface the limitation. |
| `FIX` | Fix fixture/environment and re-run; no implementation change. |

4. **Flag regression-promotion candidates** for `IMP`, `MLM`, `NBC` (and high-value `EDD` corrections once fixed). Do not decide promotion — that is `regression-promotion-recommender`.
5. **Produce the classification report** from the template: per-failure classification + treatment, aggregate counts, GitHub Issue draft inputs (inputs only) for `BLOCK`/`NBC`/`MLM`, regression candidates, and blockers/pauses.

---

## 9. Output Format

Use `templates/eval-failure-classification-template.md`. Place at `docs/delivery/slices/<slice-id>/failure-classification.md`, or `failure-classification-rerun-<date>.md` for a re-classification. Reference raw artifacts by external location; never reproduce full outputs or PHI/PII in the report.

---

## 10. Quality Bar

Before handoff, confirm:

- This classification was produced by an agent that did not run the evals or write the summary; no eval-run context carried in.
- Every `Fail` scenario from the summary has a row; none omitted.
- Each failure uses exactly one primary category, with rationale tied to that category's criteria in the severity rubric; boundary cases resolved by the rubric, not by defaulting to the less-severe category.
- Blocking rule applied strictly: every unsafe-mode and every blocking-area failure is `BLOCK`; no `BLOCK` downgraded to `NBC` without documented human instruction.
- Non-blocking candidates presented as pending human approval, with re-test criteria and GitHub Issue inputs.
- Each `AMB` failure has a specific clarification question and is not silently resolved; the gate reflects a pause.
- No full outputs, no PHI/PII; external references used instead.
- GitHub Issue draft inputs present for `BLOCK`/`NBC`/`MLM`; the report provides inputs only, never creates issues.
- Regression-promotion candidates flagged, not decided.
- Gate recommendation is one of `Proceed / Fix required / Pause for clarification / Human approval required` and matches the counts (any `BLOCK` = fix required; any `AMB` = pause; any `NBC` otherwise = human approval required; none of the three = proceed); no merge recommendation, no risk acceptance.

See AGENTS.md cross-cutting rules (Authority and human gates; Evidence, privacy, context).

---

## 11. Failure Modes to Avoid

- Downgrading a blocking failure to `NBC` without human instruction and documented rationale; treating an `AMB` failure as resolved.
- Weakening the rubric to reclassify a failure as a pass; classifying without consulting the unsafe failure-mode register.
- Producing GitHub Issues directly instead of draft inputs; treating high-risk flakiness as automatically acceptable.
- Contaminating the run with context from the eval run itself (isolation requirement).

---

## 13. Handoff to Next Skill

- **Blocking:** orchestrator routes to the fix loop (stage by root cause); `live-eval-runner` re-runs; this skill re-classifies.
- **Ambiguous:** orchestrator pauses and surfaces the question; after clarification, `eval-contract-designer` may revise the rubric and `live-eval-runner` re-runs.
- **Non-blocking only:** orchestrator surfaces to human release authority; if approved, `github-issue-drafter` creates issues and `regression-promotion-recommender` (conditional) reviews candidates; then Stage 12.
- **No failures, or all `EDD`/`FIX` with fixes applied:** orchestrator proceeds to Stage 12 (`current-state-reconciler`).
- **Regression candidates:** `regression-promotion-recommender` (conditional, Stage 11). **High-risk tier:** `high-risk-human-review-packager` (conditional, Stage 11).

Return with: blocking count; non-blocking candidate count (pending approval); ambiguous count (pause); other-category counts; overall gate recommendation. Do not approve risk, recommend merge, or weaken evals.
