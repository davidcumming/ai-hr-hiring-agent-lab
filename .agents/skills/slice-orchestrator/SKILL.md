---
name: slice-orchestrator
description: Thin router that sequences leaf skills across the slice lifecycle, tracking stage, dispatching work, and pausing at human gates. Use to drive a slice through its stages.
---
# Skill: Slice Orchestrator

**Used at:** All stages — router (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §10 Slice Lifecycle Overview, §36 Automation Posture

---

## 1. Purpose

`slice-orchestrator` is the **thin router** that sequences the leaf skills across the slice lifecycle. It holds only the stage machine, the human gates, and the dispatch logic — no stage detail (that lives in the leaf skills) and no full artifact content (it tracks paths, not bodies). It does three things: **tracks** which stage the slice is in and whether the next stage's entry conditions are met; **dispatches** each stage to the correct leaf skill using that stage's execution model; and **pauses** at every human gate until the human decides. All production work — writing, coding, evaluating, documenting, classifying — belongs to leaf skills, never to the router.

The stage sequence, conditional triggers, execution models, and fix-loop routing are defined once in the Orchestration Map (§3 stage table, §4 control flow, §5 conditionals, §6 execution model). The orchestrator reads them; it does not duplicate them.

---

## 3. Do Not Use This Skill For

- Producing any artifact (spec, code, tests, evals, docs, issues) — load the leaf skill.
- Classifying risk, approving failures, or resolving ambiguity — load the leaf skill or pause for the human.
- Auto-approving or merging at a human gate — surface the decision and stop (see AGENTS.md: recommend, never approve).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Current slice state | Yes | Stage number/name, blockers, pending gates (from the slice state record) |
| 2 | Previous stage output | Yes | Artifact path(s) only, not full content |
| 3 | Gate outcomes | When applicable | Human/ADR approvals, eval-failure clarifications |
| 4 | Conditional triggers | When applicable | Whether Orchestration Map §5 conditions apply |
| 5 | Stage table (Orchestration Map §3) | Yes | Read-only routing source |

---

## 7. Process Steps

1. Read the current slice state and confirm the entry condition for the next stage (per Orchestration Map §3) is met.
2. Check Orchestration Map §5 for any conditional stage that fires given the prior output.
3. Dispatch the stage's leaf skill(s) using that stage's execution model from Orchestration Map §6 (`inline` / `recommended-subagent` / `isolated-verification`). Pass artifact paths, not content.
4. At a human gate (below), **stop** and surface the decision. Never proceed without explicit human confirmation.
5. On a fix-loop return, record the re-entry (which stage, from where, why) in the slice state and route to the re-entry point per Orchestration Map §4. Flag any stage re-entered more than twice as a structural problem for the human.
6. Update the slice state record after every stage.

**Human gates (the orchestrator must stop at each — never auto-approves or merges):**

- **ADR approval** (Stage 6, conditional): when `adr-gap-detector` flags a required ADR. Approved → dispatch `architecture-guideline-updater` → Stage 7; rejected/deferred → surface blocked state.
- **Eval-failure clarification** (Stage 11, conditional): when `eval-failure-classifier` returns "ambiguous requirement." Clarified → re-run Stage 10; accepted as non-blocking → flag residual-risk acceptance for Stage 16 approval.
- **Closeout & merge** (Stage 16, always): present closeout package, residual-risk summary, and issue summary; merge only on explicit human approval.
- **Next-slice selection** (Stage 20): present `next-slice-recommender` output; wait for the human to choose before Stage 0 of the next slice.

Subagents are explicitly wrong at the ADR and closeout/merge gates and the ambiguous-eval-failure loop — the human must see and steer that context (Orchestration Map §6).

---

## 9. Output

The orchestrator maintains a **slice state record** (not a separate document) at `docs/delivery/slices/<slice-id>/slice-state.md`, recording: current stage, completed stages with artifact paths, pending gates and required decisions, conditional stages fired/skipped with rationale, fix-loop history, and the next-stage recommendation with its execution model.

---

## 10. Quality Bar

Before dispatching any stage, confirm:

- The current stage and the next stage's entry condition are known and recorded; the prior artifact exists.
- Required inputs for the stage (Orchestration Map §3) are present as known artifact paths.
- No human gate is pending and unresolved; no fix loop is in an unresolved state.
- The execution model matches Orchestration Map §6 (and Stage 16 dispatches no subagent).
- Every applicable conditional trigger (Map §5) has been checked.
- At Stage 19, `manual-config-debt-monitor` output is loaded; if `block-next-slice`, hold before Stage 20.
- The slice state record is updated with the completed stage, artifact paths, and next-stage execution model.

---

## 13. Handoff

The orchestrator has no single next skill — it drives the whole lifecycle, dispatching the leaf skill listed for each stage in the Orchestration Map. At each stage completion it reports: the stage just completed and its artifact path; whether a human gate is pending (and the exact decision needed) or the next stage to run; any conditional stage triggered; and the next stage's execution model. After Stage 20 and human next-slice selection, it resets to Stage 0.
