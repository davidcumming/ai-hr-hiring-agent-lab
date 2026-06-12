# Claude Code Instructions

Read [`AGENTS.md`](./AGENTS.md) first. It is the repo-level source of instructions shared by Claude and Codex.

Claude Code should discover reusable skills from `.claude/skills/` and role prompts from `.claude/agents/`. Those folders are copied mirrors of the vendored GenTech Azure Development Standards under `standards/azure-development-standards/`.

For non-trivial work, follow the three-document model named in `AGENTS.md`: the process document owns rules, the skill usage guide owns the skill index, and the orchestration map owns lifecycle flow.

# AI HR Hiring Agent Lab — how to work here

This project follows the vendored Azure Development Standards in
`standards/azure-development-standards/`. Read `AGENTS.md` first — it points
Codex and Claude to the shared process, skills, and role prompts.

- The lifecycle, stage order, gates, and agent/skill routing are defined in
  `standards/azure-development-standards/gentech_slice_lifecycle_orchestration_map.md`.
- The process and governance rules are defined in
  `standards/azure-development-standards/gentech_slice_based_development_process_revised.md`.
- The active skill index is defined in
  `standards/azure-development-standards/gentech_agent_skills_usage_and_requirements.md`.
- Codex discovers skills from `.agents/skills/`; Claude discovers skills from
  `.claude/skills/`. Both are copied mirrors of the vendored standards.
- Role prompts live in `.agents/agents/` and `.claude/agents/`, mirrored from
  `standards/azure-development-standards/agents/`.
- Per-slice working artifacts should live under
  `docs/delivery/slices/<slice-id>/`. The orchestrator should track progress in
  `docs/delivery/slices/<slice-id>/slice-state.yaml` or the slice state format
  required by the active standards.
- Treat slice specs as intent, not truth. Current-state docs must stay
  slice-agnostic.
- STOP and ask for human approval at every human gate: ADR approval,
  residual-risk acceptance, GitHub Issue creation, and any merge. Never merge,
  approve residual risk, create issues, or deploy Azure resources on your own.
