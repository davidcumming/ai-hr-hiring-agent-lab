---
name: model-drift-trigger-checker
description: Determines whether behaviour-affecting changes since the last eval run require eval re-runs, and which scenarios. Use at Stage 10 to gate the re-eval decision via versioned-artifact comparisons.
---
# Skill: Model Drift Trigger Checker

**Used at:** Stage 10 — Live eval execution (Orchestration Map §3 stage table), re-eval decision
**Execution model:** `inline`
**Supports:** Process Doc §21 Mandatory Re-Eval Triggers

---

## 1. Purpose

Determine whether behaviour-affecting changes since the last eval run require eval re-runs, and if so, which specific scenarios. This skill gates the re-eval decision and produces a trigger assessment (re-run required / not required / partial) using concrete versioned-artifact comparisons (Process Doc §21.1) to keep the decision less judgment-heavy. It does not run the evals (`live-eval-runner`) or classify failures (`eval-failure-classifier`) — it surfaces the determination and lets the orchestrator dispatch.

---

## 3. Do Not Use This Skill For

- Running evals (`live-eval-runner`) or classifying failures from a completed run (`eval-failure-classifier`).
- Approving a skip of required evals without rationale — if re-eval is required, this skill says so.
- Updating version manifests (team/coding agent), or deciding which new scenarios to write (`eval-contract-designer`).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Previous eval summary | Yes | Must include the version block with all five version values. |
| 2 | Current version manifests | Yes | Model, prompt, tool schema, orchestration, workflow/state — read the manifest files, not commits. |
| 3 | Eval contract | Yes | Maps scenarios to the behaviour areas that changed. |
| 4 | Change summary | Recommended | Commit log, PR description, or coding-agent notes — what changed and why. |
| 5 | Permissions / memory / evidence-handling change notes | If applicable | Has agent permission scope, memory read/write logic, or evidence retrieval/chunking/citation changed? |

If version manifests are unavailable or stale, surface a blocker — do not assume no change occurred. A manifest not updated when a change was deployed is itself a process gap; flag it, do not treat it as "no change."

---

## 7. Process Steps

### Step 1 — Extract previous version values

Read the version block from the most recent eval summary (model name+version, prompt, tool schema, orchestration, workflow/state). If the block is incomplete, the comparison cannot be made — flag a blocker.

### Step 2 — Compare current versions

For each of the five versioned artifacts, record previous vs. current and whether it changed. Also assess from change notes (not manifests): permissions, memory behaviour, evidence handling — `Yes / No / Unknown`.

### Step 3 — Apply the mandatory trigger rules (Process Doc §21)

A change to any of these areas always triggers a re-eval determination — there is no override for "small" changes: model, prompt, tool schema, orchestration, workflow state logic, permissions, memory behaviour, evidence handling, or any other change that may materially affect agent behaviour. For each changed area:

1. Map the change to the eval-contract scenarios that exercise the affected area; mark those for re-run.
2. Global change (e.g., model upgrade) → all scenarios re-run. Scoped change (e.g., one tool's schema) → only scenarios exercising that area.

"Materially affect agent behaviour" is a judgment call only when the change is outside the named areas; document the reasoning explicitly.

### Step 4 — Identify non-triggering changes

For any change not requiring re-eval, document explicitly: what changed, why it is not behaviour-affecting (concrete reasoning, not intent), and which scenarios are unaffected and why. A silent "no re-eval needed" is not acceptable.

### Step 5 — Produce the trigger assessment

Populate the template: version comparison table, trigger determination per change, required re-run scenarios, non-triggering changes with rationale, and any blockers (missing manifests, incomplete prior version block, unknown change scope).

---

## 9. Output Format

Use `templates/re-eval-trigger-assessment-template.md`. Place at `docs/delivery/slices/<slice-id>/re-eval-trigger-<date>.md`. This skill compares versions, not outputs — do not load raw eval artifacts or detailed diffs.

---

## 10. Quality Bar

Before handoff, confirm:

- All five version manifests were read (not inferred); the prior summary's version block was complete or a blocker recorded.
- All eight mandatory trigger areas (model, prompt, tool schema, orchestration, workflow state, permissions, memory, evidence handling) were assessed; none excluded without documented rationale.
- Affected scenarios were derived from the eval-contract scenario-to-behaviour-area mapping, not intuition; the required re-run list comes from the contract.
- Every non-triggering change has explicit concrete rationale, with unaffected scenarios identified.
- Stale/unavailable manifests and any `Unknown` behaviour-area assessments are listed as blockers with a recommended action — not silently resolved.
- The overall result is one of full re-run / partial re-run / no re-run / blocked, and the handoff specifies the next action and which scenarios to re-run if partial.
- The assessment does not skip required re-runs without rationale, and does not run the evals.

See AGENTS.md cross-cutting rules (Authority and human gates; Source of truth).

---

## 11. Failure Modes to Avoid

- Assuming no change because the manifest was not updated (the unstated change is the problem); treating a "small" prompt tweak as non-triggering.
- Scoping down the re-run without reading the eval-contract scenario map; approving a skip of required re-runs without rationale.
- Leaving "Unknown" in all behaviour areas — resolve unknowns before completing; confusing "not behaviour-affecting" with "I don't think this will matter."

---

## 13. Handoff to Next Skill

- **Re-eval required:** orchestrator dispatches `live-eval-runner` with the scenario list from the assessment and current manifests.
- **No re-eval required:** orchestrator proceeds to Stage 11 with the existing eval summary; attach this assessment to the closeout package.
- **Blockers present:** orchestrator pauses and surfaces the blocker before proceeding.

Return with: re-eval required (`Yes — full` / `Yes — partial (n scenarios)` / `No — rationale documented` / `Blocked`); the scenario list if partial; blockers if any; recommended next skill (`live-eval-runner` if required, else proceed to Stage 11). Do not run the evals or approve skipping them without rationale.
