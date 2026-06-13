# Run Your First Slice — Quickstart

A plain-language walkthrough of one slice from start to merge. It is the human's map, not the executable detail — for that, drive from the [Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md) and run each skill's `SKILL.md`. The rules behind each step live in the [Process Doc](./gentech_slice_based_development_process_revised.md).

## What a "slice" is

A slice is one small, shippable unit of agentic capability — one primary outcome you can build, test, evaluate, document, and close out together. If it has two outcomes or needs two unrelated architecture decisions, it's too big; split it (Process Doc §11).

## Before you start (once per project)

Create only the minimum governance documents listed in Process Doc §40 — source-of-truth policy, architecture guidelines, slice-spec template, test/eval strategy, issue template, debt policy, release-authority policy, and (for regulated work) the privacy/residency policy. Don't build more than that until a real slice shows you need it (§5).

## The flow, in plain language

The `slice-orchestrator` drives this; it pauses and asks you at the three **🛑 human gates**. Stages map to the [Orchestration Map stage table](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table).

**Plan it (Stages 0–3).** Reconcile what already exists against what you intend (0), check the candidate slice is small enough (1), write the slice spec — which is *intent, not truth* (2), and have it independently reviewed for readiness (3). If it's not ready, it loops back to step 2.

**Design the evals (Stage 4).** Profile the slice's risk (PHI? residency? a consequential decision?) and write the eval contract — the deterministic tests and live-model scenarios it must pass, with thresholds set by risk tier. Evals are designed *before* coding.

**Build it (Stages 5–9).** Plan the implementation (5), check it against the architecture guidelines (6), write the code and capture configuration in source control (7), write deterministic tests (8), and log any deviation from the spec (9).

> 🛑 **Gate 1 — ADR approval (Stage 6, only if needed).** If the build hits an architecture-guideline gap, the orchestrator stops. You approve (or reject) the architecture decision before coding continues.

**Evaluate it (Stages 10–11).** Run the live-model evals (10), then summarize and classify any failures (11). Blocking failures loop back to the relevant build/design stage.

> 🛑 **Gate 2 — Eval-failure clarification (Stage 11, only if a failure is ambiguous).** If a failure turns on an unclear requirement, the orchestrator stops and asks you to clarify before re-running.

**Reconcile the docs (Stages 12–13).** Update the current-state documentation to match what was actually built (12), then have a different agent independently validate the docs against the evidence (13).

**Close it out (Stages 14–15).** Build the traceability matrix, create safe follow-up issues (or draft them when tooling or publication risk requires it), and assemble the closeout package (14), then independently validate it against the definition of done (15).

> 🛑 **Gate 3 — Closeout & merge (Stage 16, always).** You review the closeout package, residual-risk summary, and issue summary, then approve the merge. Nothing merges without you. This is the one gate that fires on every slice.

**Wrap up (Stages 17–20).** Archive the historical artifacts (17), run the retro and capture lessons (18), update strategic docs and check the manual-config debt ceiling (19), and get a recommendation for the next slice — which **you** choose (20). Then it loops to Stage 0 for the next one.

## The one rule to remember

Agents recommend; **you approve.** Residual risk, architecture decisions, committed-scope changes, destructive issue actions, sensitive issue publication, and merge are always human decisions. Ordinary backlog issues may be created by agents, and they must report the issue refs. The full set of cross-cutting rules is in [`Skills/.agents/AGENTS.md`](./Skills/.agents/AGENTS.md).

## If something breaks in production

The forward flow above is for building slices. Incidents, rollbacks, and hotfixes follow a separate path in [Process Doc §28](./gentech_slice_based_development_process_revised.md#28-rollback-incident-and-hotfix-path), with retroactive documentation once the fire is out.
