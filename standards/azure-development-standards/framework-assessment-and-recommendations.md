# Framework Assessment and Recommendations

**Date:** 2026-06-09
**Scope:** End-to-end review of the slice-based development process, the 33-skill library, the 8 agent role files, and the technical architecture guidelines (40.2) — focused on a small team using Claude Code and Codex as agentic engineers.
**Status:** Recommendations only. No files were changed.

---

## 1. Overall assessment

This is an unusually mature framework. The strongest elements, worth preserving exactly as they are:

- **The three-document model with a question-indexed source-of-truth hierarchy.** Most agentic-dev failures come from agents reading stale or wrong-authority context; the "slice specs are intent, not truth" rule and the default-context deny list in `Skills/.agents/AGENTS.md` directly attack that.
- **Eval-first requirements with risk-tiered thresholds and version-pinned re-eval triggers.** Designing the eval contract before coding, and tying re-eval to concrete versioned manifests (§21.1), is genuinely best practice — most teams discover this need only after a regression.
- **Recommend-never-approve and the three human gates.** The authority model is consistent everywhere it's stated.
- **The architecture guidelines (40.2) are the strongest artifact in the repo.** The facade-owns-controls pattern, advisory-only AI, evidence ledger separate from telemetry, typed response envelope, memory-subordination model, and the §20 anti-pattern list are aligned with current Microsoft and industry guidance for agentic systems.
- **The conciseness pass already executed** (single home for cross-cutting rules, SKILL.md authoritative, catalogue demoted to index) fixed the redundancy problems that usually sink doc-heavy frameworks.

The recommendations below fall into four groups: process weight, Claude Code / Codex integration mechanics, architecture/service choices, and repo hygiene. Each is tagged **High / Medium / Low** priority.

---

## 2. Process and lifecycle

### R1. Encode a risk-tiered "lite path" through the lifecycle — **High**

§5 (progressive governance) says to start with minimum viable governance, but the Orchestration Map encodes exactly one path: 21 stages and up to 33 skills for every slice. For a small team, a low-risk slice (e.g., the QuickTodo CRUD example) traversing Stages 0–3 as four separate skill invocations with an isolated readiness review is ceremony the framework's own principles argue against. Recommendation: add a third dimension to the stage table — which stages **merge or collapse** at Low and Standard risk tiers (e.g., Stages 0–2 as one planning pass; Stage 3 review folded into the Stage 16 gate for Low; Stages 14–15 as one closeout pass). High-assurance keeps the full path. This makes the lite path *governed* rather than an ad-hoc shortcut individuals will otherwise invent.

### R2. Add a machine-readable slice state file — **High**

The orchestrator "tracks which stage the slice is in," but that state lives only in the model's context window. Sessions end, context compacts, and the team switches between Claude Code and Codex. Recommendation: define `docs/delivery/slices/<slice-id>/slice-state.yaml` recording: current stage, gate outcomes with dates and approver, risk tier, pinned versions (model/prompt/tool-schema/orchestration), open blockers, and pointers to produced artifacts. The orchestrator reads it on resume and writes it after every stage transition. This is the single cheapest change that makes the lifecycle resumable, auditable, and tool-portable — and it gives CI something to validate (see R15).

### R3. Batch low-stakes human approvals — **Medium**

§31 requires human approval for every GitHub Issue creation. With one release authority and ~3 gates per slice this becomes the bottleneck long before agent throughput does. Recommendation: pre-delegate issue creation for low-severity types (documentation-gap, test-gap, enhancement) — agents create them directly with a standard label, and the release authority reviews the batch at Gate 3 (closeout) where the issue summary already appears. Keep per-item approval for security-risk, manual-config-debt, and eval-failure types.

### R4. Use cross-model verification at the isolated-verification stages — **Medium**

You have two agentic engineers (Claude Code and Codex) — exploit that. The `isolated-verification` execution model (Stages 3, 13, 15, and the failure-classification sanity pass) currently guarantees only a fresh context, not a different reviewer. Recommendation: state a preference that verification stages run on the *other* tool/model family from the one that produced the artifact (e.g., Codex validates a Claude-built closeout package). Cross-model review catches model-specific blind spots at near-zero process cost, and your tool-neutral skill format already makes it possible.

