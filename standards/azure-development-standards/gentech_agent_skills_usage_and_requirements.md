# Agent Skill Usage and Requirements Guide

This document is the **skill catalogue** for the slice-based development process for Microsoft-stack agentic solutions. It defines the agent roles and the leaf-skill specifications (purpose, inputs, outputs, boundaries, handoff). It is one of three related documents:

- [Slice-Based Development Process](./gentech_slice_based_development_process_revised.md) — the **rules** (policy, governance, gates).
- **This document** — the **skill catalogue** (one leaf spec per skill).
- [Slice Lifecycle Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md) — the **control flow** (stage table, sequence, orchestrator, subagent model). The authoritative stage-to-skill mapping lives there, not here.

> **Link conventions.** Relative markdown links are canonical (portable across Obsidian, GitHub, and raw-file agent consumers, satisfying the tool-neutral goal in §2). Obsidian wikilink aliases are an optional convenience and must not be relied on for external/agent consumption. All three documents are assumed to live in the same folder. Headings are treated as an API: each skill has a stable `### Skill: <name>` heading; renaming one is a breaking change for inbound links from the Orchestration Map.

## 1. Purpose

This document explains:

- Which agents exist.
- Which skills each agent uses, and what each skill is and is not responsible for.
- What inputs each skill needs and what it produces.
- How each skill is executed (inline, isolated subagent, or independent verification subagent).
- Which development-process sections each skill supports, and where it runs in the lifecycle.
- What files should exist inside each skill package.

A future agent should be able to read all three documents and create any missing skill package in a consistent, focused, reusable `.agents`-style format.

## 2. Core Design Principle

Skills must be small and focused, but split along the boundaries that matter — not along every conceptual sub-task.

Do not create one large "development process" skill. Equally, do not fragment a single coherent task across many micro-skills that share inputs, authority, and context, because that adds handoff cost without protecting context. Split a skill out when it crosses one of these seams:

- **Authority boundary** — recommend vs. approve; planning that must-not-read-code vs. coding; producing a draft vs. verifying someone else's draft.
- **Context-contamination boundary** — current-state vs. historical/intent; aspirational documentation-repo text vs. implemented reality.

Where two steps share inputs, authority level, and run back-to-back, prefer one skill with internal sections (detail pushed to a referenced `rubrics/` file where it is scoring or classification policy) over two skills.

Each skill should clearly define: purpose; when to use / when not to use; required inputs; allowed and disallowed context; output format; quality checklist; failure modes to avoid; execution model; and handoff to the next skill or agent.

## 3. Recommended Generic Skill Package Structure

Each skill is packaged in a generic `.agents` format so it can be used by Codex, Claude, or another agent system.

The active unpacked packages live in this standards repo under `Skills/.agents/skills/<skill-name>/`. When copying skills into a project-specific `.claude/skills/` (Claude Code) or `.agents/skills/` (Codex) location, copy the whole package directory so the template and any rubrics remain available. The repo-root `scripts/install.sh <target-project-dir>` does this syncing idempotently into both scan locations; it is the recommended path over manual copying.

**Frontmatter.** Each `SKILL.md` now begins with a YAML frontmatter block — `---`-delimited `name` (the kebab-case skill name) and `description` (what it does + when to use), with an optional `context: fork` for the recommended-subagent / isolated-verification skills that should run in an isolated context — placed *above* the `# Skill:` H1. This mirrors how the agent role files under `agents/` are already structured (`name` / `description` / `tools` / `model` frontmatter) and lets both Claude Code and Codex auto-discover and trigger the skills rather than requiring an explicit file path every time.

```text
.agents/
  AGENTS.md          # cross-cutting rules every skill obeys
  skills/
    <skill-name>/
      SKILL.md        # authoritative spec; opens with YAML frontmatter (name, description,
                      #   optional context: fork) above the `# Skill:` H1; checklist inlined in §10
      templates/
        <primary-template>.md   # where the skill produces a document
      rubrics/                   # only where the skill encodes scoring/classification policy
        <rubric>.md
  README.md
