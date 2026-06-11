# Eval Contract: <Slice ID> — <Slice Name>

This template is self-contained. The main contract is in **## Eval Contract**. Use **## Live-Eval Scenarios** for any scenario complex enough to warrant standalone documentation (multi-turn, structured fixture, adversarial, detailed rubric); reference it from the contract scenario table. Use **## Regression-Eval Selection** when the inventory is large enough that the contract's selection table needs fuller rationale; otherwise the contract's Regression section is sufficient.

---

# Eval Contract

## 1. Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Eval Contract ID | `<EC-<slice-id>-001>` |
| Date Created | `<yyyy-mm-dd>` |
| Created By | `<agent/user>` |
| Source Slice Spec | `<path or reference>` |
| Eval Risk Profile | `<path or reference>` |
| Status | `Draft / Ready for Implementation Planning / Blocked` |
| Risk Tier (from profile) | `Low / Standard / High-Assurance` |
| Live Eval Applicability | `Required / Not Applicable — Non-Agentic Carve-Out` |

## 2. Inputs Reviewed

| Input | Reference | Present? | Notes |
|---|---|---|---|
| Approved slice spec | | Yes/No | |
| Eval risk profile | | Yes/No | |
| Reconciled planning context | | Yes/No | |
| Test/eval strategy | | Yes/No | |
| Regression eval inventory | | Yes/No | |
| Privacy/data-governance guidance | | Yes/No | |
| Architecture guidelines / ADRs | | Yes/No | |
| Known limitations and GitHub Issues | | Yes/No | |
| Model/prompt/tool change information | | Yes/No/N/A | |

## 3. Slice Behaviour Summary

`<Concise, evaluable summary of the behaviour this slice supports — enough to understand what the scenarios below test.>`

## 4. Risk Tier (from Eval Risk Profile)

**Confirmed tier:** `Low / Standard / High-Assurance` — `<one-or-two-sentence rationale from the profile>`

High-risk indicators present (Yes/No/Unknown each): PHI · PII · Canadian residency · auditability · approval/rejection · evidence claims · external sharing/export · memory · permissions/authorization · irreversible state change · authoritative user-facing output · healthcare workflow. List any that apply with notes.

## 5. Behavioural Contract

`<Statement of what the agent must and must not do, in evaluable terms a reviewer can use to score an output pass/fail. Not a user story.>`

## 6. Deterministic Test Expectations

Cover state transitions, validation, persistence, authorization, tool routing, audit events, error handling, configuration.

| ID | Test expectation | Related requirement (FR/BR/AB/AC) | Pass condition (observable) | Notes |
|---|---|---|---|---|
| DT-001 | | | | |

## 7. Live-Model Eval Scenarios

Cover happy path, missing data, ambiguity, out-of-scope, and all unsafe failure modes. If live evals are not applicable, state the non-agentic carve-out (no model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency) instead of adding scenarios.

| ID | Scenario | Input pattern | Expected behaviour | Unacceptable behaviour | Pass criteria | Runs / threshold | Risk |
|---|---|---|---|---|---|---|---|
| LE-001 | | | | | | `<§19.1 tier threshold>` | Low/Standard/High |

## 8. Unsafe Failure Modes (from Risk Profile)

| UFM ID | Description | Blocking? | Covering eval(s) | Gap? |
|---|---|---|---|---|
| UFM-001 | | Yes/No | `<LE IDs>` | Yes/No |

## 9. Pass / Partial / Fail Rubric

Use `rubrics/eval-pass-fail-rubric.md` for generic definitions; customize per slice.

| Result | Slice-specific criteria |
|---|---|
| Pass | All expected behaviours present; no unsafe mode triggered; workflow constraints respected. `<additions>` |
| Partial pass | `<which scenarios allow partial credit and under what conditions — no "mostly ok">` |
| Fail | Expected behaviour absent, unsafe mode triggered, or workflow constraint violated. |
| Blocking fail | `<behaviours always blocking for this slice: safety, privacy, evidence integrity, approval boundary, state corruption, external disclosure>` |

## 10. Repeated-Run Thresholds