### R5. Define eval-threshold confidence honestly — **Low**

§19.1's "5–10 runs at 80%" is a reasonable starting smoke policy, but 8/10 passes is statistically weak evidence of an 80% true pass rate. The doc partly acknowledges this. Recommendation: have the eval summary template record the binomial confidence interval (or simply "runs is small; treat as directional") for Standard-tier results, so a future reader doesn't over-trust early numbers. No process change needed.

---

## 3. Claude Code / Codex integration mechanics

This is where the framework most needs updating: the skill and agent packaging predates conventions that both tools have since standardized.

### R6. Add YAML frontmatter to every SKILL.md — **High**

Both Claude Code and Codex (which adopted the Agent Skills standard in December 2025) discover and auto-invoke skills via YAML frontmatter — `name` and `description` between `---` markers at the top of `SKILL.md`. Your skill files have no frontmatter; they open with `# Skill: ...` and bold fields. Consequence: neither tool can auto-trigger them; every invocation must name the file path explicitly (which `example.md` indeed teaches as the required pattern). Recommendation: add frontmatter to all 33 skills — `name` (the kebab-case skill name), `description` (what it does + when to use, ≤200 chars; the existing §1 Purpose first sentence is close to right). Keep the existing body untouched; the three standardized fields (`Used at`, `Execution model`, `Supports`) can stay in the body or move into frontmatter as custom keys. This is the highest-leverage mechanical fix in the repo.

### R7. Restructure skill/agent locations to what the tools actually scan — **High**

Skills live at `Skills/.agents/skills/<name>/` — a hidden directory nested where neither tool looks (Codex scans `.agents/skills/` at repo root and `~/.agents/skills/`; Claude Code scans `.claude/skills/`). Agent roles live in `agents/`, which Claude Code likewise ignores (it scans `.claude/agents/`). The current guidance — "copy or symlink the whole package directory" — is manual toil that will drift. Recommendation: keep one canonical source location, then add a small `install` script (or a `Makefile` target / Claude Code plugin) that symlinks or syncs into `.agents/skills/` and `.claude/skills/` + `.claude/agents/` in any consuming project. Also consider un-hiding the source folder (`Skills/agents-package/` or just `skills/`) — a hidden `.agents` inside `Skills/` is invisible in Finder and Obsidian and confuses humans maintaining it.

### R8. Verify the orchestrator-as-subagent assumption — **High**

`agents/slice-orchestrator.md` is written to run as a Claude Code subagent with the `Task` tool so it can dispatch the role agents. Historically, Claude Code subagents cannot themselves spawn subagents (no nested delegation), which would silently break the entire dispatch model. Recommendation: test this on your current Claude Code version; if nested dispatch isn't supported, run the orchestrator in the **main session** instead — as a skill or slash command that the top-level agent follows, dispatching role subagents from there. The Orchestration Map already describes the orchestrator as "thin," so the main thread is arguably the right home anyway: the human gates require the human to see the orchestrator's context directly.

### R9. Give Claude Code a CLAUDE.md entry point — **Medium**

The root `AGENTS.md` is exactly what Codex reads. Claude Code's primary instruction file is `CLAUDE.md`. Recommendation: add a one-line `CLAUDE.md` that points at `AGENTS.md` (or symlink it), so both tools load identical repo rules without duplicating content. Same for consuming project repos in the standards' guidance.

### R10. Use the tools' native isolation features for the execution model — **Medium**

Your three execution models (`inline` / `recommended-subagent` / `isolated-verification`) map cleanly onto native features that now exist: Claude Code skills support `context: fork` (run the skill in an isolated context) and subagents; Codex supports similar isolated runs. Recommendation: once frontmatter exists (R6), encode the execution model in it — e.g., `context: fork` for the `recommended-subagent` and `isolated-verification` skills — so isolation is enforced by the tool rather than by the operator remembering the field. Document the Codex equivalent alongside.

### R11. Automate the mechanical gates with hooks/CI — **Medium**

