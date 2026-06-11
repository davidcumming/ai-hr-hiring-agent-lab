---
name: slice-retro-and-lessons
description: Runs the post-slice retrospective and promotes durable implementation and process lessons in one pass. Use after slice merge to capture what worked and what did not.
---
# Skill: Slice Retro and Lessons

**Used at:** Stage 18 — Retro & lessons (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §32 Post-Merge Process, §34 Process Retrospectives

---

## 1. Purpose

Run the post-slice retrospective and promote durable lessons in one pass, producing three strictly separate outputs: a process retro (what worked / what did not across the lifecycle), curated implementation lessons (durable technical / Microsoft-stack), and curated process lessons (durable operating-model). The skill recommends; it never applies process changes or edits strategic docs — the human approves. Implementation and process lessons must never be mixed (AGENTS.md cross-cutting rule, "Evidence, privacy, context").

---

## 3. Do Not Use This Skill For

- Updating architecture guidelines or strategic docs, or creating/closing GitHub Issues — those belong to `architecture-guideline-updater`, `strategic-doc-update-recommender`, and `github-issue-drafter`.
- Mixing implementation and process lessons in one section.
- Promoting one-off noise as a durable lesson, or assigning individual blame without an actionable improvement.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Closeout package (Stage 14) | Required | Primary factual record for the slice |
| 2 | Deviation log (Stage 9) | If deviations occurred | |
| 3 | Agent and human reviewer notes | Strongly recommended | Accumulated across the slice |
| 4 | Delays and blockers log | If delays occurred | |
| 5 | Test/eval problems summary (Stage 11) | Required | From `eval-result-summarizer`, `eval-failure-classifier` |
| 6 | Documentation issues log (Stage 13) | If doc issues occurred | |
| 7 | Manual-config debt summary | If debt incurred | |
| 8 | ADRs approved this slice | Required | From closeout package |
| 9 | Existing `docs/lessons/process-lessons.md` | Required | For duplicate detection |
| 10 | Existing `docs/lessons/implementation-lessons.md` | Required | For duplicate detection |

If Inputs 9 or 10 are unavailable, state so and proceed; mark any lesson as potentially duplicating an unknown existing lesson.

---

## 7. Process Steps

**Step 1 — Orient.** Confirm the slice is archived and the closeout package is present. Load available inputs. Note slice ID, name, Stage 17 completion date.

**Step 2 — Process retro (Section A).** Work through the nine retro questions from Process Doc §34 (slice size; spec detail; evals defined early enough; evals too weak/expensive/slow; clean doc reconciliation; manual-config debt growth; right context read; gates added value vs. drag; any template/prompt/checklist/skill change). For each: what worked, what did not, recommended change. If a change rises to a durable process lesson, flag it for Section C — do not write it there yet.

**Step 3 — Implementation lessons (Section B).** Scan deviation log, eval problems, debt summary, ADRs, and agent notes for technical insights. Promote a candidate only if durable (likely to recur) and actionable (changes future planning/coding). Check against `implementation-lessons.md` — no duplicates. Categorize each. Assess whether it implies a strategic-doc update (flag for `strategic-doc-update-recommender`).

**Step 4 — Process lessons (Section C).** From the retro and slice record, identify process failures/successes that should change how the team works. Promote only durable + actionable lessons. Check against `process-lessons.md` — no duplicates. Name the affected skill, template, or checklist.

**Step 5 — Output.** Write to `docs/delivery/slices/<slice-id>/retro-and-lessons.md`. Append passing lessons (append-only, never overwrite) to `docs/lessons/implementation-lessons.md` and `docs/lessons/process-lessons.md` respectively.

---

## 10. Quality Bar

Before handoff, confirm:

- All three sections are present and non-empty (or explicitly noted as having no new content).
- Implementation lessons (Section B) contain only technical / Microsoft-stack content; process lessons (Section C) contain only operating-model content; no cross-contamination either way.
- Section A flags promotable lessons rather than restating them in B or C.
- Every promoted lesson passed the durability test (expected to recur) and the actionability test (changes future behaviour).
- Every lesson cites a source artifact; implementation lessons carry an `IL-<slice-id>-<seq>` ID, process lessons a `PL-<slice-id>-<seq>` ID and a named affected skill/template.
- Duplicate detection was run against both existing lesson files.
- No lesson assigns individual blame without an actionable improvement.
- Recommended process changes are flagged for human approval, not applied.
- All nine §34 retro questions are answered, distinguishing what worked from what did not.
- Strategic-doc-update flags from Section B are recorded with target file/section where Yes.
- Rejected candidates are logged with reasons.

---

## 9. Output Format

Use `templates/retro-and-lessons-template.md` (Process Retro / Implementation Lessons / Process Lessons — kept as distinct sections). Lesson IDs: `IL-<slice-id>-<seq>` and `PL-<slice-id>-<seq>`. Lessons must be slice-agnostic in substance but cite their slice source.

---

## 13. Handoff to Next Skill

**Stage 19 — Strategic doc update & debt monitor.** Hand off: path to `retro-and-lessons.md`; list of implementation/process lessons flagging a strategic-doc update; manual-config debt status from this slice. State slice ID/name, the counts per section, recommended strategic-doc updates, follow-up issues, and any lessons unpromotable due to missing source.

Next skills:
- `strategic-doc-update-recommender` — conditional; run if any lesson warrants a strategic-doc change (Orchestration Map §5).
- `manual-config-debt-monitor` — always runs at Stage 19.
