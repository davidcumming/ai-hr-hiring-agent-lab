# AI HR Hiring Agent Lab Instructions

This repo is a Copilot Studio / Azure AI Foundry HR hiring agent lab. It vendors the GenTech Azure Development Standards so Codex and Claude can use the same agent role prompts, skill packages, and development process.

This is a lab repo, not a production hiring system. Do not create Azure resources, deploy cloud infrastructure, store secrets, contact candidates, process real applicant data, or make hiring decisions unless the user explicitly asks for a scoped implementation step and approves the required human gate.

## Terminal and Artifact Workflow

The user works in iTerm2 on macOS, often with multiple panes and ChatGPT Work with Apps enabled.

When creating or modifying files:

- Always print absolute paths for important generated artifacts.
- At the end of work, provide concise `Changed files` and `Generated artifacts` sections.
- For important artifacts, include:
  - `open "/absolute/path"`
  - `open -R "/absolute/path"`
  - `printf '%s' "/absolute/path" | pbcopy`
- Do not copy file contents to the clipboard unless explicitly asked.
- Do not open files automatically unless explicitly asked.
- Prefer clear terminal output that is readable in split panes.
- Use quote-wrapped paths because some project folders contain spaces.

For repo work:

- Inspect project instructions before editing.
- Propose a plan first for non-trivial changes.
- Keep docs, tests, and implementation aligned.
- Run the relevant test suite before claiming completion. If no suite exists yet, say so and run structural checks instead.

## Canonical Standards

The vendored standards snapshot lives at `standards/azure-development-standards/`.

Read these three documents together before planning or executing non-trivial work:

- `standards/azure-development-standards/gentech_slice_based_development_process_revised.md` - process and governance source of truth.
- `standards/azure-development-standards/gentech_agent_skills_usage_and_requirements.md` - skill index and role table.
- `standards/azure-development-standards/gentech_slice_lifecycle_orchestration_map.md` - lifecycle control-flow source of truth.

Supporting first-project documents live under:

- `standards/azure-development-standards/Initial_Documentation/`
- `standards/azure-development-standards/docs/delivery/slices/`

Do not create a fourth copy of lifecycle, skill, or gate rules. Link to the canonical standards instead.

## Active Skills and Agent Roles

The canonical vendored skill source is:

- `standards/azure-development-standards/Skills/.agents/skills/`

Tool discovery mirrors are intentionally copied into:

- `.agents/skills/` for Codex.
- `.claude/skills/` for Claude Code.

The canonical vendored role prompt source is:

- `standards/azure-development-standards/agents/`

Role prompt mirrors are intentionally copied into:

- `.agents/agents/` for Codex-readable role files.
- `.claude/agents/` for Claude Code subagents.

Cross-cutting skill rules live in:

- `standards/azure-development-standards/Skills/.agents/AGENTS.md`
- `.agents/AGENTS.md`
- `.claude/AGENTS.md`

When updating standards, update the vendored source first, then refresh the `.agents` and `.claude` mirrors so Codex and Claude see the same active package set.

## Operating Rules

- Active skills are the unpacked packages under `.agents/skills/<skill-name>/` and `.claude/skills/<skill-name>/`.
- Superseded skill drafts are intentionally not vendored into this lab.
- Skills recommend; humans approve. Do not auto-approve ADRs, residual risk, GitHub Issue creation, merge readiness, or release decisions.
- Treat code, config, IaC, approved manual evidence, and current-state docs as implementation truth. Treat slice specs as intent.
- For Azure, Power Platform, Copilot Studio, and Foundry setup, prefer repo-first work: document the intended configuration, capture evidence for manual portal changes, and codify configuration where feasible.
- Never commit secrets, credentials, connection strings, SAS tokens, raw applicant data, regulated personal data, or private tenant details.
