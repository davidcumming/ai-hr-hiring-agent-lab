# Generic Agent Skills — GenTech Slice-Based Process

Small, focused, reusable agent skills under `.agents/skills/`. Agents load only the skill needed for the current task. The authoritative catalogue (purpose, inputs, outputs, boundaries) is `gentech_agent_skills_usage_and_requirements.md` at the repository root; the stage-by-stage usage order is in `gentech_slice_lifecycle_orchestration_map.md`; the active executable instructions live in each skill's `SKILL.md`.

## Cross-cutting rules (canonical home — every skill obeys these; none should restate them)

This file is the single home for the rules that apply to all skills. A `SKILL.md` references these by name (e.g. "obeys the recommend-never-approve rule in AGENTS.md") and states only its own *exceptions* or the one boundary most load-bearing for that skill. Do not copy this list into individual skills.

**Authority and human gates**

- Skills recommend; they never approve. Human approval is required for residual risk, ADR approval, non-blocking eval failures, GitHub Issue creation, and merge readiness.
- Skills must not silently resolve ambiguity that belongs to a human. Produce clear blockers, not vague warnings.
- Skills must not overreach into an adjacent skill's responsibility. Use a skill only within its stated scope.

**Source of truth**

- Slice specs are implementation *intent*, not truth. Current-state docs describe what exists now and stay slice-agnostic. Historical slice artifacts are not authoritative after merge.
- Code/config/IaC plus approved manual evidence are implementation truth. GitHub Issues are the source of truth for unresolved work.
- For any question, resolve it against this hierarchy: *what exists now* → current-state docs; *what is intended* → documentation repo; *what rule applies* → architecture guidelines + approved ADRs; *what is unresolved* → GitHub Issues.

**Evals and architecture**

- Deterministic tests are necessary but insufficient; live-model evals are required for agentic behaviour. Deterministic-only completion is allowed only when the risk profile and eval contract explicitly document the non-agentic carve-out.
- Architecture-guideline gaps require ADR review before implementation proceeds. Do not add a new pattern without an approved ADR.
- Treat Process Doc §19.1 as the canonical eval-threshold policy.

**Evidence, privacy, context**

- Manual configuration evidence supports merge only with tracking and follow-up when source control is feasible.
- Privacy, data residency (including Canadian requirements), and auditability are first-class concerns.
- Default context is durable documentation, not noisy historical artifacts. Not loaded by default: raw application code, old slice specs, historical branch notes, agent transcripts, archived screenshots, detailed implementation logs, full eval-output transcripts. A skill that genuinely needs one of these names it in its own Required Inputs.
- Keep skills tool-neutral (usable by Codex or Claude) and Microsoft-stack aware (Copilot, Azure AI Foundry, Power Platform, Azure services).
- Implementation lessons and process lessons must be kept distinct, even when produced by the same skill.

## Scan locations and install

- This `Skills/.agents/skills/` path is the **canonical source**. The tools do not scan it directly: Codex scans `.agents/skills/` at a project root, and Claude Code scans `.claude/skills/` (and `.claude/agents/` for role files).
- To make these skills discoverable in a consuming project, run the repo-root `scripts/install.sh <target-project-dir>`, which symlinks (or `--copy` syncs) the canonical packages into those scan locations. It is idempotent.
- A proposal to un-hide this hidden source folder (`Skills/.agents/skills/` → `skills/`) is recorded as ADR-0005 under `../../Initial_Documentation/adr/`.

## Operating rules

- Skills are task-specific. The authoritative spec for a skill is its `SKILL.md` package — not the Skills Doc catalogue, which is an index. When in doubt about a skill's scope, the `SKILL.md` wins.
- Each skill's `Execution model` (inline / recommended-subagent / isolated-verification) is defined once in Orchestration Map §6 and named (not re-justified) in its `SKILL.md`.

## Skills by owning agent role

| Role | Skills |
|---|---|
| Slice Planning | `planning-context-reconciler`, `slice-sizer`, `slice-spec-generator`, `slice-readiness-reviewer`, `next-slice-recommender` |
| Eval Design | `eval-risk-profiler`, `eval-contract-designer` |
| Coding | `implementation-plan-builder`, `architecture-guideline-checker`, `adr-gap-detector`, `source-control-config-capture`, `manual-config-evidence-capture`, `deterministic-test-author`, `implementation-deviation-capture` |
| Eval Execution & Review | `live-eval-runner`, `eval-result-summarizer`, `eval-failure-classifier`, `high-risk-human-review-packager`, `model-drift-trigger-checker`, `regression-promotion-recommender` |
| Documentation & Architecture Reconciliation | `current-state-reconciler`, `architecture-guideline-updater`, `manual-evidence-normalizer`, `documentation-consistency-validator` |
| Traceability & Closeout | `traceability-matrix-builder`, `github-issue-drafter`, `closeout-package-builder`, `definition-of-done-validator`, `archive-package-preparer` |
| Governance & Process Improvement | `slice-retro-and-lessons`, `strategic-doc-update-recommender`, `manual-config-debt-monitor` |
| Orchestration | `slice-orchestrator` |

33 skills total.

## Consolidation note (post-redesign)

These skills replace four pre-redesign skills that were merged, and one that was renamed-by-absorption:

| New / retained skill | Replaces (retired old names) |
|---|---|
| `eval-risk-profiler` | `risk-tier-classifier` + `unsafe-failure-mode-analyzer` + `eval-data-governance-checker` + `cost-latency-eval-designer` |
| `eval-contract-designer` (expanded) | `eval-contract-designer` + `regression-eval-selector` |
| `current-state-reconciler` | `branch-diff-analyzer` + `current-state-doc-reconciler` + `actual-architecture-updater` |
| `slice-retro-and-lessons` | `process-retro-facilitator` + `process-lessons-curator` + `implementation-lessons-curator` |

Pre-redesign Markdown and zip packages under `Skills/_superseded/` are historical only. Do not use them for active work.
