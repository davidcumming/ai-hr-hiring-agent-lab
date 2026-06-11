# Skill Authoring Spec (read before building any skill)

This spec governs how every skill package in `Skills/.agents/skills/` is written. It exists so that skills authored by different agents are consistent. Follow it exactly.

## Authoritative sources

- **The `SKILL.md` package** is the authoritative spec for a skill once it exists. The Skills Doc index (`gentech_agent_skills_usage_and_requirements.md`) is a non-authoritative pointer; use it to find the skill's owning role, purpose, and boundaries when first scaffolding a skill, then keep the detail only in the `SKILL.md`.
- **Cross-cutting rules** that apply to all skills — `Skills/.agents/AGENTS.md`. Reference these by name; do not restate them in a `SKILL.md`.
- **The process rules** — `gentech_slice_based_development_process_revised.md`.
- **The control flow** — `gentech_slice_lifecycle_orchestration_map.md` (stage table in §3, subagent execution model in §6).

When in doubt about a skill's scope, its `SKILL.md` wins. Do not redesign the process or invent new skills.

The packages in `Skills/.agents/skills/` are the active source form. If a project copies them into `.claude/skills/` or another agent-specific directory, copy the entire skill directory, not just `SKILL.md`.

## Output layout (unpacked, one directory per skill)

```text
Skills/.agents/skills/<skill-name>/
  SKILL.md
  templates/<...>.md        # as listed in the skill's catalogue "Recommended package files"
  checklists/<...>.md
  rubrics/<...>.md           # only if the catalogue lists rubrics for this skill
  examples/<...>.md          # add one short example output
```

`<skill-name>` is the exact kebab-case name from the catalogue (e.g., `eval-risk-profiler`). Create every file listed under that skill's "Recommended package files" in the catalogue, plus one `examples/` file.

## Required `SKILL.md` structure

Write for an Opus-class executor: state what is non-obvious and skill-specific; do not re-teach what a strong model already does or restate rules that live in `AGENTS.md`. A good `SKILL.md` is roughly **80–130 lines**. Longer is a smell, not a virtue.

Start with an H1 and the three standardized fields, then the **required core**:

```markdown
# Skill: <Title Case Name>

**Used at:** Stage <N> — <Stage Name> (Orchestration Map §3 stage table)<, and Stage M …>
**Execution model:** <inline | recommended-subagent | isolated-verification>
**Supports:** Process Doc <§X Name>, <§Y Name>

## 1. Purpose            (what it produces + the one boundary that matters most; 1 short paragraph)
## 4. Required Inputs    (the table — load-bearing, keep it)
## 7. Process Steps      (the real domain logic, rubric, or decision table — the value of the skill)
## 10. Quality Bar       (a short before-handoff confirm list, or a pointer to the checklist file)
## 13. Handoff to Next Skill   (decision → next skill)
```

Add the following sections **only when they carry skill-specific content** a model would not infer. Omit them otherwise — do not include an empty or generic section:

```markdown
## 2. When to Use This Skill      (only if triggering is ambiguous; ~2 bullets max)
## 3. Do Not Use This Skill For   (only the 2–3 genuinely confusable boundaries, not a tour of every other skill)
## 5. Default Context Rules       (only to note an EXCEPTION to the AGENTS.md default context list)
## 6. Source Authority Rules      (only if the skill OVERRIDES the standard hierarchy, e.g. "diff/evidence, not spec")
## 8. Output Location             (only if non-obvious)
## 9. Output Format               (a one-line template pointer + any non-obvious constraint — NOT a re-listing of the template's sections)
## 11. Failure Modes to Avoid     (the 2–4 non-obvious, skill-specific traps only)
## 12. Final Response Requirements (fold into §13 unless it adds something §13 doesn't)
```

Number sections as above so anchors stay stable even when optional sections are omitted (a skill may go `## 1 … ## 4 … ## 7 … ## 10 … ## 13`).

**Do not restate cross-cutting rules.** Recommend-never-approve, the source-of-truth hierarchy, the default context allow/deny list, privacy/residency, and "specs are intent" all live once in `AGENTS.md`. Reference them by name; state only this skill's own exception or the single boundary most load-bearing for it. Do not include consolidation-history paragraphs (which skills a skill replaced) — that provenance lives in `AGENTS.md`.

Match the tone of `slice-sizer`: concrete, with small tables where they earn their place. Aim for a genuinely usable spec, not a stub and not an essay.

## Reference convention — IMPORTANT

Do **not** use deep relative markdown links (`../../../../file.md`) inside SKILL.md — skills get copied into `.claude/skills/` and other locations, which breaks such links. Instead reference stages and rules **by name and number**:

- `**Used at:** Stage 4 — Eval design (Orchestration Map §3 stage table)`
- `**Supports:** Process Doc §18 Testing and Eval Requirements, §19 Live-Model Eval Rules`
- In prose: "the next skill, `eval-contract-designer`" — name skills in backticks, do not link them.

The `Execution model` value is one word — `inline`, `recommended-subagent`, or `isolated-verification` — and must match the skill's row in Orchestration Map §6. Do not add a per-skill sentence justifying the choice; the rationale for all three values lives once in §6. Verification skills (readiness review, documentation validation, definition-of-done, eval-failure-classifier sanity pass) are `isolated-verification`; heavy/parallel stages (live eval execution, current-state reconciliation, eval result handling) are `recommended-subagent`; everything else is `inline`.

## Cross-cutting rules every skill must respect

These are defined once in `Skills/.agents/AGENTS.md` (authority and human gates; source of truth; evals and architecture; evidence, privacy, and context). Read them there. Do **not** copy them into a `SKILL.md` — reference by name and state only this skill's exception.

## Boundaries while authoring

- Write **only** inside the skill directories you were assigned. Do not create or edit any shared file (`AGENTS.md`, this spec, other skills' directories) — that prevents collisions with the other authors running in parallel.
- When editing packages, use the editing mechanism provided by the active agent surface and absolute paths beginning with the repository root provided in your task.
