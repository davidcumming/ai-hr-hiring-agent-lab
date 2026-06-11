# Slice Lifecycle Orchestration Map

This document is the **single source of truth** for how a slice flows through the development process: which stage runs, in what order, under which agent role, loading which skill, behind which gate. The [Process Doc](./gentech_slice_based_development_process_revised.md) owns the *rules*; the [Skills Doc](./gentech_agent_skills_usage_and_requirements.md) owns the *leaf skill specs*; this document owns the *control flow* that connects them.

> **Link conventions.** Relative markdown links are canonical (portable across Obsidian, GitHub, and raw-file agent consumers). Obsidian wikilink aliases are an optional convenience and must not be relied on for external/agent consumption. All three documents are assumed to live in the same folder. Headings are treated as an API — renaming one is a breaking change for inbound links. Links into the Skills Doc target anchors of the form `#skill-<name>` (its per-skill entry headings) and resolve today; for a skill's full spec, follow through to its `Skills/.agents/skills/<name>/SKILL.md` package, which is authoritative.

---

## 1. How to read this document

- **§2** defines the `slice-orchestrator` — the thin router skill that drives the lifecycle.
- **§3** is the stage-indexed table: one row per stage, the operational heart of this document.
- **§4** shows the control flow, including the branches and loops a linear list cannot capture.
- **§5** lists the conditional stages and their triggers.
- **§6** defines the subagent execution model referenced by every stage and every leaf skill.

A slice does **not** run every stage every time. Conditional stages (§5) fire only on their trigger. Human gates always apply.

---

## 2. The `slice-orchestrator` skill

`slice-orchestrator` is a **thin router**, not a worker. It is the "master skill" that sequences the leaf skills. It holds only the stage machine, the gates, and the routing logic — **no stage detail**. Stage detail lives in the leaf skills.

**Responsibilities**