| Scenario type | Runs / minimum passing | Applies to (LE IDs) |
|---|---|---|
| Low-risk | 3-5 runs, no critical failures, acceptable qualitative result | |
| Standard | 5-10 runs, ≥80% pass | |
| High-risk | 20+ runs, ≥90% pass, zero critical failures + human review | |
| Safety/privacy/evidence-critical | 20+ runs, zero critical failures, stricter rubric-defined threshold + human review | |
| Adversarial | inherit applicable risk-tier minimum or stricter | |
| Regression | match original threshold or applicable risk-tier minimum | All required regression evals |

## 11. Human Review Requirements

| Scenario(s) | Required? | Review focus | Must pass before merge gate? |
|---|---|---|---|
| `<LE ID(s)>` | Yes/No/Conditional | | Yes/No |

## 12. Eval-Data Constraints (from Risk Profile Section C)

| Data category | Synthetic? | Constraint | Scenarios affected | Governance approval needed? |
|---|---|---|---|---|
| PHI | Yes/No | | `<LE IDs>` | Yes/No |
| PII | Yes/No | | `<LE IDs>` | Yes/No |
| Sensitive business data | Yes/No | | `<LE IDs>` | Yes/No |
| Canadian residency | N/A — infra constraint | Eval infra in approved Canadian regions | All | Confirmed/Required |

PHI-like artifacts must not be committed to the repo. Storage location: `<approved artifact store>`.

## 13. Cost and Latency Expectations (from Risk Profile Section D)

| Metric | Target | Threshold (failure) | Applies to | Ratification |
|---|---|---|---|---|
| End-to-end response time | | | `<scenarios>` | Ratified/Provisional |
| Token budget per interaction | | | `<scenarios>` | Ratified/Provisional |
| Model call count per interaction | | | `<scenarios>` | Ratified/Provisional |
| Tool call count per interaction | | | `<tool>` | Ratified/Provisional |

Cost/latency failure: exceeds threshold on more than `<N>` of `<M>` repeated runs.

## 14. Regression Eval Selection

| Regression eval | Coverage area | Selection trigger | Required? | Exclusion rationale |
|---|---|---|---|---|
| `<eval name / ID>` | | | Yes/No/Optional | `<if not required>` |

New regression candidates (promote after slice closes via `regression-promotion-recommender`):

| Scenario ID | Description | Reason to promote | Priority |
|---|---|---|---|
| LE-NNN | | | High/Medium/Low |

## 15. Traceability Seed

Every FR/BR/AB/AC needs ≥1 entry or a documented no-coverage reason.

| Requirement ID | Summary | Deterministic test(s) | Live eval(s) | UFM(s) | Expected evidence | Coverage gap? |
|---|---|---|---|---|---|---|
| FR-001 | | `<DT IDs>` | `<LE IDs>` | `<UFM IDs>` | | Yes/No |

## 16. Blockers and Open Questions

| ID | Blocker / question | Type | Blocks implementation planning? | Recommended action |
|---|---|---|---|---|
| BQ-001 | | Requirement ambiguity / Privacy / Architecture / Eval design / Cost-latency / Other | Yes/No | |

## 17. Handoff Notes

**Ready for implementation planning?** `Yes / No / Conditionally — list conditions`. **Next skill:** `implementation-plan-builder` (Stage 5), or name the blocker that must clear first.

Key constraints for the Coding Agent: (1) risk tier `<tier>` — implement all tests/evals to this standard; (2) do not implement `<behaviours excluded from this slice>`; (3) eval-data `<synthetic requirements; no real PHI/PII>`; (4) cost/latency `<target thresholds>`; (5) regression evals that must pass `<list>`; (6) unresolved blockers `<BQ IDs + status>`.

---

# Live-Eval Scenarios

One block per scenario needing standalone documentation. Reference from the contract scenario table as `See live-eval-scenarios/<scenario-id>` (or this section).

## Scenario: <LE-NNN> — <Name>

| Field | Value |
|---|---|
| Scenario ID | `<LE-NNN>` |
| Risk Level | `Low / Standard / High` |
| Status | `Draft / Final` |

**Purpose:** `<1-3 sentences: what aspect of the behavioural contract this tests>`

