# Slice-Based Development Process for Microsoft-Stack Agentic Solutions

This document defines the **rules** (policy, governance, gates) for the slice-based process. It is one of three related documents:

- **This document** — the rules.
- [Agent Skill Usage and Requirements Guide](./gentech_agent_skills_usage_and_requirements.md) — the **skill index** (one short entry per skill, linking to its authoritative `SKILL.md`).
- [Slice Lifecycle Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md) — the **control flow** (stage table, sequence, orchestrator, subagent model). The authoritative stage-to-skill-to-gate mapping lives there.

> **Link conventions.** Relative markdown links are canonical (portable across Obsidian, GitHub, and raw-file agent consumers). Obsidian wikilink aliases are an optional convenience. All three documents are assumed to live in the same folder. Headings are treated as an API: renaming one is a breaking change for inbound links.

## 1. Purpose

This document defines a slice-based development process for building GenTech AI solutions on the Microsoft stack, including Copilot, Azure AI Foundry, Power Platform, Azure services, GitHub, deterministic tests, and live-model agentic evals.

The process is designed for agent-assisted development. It assumes that coding agents, documentation agents, eval agents, and human reviewers will all participate in delivery, but with clearly separated responsibilities and authority.

The central goal is to use a rich documentation repository to inform implementation without allowing that documentation to overload, confuse, or contaminate the clean code repository.

It is designed to prevent the common agentic-development failure modes: requirements and implementation drifting apart; slice specs treated as truth after implementation proves them wrong; low-code or portal configuration escaping source control; deterministic tests passing while agentic behaviour stays unverified; current-state docs polluted with historical planning language; agents acting on stale planning artifacts; and evidence that cannot survive audit.

The process should be applied with discipline, but not with unnecessary ceremony. The operating model should start with minimum viable governance and become more robust as real slices expose the need for more structure.

---

## 2. Core Operating Model

The development model uses two primary repositories: a **documentation repo** (the strategic and design source — rich, messy, exploratory, and forward-looking) and a **code repo** (the clean implementation repository). §6 details what each holds.

The documentation repo informs implementation slices, but it is not the ground truth for what has been built. The code repo should remain clean enough that an implementation agent can safely use it as the authoritative baseline without treating obsolete slice plans as current reality.

---

## 3. Source-of-Truth Hierarchy

There is no single universal source of truth. Authority depends on the question being asked.

| Question | Source of Truth |
|---|---|
| What has actually been implemented? | Code, source-controlled configuration, IaC, committed assets, and approved manual evidence |
| What does the current application do? | Code repo current-state documentation |
| What is the intended product direction? | Documentation repo |
| What behaviours are verified? | Deterministic tests, live-model eval summaries, and external eval artifacts |
| What work remains unresolved? | GitHub Issues |
| Why was an architecture decision made? | Approved ADRs |
| What rules should future implementation follow? | Technical architecture guidelines |
| What architecture has actually been built? | Actual technical architecture documentation plus code/config evidence |
| What happened during a historical slice? | Archived slice package |
| What lessons should influence future slices? | Curated implementation lessons and process lessons |

This question-indexed source-of-truth model is foundational. The process should not try to make one artifact answer every question.

---

## 4. Slice Specs Are Intent, Not Truth

A slice spec is an implementation-intent document.

It describes what the slice is trying to achieve. It helps the coding agent understand the desired user behaviour, business process, workflow changes, acceptance criteria, and required evals.

However, the slice spec is not authoritative once implementation begins. It may be wrong, incomplete, over-specified, under-specified, or unrealistic based on the actual Microsoft-stack implementation path.

After the slice is complete, the slice spec becomes historical delivery evidence. It should not be treated as a current-state description of the application. The authoritative current-state baseline is whatever the §3 hierarchy points to for each question (code/config and approved evidence for implementation truth, current-state docs for behaviour, GitHub Issues for unresolved work).

The slice spec remains useful because it preserves original intent. Deviations from it should be documented, not erased. Those deviations become planning feedback for future slices.

---

## 5. Progressive Governance Principle

This process should not require the full governance universe to exist before the first functional slice.

The initial risk is overbuilding the factory before proving that the factory produces useful software. Agentic-development governance is necessary, but governance must be validated against real implementation work.

The recommended posture is:

```text
Start with minimum viable governance.
Run the first slice.
Let the first slice expose which templates and controls need to become real.
Harden the process after one or two slices.
Automate only after the manual process works.
```

Before the first functional slice, create only the minimum documents and templates required to avoid chaos. Additional templates should be created when they become necessary, not pre-emptively because they sound useful.

This process should evolve through slice retrospectives.

### 5.1 Risk-Tiered Lite Path

Progressive governance also applies to the lifecycle itself, not only to which templates exist. The full path — every stage as a separate pass with its own gate — is required for High-assurance slices, but for lower-risk work some lifecycle stages may collapse into a single pass:

- **Low and Standard risk tiers** may merge the early planning stages (Stages 0–2) into one planning pass, and merge the closeout stages (Stages 14–15) into one closeout pass.
- **Low risk tier** may additionally fold the Stage 3 readiness review into the Stage 16 gate rather than running it as a separate isolated review.
- **High-assurance slices** keep the full, unmerged path; no stage collapses.

This lite path is *governed*: it is the defined set of permitted collapses above, selected by the slice's risk tier — not an ad-hoc shortcut individuals invent slice by slice. The per-stage collapse detail (which specific stages merge at Low versus Standard, and how the merged passes preserve their gates) is owned by the [Orchestration Map stage-indexed table](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table); this section states the rule, the table states the mechanics. The lite path never removes a human gate — it only reduces the number of separate passes a low-risk slice traverses.

