# AI HR Hiring Agent Lab

This repo is a self-contained Copilot Studio / Azure AI Foundry HR hiring agent lab. It vendors the GenTech Azure Development Standards and exposes the same active skill packages to Codex and Claude.

## Layout

- `AGENTS.md` - repo instructions shared by Codex and Claude.
- `CLAUDE.md` - Claude Code entrypoint that points back to `AGENTS.md`.
- `standards/azure-development-standards/` - vendored standards snapshot.
- `.agents/skills/` - Codex skill discovery mirror.
- `.agents/agents/` - Codex-readable role prompt mirror.
- `.claude/skills/` - Claude Code skill discovery mirror.
- `.claude/agents/` - Claude Code role prompt mirror.

## Start Here

Read these standards together before planning implementation work:

- `standards/azure-development-standards/gentech_slice_based_development_process_revised.md`
- `standards/azure-development-standards/gentech_agent_skills_usage_and_requirements.md`
- `standards/azure-development-standards/gentech_slice_lifecycle_orchestration_map.md`

The first-project policy and architecture documents are in `standards/azure-development-standards/Initial_Documentation/`.

## Current Scope

This checkout currently contains standards, skills, and agent role prompts only. It does not yet contain application code, Azure resources, deployment scripts, or a test suite.

Use this repo as the source of truth for the lab plan and then codify Copilot Studio, Azure AI Foundry, Azure Functions, storage, search, identity, and evaluation work as slices under the vendored process.
