# Agent Role Files

One markdown file per agent role in the slice-based process. Each file is **dual-use**:

- **As a Claude Code subagent** — copy or symlink this folder into `.claude/agents/` (Claude Code discovers subagents there, not in an arbitrary `agents/` folder). Claude Code reads the YAML frontmatter (`name`, `description`, `tools`, `model`) and delegates based on `description`.
- **As a role prompt for Codex or any model** — attach the file (or paste its body). Ignore the YAML frontmatter; the body is a self-contained role brief. Codex does not consume the frontmatter or auto-delegate — you are simply telling the model which role to assume.

The frontmatter is Claude-Code-only metadata. The body is the portable artifact.

When executing a skill named in a role file, use the active package at `../Skills/.agents/skills/<skill-name>/SKILL.md`. The catalogue links explain the skill's purpose and boundaries; the active package is the executable instruction set.

## Files

| Role | File | Owns stages |
|---|---|---|
| Slice Orchestrator (router) | [slice-orchestrator.md](./slice-orchestrator.md) | all (dispatch) |
| Slice Planning Agent | [slice-planning-agent.md](./slice-planning-agent.md) | 0–3, 20 |
| Eval Design Agent | [eval-design-agent.md](./eval-design-agent.md) | 4 |
| Coding Agent | [coding-agent.md](./coding-agent.md) | 5–9 |
| Eval Execution and Review Agent | [eval-execution-and-review-agent.md](./eval-execution-and-review-agent.md) | 10–11 |
| Documentation and Architecture Reconciliation Agent | [documentation-and-architecture-reconciliation-agent.md](./documentation-and-architecture-reconciliation-agent.md) | 12–13 |
| Traceability and Closeout Agent | [traceability-and-closeout-agent.md](./traceability-and-closeout-agent.md) | 14–15, 17 |
| Governance and Process Improvement Agent | [governance-and-process-improvement-agent.md](./governance-and-process-improvement-agent.md) | 18–19 |

The **Release Authority** (stage 16) is intentionally not an agent file — it is a human role. Agents recommend; the human approves.

## Notes

- `model` values are sensible starting defaults (`opus` for high-judgment roles, `sonnet` for implementation/reconciliation) — adjust to taste.
- `tools` lists are minimal per role; widen only if a role genuinely needs more.
- Each body links to the authoritative definitions: the [skill catalogue](../gentech_agent_skills_usage_and_requirements.md), the [Orchestration Map](../gentech_slice_lifecycle_orchestration_map.md), and the [process rules](../gentech_slice_based_development_process_revised.md). Keep the bodies thin and let those documents plus the active skill packages stay the single source of truth.
