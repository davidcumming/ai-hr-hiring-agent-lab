# Framework Assessment — Remediation Plan and Execution Record

**Date:** 2026-06-09
**Source:** `framework-assessment-and-recommendations.md` (Mythos 5 review, 22 recommendations R1–R22)
**Decisions taken before execution:**

- **Scope:** Full pass — attempt all 22 recommendations.
- **Judgment / verification items** (R8, R12, R14, R18, and similar): draft ADRs and add "pending decision" checklist items rather than make the call. The team decides later.
- **Git:** edit in place on `master`; no branching or commits (user reviews the working-tree diff).

This document is both the plan and the execution record. Section 2 is the per-recommendation work breakdown; Section 3 is the parallel-agent partition; Section 4 is the verification gate.

---

## 1. Grounding notes (what the repo actually looks like)

A few facts from inspecting the repo that shaped this plan and correct minor assumptions in the assessment:

- The 33 skill packages live at `Skills/.agents/skills/<name>/SKILL.md` and **confirmed have no YAML frontmatter** — they open with `# Skill: ...`. (R6 is valid.)
- The 8 **agent role files in `agents/` already have YAML frontmatter** (`name`, `description`, `tools`, `model`). So R6 applies to *skills*, not agent roles. R9/R7 conventions can mirror what the role files already do.
- `.DS_Store` files are **untracked, not committed** (assessment said "dozens are tracked"). So R21's `.gitignore` is still worth adding to keep them untracked, but no `git rm` is needed.
- `slice-orchestrator` exists in **two forms**: `agents/slice-orchestrator.md` (role file, has `Task` in its tools) and `Skills/.agents/skills/slice-orchestrator/` (skill package). R8 concerns the role file's subagent dispatch assumption.
- Canonical docs are flat in the repo root; only `40.2` exists under `Initial_Documentation/` (R20 is valid — the other §40 docs are absent).

---

## 2. Recommendation-by-recommendation work breakdown

Priority tags carried from the assessment. "Owner" = which execution agent (Section 3) makes the change. Multi-file recommendations are split so **each file has exactly one writer**.

### Process & lifecycle

**R1 — Risk-tiered "lite path" (High).** Add a collapse/merge dimension for Low and Standard risk tiers.
- Process Doc §5: state the lite-path *rule* — which stages may merge at Low/Standard, that High-assurance keeps the full path, and that the lite path is governed (not an ad-hoc shortcut). → *Agent 1*
- Orchestration Map §3 stage table: add a "Collapses at Low / Standard" column or annotation per stage (e.g. Stages 0–2 = one planning pass; Stage 3 folded into Stage 16 gate at Low; Stages 14–15 = one closeout pass). → *Agent 2*

**R2 — Machine-readable slice state file (High).** `docs/delivery/slices/<slice-id>/slice-state.yaml`.
- Define the schema + a template + a worked example file. → *Agent 8*
- Orchestration Map §2: add orchestrator responsibility to **read on resume, write after every stage transition**; reference the schema. → *Agent 2*

**R3 — Treat issue creation as backlog tracking (Resolved).** Process Doc §27/§31: ordinary GitHub Issues are backlog records agents may create when safe, with created issue refs reported; human approval remains for destructive issue actions, committed-scope metadata changes, ADRs, residual-risk acceptance, merges, releases, and sensitive/publication-risk issues. → *Agent 1*

**R4 — Cross-model verification (Medium).** Process Doc: at isolated-verification stages (3, 13, 15, failure-classification sanity pass), state a *preference* that verification runs on the other tool/model family from the producer. → *Agent 1*

**R5 — Honest eval-threshold confidence (Low).** Process Doc §19.1: have the eval-summary template record a binomial confidence interval (or "runs is small; treat as directional") for Standard-tier results. → *Agent 1* (rule); summary template note coordinated with eval-result-summarizer skill if needed.

### Claude Code / Codex integration mechanics

