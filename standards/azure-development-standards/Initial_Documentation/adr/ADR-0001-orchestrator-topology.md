# ADR-0001: Orchestrator topology — subagent dispatch vs. main-session dispatch

> **Status:** Proposed / pending (decision deferred; pending a test on the team's Claude Code version)
> **Date:** 2026-06-09
> **Relates to:** R8 in `framework-assessment-and-recommendations.md`; `agents/slice-orchestrator.md`; `gentech_slice_lifecycle_orchestration_map.md` §2

## Context

`agents/slice-orchestrator.md` is written to run as a Claude Code **subagent** holding the `Task` tool so it can dispatch the eight role agents. This assumes nested delegation — a subagent spawning further subagents — is supported. Historically, Claude Code subagents cannot themselves spawn subagents, which would silently break the entire dispatch model: the orchestrator would be unable to invoke the role agents it is designed to coordinate.

Two facts shape the decision. First, the Orchestration Map already describes the orchestrator as "thin" — it tracks stage, reads/writes state, and dispatches; it holds little logic of its own. Second, the process relies on **three human gates** where the human must see the orchestrator's context directly to approve. A topology that buries the orchestrator one delegation level down from the main session makes that gate context harder for the human to observe.

This decision cannot be made from the repo alone; it depends on the behaviour of the specific Claude Code version the team runs.

## Options

**Option (a) — Orchestrator as a subagent dispatching role subagents via `Task`.**
The orchestrator runs as a Claude Code subagent and uses the `Task` tool to dispatch each role agent. Matches the current `agents/slice-orchestrator.md` shape. Depends on nested delegation being supported.

- *Pros:* keeps the orchestrator isolated in its own context; matches how the role file is written today; minimal change if nested dispatch works.
- *Cons:* breaks entirely if nested subagent dispatch is unsupported on the team's version; pushes human-gate context one level below the main session, where it is less visible to the approving human.

**Option (b) — Orchestrator in the main session as a skill / slash command, dispatching role subagents from there.**
The top-level agent in the main session follows the orchestrator as a skill (or slash command), and dispatches the role subagents directly from the main thread.

- *Pros:* no dependency on nested delegation; the human gates run in the main session where the human already sees the context; aligns with the Orchestration Map's "thin orchestrator" framing — the main thread is arguably the right home.
- *Cons:* the orchestrator's working context shares the main session rather than being isolated; requires the orchestrator to be expressed as a skill/command in addition to (or instead of) the role file.

## Recommendation

**Adopt Option (b) — orchestrator in the main session — if a test confirms nested subagent dispatch is unsupported on the team's current Claude Code version.** If the test shows nested dispatch *is* supported, Option (a) remains viable, but Option (b) is still preferable on the human-gate-visibility argument and the "thin orchestrator" framing. Treat (b) as the default and (a) as the fallback only where isolation outweighs gate visibility.

## Consequences

- If (b) is accepted: `agents/slice-orchestrator.md` and Orchestration Map §2 gain a note that the orchestrator runs in the main session when nested dispatch is unavailable; the orchestrator is also expressed as a skill or slash command; role agents are dispatched from the main thread.
- If (a) is accepted: the current role-file shape stands; document the verified Claude Code version that supports nested dispatch as a re-test trigger if the version changes.
- Either way, the slice-state file (R2) is the durable record of stage and gate outcomes, so neither topology depends on a single context window surviving.

## Open questions / what must be verified before acceptance

1. **Test nested dispatch on the team's current Claude Code version:** can a subagent holding `Task` successfully spawn another subagent? Record the version and the result.
2. If nested dispatch is supported, confirm whether human-gate context remains adequately visible to the release authority under Option (a); if not, prefer (b) regardless.
3. Confirm the Codex equivalent (how the orchestrator dispatches role agents under Codex) so the topology is tool-portable, not Claude-Code-specific.
4. Re-test on any Claude Code version upgrade that could change subagent delegation behaviour.