```

The quality checklist is inlined in `SKILL.md` §10 rather than carried as a separate file, and standalone worked examples were removed (the template is the format spec). See `Skills/.agents/_AUTHORING_SPEC.md` for the authoritative package and `SKILL.md` rules.

## 4. Standard Skill File Requirements

The authoritative `SKILL.md` structure — the slim required core plus the optional sections — is defined in `Skills/.agents/_AUTHORING_SPEC.md`. A `SKILL.md` opens with a YAML frontmatter block (`name`, `description`, optional `context: fork` for recommended-subagent / isolated-verification skills) above the `# Skill:` H1, then carries a header block and the required core (§1 Purpose, §4 Required Inputs, §7 Process Steps, §10 Quality Bar, §13 Handoff); other numbered sections appear only when they hold skill-specific, non-inferable content. Cross-cutting rules are not restated per skill — they live in [`Skills/.agents/AGENTS.md`](./Skills/.agents/AGENTS.md).

Every `SKILL.md` header carries three standardized fields:

- **Used at** — the lifecycle stage(s) in the [Orchestration Map stage table](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) where the skill runs.
- **Execution model** — one word: `inline`, `recommended-subagent`, or `isolated-verification`, as defined in [Orchestration Map §6](./gentech_slice_lifecycle_orchestration_map.md#6-subagent-execution-model). This single field replaces any prose about subagent usage.
- **Supports** — the [Process Doc](./gentech_slice_based_development_process_revised.md) section(s) the skill supports.

## 5. Agent Roles

| Agent Role | Primary Responsibility | Owns stages |
|---|---|---|
| Slice Planning Agent | Converts strategic intent and current-state context into implementation-intent slice specs; recommends next slices. | [Stages 0–3, 20](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Eval Design Agent | Defines and hardens deterministic test expectations and live-model eval contracts before coding. | [Stage 4](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Coding Agent | Implements the approved slice within architecture guidelines and writes deterministic tests. | [Stages 5–9](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Eval Execution and Review Agent | Runs or reviews live-model evals and classifies failures. | [Stages 10–11](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Documentation and Architecture Reconciliation Agent | Updates current-state documentation and actual architecture after implementation. | [Stages 12–13](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Traceability and Closeout Agent | Builds the closeout package, traceability matrix, and definition-of-done evidence; prepares the archive. | [Stages 14–15, 17](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Governance and Process Improvement Agent | Maintains the operating model, lessons, debt monitoring, and selective strategic-doc updates. | [Stages 18–19](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |
| Release Authority (human) | Approves ADRs, residual risk, issue creation, documentation truth, closeout, and merge. | [Stage 16](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table) |

The lifecycle is driven by the `slice-orchestrator` router skill, specified in [Orchestration Map §2](./gentech_slice_lifecycle_orchestration_map.md#2-the-slice-orchestrator-skill).

## 6. End-to-End Skill Usage Map → see the Orchestration Map

The stage-by-stage mapping of process area → agent → skill → gate previously lived here. It is now maintained in one place: the [Orchestration Map stage-indexed table](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table). This avoids the list drifting across documents.

### 6.1 Skill consolidation mapping (old → new)

The old→new mapping from the pre-redesign skills (four merges plus the new `slice-orchestrator`) is maintained in one place: the consolidation note in [`Skills/.agents/AGENTS.md`](./Skills/.agents/AGENTS.md). Verification and approved-ADR-authority skills (`documentation-consistency-validator`, `definition-of-done-validator`, `architecture-guideline-updater`) were deliberately kept separate.

## 7. Skill Index

One line per skill: what it does, its lifecycle stage (Orchestration Map §3), and a link to its authoritative `SKILL.md`. The `SKILL.md` package is the source of truth for purpose, inputs, outputs, and boundaries; this section is only an index. Cross-cutting rules every skill obeys are in [`Skills/.agents/AGENTS.md`](./Skills/.agents/AGENTS.md).

### 7.1 Slice Planning Agent

#### Skill: planning-context-reconciler

**Stage 0.** Reconciles documentation-repo intent against current-state docs, guidelines, ADRs, lessons, and issues into a safe planning context. → [`SKILL.md`](./Skills/.agents/skills/planning-context-reconciler/SKILL.md)

#### Skill: slice-sizer

**Stage 1.** Decides whether a candidate slice is small enough to implement, test, eval, document, and close out as one unit. → [`SKILL.md`](./Skills/.agents/skills/slice-sizer/SKILL.md)

#### Skill: slice-spec-generator

**Stage 2.** Produces a functional, business/process-oriented implementation-intent slice spec. → [`SKILL.md`](./Skills/.agents/skills/slice-spec-generator/SKILL.md)

#### Skill: slice-readiness-reviewer

**Stage 3.** Independently reviews a draft spec and decides whether it is ready for eval design. → [`SKILL.md`](./Skills/.agents/skills/slice-readiness-reviewer/SKILL.md)

#### Skill: next-slice-recommender

**Stage 20.** Recommends candidate next slices from a reconciled view of strategic intent and current reality. → [`SKILL.md`](./Skills/.agents/skills/next-slice-recommender/SKILL.md)

### 7.2 Eval Design Agent

#### Skill: eval-risk-profiler

**Stage 4.** Characterizes a slice's eval risk surface in one pass: risk tier, unsafe failure modes, data governance, cost/latency. → [`SKILL.md`](./Skills/.agents/skills/eval-risk-profiler/SKILL.md)

#### Skill: eval-contract-designer

**Stage 4.** Converts requirements into deterministic test expectations and live-eval scenarios, and selects which regression evals must run. → [`SKILL.md`](./Skills/.agents/skills/eval-contract-designer/SKILL.md)

### 7.3 Coding Agent

#### Skill: implementation-plan-builder

**Stage 5.** Converts the approved spec and hardened eval contract into a coding plan. → [`SKILL.md`](./Skills/.agents/skills/implementation-plan-builder/SKILL.md)

#### Skill: architecture-guideline-checker

**Stage 6.** Checks implementation choices against active technical architecture guidelines. → [`SKILL.md`](./Skills/.agents/skills/architecture-guideline-checker/SKILL.md)

#### Skill: adr-gap-detector

**Stage 6 (conditional).** Detects when a proposed implementation requires a new architecture decision. → [`SKILL.md`](./Skills/.agents/skills/adr-gap-detector/SKILL.md)

#### Skill: source-control-config-capture

**Stage 7.** Ensures Microsoft-stack configuration is represented in source control where feasible. → [`SKILL.md`](./Skills/.agents/skills/source-control-config-capture/SKILL.md)

#### Skill: manual-config-evidence-capture

**Stage 7 (conditional).** Captures evidence for portal/low-code configuration not yet source-controlled. → [`SKILL.md`](./Skills/.agents/skills/manual-config-evidence-capture/SKILL.md)

#### Skill: deterministic-test-author

**Stage 8.** Adds or specifies the required deterministic tests for a slice. → [`SKILL.md`](./Skills/.agents/skills/deterministic-test-author/SKILL.md)

#### Skill: implementation-deviation-capture

**Stage 9 (conditional).** Records deviations from the slice spec during implementation. → [`SKILL.md`](./Skills/.agents/skills/implementation-deviation-capture/SKILL.md)

### 7.4 Eval Execution and Review Agent

#### Skill: live-eval-runner

**Stage 10.** Runs approved live-model evals with controlled version tracking. → [`SKILL.md`](./Skills/.agents/skills/live-eval-runner/SKILL.md)

#### Skill: model-drift-trigger-checker

**Stage 10 (re-eval decision).** Determines whether behaviour-affecting changes require eval re-runs. → [`SKILL.md`](./Skills/.agents/skills/model-drift-trigger-checker/SKILL.md)

#### Skill: eval-result-summarizer

**Stage 11.** Produces concise, repo-safe eval summaries while full artifacts stay external. → [`SKILL.md`](./Skills/.agents/skills/eval-result-summarizer/SKILL.md)

#### Skill: eval-failure-classifier

**Stage 11.** Classifies eval failures and recommends treatment. → [`SKILL.md`](./Skills/.agents/skills/eval-failure-classifier/SKILL.md)

#### Skill: high-risk-human-review-packager

**Stage 11 (conditional).** Packages high-risk eval results for efficient human release-authority review. → [`SKILL.md`](./Skills/.agents/skills/high-risk-human-review-packager/SKILL.md)

#### Skill: regression-promotion-recommender

**Stage 11 (conditional).** Recommends whether a failed or important scenario should join the regression suite. → [`SKILL.md`](./Skills/.agents/skills/regression-promotion-recommender/SKILL.md)

### 7.5 Documentation and Architecture Reconciliation Agent

#### Skill: current-state-reconciler

**Stage 12.** Turns the completed branch into updated current-state reality in one pass. → [`SKILL.md`](./Skills/.agents/skills/current-state-reconciler/SKILL.md)

#### Skill: manual-evidence-normalizer

**Stage 12 (conditional).** Normalizes screenshots, portal notes, and manual-config evidence into structured closeout evidence. → [`SKILL.md`](./Skills/.agents/skills/manual-evidence-normalizer/SKILL.md)

#### Skill: documentation-consistency-validator

**Stage 13.** Independently checks updated documentation against implementation evidence; does not grade its own work. → [`SKILL.md`](./Skills/.agents/skills/documentation-consistency-validator/SKILL.md)

#### Skill: architecture-guideline-updater

**Stage 6 (after approved ADR).** Updates technical architecture guidelines after an approved ADR; carries approved-ADR authority. → [`SKILL.md`](./Skills/.agents/skills/architecture-guideline-updater/SKILL.md)

### 7.6 Traceability and Closeout Agent

#### Skill: traceability-matrix-builder

**Stage 14.** Maps requirements, acceptance criteria, business rules, behaviours, tests, evals, evidence, and issues. → [`SKILL.md`](./Skills/.agents/skills/traceability-matrix-builder/SKILL.md)

#### Skill: github-issue-drafter

**Stage 14.** Drafts GitHub Issues for unresolved work (issue types per Process Doc §27); never creates them. → [`SKILL.md`](./Skills/.agents/skills/github-issue-drafter/SKILL.md)

#### Skill: closeout-package-builder

**Stage 14.** Assembles the full slice closeout package. → [`SKILL.md`](./Skills/.agents/skills/closeout-package-builder/SKILL.md)

#### Skill: definition-of-done-validator

**Stage 15.** Independently validates whether the slice satisfies the definition of done; recommends, never approves merge. → [`SKILL.md`](./Skills/.agents/skills/definition-of-done-validator/SKILL.md)

#### Skill: archive-package-preparer

**Stage 17.** Prepares historical artifacts for archive and identifies durable outputs to keep in main. → [`SKILL.md`](./Skills/.agents/skills/archive-package-preparer/SKILL.md)

### 7.7 Governance and Process Improvement Agent

#### Skill: slice-retro-and-lessons

**Stage 18.** Runs the post-slice retro and curates durable lessons (implementation and process lessons kept distinct). → [`SKILL.md`](./Skills/.agents/skills/slice-retro-and-lessons/SKILL.md)

#### Skill: strategic-doc-update-recommender

**Stage 19 (conditional).** Recommends selective documentation-repo updates when implementation creates durable planning knowledge. → [`SKILL.md`](./Skills/.agents/skills/strategic-doc-update-recommender/SKILL.md)

#### Skill: manual-config-debt-monitor

**Stage 19.** Tracks manual-config/source-control debt and whether the debt ceiling blocks new slices. → [`SKILL.md`](./Skills/.agents/skills/manual-config-debt-monitor/SKILL.md)

### 7.8 Orchestration

#### Skill: slice-orchestrator

**all stages (router).** The thin router that sequences all other skills; full spec in Orchestration Map §2. → [`SKILL.md`](./Skills/.agents/skills/slice-orchestrator/SKILL.md)

## 8. Recommended Skill Creation Order

Build skills in the order the lifecycle needs them — the §7 index is in stage order, so build top-to-bottom. Create `slice-orchestrator` first (it sequences everything else), then the minimum first-slice set in §14, then the remaining skills as their stages come into scope.

## 9. Skill Interaction Sequence → see the Orchestration Map

The end-to-end interaction sequence and the conditional-trigger table previously lived here. They are now maintained in one place: the [Orchestration Map control flow (§4)](./gentech_slice_lifecycle_orchestration_map.md#4-control-flow) and [conditional stages (§5)](./gentech_slice_lifecycle_orchestration_map.md#5-conditional-stages-and-triggers). That diagram shows the branches and loops (split, revision, ADR pause, eval-failure fix loop, human gates) that a linear list cannot capture.

## 10. Rules for Creating a New Skill

When creating a new skill, the agent should:

1. Read the development process document.
2. Read this skill catalogue and the Orchestration Map.
3. Identify the exact skill name and owning agent role.
4. Confirm the skill's scope respects the authority and context-contamination boundaries in §2.
5. Create a `.agents/skills/<skill-name>/` folder.
6. Create `SKILL.md` with the standard headings and the three standardized fields (`Used at`, `Execution model`, `Supports`).
7. Create at least one output template and one quality checklist.
8. Add an example output if useful.
9. Keep the skill tool-neutral and compatible with Codex or Claude.
10. Ensure the skill does not duplicate the scope of an existing skill; if it shares inputs, authority, and sequence with one, fold it in rather than creating a new skill.
11. Include explicit "Do Not Use This Skill For" boundaries.
12. Add the skill to the Orchestration Map stage table and to §8 here so no list drifts.
13. Package the skill as a zip if asked.

## 12. Cross-Cutting Rules All Skills Must Respect

These rules apply to every skill and are maintained in one place: [`Skills/.agents/AGENTS.md`](./Skills/.agents/AGENTS.md). They cover authority and human gates, the source-of-truth hierarchy, evals and architecture, and evidence/privacy/context handling. Skills reference them by name and do not restate them.

## 13. Active Skill Packages

All 33 catalogue skills have active unpacked packages under `Skills/.agents/skills/`. These packages are the executable instruction sets for active work.

Each active package includes:

- `SKILL.md` — the authoritative spec, including an inlined quality checklist in §10.
- a `templates/` file where the skill produces a document.
- `rubrics/` where the skill encodes scoring or classification policy (eval-risk-profiler, eval-contract-designer, eval-failure-classifier, next-slice-recommender).

Standalone `checklists/` and `examples/` files were removed in the conciseness pass: the checklist is now inlined in `SKILL.md` §10, and worked examples were redundant with the templates (two trimmed eval references are retained under `eval-risk-profiler` and `eval-contract-designer` to show the cross-skill chain).

Historical packaged Markdown and zip files under `Skills/_superseded/` are retained only for traceability and must not be used for active work.

## 14. Minimum Skill Set Before First Real Project Slice

Before the first real project slice, the minimum useful skill set is:

```text
slice-orchestrator
planning-context-reconciler
slice-sizer
slice-spec-generator
slice-readiness-reviewer
eval-risk-profiler
eval-contract-designer
github-issue-drafter
implementation-plan-builder
architecture-guideline-checker
adr-gap-detector
deterministic-test-author
eval-result-summarizer
eval-failure-classifier
traceability-matrix-builder
closeout-package-builder
definition-of-done-validator
```

All remaining lifecycle skills are already packaged in this repo and should be copied or referenced when their stages fire. If a project chooses to start with only the minimum set, any omitted skill's responsibility must still be handled manually with the same rules and documented in the closeout package.

## 15. Final Guidance for Future Skill-Creation Agents

When asked to create a specific skill, do not redesign the development process. Implement one focused skill that fits the existing operating model. For each skill, ensure: it has one job; its boundaries are explicit; inputs and outputs are concrete; the template is usable; the checklist is practical; it can be loaded independently; it carries the three standardized fields; it hands off cleanly; and it supports — but does not replace — human release authority. If the requested skill appears too broad, recommend splitting it; if it overlaps an existing skill's inputs, authority, and sequence, recommend folding it in.