**R6 — YAML frontmatter on every SKILL.md (High).** Add `---`-delimited `name` (kebab-case) + `description` (what + when, ≤200 chars, seeded from §1 Purpose first sentence) to all 33 skills. Keep the existing body and the three standardized fields (`Used at`, `Execution model`, `Supports`). → *Agents 5–7 (11 skills each)*

**R7 — Restructure locations + install script (High).**
- Add a non-destructive `install`/sync script (or Makefile target) that symlinks/syncs the canonical package into `.agents/skills/`, `.claude/skills/`, and `.claude/agents/` of a consuming project. → *Agent 8*
- The disruptive part — un-hiding `Skills/.agents/skills/` → `skills/` — is a **structural decision** that would ripple through every doc. Per the "draft, don't decide" rule, we add an ADR proposing it (see R7-ADR under R8/Agent 4 bundle) rather than moving folders mid-pass. → *Agent 4 (ADR)* + note in AGENTS.md → *Agent 8*

**R8 — Verify orchestrator-as-subagent (High).** Cannot test the user's Claude Code version from here.
- ADR drafting the two topologies (nested subagent vs. orchestrator-in-main-session) with a "pending test" decision. → *Agent 4*
- `agents/slice-orchestrator.md` + Orchestration Map §2: add a note that if nested dispatch is unsupported, the orchestrator runs in the main session; link the ADR. → *Agent 2*

**R9 — CLAUDE.md entry point (Medium).** Add a short root `CLAUDE.md` pointing at `AGENTS.md` so both tools load identical rules. → *Agent 8*

**R10 — Native isolation features (Medium).** Once frontmatter exists, encode the execution model in it — `context: fork` (or tool-equivalent) for `recommended-subagent` and `isolated-verification` skills.
- Per-skill frontmatter key. → *Agents 5–7*
- Orchestration Map §6: document the mapping (execution model → tool-native isolation) and the Codex equivalent. → *Agent 2*

**R11 — Automate mechanical gates with CI (Medium).** GitHub Action on PR for: §21.1 re-eval version-manifest change detection, anchor/link integrity scan, stage-table ↔ skill-package consistency, current-state docs containing "Slice N" regex. → *Agent 8*

### Architecture (40.2 + ADRs)

**R12 — Refresh Microsoft naming, adopt GA stack (High).** Terminology sweep of 40.2 (and skills) — "Azure AI Foundry" → "Microsoft Foundry"; note Microsoft Agent Framework 1.0 GA (Build 2026); next-gen Foundry Agent Service GA on Responses API. Re-anchor §6 decision table's right column on Agent Framework 1.0.
- 40.2 edits. → *Agent 3*
- ADR pinning which generation new capabilities target. → *Agent 4*

**R13 — Standardize eval harness on Foundry observability + evaluations (High).** 40.2: make Foundry projects the default eval execution + artifact store; `live-eval-runner` reduces to orchestrating `azure-ai-evaluation` SDK + exporting the repo-safe summary. → *Agent 3*

**R14 — Reconsider four-database footprint (Medium).** ADR evaluating consolidation (Cosmos serverless for state+memory+vectors, or Postgres for memory+RAG) before the pattern hardens. Keep role-separation principle. → *Agent 4 (ADR)*; cross-reference in 40.2 → *Agent 3*.

**R15 — Async path in the shared contract (Medium).**
- Process Doc §17: add `in_progress` status + operation ID + status-poll tool to the envelope vocabulary. → *Agent 1*
- 40.2: Durable Functions / Agent Service async run API behind the facade. → *Agent 3*

**R16 — Tighten Copilot Studio ALM (Medium).** 40.2 §4 integration-validation gate: "agent is in a solution and committed via Git integration" as a hard precondition; name solution-based ALM, native Git integration, Power Platform pipelines, `microsoft/copilot-alm-starter`. → *Agent 3*; update `source-control-config-capture` skill body coordinated by its frontmatter agent if in range.