**Related references:** functional requirement `FR-NNN`, business rule `BR-NNN`, agent behaviour `AB-NNN`, unsafe failure mode `UFM-NNN` (list those that apply).

**Input pattern** — for multi-turn, number each turn:

```
Turn 1 (user/system input): <input>
Turn 2 (after expected agent response <describe intermediate state>): <follow-up input>
```

**Expected behaviour** — specific enough to score without subjective judgment:

| Step | Expected agent action |
|---|---|
| 1 | |

**Unacceptable behaviour** — any one is a fail:

| # | Unacceptable action | Why it fails (safety/privacy/workflow/evidence/…) |
|---|---|---|
| 1 | | |

**Scenario-specific rubric:**

| Result | Definition for this scenario |
|---|---|
| Pass | `<specific observable outcome>` |
| Partial pass | `<what qualifies, if allowed>` |
| Fail | `<observable failure outcome(s)>` |
| Blocking fail | `<outcome that blocks merge, if applicable>` |

**Threshold:** `<N>` runs, `<M>` minimum passing. **Human review:** `Yes/No/Conditional` — `<focus>`, must pass before merge gate `Yes/No`.

**Eval fixture / test data:** describe required data; for PHI-like/PII confirm synthetic + source.

| Data element | Value / description | Synthetic? | Notes |
|---|---|---|---|
| | | Yes/No | |

Governance note: `<synthetic plan or governance approval ref>`. Canadian residency note: `<eval infra location or flag>`.

**Cost/latency (if applicable):** response time `<target/threshold>`, token budget, model calls, tool calls.

**Notes for the eval runner:** `<model config, system-prompt version, environment, edge cases to watch>`.

---

# Regression-Eval Selection

Use when the inventory is large enough to need fuller rationale than the contract's Section 14. Reference from Section 14 as `See Regression-Eval Selection`.

## Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Eval Contract ID | `<EC-<slice-id>-001>` |
| Regression inventory version | `<version / date reviewed>` |
| Status | `Draft / Final` |

## 1. Change Summary (drives selection)

| Change type | Present? | Notes |
|---|---|---|
| Model version change | Yes/No | `<model/component>` |
| Prompt template change | Yes/No | `<template(s)>` |
| Tool schema change | Yes/No | `<tool(s)>` |
| Orchestration logic change | Yes/No | `<routing/branching change>` |
| Workflow-state logic change | Yes/No | |
| Permissions / memory / evidence-handling change | Yes/No | |
| New behaviour in an area covered by existing regressions | Yes/No | `<area(s)>` |

Selection rule per eval — does this slice change behaviour it covers, or add closely-related behaviour? `Required` (must run) / `Optional` (related but unlikely affected; recommended) / `Not applicable` (no effect on its area).

## 2. Selection Table

| Eval ID / Name | Coverage area | Selection trigger | Required? | Exclusion rationale | Threshold |
|---|---|---|---|---|---|
| `<REG-NNN>` | | `<triggering change or N/A>` | Required / Optional / Not applicable | `<if Optional/NA>` | `<original or §19.1 tier minimum>` |

## 3. Required Evals (Summary)

| Eval ID / Name | Coverage area | Trigger |
|---|---|---|
| | | |

Total required: `<N>`.

## 4. Skipped Core Evals (require human approval)

| Eval ID / Name | Coverage area | Reason for exclusion | Human approval obtained? |
|---|---|---|---|
| | | | Yes/No/Pending |

## 5. New Regression Candidates

Become regression evals via `regression-promotion-recommender` (Stage 11).

| Slice scenario (LE ID) | Description | Coverage area (future behaviour protected) | Priority |
|---|---|---|---|
| `<LE-NNN>` | | | High/Medium/Low |

## 6. Coverage Gap Analysis

| Behaviour area | Covered by existing regression? | Candidate proposed? | Notes |
|---|---|---|---|
| | Yes/No | Yes/No | |

If gaps exist, note whether acceptable for this slice or whether they should produce a GitHub Issue recommendation.

## 7. Notes for the Eval Runner

`<Ordering constraints (e.g. regressions run after slice-specific evals), environment notes, known conflicts between regressions and new behaviour.>`
