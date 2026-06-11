---
name: next-slice-recommender
description: Recommends a ranked list of candidate next slices at the end of a completed slice cycle. Use after archive, retro, and lessons to plan what to build next.
---
# Skill: Next Slice Recommender

**Used at:** Stage 20 — Next-slice recommendation (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §32 Post-Merge Process, §35 Next-Slice Recommendation

---

## 1. Purpose

Recommend candidate next slices at the end of a completed slice cycle (after archive, retro, and lessons), synthesizing the reconciled planning context, current-state docs, implementation and process lessons, ADRs, GitHub Issues, known limitations, test/eval status, manual-config debt status, and any user-provided priorities. The output is a ranked candidate list with rationale, dependencies, and risks. The human always chooses the next slice — this skill recommends and never decides, and always returns a ranked list rather than a single answer.

---

## 3. Do Not Use This Skill For

- Creating the slice spec (`slice-spec-generator`, Stage 2) or starting implementation.
- Overriding human priority decisions, or treating the recommendation as approval.
- Recommending a candidate blocked by an unresolved Issue, outstanding ADR, or manual-config debt above the ceiling.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Reconciled planning context (most recent) | Required | Strategic intent vs. current reality |
| 2 | Current-state documentation | Required | Updated after last slice merge |
| 3 | Implementation lessons | Required | Durable technical lessons from prior slices |
| 4 | Process lessons | Recommended | Durable process lessons that affect sequencing |
| 5 | Approved ADRs and active architecture guidelines | Required | Architecture readiness of candidates |
| 6 | GitHub Issues (open) | Required | Blockers, debt, and unresolved work |
| 7 | Known limitations | Required | Hard planning boundaries |
| 8 | Test/eval status summaries | Recommended | Verified behaviour baseline for assessing gaps |
| 9 | Manual-config/source-control debt status | Recommended | May block new slice planning |
| 10 | Strategic doc update status | Optional | Whether strategic docs were updated in Stage 19 |
| 11 | Product priorities or delivery themes from the user | Optional | Weights the assessment |

If product priorities are not provided, weigh all sequencing dimensions equally.

---

## 7. Process Steps

1. **Check for debt-ceiling blockers first.** If the manual-config debt report shows the ceiling exceeded, recommend no new slice until ceiling burn-down is flagged as the first required action.
2. **Identify candidate areas** from the reconciled planning context and current-state docs, including candidates carried forward plus new gaps revealed by the closed slice.
3. **Filter blocked candidates.** Remove any blocked by an unresolved Issue, outstanding ADR decision, unresolved privacy/governance concern, or known limitation. Flag these separately.
4. **Assess each unblocked candidate** against the balanced sequencing dimensions (§7.1), recording a brief rationale per dimension.
5. **Assess architecture readiness** — whether a new ADR is needed before spec generation; flag uncertainty.
6. **Assess eval readiness** — whether behaviour can be defined and evaluated; flag candidates where eval design is expected to be hard.
7. **Identify dependencies between candidates.** Note explicit dependency relationships; do not recommend an out-of-order candidate as the top choice when a dependency is unresolved.
8. **Rank candidates** by overall sequencing strength, adjusted for hard dependencies (an unmet dependency moves a candidate down regardless of strength), manual-config debt risk, and lessons that suggest earlier/later sequencing.
9. **State whether each candidate is ready for `slice-spec-generator`** — ready means no blocking issues, clear architecture, plausible eval design, and no debt-ceiling blocker.
10. **Recommend a default next action** (top candidate and why), making clear it is a recommendation and the human chooses.

### 7.1 Balanced Sequencing Dimensions

Assess each candidate against all ten dimensions (full prompts and the two hard rules in `rubrics/balanced-sequencing-score-rubric.md`):

| Dimension | Question |
|---|---|
| Business value | Does this advance a primary business/process outcome? |
| Dependency order | Does it depend on unresolved prior work, or enable future work? |
| Testability | How well-defined are acceptance criteria and deterministic test coverage? |
| Eval readiness | How ready is the behaviour definition for live-model eval design? |
| Technical risk | How much new architecture, unknown patterns, or external dependencies does it introduce? |
| Demo/stakeholder value | Useful to demonstrate to stakeholders now? (lower weight if not relevant) |
| Unresolved issue impact | Do open GitHub Issues block, constrain, or strongly suggest this area? |
| Architecture readiness | Are required guidelines and ADRs in place? |
| Manual-config/source-control risk | Would this push manual-config debt beyond the ceiling? |
| Implementation complexity | Relative effort given lessons learned and available patterns? |

A candidate that is "blocked" on **dependency order** or **testability/eval readiness** (no resolvable path) is a blocked candidate and must not be ranked first. If the user provides product priorities, weight Business value, Demo/stakeholder value, and any explicitly prioritized dimension more heavily.

---

## 9. Output Format

Use `templates/next-slice-recommendation-template.md`. Always a ranked list with per-candidate rationale; never a single answer and never a slice spec.

---

## 10. Quality Bar

Before handoff, confirm:

- The debt-ceiling check was performed first; if exceeded, no new slice is recommended until burn-down is addressed.
- All blocked candidates are identified and separated, with explicit blocking reasons.
- All unblocked candidates are assessed on all ten dimensions, each with a rationale.
- A candidate blocked on dependency order or testability/eval readiness is not ranked first.
- The dependency map is complete; no candidate with an unresolved dependency is ranked first.
- Architecture readiness and eval readiness are assessed for each candidate; ADR needs flagged.
- Each candidate states whether it is ready for `slice-spec-generator`.
- A ranked list is present and the default recommendation is justified.
- The recommendation informs but does not override human priority; no slice spec was created and no implementation started.
- Implementation lessons and process lessons are kept in distinct sections (AGENTS.md cross-cutting rule).

---

## 11. Failure Modes to Avoid

- Recommending a blocked candidate as the top choice, or ignoring the debt ceiling.
- Picking one candidate without a ranked list (human cannot make an informed choice).
- Assessing without rationale (human cannot validate or override).
- Ignoring dependency order (downstream slice blocked because the foundation was skipped).

---

## 13. Handoff to Next Skill

| Condition | Recommended Next Action |
|---|---|
| Human selects a candidate | Stage 0 — `planning-context-reconciler` (new planning cycle begins) |
| Debt ceiling exceeded | `manual-config-debt-monitor` to assess burn-down before any new slice |
| Top candidate requires an ADR | `adr-gap-detector` before `planning-context-reconciler` |
| Strategic docs need updating first | `strategic-doc-update-recommender` (if not already run in Stage 19) |
| Human selects a blocked candidate | Resolve the blocker first, then Stage 0 |

Do not create a slice spec, start implementation, or make the choice for the human.
