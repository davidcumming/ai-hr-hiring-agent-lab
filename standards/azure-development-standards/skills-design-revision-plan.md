# Skills Design Revision Plan

> **Status: EXECUTED, retained for maintenance.** The Spine Doc (`gentech_slice_lifecycle_orchestration_map.md`) was created; the Skills Doc was consolidated to 33 skills; the active unpacked packages now live under `Skills/.agents/skills/`; and the Process Doc was cross-linked and de-duplicated. Re-run the validation checks in the completion checklist after future edits rather than relying on an old link-count snapshot.

A detailed, sequenced plan for revising the two GenTech documents based on the design review. The plan covers a recommended document structure, an inter-document linking convention (portable links plus Obsidian aliases), section-by-section edits to each existing document, a new orchestration "spine" document, a subagent execution model, and a consistency/de-duplication pass.

**Documents in scope**

- `gentech_slice_based_development_process_revised.md` — the development process (referred to below as **Process Doc**).
- `gentech_agent_skills_usage_and_requirements.md` — the skill catalogue and usage guide (referred to below as **Skills Doc**).
- `gentech_slice_lifecycle_orchestration_map.md` — **new** spine document proposed in §1 (referred to below as **Spine Doc**).

---

## 0. Review findings this plan operationalizes

The plan addresses four findings from the review:

1. **Stage-to-skill linkage is unclear.** The mapping exists (Skills Doc §6, §9) but lives in flat tables disconnected from the Process Doc lifecycle, and the catalogue is internally inconsistent (skills appear in some lists, not others).
2. **Skill scope is too granular in places.** Several skills share inputs, authority level, and run back-to-back; splitting them adds handoff cost without protecting context.
3. **No orchestration spine.** The 38 skills are all leaves with no controller; the "master skill calls sub-skills" hierarchy is missing and should be realized as a thin router plus subagent dispatch.
4. **No subagent execution model.** Subagent usage should be specified centrally and flagged per-skill with a single field, not repeated as prose in every skill.

---

## 1. Recommended document structure (decision + rationale)

**Recommendation: move to a three-document model, each with one job — mirroring the Skills Doc's own "one skill, one job" principle.**

| Document | Single job | What it stops being |
|---|---|---|
| **Process Doc** | Policy and governance rules: source-of-truth model, sizing, eval thresholds, governance gates, MVG. | Stops trying to also imply sequence/ownership. |
| **Skills Doc** | Skill *catalogue* only: one leaf spec per skill (purpose, inputs, outputs, boundaries, handoff). | Stops carrying the lifecycle map and interaction sequence. |
| **Spine Doc (new)** | The lifecycle controller: stage-indexed table, orchestrator skill spec, conditional routing, subagent conventions. Single source of truth for "what happens at each stage, who acts, which skill loads, which gate must pass." | n/a — new. |

**Why three and not two.** The review's two biggest gaps — stage clarity (finding 1) and the missing spine (finding 3) — are both "where does the sequence and control flow live?" problems. Today that content is smeared across Process Doc §10/§37 and Skills Doc §5/§6/§9, which is exactly why it has drifted out of sync. A dedicated Spine Doc gives that content one home, becomes the natural hub for inter-document links, and lets the other two documents shrink to a single responsibility each. The cost is one more file; the benefit is that de-duplication becomes structural rather than a recurring manual chore.

**Why not keep everything in two docs.** You can, but then the stage-indexed table has to live inside either the Process Doc (bloats the policy reference) or the Skills Doc (re-couples catalogue to sequence). Either choice recreates the drift the review flagged.

**If you reject the third doc:** put the Spine content as a new top section of the Skills Doc (new §0 "Lifecycle Orchestration Map") and delete the scattered duplicates (Skills Doc §6 and §9 collapse into it). The rest of this plan still applies; only the link targets change.

---

## 2. Cross-document linking convention

