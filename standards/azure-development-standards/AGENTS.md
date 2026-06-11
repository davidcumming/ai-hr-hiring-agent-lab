# Azure Development Standards Agent Instructions

This repo is a documentation and reusable-skill standards package for GenTech Microsoft-stack agentic development. It is not an application repo.

## Canonical Documents

- `gentech_slice_based_development_process_revised.md` is the process and governance source of truth.
- `gentech_agent_skills_usage_and_requirements.md` is the skill **index** (design principles, role table, one short entry per skill). It is not authoritative for skill detail — the `SKILL.md` package is.
- `gentech_slice_lifecycle_orchestration_map.md` is the lifecycle control-flow source of truth.

Use those three documents together. Do not create a fourth copy of lifecycle, skill, or gate rules.

## Active Skills and Roles

- Active executable skill packages live under `Skills/.agents/skills/<skill-name>/`.
- Each active package includes `SKILL.md` plus a `templates/` file where the skill produces a document, and `rubrics/` where the skill encodes scoring or classification policy. The quality checklist is inlined in each `SKILL.md` §10; standalone worked examples were removed as redundant with the templates (two trimmed eval references are retained for the cross-skill chain).
- Role prompts live under `agents/`.
- The Skills Doc index is useful for finding a skill, but active work must follow the unpacked `SKILL.md` package, which is the authoritative spec for the skill being run.
- Cross-cutting rules that apply to all skills live once in `Skills/.agents/AGENTS.md`; do not restate them per skill.
- If a skill package is copied to another agent surface, copy the whole package directory, not only `SKILL.md`.
- To install into a consuming project, run `scripts/install.sh <target-project-dir>` (add `--copy` to vendor instead of symlink). It is idempotent and syncs the canonical source — `Skills/.agents/skills/` and `agents/` — into the locations the tools actually scan: `.agents/skills/` (Codex) and `.claude/skills/` + `.claude/agents/` (Claude Code). A proposal to un-hide the canonical source folder (`Skills/.agents/skills/` → `skills/`) is recorded as an ADR under `Initial_Documentation/adr/` (ADR-0005); until decided, the install script is the bridge.

## Superseded Material

- `Skills/_superseded/` contains historical packaged-skill drafts and zip files.
- Do not use superseded Markdown or zip packages for active work.
- Keep superseded files only for traceability unless the user explicitly asks to archive or delete them.

## Editing Rules

- Keep docs, active skills, templates, checklists, examples, and orchestration references aligned.
- Treat Process Doc §19.1 as the canonical eval-threshold policy.
- Use `docs/delivery/slices/<slice-id>/...` for active per-slice delivery artifacts.
- Use `docs/planning/...` only for planning artifacts not yet attached to an approved slice.
- Do not touch unrelated parent-folder files or generated `.DS_Store` files.