---

## 6. Repository Roles

### 6.1 Documentation Repo

The documentation repo is the strategic and planning source. It holds the rich, forward-looking material — product vision, business and functional requirements, target architecture thinking, process models, user journeys, roadmap ideas, domain research, prior slice archives, and lessons promoted back from implementation.

It must not be treated as the current-state implementation record. It should be selectively updated after completed slices when durable lessons affect future planning.

### 6.2 Code Repo

The code repo is the clean implementation repository. It holds application source, source-controlled configuration or IaC where feasible, tests, eval definitions, current-state product documentation, technical architecture guidelines and actual architecture, ADRs, implementation and process lessons, changelog, and the governance templates as they mature.

It must not retain raw slice-planning artifacts in main after merge unless they have been curated into durable documentation. The code repo must stay clean enough that an implementation agent can use it as the authoritative baseline without mistaking obsolete slice plans for current reality.

---

## 7. Current-State Documentation Versus Historical Slice Documentation

The code repo must distinguish between current-state documentation and historical delivery evidence.

### 7.1 Current-State Documentation

Current-state documentation describes what the application currently does. It must remain slice-agnostic: it should not say "Slice 1 added..." or "The next slice will...", and instead say "The system supports..." or "The current architecture uses...".

### 7.2 Historical Slice Evidence

Historical slice evidence describes how something was delivered — for example the original slice spec, deviation log, implementation summary, screenshot/manual-config evidence, traceability matrix, eval summary, test results, approval notes, and closeout report.

Most historical slice evidence should be archived outside the code repo main branch after the slice is complete.

---

## 8. Recommended Code Repo Documentation Structure

The code repo should eventually support a `/docs` tree organised into four areas:

```text
/docs
  /product-current-state   slice-agnostic current behaviour, architecture, data, security/privacy, ops, eval strategy, known limitations
  /architecture            architecture guidelines, actual architecture, ADR index, /adrs
  /delivery                implementation & process lessons, changelog, per-slice packages under /slices/<slice-id>/, and the slice/closeout/traceability/eval/evidence templates
  /governance              source-of-truth, definition-of-done, PR checklist, GitHub issue template, manual-config-debt policy, release-authority policy
```

This is the mature target structure, not the mandatory pre-slice-1 structure. For slice 1, create only the minimum viable governance subset defined at the end of this document.

---

## 9. Architecture Guidelines Versus Actual Architecture

The code repo must contain two distinct architecture concepts.

### 9.1 Technical Architecture Guidelines

The technical architecture guidelines describe the intended Microsoft-stack mapping for foreseeable categories of functionality.

Examples:

- Copilot is the front door and primary user-facing orchestrator.
- Agent memory uses the approved Microsoft memory pattern and approved persistence layer.
- Workflow state uses the approved Azure data service or storage pattern.
- AI backend services, Foundry agents, model deployments, and tool integrations follow approved boundaries.
- Deterministic workflow services validate, gate, persist, and audit state changes.
- Human approval is required before AI-generated outputs become official where risk is material.
- Identity, authorization, logging, and auditability follow the approved Microsoft-stack pattern.

The guidelines are forward-looking guardrails. They apply to foreseeable functionality, even before all of it has been built.

### 9.2 Actual Technical Architecture

The actual technical architecture describes only what has actually been implemented.

It should not include aspirational components unless they are clearly marked as future considerations, limitations, or known gaps.

### 9.3 Handling Guideline Gaps

If a coding agent determines that the current guidelines are insufficient, contradictory, or unsuitable for a required implementation, it must stop and produce a proposed ADR.

The process is:

1. Identify the guideline gap or conflict.
2. Draft a proposed ADR.
3. Human release authority reviews and approves or rejects the ADR.
4. If approved, update the technical architecture guidelines.
5. Proceed with implementation under the updated guidelines.

The ADR explains why the rule changed. The guidelines define the active rule going forward.

---

## 10. Slice Lifecycle Overview

Each implementation slice follows this lifecycle:

```text
Documentation repo intent
  ↓
Reconciled planning context
  ↓
Slice specification
  ↓
Eval design and hardening
  ↓
Feature branch implementation
  ↓
Deterministic tests
  ↓
Live-model evals
  ↓
Documentation reconciliation
  ↓
Traceability and closeout
  ↓
Human approval
  ↓
Merge
  ↓
Archive historical artifacts
  ↓
Promote durable lessons
  ↓
Recommend next slice candidate
```

The lifecycle is deliberately end-of-slice documentation driven. Current-state documentation should be updated after the functioning branch can be reviewed as a whole, not continuously after individual commits.