Per your choice, **relative markdown links are canonical** (portable across Obsidian, GitHub, and raw-file agent consumers, satisfying the Skills Doc's "tool-neutral / Codex-or-Claude" goal). Obsidian wikilink aliases are documented as an optional convenience.

### 2.1 Canonical form (use everywhere)

```markdown
[Stage 4 — Eval Design](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table)
```

- Always relative (`./`), always include the `.md` extension, always deep-link to a heading anchor.
- Anchors follow **GitHub slug rules**: lowercase, spaces → hyphens, punctuation stripped, em-dash `—` becomes a double hyphen `--`. Verify each anchor against the actual heading after editing.

### 2.2 Obsidian alias (optional, document once)

```markdown
[[gentech_slice_lifecycle_orchestration_map#Stage 4 — Eval Design|Stage 4 — Eval Design]]
```

- Obsidian resolves by *heading text*, not slug, so the two styles can coexist if heading text is kept stable.
- Add a short "Link conventions" note to each document header stating: relative links are canonical; wikilinks are an Obsidian convenience; do not rely on wikilinks for external/agent consumption.

### 2.3 Stable-anchor rules (prevents broken links)

- Give every skill a stable heading of the exact form `### Skill: <skill-name>` in the Skills Doc. Links target `#skill-<skill-name>`.
- Give every lifecycle stage a stable heading `## Stage <n> — <Name>` in the Spine Doc.
- Treat headings as an API: renaming a heading is a breaking change that requires updating inbound links. Note this rule in each document header.

### 2.4 Cross-reference map (what links to what)

| From | To | Link purpose |
|---|---|---|
| Process Doc §10 lifecycle (each stage) | Spine Doc matching stage | "How this stage is executed (agent, skill, gate)." |
| Process Doc §37 agent roles | Spine Doc stages that role owns | Role → stage ownership. |
| Process Doc §39/§40 MVG lists | Skills Doc skills in the minimum set | Each named skill links to its leaf spec. |
| Spine Doc stage rows | Skills Doc leaf skill specs | Stage → skill it loads. |
| Spine Doc stage rows | Process Doc policy section | Stage → the rule/gate that governs it. |
| Skills Doc each leaf skill | Spine Doc stage where it runs | Skill → its place in the flow ("Used at"). |
| Skills Doc each leaf skill | Process Doc section(s) it supports | Replaces today's prose "Use in development process" with real links. |

---

## 3. Changes to the Process Doc

Section-by-section. Numbers refer to existing Process Doc sections.

1. **Header (new):** add a "Related documents" block linking the Skills Doc and Spine Doc, plus the §2.2 link-conventions note.
2. **§10 Slice Lifecycle Overview:** keep the diagram, but annotate each lifecycle node with a link to its Spine Doc stage. Add one sentence: "Execution detail (active agent, skill loaded, entry/exit gate) lives in the [Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md)." This is the core fix for finding 1.
3. **§37 Agent Roles:** under each role, add a "Stages owned" line linking to Spine Doc stages. Remove any sentence that restates skill sequence (now owned by the Spine Doc).
4. **§38 Skills and Standard Prompts:** this list is now redundant with the Skills Doc catalogue and partially stale. Replace the enumerated list with a single pointer to the Skills Doc, plus a note that the authoritative sequence is in the Spine Doc. Prevents a third copy of the skill list drifting.
5. **§39 and §40 (MVG lists, currently duplicated):** these two sections overlap heavily. Keep **§40** as the canonical "documents required before first project" list; convert **§39** into a short subsection that links to §40 rather than restating it. Link each named skill in the minimum set to its Skills Doc leaf spec.
6. **§41 Mature Documentation Backlog:** cross-link each backlog item that corresponds to a skill to its Skills Doc spec, so "create later" items are traceable.
7. **Issue-types block (appears in §27 and §40.5):** keep the canonical list in §27; replace the copy in §40.5 with a link to §27. (De-dup — see §6 below.)
8. **§15 Parallel Work:** add a forward link to the Spine Doc's subagent/parallelism conventions (§5 of this plan), since controlled parallelism is where subagent fan-out applies.

---

## 4. Changes to the Skills Doc

### 4.1 Structural edits

1. **Header (new):** "Related documents" block + link-conventions note.
2. **§5 Agent Roles table:** keep, but link each role to the Spine Doc stages it owns.
3. **§6 End-to-End Skill Usage Map:** **move to the Spine Doc.** Replace in place with a one-line pointer. (This table is sequence/control-flow, not catalogue.)
4. **§9 Skill Interaction Sequence + conditional-trigger table:** **move to the Spine Doc.** Replace with a pointer. The Spine Doc renders this as the stage machine.
5. **§7.x leaf specs:** keep as the catalogue, but standardize each (see §4.2).
6. **§8 Recommended Skill Creation Order, §13 Minimum Skill Set:** reconcile against the consolidated skill list (§4.3) so every named skill exists and every existing skill is named. This fixes the internal inconsistency the review flagged.
7. **§12 Existing Skill Packages:** keep; add a note mapping the two built packages onto any consolidated names.

### 4.2 Per-leaf-skill standardization

For every skill in §7.x, enforce a consistent spec by adding two fields and converting prose to links:

- **`Used at` (new):** link to the Spine Doc stage(s) where the skill runs.
- **`Execution model` (new):** one of `inline | recommended-subagent | isolated-verification` (defined in §5). Single line, not prose.
- **`Supports` (replaces the prose "Use in development process"):** real relative links to Process Doc sections.
- Confirm every skill has the first five SKILL.md headings plus "final response requirements" per Skills Doc §4.

### 4.3 Skill consolidation (finding 2)

Merge skills that share inputs, authority level, and run back-to-back. Keep separate any skill that crosses an **authority boundary** (recommend vs. approve; must-not-read-code vs. reads-code) or a **context-contamination boundary** (current-state vs. historical/intent), and keep **verification** skills separate so they can run as isolated subagents.

| Proposed skill | Absorbs | Rationale |
|---|---|---|
| `eval-risk-profiler` | `risk-tier-classifier`, `unsafe-failure-mode-analyzer`, `eval-data-governance-checker`, `cost-latency-eval-designer` | All run on the same slice spec, same recommend-only authority, in immediate sequence. Keep each as an internal section with detail pushed to referenced `rubrics/`. |
| `eval-contract-designer` (expanded) | `regression-eval-selector` | Regression selection is part of producing the eval contract; same inputs and authority. |
| `slice-retro-and-lessons` | `process-retro-facilitator`, `process-lessons-curator`, `implementation-lessons-curator` | Same trigger (closeout package), same authority. Keep process-vs-implementation lessons as distinct output sections so they are not mixed (per Skills Doc cross-cutting rule). |
| `current-state-reconciler` | `branch-diff-analyzer`, `current-state-doc-reconciler`, `actual-architecture-updater` | These chain on one branch diff, same authority, all produce drafts. **Keep `documentation-consistency-validator` separate** — it is verification and must run isolated. |

**Keep separate (do not merge), with reasons:**

- `manual-config-evidence-capture` vs. `manual-evidence-normalizer` — different stages and different agents (coding-time capture vs. reconciliation-time normalization); may share a template.
- Anything touching approval (`definition-of-done-validator`, release-authority flows) stays standalone.
- `slice-readiness-reviewer` and `implementation-deviation-capture` — currently missing from §6/§8; **add them to every list**, do not drop.
- Planning skills that must-not-read-code stay separate from coding skills.

Net effect: ~38 → ~30 skills, with the reduction concentrated in the eval-design and governance clusters where the review found over-fragmentation. Provide an explicit old→new mapping table in the Skills Doc so the two already-built packages and any references remain traceable.

---

## 5. New Spine Doc specification

Create `gentech_slice_lifecycle_orchestration_map.md`. Proposed outline:

1. **Purpose & how to read this document** — the single source of truth for stage → agent → skill → gate; the other two docs link here.
2. **The `slice-orchestrator` skill spec** — a *thin router* SKILL.md (this is the "master skill" you asked about). It contains only: the stage list, entry/exit gates, conditional branches, and "given current state, load skill X / dispatch subagent Y next." It carries **no** stage detail. Explicitly state it pauses at human-approval gates (Process Doc §31/§36) rather than auto-running the pipeline.
3. **Stage-indexed table (the spine)** — one row per stage with columns: `Stage` · `Entry condition` · `Agent role` · `Skill(s) loaded` · `Required inputs (must already exist)` · `Output / gate` · `Exit handoff` · `Execution model`. Each cell links to the relevant Skills Doc spec or Process Doc rule. This replaces Skills Doc §6.
4. **Control-flow diagram** — the §9 sequence, but showing branches and loops (e.g., ambiguous eval failure → human clarification → re-run), not just a straight line. This replaces Skills Doc §9.
5. **Conditional-trigger table** — migrated from Skills Doc §9, with links.
6. **Subagent execution conventions** — the shared model (see §6 below), referenced by every leaf skill's `Execution model` field instead of being repeated.

---

## 6. Subagent execution model (finding 4)

Define once, in the Spine Doc §5.6; reference from each skill via the one-line `Execution model` field. Do **not** repeat subagent prose in 30 SKILL.md files.

Three values:

- **`inline`** — run in the current context. Default for lightweight, low-context skills and anything in an interactive human loop.
- **`recommended-subagent`** — dispatch to an isolated subagent when the stage is heavy-context or parallelizable, so its working context is discarded on return. Apply to: `current-state-reconciler` (large diffs), live-eval execution, branch-diff fan-out, and the controlled-parallelism slices (Process Doc §15).
- **`isolated-verification`** — must run as an independent subagent that did not produce the artifact it checks. Apply to: `documentation-consistency-validator`, `definition-of-done-validator`, and a sanity pass on `eval-failure-classifier`.

**Where subagents are explicitly wrong** (state this in the conventions): human-approval gates and the ambiguous-eval-failure clarification loop, where the human must see and steer the context.

---

## 7. Consistency & de-duplication register

Concrete fixes to make during the edit pass:

- **Triplicated issue-types list** (Process Doc §27, §40.5; Skills Doc §7.6.4) → one canonical copy in Process Doc §27; the other two link to it.
- **Duplicated MVG lists** (Process Doc §39 vs §40) → §40 canonical; §39 links to it.
- **Skills missing from maps** — `slice-readiness-reviewer`, `implementation-deviation-capture` absent from Skills Doc §6/§8; add everywhere or the catalogue can't be enumerated from any single list.
- **Skill-list drift** across Skills Doc §6, §8, §13 and Process Doc §38 → after consolidation, regenerate all four from the Spine Doc stage table so they cannot diverge again.
- **Anchor audit** — after all edits, verify every relative link resolves to a real heading slug (a quick scripted check over the three files).

---

## 8. Sequenced implementation plan

Do the edits in this order to avoid editing content you're about to move:

1. **Create the Spine Doc shell** (§5 outline, headings only) so link targets exist.
2. **Consolidate skills** in the Skills Doc (§4.3) — names must stabilize before anything links to them.
3. **Migrate** Skills Doc §6 and §9 into the Spine Doc stage table and control-flow diagram (§4.1, §5).
4. **Standardize leaf specs** — add `Used at` / `Execution model` / linked `Supports` (§4.2).
5. **Write the `slice-orchestrator` spec and subagent conventions** in the Spine Doc (§5.2, §6).
6. **Edit the Process Doc** — annotate §10, §37; de-dup §38/§39/§40/§27 (§3).
7. **Add headers and link-convention notes** to all three docs (§2.2).
8. **Run the de-dup register and anchor audit** (§7).
9. **Final verification** — confirm every stage has exactly one owning role and one gate; every skill appears in the stage table, the creation order, and (if applicable) the minimum set; every cross-link resolves.

### Completion checklist

- [x] Spine Doc exists and is the only home for the stage table and sequence.
- [x] Process Doc §10 links each lifecycle node to a Spine stage.
- [x] Every leaf skill has `Used at` + `Execution model` + linked `Supports`.
- [x] Skill consolidation done; old→new mapping table present.
- [x] Issue-types and MVG lists each exist once, others link.
- [x] Subagent conventions defined once; referenced, not repeated.
- [ ] After each maintenance edit, re-run link resolution, active-skill inventory, orchestration coverage, skill-heading, and obsolete-threshold checks.
- [ ] All relative anchors verified; Obsidian alias note present.

---

## Appendix A — Proposed consolidated skill list (old → new)

| New / retained skill | Replaces |
|---|---|
| `planning-context-reconciler` | (unchanged) |
| `slice-sizer` | (unchanged) |
| `slice-spec-generator` | (unchanged) |
| `slice-readiness-reviewer` | (unchanged — ensure it's in all lists) |
| `eval-risk-profiler` | risk-tier-classifier + unsafe-failure-mode-analyzer + eval-data-governance-checker + cost-latency-eval-designer |
| `eval-contract-designer` | eval-contract-designer + regression-eval-selector |
| `implementation-plan-builder` | (unchanged) |
| `architecture-guideline-checker` | (unchanged) |
| `adr-gap-detector` | (unchanged) |
| `source-control-config-capture` | (unchanged) |
| `manual-config-evidence-capture` | (unchanged) |
| `deterministic-test-author` | (unchanged) |
| `implementation-deviation-capture` | (unchanged — ensure it's in all lists) |
| `live-eval-runner` | (unchanged) |
| `eval-result-summarizer` | (unchanged) |
| `eval-failure-classifier` | (unchanged) |
| `high-risk-human-review-packager` | (unchanged) |
| `model-drift-trigger-checker` | (unchanged) |
| `regression-promotion-recommender` | (unchanged) |
| `current-state-reconciler` | branch-diff-analyzer + current-state-doc-reconciler + actual-architecture-updater |
| `architecture-guideline-updater` | (unchanged — kept separate; touches approved-ADR authority) |
| `manual-evidence-normalizer` | (unchanged) |
| `documentation-consistency-validator` | (unchanged — isolated-verification) |
| `traceability-matrix-builder` | (unchanged) |
| `closeout-package-builder` | (unchanged) |
| `definition-of-done-validator` | (unchanged — isolated-verification) |
| `github-issue-drafter` | (unchanged) |
| `archive-package-preparer` | (unchanged) |
| `slice-retro-and-lessons` | process-retro-facilitator + process-lessons-curator + implementation-lessons-curator |
| `strategic-doc-update-recommender` | (unchanged) |
| `manual-config-debt-monitor` | (unchanged) |
| `next-slice-recommender` | (unchanged) |
| `slice-orchestrator` | **new** — thin router / master skill |

Roughly 38 → 33 (including the new orchestrator), with merges concentrated where the review found over-fragmentation and verification/authority boundaries preserved. **Final inventory: 33 skills** — this is the canonical count (see `Skills/.agents/AGENTS.md` and Skills Doc §13). Any other figures earlier in this historical plan describe interim estimates, not the delivered set.
