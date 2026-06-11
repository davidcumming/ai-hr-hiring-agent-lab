---
name: traceability-matrix-builder
description: Builds a matrix mapping every requirement, acceptance criterion, and agent behavior in a slice spec to its implementation evidence. Use at closeout to prove what was built and proven.
---
# Skill: Traceability Matrix Builder

**Used at:** Stage 14 — Traceability & closeout (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §24 Traceability, §29 Slice Closeout Package

---

## 1. Purpose

Build a structured matrix mapping every requirement, acceptance criterion, business rule, and agent behavior in the slice spec to its implementation evidence (tests, evals, manual evidence), and flag every unresolved item with a GitHub Issue reference. The matrix answers: what was implemented, how it was proven, what eval proves correct agent behavior, what remains unresolved or untestable, and who accepted any residual risk. It is a component of the closeout package and is independently re-checked by `definition-of-done-validator` at Stage 15. It identifies issue candidates but never creates issues — those go to `github-issue-drafter` and need human approval.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Slice spec (final, post-deviation) | Yes | Trace to implemented intent, not the original draft, where deviations were captured |
| 2 | Eval contract (hardened) | Yes | Maps evals to acceptance criteria |
| 3 | Deterministic test summary | Yes | Coverage map linking tests to spec items |
| 4 | Live eval summary | Yes | Pass/fail, artifact references, version metadata |
| 5 | Manual evidence summary | Conditional | Required when portal/low-code config was captured |
| 6 | Implementation summary / deviation log | Yes | What was actually built |
| 7 | Open GitHub Issues | Yes | Check before creating new candidates; reference by number, never invent numbers |
| 8 | Documentation validation report | Yes | Non-blocking gaps may become traceability notes |

---

## 6. Source Authority Rules

| Question | Use this source |
|---|---|
| Is a requirement implemented? | Code/config/IaC evidence + test/eval pass |
| Is agent behavior verified? | Live eval summary (deterministic tests alone are insufficient) |
| What is unresolved? | Open GitHub Issues + gaps with no evidence |
| Was a deviation accepted? | Deviation log + human approval record |
| Is a behavior untestable / deferred? | Deviation log or explicit agent note; never silently omit |

---

## 7. Process Steps

### Step 1 — Extract traceable items
Read the spec (adjusted for accepted deviations) and extract, numbering sequentially per category (reuse existing spec IDs if present): functional requirements (FR-N), business rules (BR-N), agent behavior requirements (AB-N), acceptance criteria (AC-N), high-risk behaviors (HRB-N — items that triggered high-assurance risk tier or human eval review).

### Step 2 — Map each item to evidence
Record evidence by type: deterministic test (name/file/ID), live eval scenario (scenario ID + pass/fail), manual evidence (evidence ID), or combination. Mark coverage status:

- **Covered** — at least one passing test or eval maps to the item.
- **Partial** — some scenarios pass, some are non-blocking failures (record issue ref).
- **Untested** — no test or eval covers the item.
- **Deferred** — explicitly deferred by accepted deviation or scope reduction (record reason + issue ref).
- **Untestable** — cannot be automatically tested by design (record rationale; must have a human review note).

### Step 3 — Identify coverage gaps
List every Untested, Partial, or Untestable item with its ID, text, why it lacks coverage, and whether an issue is needed (Step 5).

### Step 4 — Resolve unresolved items
For items already linked to open GitHub Issues, record the issue reference. Issue references in the matrix are for unresolved, deferred, failed, or open items only (Process Doc §24) — do not attach references to fully completed, passing items.

### Step 5 — Identify issue candidates
For each gap or unresolved item not already tracked, decide whether it warrants a new draft. Pass the candidate list to `github-issue-drafter`. Candidates include: requirements with no coverage (test-gap), accepted non-blocking eval failures not yet tracked (eval-failure), accepted deviations with no existing issue (technical-debt / source-control-debt), untestable items with no human-review record.

### Step 6 — Build the matrix output
Produce three sections per `templates/traceability-matrix-template.md`: full coverage table; coverage summary (counts by status and risk tier; coverage percentage is informational, not a gate); gap and issue-candidate list formatted for `github-issue-drafter`.

---

## 10. Quality Bar

Before handoff, confirm:

- [ ] Every functional requirement, business rule, acceptance criterion, agent behavior, and high-risk behavior from the spec appears in the matrix — none silently omitted.
- [ ] Every Untested, Partial, Deferred, or Untestable item appears in the gap section with a blocking/non-blocking assessment.
- [ ] Each Covered item cites a specific evidence reference (test name/ID, eval scenario ID, evidence ID), not "tests pass".
- [ ] Agent behavior items have at least one live eval scenario reference, not only deterministic tests.
- [ ] High-risk behaviors have a human review record or an explicit note that none was produced.
- [ ] Where a deviation was accepted, the matrix traces to implemented behavior, not the original spec text.
- [ ] GitHub Issue references appear only for unresolved items; every referenced issue was verified open; no numbers invented.
- [ ] The matrix does not assert that untested requirements are complete.
- [ ] The issue candidate list is present (even if empty) and does not duplicate existing open issues.
- [ ] No aspirational documentation-repo text is cited as implementation evidence.
- [ ] Any unavailable or incomplete input is noted as a caveat; affected items are marked Untested with that caveat as the reason.
- [ ] The matrix neither approves closeout nor waives gaps (per AGENTS.md recommend-never-approve rule).

---

## 11. Failure Modes to Avoid

| Failure mode | Why it matters |
|---|---|
| Silently omitting untested requirements | Creates a false completeness picture and blocks audit |
| Tracing to original spec when an accepted deviation changed behavior | Maps to the wrong intent |
| Accepting "code passes tests" for agent behavior items | Live evals are required for agentic behavior |
| Propagating stale issue numbers from prior slices without verifying they are open | Misleads the Release Authority at Stage 16 |
| Presenting coverage percentage as the sole gate | The percentage is informational; every blocking gap must be listed |

---

## 13. Handoff to Next Skill

Pass the full matrix and the issue-candidate list to `github-issue-drafter`, and the full matrix to `closeout-package-builder` as a required input (both Stage 14). The `definition-of-done-validator` (Stage 15) re-checks the matrix independently — do not pre-empt that check. The skill response must include the complete matrix, coverage summary, an explicit gap list (state "No coverage gaps identified" if empty), an issue-candidate list (state "No new issue candidates" if empty), any input caveats, and a clear statement of whether the matrix is ready for `closeout-package-builder` or blocked. If a gap requires returning to an earlier stage (e.g., a missing eval scenario), name that stage so the `slice-orchestrator` routes correctly. Obeys the recommend-never-approve and source-of-truth rules in AGENTS.md.