Several gates are pure file checks that today rely on agent diligence: §21.1 re-eval triggers (did a version manifest change in this branch?), the anchor/link integrity scan (currently run manually after edits), stage-table ↔ skill-package consistency (every skill in the Orchestration Map has a package, and vice versa), and current-state docs containing slice-specific language (a regex for "Slice N" catches most). Recommendation: implement these as a GitHub Action on PR plus, optionally, Claude Code hooks locally. Agents are good at judgment gates; deterministic gates should be deterministic code — your own §36 automation posture ("automate after the manual process works") says you're now at that point.

---

## 4. Architecture: services per agentic capability

The core shape — Copilot Studio front door → Entra-authenticated tool boundary → Azure Functions facade owning all controls → advisory Foundry backends → Storage as system of record + evidence ledger — is sound and current. Recommendations are refinements, not redesigns.

### R12. Refresh Microsoft naming and adopt the GA agent stack — **High**

The platform moved under the framework's feet: "Azure AI Foundry" is now **Microsoft Foundry**; **Microsoft Agent Framework 1.0 reached GA at Build 2026** (the production successor to Semantic Kernel/AutoGen patterns, with skills, memory, and middleware as first-class concepts); and the **next-generation Foundry Agent Service is GA**, built on the OpenAI Responses API. Recommendation: do a terminology sweep of 40.2 and the skills, and record an ADR that pins which generation of Foundry Agent Service / Agent Framework new capabilities target. The §6 "smallest backend that meets the need" decision table remains valid — just re-anchor its right-hand column on Agent Framework 1.0 workflows.

### R13. Standardize the eval harness on Foundry observability + evaluations — **High**

The process defines eval governance thoroughly but no tooling, which means `live-eval-runner` implies a hand-rolled harness (scenario execution, repeated runs, version capture, artifact storage). Foundry's **tracing and evaluations are now GA** (any-framework support in preview), including trace-based evaluation of real runs, and the `azure-ai-evaluation` SDK covers programmatic scenario runs with built-in and custom rubric evaluators. Recommendation: make Foundry projects the default eval execution and artifact store — you get run records, model/prompt version capture, dashboards, and access control inside your Azure tenant and residency boundary essentially for free, and `live-eval-runner` reduces to orchestrating the SDK and exporting the repo-safe summary. Hand-roll only what the contract needs and Foundry doesn't provide (e.g., your specific pass-threshold table).

### R14. Reconsider the four-database footprint — **Medium**

Per capability you currently run: Azure Table + Blob (system of record/evidence), Cosmos DB (memory), and PostgreSQL + pgvector (RAG). For a small team that is four data services to provision, secure, back up, residency-pin, and restore-test — and 40.2 itself flags that Table Storage has no point-in-time restore, forcing a bespoke backup/export mechanism. Recommendation: record an ADR evaluating consolidation before the pattern hardens across capabilities. Two credible options: (a) **Cosmos DB serverless for state + memory + vectors** — PITR built in, change feed (useful for the evidence reconciliation sweeps §5 requires and memory save-triggers), DiskANN vector search eliminating Postgres; or (b) **Postgres for memory + RAG**, dropping Cosmos. Either removes one or two services per capability. Azure Storage remains a fine evidence-payload store (Blob immutability) regardless. The binding principle to keep is the *role separation* (system of record ≠ memory ≠ RAG ≠ telemetry), which doesn't require physical separation into four engines.

### R15. Add an async path to the shared contract — **Medium**

§17's envelope is synchronous: the facade does validation → gates → AI call → persistence inside one Copilot Studio tool-call turn. A Foundry Agent Service multi-step workflow (or a 429-heavy PAYG endpoint with backoff, per §6) can easily exceed connector/turn timeouts, and the status vocabulary has no `in_progress`. Recommendation: extend the contract with an explicit long-running pattern — `in_progress` status + operation ID, a status-poll tool, and Durable Functions (or the Agent Service's own async run API) behind the facade. Defining it now prevents each capability inventing its own workaround, which is exactly the per-capability one-off architecture §20 prohibits.

### R16. Tighten Copilot Studio ALM to current mechanisms — **Medium**

`source-control-config-capture` says "export where feasible." Feasibility is now concrete: Copilot Studio supports **solution-based ALM, native Git integration, and Power Platform pipelines**, and Microsoft ships a GitHub Actions ALM starter (`microsoft/copilot-alm-starter`). Recommendation: make the 40.2 §4 integration-validation gate include "agent is in a solution and committed via Git integration" as a hard precondition, and update the skill to name these mechanisms. This converts most would-be manual-config debt for the front door into normal source control on day one.