Each node above maps to one or more stages in the [Orchestration Map stage-indexed table](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table), where the active agent role, the skill loaded, the entry/exit gate, and the execution model for that step are defined. This document owns *why* each step exists; the Orchestration Map owns *how* it is executed. The lifecycle is driven by the [`slice-orchestrator`](./gentech_slice_lifecycle_orchestration_map.md#2-the-slice-orchestrator-skill) router, which pauses at every human gate (ADR approval, eval-failure clarification, and closeout/merge).

### 10.1 Cross-Model Verification Preference

The isolated-verification stages (Stages 3, 13, and 15, and the failure-classification sanity pass) exist to review an artifact in a fresh context, independent of the agent that produced it. Where the team runs more than one agentic tool or model family (for example Claude Code and Codex), the *preferred* execution of these stages is on the **other** tool or model family from the one that produced the artifact — for example Codex validating a Claude-built closeout package, or vice versa. Cross-family review catches model-specific blind spots that a same-family re-run shares.

This is a preference, not a hard gate: the tool-neutral skill format already makes either family able to run the verification skill, so the process cost is near zero. When only one family is available, a fresh isolated context on that family satisfies the stage.

---

## 11. Slice Sizing Rules

The success of this process depends on slices staying small.

A slice is not a milestone. A slice is a bounded implementation increment that can be specified, implemented, tested, evaluated, documented, reviewed, and closed out in one coherent branch.

### 11.1 Preferred Slice Characteristics

A good slice should:

- Deliver one coherent user or process capability.
- Fit in one feature branch.
- Fit in one PR.
- Have clear acceptance criteria.
- Have clear deterministic test coverage.
- Have clear live-model eval coverage.
- Be explainable in one closeout package.
- Be small enough that documentation reconciliation is tractable.
- Be small enough that re-running relevant evals is affordable and useful.

### 11.2 Split-the-Slice Triggers

A proposed slice should be split if any of the following are true:

- It introduces multiple unrelated user workflows.
- It changes more than one major process area.
- It requires multiple independent architecture decisions.
- It introduces several high-risk behaviours at once.
- It requires significant manual portal configuration across multiple Microsoft surfaces.
- It cannot be evaluated with a manageable scenario set.
- Its closeout package would be too large for practical human review.
- Its implementation cannot be understood as one coherent branch delta.
- It is likely to create documentation updates across most of the master docs.
- It depends on unresolved platform exploration.

### 11.3 Practical Heuristic

As a practical rule, a slice should normally be small enough that:

```text
One agent can implement it.
One reviewer can understand it.
One eval package can verify it.
One documentation pass can reconcile it.
One closeout review can approve it.
```

If that is not true, the slice is probably too large.

The 80% functional / 20% technical guideline for slice specs is guidance, not a formal gate. The important rule is that slice specs define product behaviour and process intent, not implementation design.

---

## 12. Slice Planning

### 12.1 Planning Inputs

The slice-planning agent reads durable planning context — documentation-repo source material, current-state docs, architecture guidelines, approved ADRs, implementation and process lessons, changelog, open GitHub Issues, and test/eval status. It should not read code artifacts by default (consistent with the default-context rule in AGENTS.md).

The purpose of slice planning is to define what users can do, what process changes are introduced, and what behaviours the agent must support. It is not primarily a coding exercise.

### 12.2 Slice Spec Content

A slice spec must focus primarily on functional, business, and process behaviour: the business outcome and user value, the workflow and process changes, business rules, acceptance criteria, agent behaviours, the required deterministic tests and live-model eval scenarios, unsafe failure modes, expected and unacceptable outputs, and any governing architecture constraints, scope boundaries, assumptions, and open questions. The full field list and structure are owned by the `slice-spec-generator` template (see also §40.3).

It must not include detailed implementation design unless the detail is required as an architecture constraint.

---

## 13. Eval-Driven Requirements

For agentic systems, requirements are incomplete unless evals are defined.

A slice spec must define the behavioural contract for the agent — acceptance criteria, deterministic tests and live-model eval scenarios, unsafe failure modes, expected behaviour under ambiguity, expected evidence usage, expected refusal/escalation behaviour, pass/fail criteria, and cost/latency budgets where relevant.

The eval design should happen before implementation begins.

The slice-planning agent may draft evals, but a separate eval-design or eval-review step should harden them before coding starts.

---

## 14. Branching Model

Each slice should be developed on a dedicated feature branch.

Example:

```text
feature/slice-001-user-intake-foundation
```

The slice branch may contain temporary delivery artifacts during development, such as:

- Slice spec
- Eval design notes
- Traceability matrix
- Implementation summary
- Manual evidence
- Deviation log
- Closeout package

Before merge, the branch must be reviewed and closed out.

After merge, most temporary slice artifacts should be archived outside the code repo main branch. Only durable outputs should remain in main.

---

## 15. Parallel Work and Dependency Model

The default model should be serial for the first one or two functional slices. This reduces baseline drift while the process is being validated.

After the workflow is proven, controlled parallelism may be allowed. Parallel and fan-out work is dispatched through isolated subagents per the [subagent execution model](./gentech_slice_lifecycle_orchestration_map.md#6-subagent-execution-model) in the Orchestration Map.

### 15.1 Serial Default

Under the serial default:

```text
Only one implementation slice is active at a time.
The slice is closed out before the next implementation slice begins.
Next-slice planning can happen near the end of the active slice, but should use the latest reconciled current-state baseline.
```

This reduces documentation conflicts, eval baseline drift, and merge-order ambiguity.

### 15.2 Controlled Parallelism

Concurrent slices may be allowed only if:

- Their functional areas do not overlap.
- Their architecture impact is independent.
- Their eval suites do not modify the same baseline behaviours.
- Their documentation updates do not target the same current-state sections.
- Each branch rebases against the latest main before closeout.
- Relevant evals are re-run after rebase.
- Documentation reconciliation is repeated after rebase.
- Merge order is explicitly decided.

### 15.3 Dependency Rules

If one slice depends on another:

- The dependent slice may be planned, but should not be implemented until the prerequisite slice is merged.
- If implementation starts anyway, the branch must be treated as unstable until rebased onto the completed prerequisite.
- Evals must run against the final dependency baseline, not against a speculative intermediate state.

---

## 16. Implementation Process

The coding agent implements the slice using the slice spec, the architecture guidelines and approved ADRs, current-state docs, existing tests and evals, and relevant implementation and process lessons.

The coding agent should not treat the slice spec as absolute truth. If implementation realities require deviation, the agent should document the deviation.

If a deviation reveals a reusable Microsoft-stack lesson, that lesson should be promoted to the central implementation lessons document.

If a deviation reveals an architecture gap, the agent should create a proposed ADR before proceeding.

---

## 17. Manual Portal and Configuration Evidence

Some Microsoft-stack work may happen through Azure Portal, Power Platform, Copilot Studio, Foundry UI, or other web-based configuration surfaces.

Manual evidence is allowed, but it must be treated as an exception path, not the preferred implementation path.

### 17.1 Default Representation Rule

Where feasible:

- Azure infrastructure should be represented through IaC, deployment scripts, or source-controlled configuration.
- Power Platform assets should be represented through managed solution ALM practices, exported/unpacked artifacts, or other source-control-compatible representation.
- Copilot, Foundry, and agent configuration should be exported, scripted, versioned, or captured through supported configuration mechanisms where feasible.
- Prompts, tool schemas, orchestration definitions, policy files, and evaluation datasets should be versioned.

Manual portal evidence is acceptable only when source-controlled representation is not yet feasible, not yet understood, or temporarily blocked.

### 17.2 Manual Evidence Requirements

Manual changes may support merge only if:

1. They are documented.
2. Screenshots or exports are captured where useful.
3. The change is reviewed and approved.
4. A GitHub Issue is created if the change should later be source-controlled, automated, exported, or represented as IaC/config.

Manual evidence should capture what changed, where, by whom, and why; screenshot/export references; whether it is represented in the repo; the risk if it is not source-controlled; and any follow-up issue reference. The field layout is owned by the `manual-config-evidence-capture` skill / manual-evidence template.

### 17.3 Manual-Config Debt Ceiling

Manual configuration debt must not grow without limit.

A project should define a debt ceiling before feature delivery begins. A reasonable starting policy is:

```text
No new feature slice may begin if:
- there is any unresolved critical manual-config or source-control debt, or
- more than three non-critical manual-config/source-control-debt issues remain open, or
- a manual-config debt issue has survived more than one subsequent slice without explicit re-approval.
```

The exact threshold can be adjusted, but the process must include a ceiling. Otherwise every slice can pass while hidden operational risk accumulates.

---

## 18. Testing and Eval Requirements

Code is not complete unless deterministic tests pass and the eval contract is satisfied. For agentic behaviour, that means both deterministic tests and live-model evals pass according to the required quality gate.

Deterministic testing alone is insufficient for agentic solutions. A deterministic-only completion path is allowed only for a non-agentic slice when the eval risk profile and eval contract explicitly state that the slice has no model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency.

Each slice requires deterministic tests as applicable (unit, integration, workflow/state), slice-specific live-model evals and core regression evals unless the non-agentic carve-out is documented, an eval summary report, and human review for high-risk behaviours.

### 18.1 Standard Test/Eval Package

Every normal agentic slice requires deterministic tests, workflow/state tests where relevant, slice-specific live evals, core regression evals, an eval summary, and a traceability matrix; the contract's exact contents are owned by the `eval-contract-designer` contract.

For non-agentic slices that qualify for the carve-out, the eval summary must record the deterministic test results and the explicit "live eval not applicable" rationale from the eval contract. This is a documented exception, not an implicit shortcut.

### 18.2 High-Assurance Test/Eval Package

High-risk slices require a stronger package.

High-risk areas include:

- Approvals
- Evidence claims
- Privacy
- External sharing
- Memory
- Permissions
- Irreversible state changes
- User-facing authoritative outputs
- Workflow decisions with material consequences
- Healthcare, sensitive, or regulated data handling
- Audit-relevant decision support

High-assurance slices require everything in the standard package plus adversarial evals, larger repeated-run sample sizes, stronger pass thresholds (see §19.1), human review notes, explicit unsafe-failure analysis, cost and latency analysis, stronger traceability, and multi-model comparison where model choice is material.

---

## 19. Live-Model Eval Rules

Live-model evals must be run against real models whenever the eval contract includes model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency.

When the non-agentic carve-out from §18 applies, Stage 10 live eval execution is skipped and Stage 11 records the "live eval not applicable" rationale in the eval summary.

A single successful run is not enough.

### 19.1 Risk-Tiered Eval Thresholds

The exact thresholds should be adjusted as the eval harness matures, but the starting point should distinguish between normal and high-assurance behaviours.

Suggested starting policy:

| Risk Tier | Minimum Runs | Suggested Threshold | Human Review |
|---|---:|---:|---|
| Low-risk / exploratory | 3-5 | No critical failures; acceptable qualitative result | Optional |
| Standard slice behaviour | 5-10 | At least 80% pass rate | Recommended for failures |
| High-risk behaviour | 20+ | At least 90% pass rate and zero critical failures | Required |
| Safety/privacy/evidence-critical behaviour | 20+ | Zero critical failures; stricter rubric-defined threshold | Required |

A 4-of-5 result may be useful as a smoke check. It should not be treated as strong evidence for high-assurance behaviour.

This policy is unchanged, but the eval summary should be honest about confidence: for Standard-tier results, where the run count is small (5–10), the summary should record a binomial confidence interval for the observed pass rate — or, where that is not practical, simply state "runs is small; treat as directional." The point is to stop a future reader over-trusting an 8/10 as if it were a precise 80% true pass rate. The threshold table above still governs the pass/fail decision.

### 19.2 Eval Summary Fields

Eval summaries must record the pinned versions of every behaviour-affecting element (model name and version, prompt, tool schema, orchestration, and workflow/state version), the run metadata (date, scenario set, number of runs, pass threshold), the results and failures with reviewer notes, the cost/latency measurements (token usage, estimated model cost, latency), and artifact references. The version pinning is what makes the §21 re-eval triggers enforceable, so it is mandatory, not optional; the field layout is owned by the eval-summary template.

Full eval artifacts should usually live outside the code repo. The code repo should keep concise summaries and references.

---

## 20. Cost and Latency as Eval Dimensions

For production agentic systems, cost and latency are quality attributes.

A slice can be behaviourally correct but still operationally unacceptable if it is too slow, too expensive, or too tool-call-heavy.

Where relevant, eval contracts should include:

- Maximum acceptable response latency
- Maximum acceptable number of model calls
- Maximum acceptable number of tool calls
- Maximum token budget
- Expected cost envelope
- Timeout behaviour
- Retry behaviour
- Degraded-mode behaviour

Cost or latency failures may be classified as blocking or non-blocking depending on severity and user impact, but they should be visible in eval summaries.

### 20.1 Long-Running Operations in the Shared Contract

The shared response contract — whose envelope and status vocabulary are defined in [Technical Architecture Guidelines §17](./Initial_Documentation/40.2-technical-architecture-guidelines.md#17-the-shared-contract) — is synchronous by default: validation, gates, the AI call, and persistence all complete inside one tool-call turn. A multi-step workflow or a throttled pay-as-you-go endpoint with backoff can exceed connector or turn timeouts, so the contract must also define a long-running pattern rather than letting each capability invent its own (which §20-class anti-patterns and the per-capability one-off prohibition forbid).

The contract-level rule is:

- The status vocabulary includes an **`in_progress`** status, returned when the facade has accepted the request but has not finished. An `in_progress` envelope carries an **operation ID** identifying the running operation.
- A dedicated **status-poll tool** takes the operation ID and returns the current envelope — still `in_progress`, or a terminal status (`completed`, `blocked`, `error`, and so on) once the operation resolves. The agent polls rather than blocking the original turn.
- Agents must treat `in_progress` as non-terminal: surface a "still working" message, poll on the operation ID, and never fabricate a result before a terminal status returns.

This section defines the pattern at the contract level. The facade implementation behind it — Durable Functions or the Agent Service async run API — is specified in [Technical Architecture Guidelines §40.2](./Initial_Documentation/40.2-technical-architecture-guidelines.md), not here.

---

## 21. Mandatory Re-Eval Triggers

Relevant evals must be re-run when behaviour-affecting elements change.

Mandatory re-eval triggers include:

- Model changes
- Prompt changes
- Tool schema changes
- Orchestration changes
- Workflow state logic changes
- Permissions changes
- Memory behaviour changes
- Evidence handling changes
- Any change that may materially affect agent behaviour

### 21.1 Versioned Artifact Triggering

Because "behaviour-affecting change" is judgment-heavy, the repo should use versioned artifacts wherever possible.

Examples:

```text
/prompts/prompt-manifest.json
/tools/tool-schema-version.json
/orchestration/orchestration-version.json
/evals/eval-suite-version.json
/config/model-version-policy.md
```

A change to any of these artifacts should automatically flag that relevant evals must be considered or re-run.

Not every code change requires a full eval run. Re-eval should be triggered by behaviour-affecting changes, but the trigger should be tied to concrete versioned files as much as possible.

---

## 22. Handling Eval Failures

Eval failures are severity-gated.

### 22.1 Blocking Failures

A failure blocks merge if it affects:

- Safety
- Privacy
- Evidence integrity
- Approval logic
- User trust
- Workflow state changes
- Incorrect authoritative claims
- Core agent behaviour
- Any high-risk scenario

### 22.2 Non-Blocking Failures

Low-risk failures may be accepted as non-blocking only if:

1. The agent classifies the severity.
2. The failure is documented.
3. The human release authority explicitly approves the residual risk.
4. A GitHub Issue is created.
5. Re-test criteria are defined.

Important behavioural weaknesses should become future regression evals once the desired behaviour is clarified.

### 22.3 Ambiguous Eval Failures

If an eval fails because the requirement itself is ambiguous, the slice pauses.

The coding agent must not silently guess.

The eval agent must not weaken the eval simply to make it pass.

The requirement, expected behaviour, and pass/fail criteria must be clarified before proceeding.

---

## 23. Privacy, Data Residency, and Auditability

For healthcare, public-sector, or otherwise sensitive deployments, privacy, data residency, and auditability must be first-class concerns rather than subtopics buried inside a generic security document.

### 23.1 Eval Data Governance

Eval scenarios should use synthetic or de-identified data by default.

Eval design must explicitly state whether scenarios contain:

- PHI
- PII
- Sensitive business information
- Regulated operational data
- Confidential client information

Production data should not be used in evals unless explicitly approved under a documented policy.

Eval artifacts may contain model outputs that reproduce sensitive input. Therefore, full eval artifacts require access controls, retention rules, and auditability.

### 23.2 Data Residency

The architecture guidelines should define data residency expectations for:

- Azure resources
- Foundry/model services
- Storage accounts
- Cosmos DB or other persistence layers
- Logging and telemetry
- Eval artifact storage
- Archive storage
- Backup and disaster recovery

For Canadian healthcare or public-sector work, Canadian data residency requirements should be explicitly documented and reviewed before implementation.

### 23.3 Durable Audit Archive

"Archived outside main" does not mean informal storage.

Archived slice packages, eval artifacts, screenshots, manual evidence, and approvals should live in a durable, access-controlled, auditable location.

The archive should preserve:

- Slice closeout package
- Approval evidence
- Eval summaries
- External eval artifact references
- Manual evidence
- ADRs
- Follow-up issue references
- Date and reviewer identity where applicable

The archive must be suitable for future compliance review, not merely convenient cleanup.

---

## 24. Traceability

Each slice requires traceability appropriate to its risk level.

The traceability matrix maps requirements, acceptance criteria, business rules, and agent/high-risk behaviours to the evidence that proves them (deterministic tests, live-model evals, manual evidence, external eval artifacts) and to GitHub Issues for any unresolved items; the field layout is owned by the `traceability-matrix-builder` template.

GitHub Issues should be referenced only for incomplete, deferred, failed, or unresolved items.

Fully completed requirements do not need GitHub Issue references.

### 24.1 Progressive Traceability

For early low-risk slices, traceability may start as a simple table in the closeout package.

For high-risk or regulated slices, traceability should be structured and reviewable.

The key is not bureaucratic perfection. The key is being able to answer:

```text
What requirement did we implement?
How did we prove it works?
What eval proves the agent behaves correctly?
What remains unresolved?
Who accepted the residual risk?
```

---

## 25. Documentation Reconciliation

Master documentation is updated at the end of the slice, before merge.

It should not be updated continuously based on individual commits.

The documentation agent should review the full functioning branch — code, configuration, and IaC changes; test and eval changes; manual evidence; implementation deviations; ADRs; and follow-up issues — then update the current-state master documentation to reflect what has actually been built.

The master documentation should describe the current application state, not the slice history.

---

## 26. Documentation Validation

Before merge, documentation validation must confirm that:

- Current-state docs do not contain slice-specific language.
- User-visible behaviours are accurately documented.
- Major implemented functionality is not omitted.
- Architecture docs reflect actual implementation.
- Architecture guidelines remain consistent with approved ADRs.
- Security, privacy, compliance, and audit implications are documented.
- Test/eval strategy reflects current reality.
- Known limitations are documented.
- Unresolved items are tracked in GitHub Issues.

Documentation validation blocks merge only on major mismatches.

Major mismatches include:

- False descriptions of current behaviour
- Missing major user-visible functionality
- Contradictions with architecture/security/privacy decisions
- Claims that are not supported by code, evidence, tests, or evals

Minor gaps may become follow-up issues.

---

## 27. GitHub Issues

GitHub Issues are the source of truth for unresolved work.

Agents may draft GitHub Issues, but the human release authority approves issue creation.

The initial follow-up issue types are:

```text
bug
documentation-gap
source-control-debt
eval-failure
architecture-decision-needed
security-risk
manual-config-debt
test-gap
technical-debt
enhancement
```

A single structured issue template should be used, with a required follow-up type field.

Each issue should include:

- Type
- Summary
- Context
- Reason created
- Severity
- Risk
- Acceptance criteria
- Re-test or verification criteria
- Related slice
- Related evidence
- Related docs
- Owner, if known
- Priority, if known

---

## 28. Rollback, Incident, and Hotfix Path

The normal slice process flows forward, but production systems need a path for failures.

### 28.1 Incident Response

If a merged slice breaks production or creates a serious behavioural issue:

1. Create or identify a GitHub Issue.
2. Classify the severity.
3. Decide whether to roll back, disable, patch, or hotfix.
4. Preserve evidence of the failure.
5. Run targeted deterministic tests and relevant live evals.
6. Update current-state docs if the operational behaviour changes.
7. Complete a post-incident review.

### 28.2 Hotfix Branches

Urgent fixes should use a hotfix branch.

Example:

```text
hotfix/issue-123-eval-regression
```

A hotfix may use a reduced closeout package, but it cannot ignore quality evidence.

At minimum, a hotfix requires:

- Issue reference
- Risk classification
- Implementation summary
- Targeted deterministic tests
- Targeted live evals if agent behaviour is affected
- Documentation update if current behaviour changes
- Follow-up issue for any deferred full closeout work
- Human approval

### 28.3 Retroactive Documentation

If emergency conditions require a fix before full documentation can be completed, the missing documentation must be tracked and completed through a follow-up issue.

Emergency speed does not eliminate documentation and eval obligations. It only changes the order.

---

## 29. Slice Closeout Package

Each slice branch requires a structured closeout package before merge. It assembles the slice's evidence into one reviewable whole — implementation summary, deviation log, traceability matrix, deterministic and live eval summaries (and cost/latency where relevant), manual evidence summary, ADRs and architecture-guideline updates, master documentation updates, follow-up issue summary, known residual risks, and a merge-readiness recommendation. The exact contents are owned by the `closeout-package-builder` template.

The closeout package is reviewed as a whole. Approvals follow [§31 Release Authority and Delegation](#31-release-authority-and-delegation).

---

## 30. Definition of Done

A slice is done only when the full closeout package is complete and approved.

A slice is not done merely because the code works.

A slice is done when:

- The functionality works.
- Deterministic tests pass.
- Required live-model evals pass.
- Cost and latency budgets are reviewed where relevant.
- High-risk behaviours are reviewed.
- Non-blocking failures are approved and tracked.
- Current-state documentation is updated.
- Architecture guidelines and ADRs are consistent.
- Traceability is complete for the slice risk level.
- Manual evidence is reviewed.
- Required GitHub Issues are created.
- Manual-config debt remains below the defined ceiling.
- Durable implementation lessons are promoted.
- Durable process lessons are promoted.
- Historical artifacts are archived.
- The release authority approves closeout.

---

## 31. Release Authority and Delegation

The process should not depend on a single person without a backup path.

The release authority role is responsible for approving:

- ADRs
- Architecture guideline updates
- Non-blocking eval failures
- GitHub Issue creation
- Documentation truth
- Residual risks
- Slice closeout
- Merge readiness

The project should define:

- Primary release authority
- Backup release authority
- Which decisions can be delegated
- Which decisions require explicit primary approval
- Which decisions require domain/privacy/security review

For high-risk or regulated work, residual risk approval should not be delegated casually.

Agents can recommend. Humans approve.

### 31.1 Batch Approval of Low-Severity Issue Creation

Per-item human approval of every GitHub Issue (§27) becomes the throughput bottleneck long before agent work does. The release authority therefore pre-delegates creation of low-severity issue types: agents may create `documentation-gap`, `test-gap`, and `enhancement` issues directly, each carrying a standard label (e.g. `agent-created`) that marks it as pending batch review, and the release authority reviews the whole batch at Gate 3 (closeout), where the follow-up issue summary already appears in the closeout package (§29).

Per-item human approval is still required before creating `security-risk`, `manual-config-debt`, and `eval-failure` issues; these are not delegated. This is a delegation of *which* approvals batch, not a relaxation of the recommend-never-approve rule — the release authority still owns every issue, just reviewed as a batch for the low-severity types.

---

## 32. Post-Merge Process

After a slice is approved and merged:

1. Promote durable documentation into main.
2. Archive temporary slice artifacts outside the code repo main branch.
3. Preserve current-state documentation in the code repo.
4. Preserve ADRs and architecture guideline updates in the code repo.
5. Preserve implementation lessons in the code repo.
6. Preserve process lessons in the code repo.
7. Preserve eval summary references in the code repo.
8. Preserve unresolved work in GitHub Issues.
9. Selectively update the documentation repo if the slice produced durable planning lessons.
10. Recommend the next best slice candidate using reconciled planning context.

The agent may recommend the next slice, but it should not automatically create the next slice spec without human approval.

---

## 33. Strategic Documentation Repo Reconciliation

The documentation repo will rot if completed implementation lessons never flow back into it.

At the same time, the documentation repo should not become a second current-state system of record.

The recommended rule is selective reconciliation.

### 33.1 Reconciliation Triggers

The documentation repo should be reviewed and selectively updated:

- After every few completed slices
- After a major ADR
- After a recurring deviation pattern appears
- After a material Microsoft-stack constraint is discovered
- Before major roadmap or planning work
- When slice-planning agents begin encountering stale assumptions

### 33.2 What to Update

Update the documentation repo when implementation reveals durable lessons about:

- Product direction
- Business process design
- Architecture constraints
- Microsoft-stack feasibility
- Evaluation strategy
- Data governance
- Security/privacy assumptions
- Roadmap sequencing
- Deprecated assumptions

Do not try to make the documentation repo mirror the code repo current-state docs.

---

## 34. Process Retrospectives

Implementation lessons capture technical learning. The workflow also needs process learning.

Each slice closeout should include a brief process retro.

The retro should ask:

- Was the slice the right size?
- Did the slice spec contain the right level of detail?
- Were evals defined early enough?
- Were evals too weak, too expensive, or too slow?
- Did documentation reconciliation happen cleanly?
- Did manual configuration debt increase?
- Did agents read the right context?
- Did approval gates add value or create drag?
- Should any template, prompt, checklist, or skill be changed?

Durable process lessons should be promoted into `process-lessons.md`.

---

## 35. Next-Slice Recommendation

Next-slice recommendation should use a reconciled view drawn from strategic intent, current-state docs and actual architecture, the architecture guidelines and approved ADRs, implementation and process lessons, open GitHub Issues, test/eval status, known limitations, and manual-config debt status.

The recommendation must use a balanced scoring model — weighing business value, dependency order, testability and eval readiness, technical and manual-configuration risk, architecture readiness, cost/latency risk, unresolved-issue impact, and compliance/privacy sensitivity — and must include rationale and tradeoffs.

The process should not drift into selecting a slice based on demo value alone or architecture plumbing alone. Slice sequencing should be explained through the balanced score.

---

## 36. Automation Posture

The initial posture should be semi-automated with human approval gates.

Agents may:

- Generate slice specs
- Generate evals
- Run standard scripts
- Generate reports
- Update docs
- Draft issues
- Prepare closeout packages
- Recommend next slices

Approvals follow [§31 Release Authority and Delegation](#31-release-authority-and-delegation).

The process should not start as a fully automated CI/CD governance pipeline. Automation should be added after the manual process stabilizes.

---

## 37. Agent Roles

Which roles exist, the lifecycle stages each owns, and what each produces are defined canonically in the [Skill Index §5 Agent Roles](./gentech_agent_skills_usage_and_requirements.md#5-agent-roles) table, the [Orchestration Map stage table](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table), and the role briefs under `agents/`. Role names match across all documents; this section does not restate them. The governing rule is the one that runs throughout the process: every agent role *recommends*, and the human Release Authority (§31) *approves*. No agent role approves residual risk, ADRs, documentation truth, issue creation, or merge readiness.

---

## 38. Skills and Standard Prompts

The workflow is supported by reusable skills. The authoritative skill catalogue — purpose, inputs, outputs, boundaries, execution model, and handoff for each skill — is maintained in the [Agent Skill Usage and Requirements Guide](./gentech_agent_skills_usage_and_requirements.md), and the order in which skills run is defined in the [Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md#3-stage-indexed-table). The enumerated skill list that previously lived here was removed to prevent a third copy of the skill set from drifting out of sync; consult the catalogue instead.

---

## 39. Minimum Viable Governance Before First Functional Slice

Before the first functional slice begins, create only the minimum viable governance pack.

This avoids the failure mode where the team spends weeks building templates and never validates the process against real implementation.

### Required Before First Functional Slice

The set of documents required before the first slice is maintained canonically in [§40 Additional Documents Required Prior to First Project Development](#40-additional-documents-required-prior-to-first-project-development): Source-of-Truth Policy, Technical Architecture Guidelines, Slice Specification Template, Test and Eval Strategy / Definition of Done, GitHub Issue Template, Manual Configuration Debt Policy, Release Authority Policy, and (for sensitive/regulated work) the Privacy, Data Residency, and Auditability Policy. Those documents are sufficient to begin the first functional slice; see §40 for what each must contain. The minimum *skill* set for the first slice is in the [Skill Catalogue §14](./gentech_agent_skills_usage_and_requirements.md#14-minimum-skill-set-before-first-real-project-slice).

### Created During or Immediately After Slice 1

The first slice should produce or refine:

- Current-state documentation templates
- Eval summary template
- Manual evidence template
- Deviation log template
- Closeout package template
- Lightweight traceability matrix
- Implementation lessons register
- Process lessons register
- PR checklist

### Created After the Process Stabilizes

After one or two slices, create or harden:

- Documentation reconciliation prompt
- Documentation validation prompt
- Traceability matrix builder prompt
- Eval results summarizer prompt
- Portal evidence normalizer prompt
- GitHub Issue drafting prompt
- Slice closeout builder prompt
- Next-slice recommendation prompt
- Basic automation scripts
- GitHub Actions for repeatable checks
- External artifact storage policy, if not already required by compliance

If the project operates in a healthcare, public-sector, or regulated context, the external artifact storage policy should be created earlier, before any sensitive evals or manual evidence are generated.

---

## 40. Additional Documents Required Prior to First Project Development

Prior to commencing development on the first project, create the following documents.

These are the minimum recommended documents, not the full mature documentation set.

### 40.1 Source-of-Truth Policy

Defines the context-specific authority model for the project (implementation truth, current product description, strategic intent, behavioural quality evidence, unresolved work, architecture decisions, historical evidence) — i.e. instantiates the §3 hierarchy for this project.

### 40.2 Technical Architecture Guidelines

Defines the Microsoft-stack guardrails and service mappings per §9.1: the Copilot front door and orchestration, Foundry/Power Platform/Azure usage boundaries, the memory, workflow-state, storage, and API/tool-integration patterns, identity and access control, security/privacy controls, auditability and observability, data residency expectations, and manual-configuration policy references.

### 40.3 Slice Specification Template

Defines the required structure for slice specs (owned by the `slice-spec-generator` template). It must capture the functional/business/process content listed in §12.2 and must also embed the slice sizing checks (§11.1) and split-the-slice triggers (§11.2) so every spec is sized before it proceeds.

### 40.4 Test and Eval Strategy / Definition of Done

Consolidates the testing and eval policy already defined in this document: deterministic and live-model eval expectations, the standard versus high-assurance packages (§18), the repeated-run thresholds and human-review requirements (§19.1), cost and latency budgets (§20), blocking versus non-blocking failures (§22), model/prompt/tool/orchestration version tracking and mandatory re-eval triggers (§19.2, §21), and the Definition of Done (§30).

### 40.5 GitHub Issue Template

Defines one structured issue template with a required follow-up type field. The canonical list of follow-up types is maintained in [§27 GitHub Issues](#27-github-issues); do not restate it here.

### 40.6 Manual Configuration Debt Policy

Defines the §17 policy for the project: default source-control representation expectations, when manual evidence is allowed and what it must capture, GitHub Issue requirements, the debt ceiling, and the conditions that block new feature slices (§17.3).

### 40.7 Release Authority and Delegation Policy

Defines the §31 role for the project: the primary and backup release authority, their approval responsibilities, delegation rules, the decisions requiring explicit human approval, and the decisions requiring privacy/security/domain review.

### 40.8 Privacy, Data Residency, and Auditability Policy

Required before first project development if the project may involve healthcare, public-sector, sensitive, regulated, PHI, PII, or confidential client data. It instantiates §23: eval data governance, synthetic/de-identified data expectations, production-data restrictions, Azure/Foundry data residency expectations, and audit-archive, access-control, and retention requirements.

If the first project is purely non-sensitive and exploratory, this document may start as a short policy stub and be expanded before sensitive data is introduced.

---

## 41. Mature Documentation Backlog

The following are valuable but should not block the first functional slice unless the project risk profile requires them immediately: the remaining templates (current-state docs, actual-architecture, ADR template and index, eval design and eval summary, traceability matrix, manual-evidence capture, deviation log, slice closeout, process retro); the lessons and PR-checklist registers; the reconciliation, validation, GitHub-issue-drafting, and next-slice recommendation prompts/processes; the hotfix and strategic-reconciliation checklists; and the external artifact storage policy.

These should be created progressively as the first one or two slices reveal the practical need for them.

---

## 42. Final Operating Principle

The purpose of this process is not to create documentation for its own sake.

The purpose is to ensure that every implemented slice becomes part of a trustworthy product baseline:

```text
Implemented reality is known.
Agent behaviour is evaluated.
Manual configuration is controlled.
Current-state documentation is accurate.
Unresolved work is tracked.
Historical evidence is auditable.
Future planning improves from what was learned.
```

The process should remain lightweight enough to use and strong enough to prevent agentic development from drifting into unverified, undocumented, low-code configuration chaos.
