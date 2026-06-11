# Azure Development Standards — GenTech Agentic Solutions

This folder defines the slice-based development process for building GenTech AI solutions on the Microsoft stack, and the agent skills that support it. The governance is split across three documents, each with one job, plus active reusable skill packages and role prompts.

## The three-document model

| Document | Owns | Read it to answer |
|---|---|---|
| [Slice-Based Development Process](./gentech_slice_based_development_process_revised.md) | The **rules** — source-of-truth model, slice sizing, eval thresholds, governance gates, minimum viable governance. | "What is the policy / what must be true?" |
| [Agent Skill Usage and Requirements Guide](./gentech_agent_skills_usage_and_requirements.md) | The **skill index** — design principles, the standard skill structure, the role table, and a short entry per skill that links to its package. | "Which skills exist, who owns them, and where is each one's spec?" |
| [Slice Lifecycle Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md) | The **control flow** — stage-indexed table, branching sequence, the `slice-orchestrator` router, and the subagent execution model. | "At this stage, who acts, which skill loads, which gate applies?" |

The [Skills Design Revision Plan](./skills-design-revision-plan.md) records why the documents are structured this way and serves as design rationale plus a maintenance checklist. The active skill packages have since been built under `Skills/.agents/skills/`.

## How they fit together

The Orchestration Map is the hub. The Process Doc lifecycle links into it for execution detail; the Skills Doc index links into it for where each skill runs; and both the Map and the index link back into the Process Doc for the governing rule. The lifecycle stage list lives in exactly one place (the Orchestration Map) and is referenced elsewhere.

**Where the truth lives (read this first if you're unsure which file wins):**

- A **skill's** detailed spec → its `Skills/.agents/skills/<name>/SKILL.md` package. This is authoritative. The Skills Doc is a non-authoritative index that points here.
- The **control flow** (what runs at each stage, who acts, which gate) → the Orchestration Map.
- A **rule or policy** → the Process Doc.
- A **role's** brief → its `agents/<role>.md` file.
- The **cross-cutting rules** every skill obeys → `Skills/.agents/AGENTS.md` (stated once there, not repeated per skill).

```text
Process Doc (rules) ──► Orchestration Map (stage → agent → skill → gate) ◄── Skills Doc (leaf specs)
        ▲                                                                            │
        └──────────────────────── rules referenced by both ◄─────────────────────────┘
```

## Reading order

0. **Just want to see how it works end to end?** Read the worked example, [QuickTodo walkthrough](./example.md) — the most concrete onboarding artifact in the repo and the only place the Claude Code invocation pattern is taught — alongside the one-page [Run Your First Slice](./run-your-first-slice.md) quickstart.
1. **New to the process?** Start with the Process Doc (§1–§10), then skim the Orchestration Map stage table.
2. **Running a slice?** Drive from the Orchestration Map; execute the active package at `Skills/.agents/skills/<skill-name>/SKILL.md` (the Skills Doc index is only for finding the right skill).
3. **Creating or changing a skill?** Read Skills Doc §2 (design principle) and §10 (rules for creating a skill), `Skills/.agents/AGENTS.md` (cross-cutting rules), and `Skills/.agents/_AUTHORING_SPEC.md`; update the active package and keep the Orchestration Map stage table plus the Skills Doc index aligned.

## Conventions

- **Links:** relative markdown links are canonical (portable across Obsidian, GitHub, and raw-file agent consumers). Obsidian wikilink aliases are an optional convenience. Keep all of these documents in the same folder so links resolve.
- **Headings are an API:** each skill has a stable `### Skill: <name>` heading and each document section is link-targeted by slug. Renaming a heading is a breaking change — update inbound links.
- **Active skill packages** live under `Skills/.agents/skills/` and follow the `.agents` structure described in Skills Doc §3. `Skills/_superseded/` is historical only and must not be used for active work.
- **Role prompts** live under `agents/`. They are thin wrappers that point back to the three canonical docs and the active skill packages.
- **Commit messages:** recent history used `slice N` subjects; prefer Conventional Commits going forward — `type(scope): subject` (e.g. `docs(orchestration): add lite-path table`) so the changelog carries audit value.
- **Superseded material:** `Skills/_superseded/` zips are retained for traceability but are candidates for removal later (git history preserves them); do not delete them as part of routine work.
