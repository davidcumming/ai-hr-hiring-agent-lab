---
name: regression-promotion-recommender
description: Recommends whether a failed or important eval scenario should be promoted into the standing regression suite, and what fix it needs first. Use when classifying eval failures.
---
# Skill: Regression Promotion Recommender

**Used at:** Stage 11 — Eval results & failure classification (Orchestration Map §3 stage table), conditional — fires when a failed or important eval scenario should be considered for the standing regression suite.
**Execution model:** `inline`
**Supports:** Process Doc §22 Handling Eval Failures

---

## 1. Purpose

Recommend whether a specific failed or important eval scenario should be promoted into the standing regression suite, and if so, what rewrite or fix is needed first. This skill protects the regression suite's integrity: scenarios are promoted only when well-defined, with clear expected behaviour and durable value for future slice protection; ambiguous scenarios are held until clarified. This skill recommends — the decision to add a scenario requires human approval and a tracking GitHub Issue (Process Doc §22.2, §27).

---

## 3. Do Not Use This Skill For

- Deciding whether a failure is blocking/non-blocking (`eval-failure-classifier`) or running evals (`live-eval-runner`).
- Writing the final revised scenario files (recommendations only), or deciding which scenarios to retire from the suite (future governance).
- Replacing GitHub Issues as the tracking mechanism — an issue is required for each approved promotion.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Failure classification report | Yes | Specifically the regression-promotion-candidates section. |
| 2 | Eval contract | Yes | Original scenario definitions, rubrics, expected behaviour. |
| 3 | Risk tier | Yes | How strongly a scenario should be protected by regression. |
| 4 | Current regression eval inventory | Yes | To check duplicates and gaps. |
| 5 | Human review notes | If available | Release-authority notes on what the scenario should test. |
| 6 | GitHub Issues | If available | Confirm no duplicate issue; reference related issues. |

---

## 7. Process Steps

### 7.1 Promotion Decision Criteria

Recommend exactly one of `promote`, `promote after fix`, `do not promote`, or `clarify first`.

**Promote** — when all hold: clear unambiguous scenario description; precisely specified expected behaviour in the rubric; tests a behaviour valuable to detect in future slices; not already covered by an existing regression eval (or this strengthens/replaces a weaker one); reusable data/fixtures (synthetic or de-identified, no environment-specific setup that would cause flakiness); rubric is correct (not `EDD`).

**Promote after fix** — the scenario has value but needs correction first: rubric too strict/loose (`EDD`); expected behaviour clarified after an `AMB` classification and the scenario must be rewritten to match; or test data/fixture needs fixing (`FIX`). Provide a specific rewrite suggestion.

**Do not promote** — tests a one-off slice-specific condition that would not generalize; failure was an accepted model limitation that will not be retested; already well-covered by an existing regression eval; or data contains sensitive content that cannot be properly governed in a regression suite.

**Clarify first** — classified `AMB` with expected behaviour still unresolved; promotion would add a scenario that could fail for ambiguous reasons in future slices; or scenario intent is unclear from the eval contract.

### 7.2 Recommendation Steps

1. **Review candidates** — for each, read the original scenario definition, its classification category and rationale, any human-review clarification, and whether it (or a weaker equivalent) already exists in the regression inventory.
2. **Assess against §7.1 criteria** and produce one of the four recommendations.
3. **For "promote after fix," produce a rewrite suggestion** — what is wrong (definition/rubric/data), what the corrected version should be, and whether it needs an `eval-contract-designer` revision or can be done inline.
4. **Flag fix dependencies** — if a promotion needs a code/prompt fix completed first (e.g., a scenario testing an unfixed `IMP`), the scenario must not enter the regression suite until the fix is verified.
5. **Provide GitHub Issue draft inputs** for each recommended promotion (inputs only; `github-issue-drafter` creates issues).
6. **Produce the recommendation report** from the template: per-candidate table, rewrite suggestions, fix dependencies, duplication check, GitHub Issue draft inputs, handoff notes.

---

## 9. Output Format

Use `templates/regression-promotion-recommendation-template.md`. Place at `docs/delivery/slices/<slice-id>/regression-promotion.md`. Work from the classification report and eval contract, not raw transcripts.

---

## 10. Quality Bar

Before handoff, confirm:

- Every candidate from the classification report is addressed; none silently omitted.
- "Promote" recommendations satisfy all §7.1 criteria — not a single factor; the scenario tests durable behaviour, not a one-off slice condition.
- "Promote after fix" candidates have a specific, actionable rewrite addressing the identified defect, stating whether `eval-contract-designer` is needed.
- "Do not promote" rationale is specific (one-off / duplicate / model limitation / data governance); "clarify first" describes the ambiguity and states the clarification question.
- No ambiguous scenario is recommended for promotion without clarification.
- The existing regression inventory was checked for each candidate; the duplication result (duplicate / weaker / no overlap) is recorded.
- Fix dependencies are explicitly flagged; dependent scenarios are not recommended for promotion until the fix is verified.
- GitHub Issue draft inputs are provided for every promote / promote-after-fix recommendation; the skill provides inputs only, never creates issues.
- The report states clearly that human approval is required for all promotions and does not add scenarios to the suite directly.

See AGENTS.md cross-cutting rules (Authority and human gates; Evidence, privacy, context).

---

## 11. Failure Modes to Avoid

- Promoting a scenario with ambiguous expected behaviour, or one testing a one-off slice condition rather than durable behaviour.
- Adding a scenario without a GitHub Issue; promoting a scenario that will be flaky due to unfixed data/environment.
- Skipping the existing-inventory duplication check; promoting before a related `IMP` defect is fixed and verified.

---

## 13. Handoff to Next Skill

- **Approved promotions:** `github-issue-drafter` creates a tracking issue for each.
- **Rewrite-required scenarios:** refer to `eval-contract-designer` for rubric/scenario revision.
- **Promotions pending a fix:** block until the fix is verified (link to the relevant `IMP` fix loop).
- **All recommendations complete:** attach the report to the closeout package; orchestrator proceeds to Stage 12.

Return with: total candidates reviewed; recommend-promote count; promote-after-fix count; do-not-promote count; clarify-first count; any fix dependencies blocking promotion. Do not add scenarios to the suite or create GitHub Issues — provide recommendations and inputs only.