### R17. Enable evidence-ledger immutability earlier than "production-readiness" — **Medium**

40.2 defers WORM to a production-readiness decision. For a healthcare/public-sector organization, Blob **versioning + time-based immutability policies** are cheap to enable from the first slice and retroactively impossible to add to already-written evidence. Recommendation: enable versioning + soft delete from slice 1 (already required) and adopt time-based retention on evidence containers as the lab default, with the legal-hold/WORM decision documented per capability overlay.

### R18. Verify Canadian residency end-to-end, including Copilot Studio generative features — **High**

§15 handles Azure data services well, but two boundary points deserve explicit verification before the first PHI-adjacent capability: (1) **model availability in Canadian Foundry regions** — not every model/version is deployable in Canada Central/East, and a capability designed around an unavailable model forces a cross-region inference exception; (2) **Copilot Studio cross-geo data movement** — generative features in Power Platform environments can involve data movement outside the environment's geography unless the relevant admin settings restrict it. Recommendation: add both checks to the 40.2 §19 new-capability checklist and record the findings in each capability overlay. (Flagging for verification, not asserting current behaviour — both change frequently.)

### R19. Note API Management as the growth path — **Low**

With one or two capabilities, per-capability Function facades with Entra auth are right-sized. As the capability count grows, Azure API Management in front of the facades standardizes auth, throttling, versioning, and the OpenAPI surface Copilot Studio consumes. Recommendation: one sentence in 40.2 §5 naming APIM as the intended evolution, so nobody ADRs it from scratch later.

---

## 5. Artifacts and repo hygiene

### R20. Reconcile `Initial_Documentation/` with §40 — **Medium**

§40 requires eight documents before first development; only 40.2 exists, and the folder isn't mentioned in the README or AGENTS.md. Recommendation: either add the remaining §40 stubs (40.1, 40.3–40.8 — several are one-page instantiations of process sections) with a status header, or add a tracking note stating which exist and where the rest will live. Right now an agent following §40 can't tell whether the documents are missing or located elsewhere.

### R21. Clean the working tree — **Low**

Add a `.gitignore` for `.DS_Store` (dozens are tracked) and consider removing `Skills/_superseded/` zips from the working tree — git history (or a tag) already preserves them, AGENTS.md already forbids their use, and their presence is pure context noise for agents that glob the repo. Adopt conventional commit messages (recent history is "slice 4", "slice 5") so the changelog has audit value.

### R22. Link the worked example from the README — **Low**

`example.md` (the QuickTodo walkthrough) is the most effective onboarding artifact in the repo and the only place the Claude Code invocation pattern is taught concretely — but the README's reading order never mentions it. Add it as step 0 alongside `run-your-first-slice.md`.

---

## 6. Suggested sequencing

1. **Now (mechanical, high leverage):** R6 frontmatter, R7 locations + install script, R9 CLAUDE.md, R8 orchestrator test, R2 slice-state file.
2. **Before the first real slice:** R1 lite path, R18 residency verification, R12 naming/ADR, R20 §40 stubs, R16 Copilot Studio ALM gate.
3. **During slices 1–2:** R13 Foundry eval harness, R15 async contract, R3 approval batching, R4 cross-model verification, R17 immutability.
4. **After the process stabilizes:** R11 CI gates, R14 database consolidation ADR, R5, R19, R21, R22.

---

## Sources

- [Claude Code — Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [OpenAI Codex — Agent Skills](https://developers.openai.com/codex/skills) and [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [Microsoft Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) and [Build 2026 announcements](https://devblogs.microsoft.com/foundry/agent-service-build2026/)
- [Foundry observability and evaluations at Build 2026](https://devblogs.microsoft.com/foundry/build-2026-from-observability-to-roi-for-ai-agents-on-any-framework/)
- [Microsoft Agent Framework](https://azure.microsoft.com/en-us/blog/introducing-microsoft-agent-framework/)
- [Copilot Studio ALM strategy](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/alm) and [copilot-alm-starter](https://github.com/microsoft/copilot-alm-starter)