**R17 — Evidence-ledger immutability earlier (Medium).** 40.2: enable Blob versioning + soft delete from slice 1; time-based retention on evidence containers as lab default; legal-hold/WORM per capability overlay. → *Agent 3*

**R18 — Verify Canadian residency end-to-end (High).** Flagged for verification, not assertion.
- 40.2 §19 new-capability checklist: add (1) model availability in Canadian Foundry regions, (2) Copilot Studio cross-geo data movement. → *Agent 3*
- ADR/checklist doc capturing the two checks as "pending verification per capability." → *Agent 4*

**R19 — APIM as growth path (Low).** 40.2 §5: one sentence naming Azure API Management as the intended evolution once capability count grows. → *Agent 3*

### Artifacts & repo hygiene

**R20 — Reconcile Initial_Documentation/ with §40 (Medium).** Add §40 stubs (40.1, 40.3–40.8) with status headers, or a tracking note stating which exist and where the rest will live. → *Agent 4 (stubs)* + README mention → *Agent 8*.

**R21 — Clean the working tree (Low).** `.gitignore` for `.DS_Store`; note to remove `Skills/_superseded/` zips (history preserves them) — flag, don't delete, since they aid traceability; adopt conventional-commit guidance. → *Agent 8*

**R22 — Link the worked example from README (Low).** Add `example.md` (QuickTodo walkthrough) as step 0 alongside `run-your-first-slice.md`. → *Agent 8*

---

## 3. Parallel-agent partition (single writer per file)

The skill authoring spec warns that parallel authors must not touch shared files. The partition below guarantees **each file has exactly one writing agent**; cross-file recommendations are coordinated through this plan, not through shared edits.

| Agent | Owns (writes only these) | Recommendations |
|---|---|---|
| **A1 Process Doc** | `gentech_slice_based_development_process_revised.md` | R1(rule), R3, R4, R5, R15(envelope) |
| **A2 Orchestration** | `gentech_slice_lifecycle_orchestration_map.md`, `agents/slice-orchestrator.md` | R1(table), R2(orchestrator), R8(note), R10(§6) |
| **A3 Architecture** | `Initial_Documentation/40.2-technical-architecture-guidelines.md` | R12, R13, R14(xref), R15(arch), R16, R17, R18(checklist), R19 |
| **A4 ADRs & stubs** | `Initial_Documentation/adr/*` (new), `Initial_Documentation/40.x-*` stubs (new) | R7-ADR, R8-ADR, R12-ADR, R14-ADR, R18-ADR, R20-stubs |
| **A5 Skills 1–11** | those 11 `SKILL.md` only | R6, R10 |
| **A6 Skills 12–22** | those 11 `SKILL.md` only | R6, R10 |
| **A7 Skills 23–33** | those 11 `SKILL.md` only | R6, R10 |
| **A8 Mechanics & hygiene** | `CLAUDE.md`, `.gitignore`, `scripts/install*`, `.github/workflows/*`, slice-state schema+template, `README.md`, root `AGENTS.md`, `Skills/.agents/AGENTS.md`, `gentech_agent_skills_usage_and_requirements.md` | R2(schema), R7(script+notes), R9, R11, R21, R22, R20(README note) |

No file appears under two agents. A4 and A8 both relate to R20 but write different files (A4 the stubs, A8 the README pointer).

---

## 4. Verification gate (run after all agents finish)

1. **Frontmatter validity** — parse YAML frontmatter on all 33 `SKILL.md`; confirm `name` matches the directory and `description` ≤200 chars.
2. **Execution-model consistency** — each skill's frontmatter `context` value matches its body `Execution model` and Orchestration Map §6.
3. **Anchor/link integrity** — no broken intra-repo anchors after edits; stage-table skill links still resolve.
4. **Stage-table ↔ skill-package consistency** — every skill in the map has a package and vice versa (33).
5. **Diff review** — read the full `git diff` for accidental cross-file collisions, truncation, or destructive changes; confirm no folder was moved and no superseded file deleted.
