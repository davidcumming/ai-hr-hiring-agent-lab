# Eval Failure Severity Rubric

Use this rubric alongside the failure category taxonomy in `SKILL.md §6` when a failure is near a category boundary. The taxonomy defines the categories; this rubric provides decision guidance for edge cases.

---

## Blocking (`BLOCK`) — Decision Criteria

A failure is `BLOCK` when **any one** of the following is true:

| Criterion | Examples |
|---|---|
| The scenario is listed in the unsafe failure-mode register | As designated by `eval-risk-profiler` |
| Safety is affected | Model provides harmful instructions, unsafe advice, or dangerous recommendations |
| Privacy is violated | PHI/PII is disclosed, shared, or mishandled; Canadian data residency is breached |
| Evidence integrity is compromised | Model makes false authoritative claims, fabricates evidence, or misrepresents its confidence |
| Approval or authorization logic is wrong | Model approves something it should not; fails to apply correct approval rules |
| User trust is materially damaged | Model makes incorrect factual claims to users in authoritative contexts |
| Workflow state is corrupted | Model takes state transitions it should not; leaves state in an incorrect condition |
| Core agent behaviour is wrong | The primary purpose of the agent is not fulfilled |
| Any scenario designated high-risk fails | Regardless of pass rate, a failure in a mandatory high-risk scenario is blocking |

**Do not negotiate with this criterion.** If in doubt between `BLOCK` and `NBC`, apply `BLOCK` and surface it for human review. A human can downgrade; an agent must not.

---

## Non-Blocking Candidate (`NBC`) — Decision Criteria

All of the following must be true for `NBC`:

| Criterion | Guidance |
|---|---|
| The failure is not in the unsafe failure-mode register | Check explicitly; do not assume. |
| The affected scenario is low-risk | No safety, privacy, evidence, approval, state, or core-behaviour impact. |
| The failure is a quality degradation, not a correctness failure | e.g., response is less elegant or slightly less complete, but factually correct and safe. |
| The failure rate is within a range the team can track and manage | A 1-in-8 miss on a minor formatting scenario may be `NBC`; a 3-in-8 miss on core logic is likely `BLOCK`. |
| A GitHub Issue can capture the residual risk and re-test criteria | The deficiency can be tracked and re-tested in a future slice. |
| Human release authority can make a meaningful risk decision | The information is available to support the approval. |

`NBC` is not an approval. It is a classification that routes to a human for approval. Do not present `NBC` as acceptable without that sign-off.

---

## Ambiguous Requirement (`AMB`) — Decision Criteria

Use `AMB` when the failure cannot be cleanly classified because the requirement itself is in dispute:

| Signal | Guidance |
|---|---|
| The expected behaviour in the eval contract is open to multiple interpretations | The rubric says "request clarification" but does not specify when clarification is mandatory vs. optional. |
| Two valid readings of the requirement produce different pass/fail outcomes | The model could be right under one interpretation and wrong under another. |
| The pass/fail rubric is under-specified for the observed case | The rubric handles the happy path but not the observed edge case. |
| The failure rate is mixed in a way that suggests interpretation variance rather than defect | e.g., 4/8 passes with no obvious pattern. |

**Do not resolve `AMB` failures silently.** The slice pauses. The human must clarify the requirement before any agent proceeds. Record the clarification question clearly in the classification report.

---

## Flaky / Nondeterministic (`FLAKY`) — Decision Criteria

Use `FLAKY` only when all of the following apply:

| Criterion | Guidance |
|---|---|
| The failure is inconsistent across runs | The scenario sometimes passes and sometimes fails with no clear pattern. |
| The failure rate is low | Indicative range: 1–2 failures in 8–10 runs. Higher rates should be investigated as `IMP`, `AMB`, or `EDD`. |
| The failure content varies across runs | The failing runs produce different failure behaviours, not the same failure repeatedly. |
| The scenario is not high-risk | A flaky failure in a high-risk scenario should be investigated more aggressively — do not dismiss as merely flaky. |

Even if classified as `FLAKY`, the failure must be documented and approved by human release authority before being accepted. Repeated flakiness across multiple eval runs should be escalated.

---

## Eval-Design Defect (`EDD`) — Decision Criteria

Use `EDD` when the eval design is the problem, not the model behaviour:

| Signal | Guidance |
|---|---|
| The rubric penalizes correct behaviour | The model produced the right outcome but the rubric classified it as wrong. |
| The scenario inputs are unrealistic or contradictory | The test data would never occur in production; the model is responding reasonably to a bad setup. |
| The expected output is over-specified | The rubric requires a specific phrasing, but any clear equivalent phrasing should be acceptable. |
| The scenario tests the wrong behaviour | The scenario was intended to test X but actually tests Y. |

`EDD` does not mean the model passed. It means the test was wrong. The eval contract must be revised and the scenario re-run with the corrected design before the slice can proceed.

---

## Implementation Defect (`IMP`) — Decision Criteria

Use `IMP` when the model behaviour is clearly and consistently wrong according to a well-defined rubric:

| Signal | Guidance |
|---|---|
| The failure is consistent across most or all runs | Not a flaky 1-in-8; a systematic miss. |
| The expected behaviour is unambiguous in the eval contract | No interpretation dispute. |
| The failure can be traced to a specific prompt, tool, workflow, or logic deficiency | The team should be able to identify what needs to change. |
| Fixing the implementation is the clear path forward | Not a model limitation; a fixable code/prompt/tool defect. |

`IMP` routes to the fix loop. After the fix, `live-eval-runner` re-runs the affected scenarios and `eval-failure-classifier` re-classifies.

---

## Model Limitation (`MLM`) — Decision Criteria

Use `MLM` when the failure reflects a genuine capability boundary of the underlying model:

| Signal | Guidance |
|---|---|
| The failure is consistent and systematic | Not flaky; the model always fails this type of task. |
| The failure is not addressable by prompt or tool changes | Prompt engineering and tool adjustments have been reasonably explored; the model simply cannot do this reliably. |
| The limitation is recognized or documentable | It can be described clearly enough for a human to make a scope or model-selection decision. |
| The task may be achievable with a different model | A model upgrade or model comparison is a possible path. |

`MLM` requires human decision: accept the limitation and reduce scope, upgrade the model, run a multi-model comparison, or add it to the known limitations register. The skill recommends; the human decides.

---

## Fixture Defect (`FIX`) — Decision Criteria

Use `FIX` when the environment or test data caused the failure, not the model:

| Signal | Guidance |
|---|---|
| The failure is environment-dependent | Works in one environment, fails in another due to config, mock service, or endpoint differences. |
| The test data is malformed or incomplete | Synthetic scenario inputs were constructed incorrectly; fixing the data resolves the failure. |
| A mock service or stub returned unexpected data | The failure traces to a test infrastructure problem, not model behaviour. |
| Re-running with corrected fixtures produces a pass | The fix is in the test infrastructure. |

`FIX` does not require a code or prompt change. Fix the fixture or environment and re-run. Document what was wrong and what was changed.

---

## Edge Case: `BLOCK` vs. `NBC` under ambiguity

When there is genuine uncertainty about whether a failure reaches the blocking threshold:

1. Check the unsafe failure-mode register. If listed there, it is `BLOCK`.
2. Check Process Doc §22.1 blocking criteria. If any apply, it is `BLOCK`.
3. If still uncertain, default to `BLOCK` and note the uncertainty. A human can downgrade with documented rationale.

**Never default to `NBC` when blocking criteria might apply.**
