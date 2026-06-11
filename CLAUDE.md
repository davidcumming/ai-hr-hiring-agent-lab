# Claude Code Instructions

Read [`AGENTS.md`](./AGENTS.md) first. It is the repo-level source of instructions shared by Claude and Codex.

Claude Code should discover reusable skills from `.claude/skills/` and role prompts from `.claude/agents/`. Those folders are copied mirrors of the vendored GenTech Azure Development Standards under `standards/azure-development-standards/`.

For non-trivial work, follow the three-document model named in `AGENTS.md`: the process document owns rules, the skill usage guide owns the skill index, and the orchestration map owns lifecycle flow.
