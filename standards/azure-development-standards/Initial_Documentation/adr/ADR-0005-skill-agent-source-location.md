# ADR-0005: Skill/agent source location — un-hiding the canonical package

> **Status:** Proposed / pending (recommended as a dedicated follow-up, not a mid-pass change)
> **Date:** 2026-06-09
> **Relates to:** R7 in `framework-assessment-and-recommendations.md`; `Skills/.agents/skills/`, `agents/`, `AGENTS.md`

## Context

The 33 skill packages live at `Skills/.agents/skills/<name>/SKILL.md` — a **hidden** directory (`.agents`) nested inside `Skills/`. Agent role files live in `agents/`. This layout has two problems:

1. **The tools do not scan these paths.** Codex scans `.agents/skills/` at the repo root and `~/.agents/skills/`; Claude Code scans `.claude/skills/` and `.claude/agents/`. The canonical source at `Skills/.agents/skills/` is in none of those locations, so neither tool auto-discovers the skills there; the current guidance is to "copy or symlink the whole package directory," which is manual toil that drifts.
2. **The hidden source folder is invisible to humans.** A hidden `.agents` inside `Skills/` does not show in Finder or Obsidian and confuses the humans who maintain it.

The fix is to keep **one visible canonical source** and **project** it (via symlink/sync) into the locations the tools actually scan, rather than maintaining the canonical copy in a hidden, un-scanned path.

The reason this is a *proposed* ADR rather than an executed change: the move ripples through **every document that references the current path** (`AGENTS.md`, the orchestration map, the skills-usage doc, the worked example, and any skill cross-references). Doing it mid-remediation-pass would collide with the other agents editing those same documents and risk leaving references half-updated. It is a structural change best done as a single, focused follow-up with all reference updates in one diff.

## Options

**Option (a) — Un-hide to a top-level `skills/` directory as the canonical source; sync/install script projects into the tool paths.**
Canonical source becomes `skills/<name>/SKILL.md`; a script symlinks/syncs into `.agents/skills/`, `.claude/skills/`, and `.claude/agents/`.

- *Pros:* most visible and conventional; short path; matches a plain `skills/` mental model.
- *Cons:* `skills/` at root may collide with consuming-project conventions; large rename touching every reference.

**Option (b) — Un-hide to `Skills/agents-package/` as the canonical source; same sync/install script.**
Keeps the existing `Skills/` parent but replaces the hidden `.agents` with a visible `agents-package/`.

- *Pros:* visible to Finder/Obsidian; smallest conceptual move (stays under `Skills/`); clearly signals "this is the source package, not a tool-scanned path."
- *Cons:* longer path; still a rename touching references.

**Option (c) — Status quo (hidden `Skills/.agents/skills/` + manual copy/symlink).**

- *Pros:* no reference churn.
- *Cons:* hidden source confuses maintainers; tools do not scan it; manual sync drifts.

## Recommendation

**Un-hide the canonical source and add a sync/install script (Option a or b), executed as a dedicated follow-up — not mid-pass.** Of the two un-hiding targets, **Option (b) (`Skills/agents-package/`)** is the lower-disruption choice: it removes the hidden-folder problem while keeping the existing `Skills/` parent, and the name signals that it is the authored source rather than a tool-scanned projection. The install/sync script (owned by another agent under R7) projects the package into `.agents/skills/`, `.claude/skills/`, and `.claude/agents/` in any consuming project. Defer the actual move until this remediation pass is complete so all reference updates land in one clean diff.

## Consequences

- When accepted and executed: the canonical path changes; every reference (`AGENTS.md`, `Skills/.agents/AGENTS.md`, the orchestration map, the skills-usage-and-requirements doc, the worked example, skill cross-references) is updated in the same change set.
- The sync/install script (R7) becomes the supported way to populate tool-scanned paths; the "copy or symlink the whole package directory" guidance is replaced.
- Until executed, the status quo holds and the install script (added now under R7) can target the existing path, then be re-pointed when the move happens.

## Open questions / what must be verified before acceptance

1. Choose the canonical target: `skills/` (Option a) vs. `Skills/agents-package/` (Option b). Confirm neither collides with consuming-project conventions.
2. Enumerate **every** file referencing the current `Skills/.agents/skills/` path so the move updates all references in one diff (grep the repo before executing).
3. Confirm the sync/install script's symlink vs. copy behaviour works on the team's platforms (macOS/Obsidian/iCloud sync can mishandle symlinks — verify).
4. Confirm whether the agent role files (`agents/`) move alongside the skills or stay put, and how the script projects them into `.claude/agents/`.
5. Schedule as a single dedicated follow-up after the current remediation pass; do not interleave with other agents' edits to the referencing documents.
