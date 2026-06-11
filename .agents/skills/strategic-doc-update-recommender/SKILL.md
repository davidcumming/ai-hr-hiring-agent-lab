---
name: strategic-doc-update-recommender
description: Recommends selective, targeted updates to the documentation repo when implementation produces durable planning knowledge it lacks. Use post-merge when lessons warrant doc changes.
---
# Skill: Strategic Doc Update Recommender

**Used at:** Stage 19 — Strategic doc update & debt monitor (Orchestration Map §3 stage table) — conditional
**Execution model:** `inline`
**Supports:** Process Doc §33 Strategic Documentation Repo Reconciliation

---

## 1. Purpose

Recommend selective, targeted updates to the documentation repo when implementation reality has produced durable planning knowledge the repo does not yet contain. The output is a recommendation list, never applied edits — no documentation repo file is modified without human approval (AGENTS.md "Authority and human gates"). The skill protects the documentation repo from both rot (stale planning guidance) and from becoming a current-state mirror (the code repo's current-state docs already track implementation detail).

---

## 2. When to Use This Skill

Fires at Stage 19 only when durable lessons warrant documentation repo changes: `slice-retro-and-lessons` flagged a strategic-doc update, an ADR revealed a strategic constraint, a cross-slice deviation pattern shows a planning assumption is obsolete, a material Microsoft-stack feasibility finding changes future planning, or a major planning cycle is about to begin. If Stage 18 produced no strategic-doc flags, this skill may be skipped (Orchestration Map §5).

---

## 3. Do Not Use This Skill For

- Making the documentation repo a current-state system of record, or adding slice-specific language to it — current-state and historical slice artifacts belong in the code repo / archive.
- Updating current-state docs, architecture guidelines, or ADRs — those are code repo artifacts governed by `current-state-reconciler` and `architecture-guideline-updater`.
- Wholesale rewrites of strategic intent — recommend targeted edits unless a section is factually wrong.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Implementation lessons (Section B), Stage 18 | Required | Source of strategic-doc flags |
| 2 | Process lessons (Section C), Stage 18 | Required | |
| 3 | ADRs approved this slice | If ADRs approved | Closeout package or `docs/adrs/` |
| 4 | Reconciled planning context (Stage 0) | Required | |
| 5 | Closeout package (Stage 14) | Strongly recommended | |
| 6 | Documentation repo file/section references | Required | At minimum, candidate file names/sections |
| 7 | Current-state docs (code repo) | Required | To confirm what is already current-state |
| 8 | Known strategic-doc update backlog | Recommended | Prior retro outputs or doc repo issues |

If Input 6 is missing, ask the user which sections/files to check, or state that recommendations are based on lesson content without a known target file.

---

## 6. Source Authority Rules

Resolve "is this a current-state fact or durable planning insight?" by the strategic update test in Step 2, supported by human judgment. Whether to apply any recommendation is a human decision — this skill never applies updates. Do not mix current-state language into doc-repo recommendations (the two repos serve different purposes; Process Doc §2, §7).

---

## 7. Process Steps

**Step 1 — Orient.** Load implementation and process lessons; identify those flagged `strategic-doc update recommended: Yes`. Load ADRs approved this slice. Confirm doc-repo source references. Load current-state docs to understand what is already recorded as current reality.

**Step 2 — Apply the strategic update test.** For each candidate lesson or ADR, recommend only if it passes all four tests; otherwise log it in the rejection log with the reason:

| Test | Passes if |
|---|---|
| Durable planning knowledge | Reveals a constraint, feasibility limit, strategy shift, or architecture reality affecting planning across multiple future slices |
| Not current-state | Belongs in forward-looking / strategic sections, not a current-state description |
| Not already recorded | The insight is not already present in equivalent form in the doc repo |
| Documentation repo scope | The doc repo has a natural home for this content type (architecture constraints, feasibility, roadmap, etc.) |

**Step 3 — Identify triggers.** Document which Process Doc §33.1 reconciliation triggers apply this cycle (e.g., after a major ADR, recurring deviation pattern, material Microsoft-stack constraint, before major roadmap work, stale-assumption encounters).

**Step 4 — Formulate recommendations.** For each passing update, produce an entry with target file + section, nature of update (add / revise / deprecate / delete), rationale, source lesson/ADR, priority, and draft text only if the user explicitly requested it (otherwise a change description suffices).

**Step 5 — Output.** Write to `docs/delivery/slices/<slice-id>/strategic-doc-update-recommendations.md`. Modify no documentation repo file.

---

## 10. Quality Bar

Before handoff, confirm:

- At least one §33.1 reconciliation trigger is documented as applying (or the output explicitly recommends skipping the stage).
- Each candidate was run through all four strategic-update tests; failures are in the rejection log.
- No recommendation pushes current-state detail, slice-specific language, or code-repo content (architecture guidelines, ADRs, current-state docs) into the documentation repo.
- Every recommendation carries an `SDU-<slice-id>-<seq>` ID, a specific target file and section, a stated nature of update, and a priority.
- Every recommendation is traceable to a specific lesson ID or ADR ID.
- Draft text appears only where the user explicitly requested it.
- Targeted add/revise is preferred; delete or full rewrite carries a strong rationale.
- No documentation repo file was modified; every recommendation is marked "Approval required: Yes".
- A human approval checklist and a rejection log are present.

---

## 9. Output Format

Use `templates/strategic-doc-update-recommendation-template.md`. One entry per update (ID `SDU-<slice-id>-<seq>`, target file/section, nature, rationale, source, priority, draft text only if requested, approval required: Yes), plus a rejection log and a human approval checklist. All recommended text must be slice-agnostic.

---

## 13. Handoff to Next Skill

**Stage 19 continues with `manual-config-debt-monitor`** (always runs at Stage 19). Hand off: path to `strategic-doc-update-recommendations.md`; summary of recommendations awaiting human approval; confirmation that no doc-repo files were modified. State the recommendation count, rejection count by reason category, recommendations by priority (High first), and the applicable triggers. After Stage 19 the orchestrator proceeds to Stage 20 (`next-slice-recommender`) unless `manual-config-debt-monitor` recommends blocking.