- Track which stage the slice is in and what its entry conditions require.
- **Read and write the slice-state file.** On resume, read `docs/delivery/slices/<slice-id>/slice-state.yaml` to recover where the slice is; after every stage transition, write it back — recording the current stage, gate outcomes (each with date and approver), the risk tier, pinned versions (model/prompt/tool-schema/orchestration), open blockers, and pointers to produced artifacts. The file's structure follows the `slice-state.yaml` schema and template under `docs/delivery/slices/` (defined separately — do not inline the schema here). Persisting this state is what makes the lifecycle **resumable** (sessions end and context compacts), **auditable** (gate outcomes carry date + approver), and **portable** between Claude Code and Codex.
- Given the current state and the previous stage's output, decide the next stage to run (including conditional stages per §5).
- Dispatch each stage according to its **execution model** (§6): run inline, hand to an isolated subagent, or hand to an independent verification subagent.
- **Pause at every human gate.** The orchestrator never auto-approves, never merges, and never accepts residual risk. It surfaces the decision and stops. See Process Doc [§31 Release Authority](./gentech_slice_based_development_process_revised.md#31-release-authority-and-delegation) and [§36 Automation Posture](./gentech_slice_based_development_process_revised.md#36-automation-posture).

**Explicit non-responsibilities**

- It does not write specs, code, tests, evals, docs, or issues.
- It does not classify risk, approve failures, or resolve ambiguity that belongs to a human.
- It does not carry stage content into its own context; it loads the leaf skill (or dispatches a subagent) for that.

**Inputs:** current slice state, last stage output, gate outcomes, the stage table (§3).
**Outputs:** next-stage decision, dispatch instruction (inline / subagent / verification subagent), and the list of inputs that stage requires.

> **Topology note (pending test).** The dispatch model above assumes the orchestrator can itself spawn role subagents — i.e. that **nested subagent delegation is supported by the running tool/version**. Historically, Claude Code subagents could not spawn further subagents; if that limit applies, the orchestrator must instead run in the **main session** as a skill / slash-command that the top-level agent follows, dispatching the role subagents from there. The main-session topology is arguably preferable anyway: it keeps the human-gate context visible to the human (who must see and steer the orchestrator's context directly). The choice is pending a test on the team's current tool version and an ADR being drafted under `Initial_Documentation/adr/`.

---

## 3. Stage-indexed table

Columns: **Stage** · **Entry condition** · **Agent role** · **Skill(s) loaded** · **Required inputs (must already exist)** · **Output / gate** · **Exit handoff** · **Exec model**.

Agent roles are defined in Process Doc [§37 Agent Roles](./gentech_slice_based_development_process_revised.md#37-agent-roles). Exec model values are defined in §6 below.

| Stage | Entry condition | Agent role | Skill(s) loaded | Required inputs | Output / gate | Exit handoff | Exec model |
|---|---|---|---|---|---|---|---|
| **0 — Planning context reconciliation** | New planning cycle begins | Slice Planning | [`planning-context-reconciler`](./gentech_agent_skills_usage_and_requirements.md#skill-planning-context-reconciler) | Doc-repo intent, current-state docs, guidelines, actual arch, ADRs, lessons, known limits, issues, eval status | Reconciled planning context | → Stage 1 | inline |
| **1 — Slice sizing** | Reconciled context exists | Slice Planning | [`slice-sizer`](./gentech_agent_skills_usage_and_requirements.md#skill-slice-sizer) | Reconciled context, candidate slice | Sizing verdict: accept / split / block | Accept → Stage 2; Split → back to candidate selection | inline |
| **2 — Slice specification** | Slice accepted as one unit | Slice Planning | [`slice-spec-generator`](./gentech_agent_skills_usage_and_requirements.md#skill-slice-spec-generator) | Reconciled context, doc-repo source, guidelines, ADRs, lessons | Draft slice spec (intent, not truth) | → Stage 3 | inline |
| **3 — Slice readiness review** | Draft spec exists | Slice Planning | [`slice-readiness-reviewer`](./gentech_agent_skills_usage_and_requirements.md#skill-slice-readiness-reviewer) | Draft spec, reconciled context, guidelines, source-of-truth policy | **Gate:** ready for eval design / needs revision / blocked | Ready → Stage 4; else → Stage 2 | isolated-verification |
| **4 — Eval design** | Spec ready for eval design | Eval Design | [`eval-risk-profiler`](./gentech_agent_skills_usage_and_requirements.md#skill-eval-risk-profiler), [`eval-contract-designer`](./gentech_agent_skills_usage_and_requirements.md#skill-eval-contract-designer) | Slice spec, reconciled context, test/eval strategy, regression inventory, privacy guidance | Risk tier + hardened eval contract (incl. regression selection, cost/latency, unsafe modes, data governance) | → Stage 5 | inline |
| **5 — Implementation planning** | Eval contract hardened | Coding | [`implementation-plan-builder`](./gentech_agent_skills_usage_and_requirements.md#skill-implementation-plan-builder) | Approved spec, eval contract, guidelines, current-state docs, ADRs, test structure | Implementation + test + eval-integration plan | → Stage 6 | inline |
| **6 — Architecture compliance & ADR check** | Implementation plan exists | Coding | [`architecture-guideline-checker`](./gentech_agent_skills_usage_and_requirements.md#skill-architecture-guideline-checker), [`adr-gap-detector`](./gentech_agent_skills_usage_and_requirements.md#skill-adr-gap-detector) *(conditional)* | Plan, guidelines, ADRs, actual arch | Compliance report; **gate if ADR needed** | Clear → Stage 7; ADR needed → **pause for human** then [`architecture-guideline-updater`](./gentech_agent_skills_usage_and_requirements.md#skill-architecture-guideline-updater) | inline |
| **7 — Implementation & config capture** | Architecture clear (or ADR approved) | Coding | [`source-control-config-capture`](./gentech_agent_skills_usage_and_requirements.md#skill-source-control-config-capture), [`manual-config-evidence-capture`](./gentech_agent_skills_usage_and_requirements.md#skill-manual-config-evidence-capture) *(conditional)* | Plan, repo conventions, guidelines | Branch changes + config/IaC + manual-config evidence | → Stage 8 | inline |
| **8 — Deterministic tests** | Implementation in place | Coding | [`deterministic-test-author`](./gentech_agent_skills_usage_and_requirements.md#skill-deterministic-test-author) | Spec, eval contract, plan, existing tests | Unit/integration/workflow tests + coverage map | → Stage 9 | inline |
| **9 — Deviation capture** | Implementation diverged from spec | Coding | [`implementation-deviation-capture`](./gentech_agent_skills_usage_and_requirements.md#skill-implementation-deviation-capture) | Original spec, branch changes, ADRs, evidence | Deviation log (+ lesson/strategic-doc flags) | → Stage 10 | inline |
| **10 — Live eval execution** | Tests pass; eval contract approved | Eval Exec & Review | [`model-drift-trigger-checker`](./gentech_agent_skills_usage_and_requirements.md#skill-model-drift-trigger-checker) *(conditional)*, [`live-eval-runner`](./gentech_agent_skills_usage_and_requirements.md#skill-live-eval-runner) | Approved eval contract, scenarios or non-agentic carve-out rationale, model/prompt/tool/orchestration versions, data-governance approval | Re-eval trigger assessment if applicable; raw eval artifacts + run metadata, or documented "live eval not applicable" skip | → Stage 11 | `model-drift-trigger-checker`: inline; `live-eval-runner`: recommended-subagent |
| **11 — Eval results & failure classification** | Eval run complete, or live eval explicitly not applicable under the non-agentic carve-out | Eval Exec & Review | [`eval-result-summarizer`](./gentech_agent_skills_usage_and_requirements.md#skill-eval-result-summarizer), [`eval-failure-classifier`](./gentech_agent_skills_usage_and_requirements.md#skill-eval-failure-classifier), [`high-risk-human-review-packager`](./gentech_agent_skills_usage_and_requirements.md#skill-high-risk-human-review-packager) *(cond.)*, [`regression-promotion-recommender`](./gentech_agent_skills_usage_and_requirements.md#skill-regression-promotion-recommender) *(cond.)* | Raw artifacts or non-agentic skip rationale, eval contract, risk tier, unsafe-mode register | Eval summary + failure classification if failures exist; **gate on blocking failures**; ambiguous → pause | Pass / not applicable accepted → Stage 12; blocking → fix loop; ambiguous → human clarification | recommended-subagent (classification sanity pass: isolated-verification) |
| **12 — Current-state reconciliation** | Evals pass / accepted | Doc & Arch Reconciliation | [`current-state-reconciler`](./gentech_agent_skills_usage_and_requirements.md#skill-current-state-reconciler), [`manual-evidence-normalizer`](./gentech_agent_skills_usage_and_requirements.md#skill-manual-evidence-normalizer) *(cond.)* | Branch diff, implementation summary, evidence, test/eval summaries, ADRs, guidelines | Updated current-state docs + actual architecture | → Stage 13 | recommended-subagent |
| **13 — Documentation validation** | Docs updated | Doc & Arch Reconciliation | [`documentation-consistency-validator`](./gentech_agent_skills_usage_and_requirements.md#skill-documentation-consistency-validator) | Updated docs, branch diff, summaries, ADRs, guidelines, issues | **Gate:** pass / blocking mismatch / non-blocking gap | Pass → Stage 14; blocking → Stage 12 | isolated-verification |
| **14 — Traceability & closeout** | Docs validated | Traceability & Closeout | [`traceability-matrix-builder`](./gentech_agent_skills_usage_and_requirements.md#skill-traceability-matrix-builder), [`github-issue-drafter`](./gentech_agent_skills_usage_and_requirements.md#skill-github-issue-drafter), [`closeout-package-builder`](./gentech_agent_skills_usage_and_requirements.md#skill-closeout-package-builder) | Spec, eval contract, test/eval summaries, evidence, deviation log, ADRs, doc updates | Traceability matrix + drafted issues + closeout package | → Stage 15 | inline |
| **15 — Definition-of-done validation** | Closeout assembled | Traceability & Closeout | [`definition-of-done-validator`](./gentech_agent_skills_usage_and_requirements.md#skill-definition-of-done-validator) | Closeout package, traceability, summaries, validation report, issue summary | **Gate:** done / not done (recommendation only) | Done → Stage 16; gaps → relevant prior stage | isolated-verification |
| **16 — Human approval & merge** | DoD recommendation = done | Release Authority | *(none — human)* | Closeout package, residual-risk summary, issue drafts | **Human gate:** approve closeout, residual risk, issue creation, merge | Approved → merge → Stage 17 | human (no subagent) |
| **17 — Archive** | Merged | Traceability & Closeout | [`archive-package-preparer`](./gentech_agent_skills_usage_and_requirements.md#skill-archive-package-preparer) | Closeout package, slice folder, evidence, eval refs, doc updates, ADRs, issues | Archive manifest; durable outputs kept in main, historical artifacts archived | → Stage 18 | inline |
| **18 — Retro & lessons** | Archive prepared | Governance & Process Improvement | [`slice-retro-and-lessons`](./gentech_agent_skills_usage_and_requirements.md#skill-slice-retro-and-lessons) | Closeout package, agent/human notes, blockers, deviation log | Process retro + curated implementation lessons + curated process lessons (kept distinct) | → Stage 19 | inline |
| **19 — Strategic doc update & debt monitor** | Durable lessons or debt exist | Governance & Process Improvement | [`strategic-doc-update-recommender`](./gentech_agent_skills_usage_and_requirements.md#skill-strategic-doc-update-recommender) *(cond.)*, [`manual-config-debt-monitor`](./gentech_agent_skills_usage_and_requirements.md#skill-manual-config-debt-monitor) | Lessons, ADRs, current-state docs, debt issues, debt ceiling policy | Strategic-doc update recommendations + debt report (**may block next slice**) | → Stage 20 | inline |
| **20 — Next-slice recommendation** | Slice closed | Slice Planning | [`next-slice-recommender`](./gentech_agent_skills_usage_and_requirements.md#skill-next-slice-recommender) | Reconciled context, current-state docs, lessons, ADRs, issues, eval status, debt status | Scored candidate next slices + rationale (**human chooses**) | → human selection → Stage 0 | inline |

Process-rule anchors per stage: sizing → [§11](./gentech_slice_based_development_process_revised.md#11-slice-sizing-rules); spec → [§12](./gentech_slice_based_development_process_revised.md#12-slice-planning); eval design → [§13](./gentech_slice_based_development_process_revised.md#13-eval-driven-requirements)/[§18](./gentech_slice_based_development_process_revised.md#18-testing-and-eval-requirements)/[§19](./gentech_slice_based_development_process_revised.md#19-live-model-eval-rules)/[§20](./gentech_slice_based_development_process_revised.md#20-cost-and-latency-as-eval-dimensions)/[§23](./gentech_slice_based_development_process_revised.md#23-privacy-data-residency-and-auditability); implementation → [§16](./gentech_slice_based_development_process_revised.md#16-implementation-process); config evidence → [§17](./gentech_slice_based_development_process_revised.md#17-manual-portal-and-configuration-evidence); failures → [§22](./gentech_slice_based_development_process_revised.md#22-handling-eval-failures); reconciliation → [§25](./gentech_slice_based_development_process_revised.md#25-documentation-reconciliation); validation → [§26](./gentech_slice_based_development_process_revised.md#26-documentation-validation); traceability → [§24](./gentech_slice_based_development_process_revised.md#24-traceability); closeout → [§29](./gentech_slice_based_development_process_revised.md#29-slice-closeout-package); DoD → [§30](./gentech_slice_based_development_process_revised.md#30-definition-of-done); merge/authority → [§31](./gentech_slice_based_development_process_revised.md#31-release-authority-and-delegation); archive → [§32](./gentech_slice_based_development_process_revised.md#32-post-merge-process); retro → [§34](./gentech_slice_based_development_process_revised.md#34-process-retrospectives); strategic update → [§33](./gentech_slice_based_development_process_revised.md#33-strategic-documentation-repo-reconciliation); next slice → [§35](./gentech_slice_based_development_process_revised.md#35-next-slice-recommendation).

### 3.1 Risk-tiered collapse (lite path)

A slice does not always run all 21 stages as separate passes. The Process Doc [§5 Progressive Governance](./gentech_slice_based_development_process_revised.md#5-progressive-governance-principle) states the *rule* for which stages may merge at lower risk tiers; the table below is the *operational detail* — how the stages in §3 collapse per tier. This is a **governed lite path**, not an ad-hoc shortcut: the stages still run, they are just folded into fewer passes.

| Stage(s) in §3 | Low | Standard | High-assurance |
|---|---|---|---|
| **0–2** Planning context → sizing → spec | One planning pass (single context) | One planning pass (single context) | Three separate passes |
| **3** Slice readiness review | Folded into the Stage 16 human gate | Separate isolated-verification pass | Separate isolated-verification pass |
| **4–9** Eval design → implementation → tests → deviation | Per §3 (eval design may inline into planning if non-agentic) | Per §3 | Per §3, full rigour |
| **10–11** Live eval → results & classification | Per §3 (or non-agentic skip per §5) | Per §3 | Per §3, full rigour |
| **12–13** Current-state reconciliation → doc validation | Per §3 | Per §3 | Per §3 |
| **14–15** Traceability/closeout → definition-of-done | One closeout pass | One closeout pass | Two separate passes |
| **16** Human approval & merge | Always (full gate) | Always (full gate) | Always (full gate) |
| **17–20** Archive → retro → strategic/debt → next slice | Per §3 | Per §3 | Per §3 |

**Human gates always apply regardless of tier.** Collapsing stages changes how many *passes* the orchestrator runs and how much context each carries — it never removes a human gate. The three mandatory gates (ADR approval at Stage 6 when triggered, eval-failure clarification at Stage 11 when ambiguous, and closeout/merge at Stage 16) and the Stage 20 next-slice selection are unaffected by tier. High-assurance keeps the full, un-collapsed path. The orchestrator records the active tier in the slice-state file (§2) so the chosen collapse is auditable.

---

## 4. Control flow

A linear list hides the branches and loops that actually govern the slice. The real flow:

```text
Stage 0  Planning context reconciliation
   ↓
Stage 1  Slice sizing ──(split)──► re-select candidate ──► Stage 1
   ↓ (accept)
Stage 2  Slice specification
   ↓
Stage 3  Readiness review ──(needs revision)──► Stage 2
   ↓ (ready)
Stage 4  Eval design (risk profile + contract)
   ↓
Stage 5  Implementation planning
   ↓
Stage 6  Architecture compliance ──(ADR needed)──► [HUMAN: approve ADR] ──► guideline-updater ──► Stage 7
   ↓ (clear)
Stage 7  Implementation & config capture
   ↓
Stage 8  Deterministic tests ──(fail)──► Stage 7
   ↓ (pass)
Stage 9  Deviation capture (if diverged)
   ↓
Stage 10 Live eval execution (or explicit non-agentic skip)
   ↓
Stage 11 Eval results & failure classification
   │
   ├─(blocking failure)────► fix loop: Stage 7 / Stage 4 / Stage 2 (by cause)
   ├─(ambiguous)───────────► [HUMAN: clarify requirement] ──► re-run Stage 10
   └─(pass / accepted)
        ↓
Stage 12 Current-state reconciliation
   ↓
Stage 13 Documentation validation ──(blocking mismatch)──► Stage 12
   ↓ (pass)
Stage 14 Traceability & closeout
   ↓
Stage 15 Definition-of-done validation ──(gaps)──► relevant prior stage
   ↓ (done)
Stage 16 [HUMAN: approve closeout, residual risk, issues, merge] ──► MERGE
   ↓
Stage 17 Archive
   ↓
Stage 18 Retro & lessons
   ↓
Stage 19 Strategic doc update & debt monitor ──(debt over ceiling)──► blocks next slice until burned down
   ↓
Stage 20 Next-slice recommendation ──► [HUMAN: choose] ──► Stage 0
```

Three human gates are mandatory and the orchestrator must stop at each: ADR approval (Stage 6, conditional), eval-failure clarification (Stage 11, conditional), and closeout/merge approval (Stage 16, always). Next-slice selection (Stage 20) is also a human decision.

---

## 5. Conditional stages and triggers

| Stage / skill | Fires only when |
|---|---|
| Stage 6 — `adr-gap-detector` | Implementation hits an architecture-guideline gap or conflict. |
| Stage 6 — `architecture-guideline-updater` | An ADR has been **approved** and active guidelines must change. |
| Stage 7 — `manual-config-evidence-capture` | Portal / low-code configuration is not yet source-controllable. |
| Stage 9 — `implementation-deviation-capture` | Implementation diverged from the slice spec. |
| Stage 10 — `model-drift-trigger-checker` | Prior evals exist, a fix loop completed, or model/prompt/tool/orchestration/workflow-state/permission/memory/evidence-handling versions may have changed. |
| Stage 10 — live eval skip | The eval risk profile and eval contract explicitly document the non-agentic carve-out: no model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency. Stage 11 must summarize the rationale. |
| Stage 11 — `high-risk-human-review-packager` | High-risk eval scenarios exist (see Process Doc [§18.2](./gentech_slice_based_development_process_revised.md#18-testing-and-eval-requirements)). |
| Stage 11 — `regression-promotion-recommender` | A failure or edge case should become a future regression eval. |
| Stage 12 — `manual-evidence-normalizer` | Manual evidence exists and must enter closeout. |
| Stage 19 — `strategic-doc-update-recommender` | Durable lessons should flow back to the documentation repo. |

---

## 6. Subagent execution model

Defined once here; every leaf skill references it via a one-line `Execution model` field rather than repeating the guidance. Three values:

- **`inline`** — run in the current context. Default for lightweight, low-context skills and any stage inside an interactive human loop.
- **`recommended-subagent`** — dispatch to an isolated subagent when the stage is heavy-context or parallelizable, so its large working context (diffs, eval logs, drafts) is discarded on return and only the artifact comes back. Applies to live eval execution (Stage 10), eval result handling (Stage 11), current-state reconciliation (Stage 12), and the controlled-parallelism slices in Process Doc [§15](./gentech_slice_based_development_process_revised.md#15-parallel-work-and-dependency-model).
- **`isolated-verification`** — must run as an **independent** subagent that did not produce the artifact it checks. Applies to readiness review (Stage 3), documentation validation (Stage 13), definition-of-done validation (Stage 15), and the failure-classification sanity pass (Stage 11).

**Where subagents are explicitly wrong:** human-approval gates (Stages 6, 16) and the ambiguous-eval-failure clarification loop (Stage 11), where the human must see and steer the context directly. The orchestrator runs these inline and pauses.

### 6.1 Mapping to tool-native isolation

The three execution models above are enforced by the tools' own isolation features, not by operator memory. The mapping (declared in each skill's `SKILL.md` frontmatter, which is added separately — only the mapping is documented here):

| Execution model (§6) | Claude Code | Codex |
|---|---|---|
| **`recommended-subagent`** | Declare `context: fork` in SKILL.md frontmatter — the skill runs in a forked, isolated context so its heavy working set is discarded on return. | Equivalent isolated run (the skill runs in its own isolated session/context). |
| **`isolated-verification`** | Declare `context: fork` — the verification skill runs in an independent context that did not produce the artifact. | Equivalent isolated run, dispatched on an independent pass. |
| **`inline`** | Declare nothing — runs in the current context. | Declare nothing — runs in the current context. |

With the isolation declared in frontmatter, the tool enforces the boundary; the orchestrator does not have to remember to fork. This keeps §6's `recommended-subagent` / `isolated-verification` / `inline` values consistent with what the tool actually does at dispatch time.

---

## 7. Paths outside the forward lifecycle

Stages 0–20 are the forward path for building a new slice. Two governed activities sit outside that path and are intentionally not stages in the table above:

- **Incident, rollback, and hotfix.** When something breaks in production, follow [Process Doc §28](./gentech_slice_based_development_process_revised.md#28-rollback-incident-and-hotfix-path), not the forward lifecycle. A hotfix branches from the released state, fixes the issue under a human-approved merge (the §16-equivalent gate still applies — a human approves the merge), and then **reconciles documentation and evals retroactively** (§28.3) so the current-state docs and the evidence trail catch up. The orchestrator does not auto-run this; a human drives it.
- **Cross-slice strategic reconciliation.** Stage 19 handles per-slice strategic-doc updates. The broader cadence — reviewing the documentation repo "after every few slices," after a major ADR, or when planning agents start hitting stale assumptions — is governed by [Process Doc §33](./gentech_slice_based_development_process_revised.md#33-strategic-documentation-repo-reconciliation) and runs between slices, not within one.
