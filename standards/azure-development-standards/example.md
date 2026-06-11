# Worked Example — Using the Agents, Skills, and Process on a Real Project (Claude Code)

This is an **educational walkthrough**. It shows, concretely, how you would build a real project with this system: which agent you talk to at each step, how you put that agent into a role, and how you force the exact skill to run from inside your prompt. It is written for **Claude Code**; the Codex equivalent (attaching the same role files as prompts) you can derive yourself.

> **Where this fits the standards.** This repo's rules are split across the **three-document model** that [`AGENTS.md`](./AGENTS.md) points into: the [Process Doc](./gentech_slice_based_development_process_revised.md) holds the rules and gates, the [Skill Usage Guide](./gentech_agent_skills_usage_and_requirements.md) is the skill catalogue, and the [Orchestration Map](./gentech_slice_lifecycle_orchestration_map.md) is the lifecycle control flow. This worked example is *not* a fourth source of truth — where it summarizes a stage or a threshold, those three documents win. The lifecycle has **21 stages, numbered 0–20**.

The example project is **QuickTodo**, a full-stack web todo app. We set up the repos, decide what to store initially, write the first prompt, and run **three full slices**:

- **Slice 1** — create a todo and see it in a list (plain CRUD; deterministic-only under the formal non-agentic carve-out).
- **Slice 2** — mark a todo complete and filter the list (small delta; shows re-eval/regression).
- **Slice 3** — natural-language "quick add" (an LLM parses "buy milk tomorrow" into a structured todo; this is the *agentic* slice and shows why the live-eval machinery exists).

> The prompts here don't need to be perfect or actually compile — they exist to teach the *pattern*: **assign a role → force a skill → respect the human gate.**

---

## 0. The mental model: two layers in every prompt

Every working prompt you send does two things explicitly:

1. **Assign the role** — you tell Claude Code which subagent to use. The subagent's file in `.claude/agents/` becomes its system prompt, so it inherits that role's mission, boundaries, and tool set. Pattern: `Use the <agent-name> subagent.`
2. **Force the skill** — you name the exact skill the agent must follow. Each `SKILL.md` now opens with YAML frontmatter (`name`, `description`, and an optional `context: fork`), so Claude Code can auto-discover and trigger it by name. You can therefore name the skill (`Have it follow the <skill-name> skill …`) or, for maximum explicitness, point at the full path (`Have it follow .claude/skills/<skill-name>/SKILL.md to <task>.`). Either way the point is the same: you decide the skill, rather than relying on Claude to *choose* one. This guide forces by path throughout so the mapping is unambiguous.

Then a third thing happens at certain stages: **you stop and approve** (the human gate). Agents recommend; you approve ADRs, residual risk, issue creation, and merges.

That's the whole loop. Everything below is that loop repeated, stage by stage.

> **Manual vs. orchestrated.** This guide drives every stage **manually** (you name the agent and skill each time) because you asked for explicit control and because it's the best way to learn. Once it's second nature, you can instead hand the whole slice to the `slice-orchestrator` — a **thin router** that holds only the stage machine, the gates, and the routing logic (no stage detail of its own). It ships as *both* a role file (`agents/slice-orchestrator.md`) and a skill package (`slice-orchestrator/SKILL.md`). It reads and writes a per-slice `slice-state.yaml` so a slice is **resumable** across sessions and **auditable** (every gate outcome carries a date and approver). One prompt — `Use the slice-orchestrator to drive slice 002 end to end, pausing at every human gate` — and it dispatches the role agents and skills for you. Start manual.
>
> **Orchestrator topology (pending test).** Whether the orchestrator runs as a *subagent* (spawning the role agents) or as a *skill/slash-command in the main session* depends on whether your tool version supports nested subagent delegation. The main-session form is arguably preferable because it keeps the human-gate context visible to you. This is pending a test and an ADR; until then, running it in the main session is the safe default. See [Orchestration Map §2](./gentech_slice_lifecycle_orchestration_map.md#2-the-slice-orchestrator-skill).

---

## 1. One-time setup (before any slice)

### 1.1 Create two repositories

The process separates *strategic/aspirational* material from the *clean implementation*:

- **`quicktodo-docs/`** — the **documentation repo**. Rich, messy, forward-looking: product vision, requirements, user journeys, roadmap. Informs slices but is **not** the record of what's built.
- **`quicktodo/`** — the **code repo**. The clean implementation plus current-state docs, architecture, ADRs, delivery records, and (vendored) the standards themselves.

Keep them as sibling folders so the code repo can read `../quicktodo-docs/`.

### 1.2 What to store initially in `quicktodo-docs/`

Only strategic intent — no implementation:

```text
quicktodo-docs/
  product-vision.md          # "A fast, keyboard-first todo app for individuals."
  business-requirements.md   # goals, success measures
  functional-requirements.md # capabilities we eventually want
  user-journeys.md           # how a user adds/completes/organizes todos
  roadmap.md                 # rough sequence of capabilities
```

### 1.3 What to store initially in `quicktodo/`

Before slice 1 you create only the **standards**, the **minimum viable governance** docs, and the empty skeleton — **not** the app itself (the app is built in slice 1). This is the progressive-governance principle: don't build the whole factory before proving it makes software.

**Install the standards instead of hand-copying them.** You don't paste 33 skill folders and 8 role files by hand. The standards repo ships an idempotent installer that syncs the canonical source into the exact locations each tool scans:

```text
# from the standards repo, pointing at your project
scripts/install.sh ../quicktodo          # symlink (default) — stays live with the standards
scripts/install.sh ../quicktodo --copy   # vendor a frozen snapshot instead
```

It installs the **33 skill packages** (canonical source: `Skills/.agents/skills/<skill-name>/`) and the **8 role files** (`agents/`) into:

- `.claude/skills/` and `.claude/agents/` — where **Claude Code** discovers them.
- `.agents/skills/` — where **Codex** discovers them.

Each skill is a *package*, not a lone file: `SKILL.md` (authoritative spec, opening with `name` / `description` / optional `context: fork` frontmatter) plus a `templates/` file where the skill produces a document and, where it encodes scoring or classification policy, a `rubrics/` file. When you move a skill, you move the whole directory. After running the installer your project looks like this:

```text
quicktodo/
  CLAUDE.md                                  # tells Claude how to operate (see 1.5)
  .claude/
    agents/                                  # the 8 role files (installed from the standards)
      slice-orchestrator.md                  # thin router (also ships as a skill below)
      slice-planning-agent.md
      eval-design-agent.md
      coding-agent.md
      eval-execution-and-review-agent.md
      documentation-and-architecture-reconciliation-agent.md
      traceability-and-closeout-agent.md
      governance-and-process-improvement-agent.md
    skills/                                  # the 33 skill packages (each a directory)
      slice-orchestrator/SKILL.md            # the master router skill (drives the lifecycle)
      planning-context-reconciler/           # SKILL.md + templates/ (+ rubrics/ where used)
      slice-sizer/
      slice-spec-generator/
      slice-readiness-reviewer/
      eval-risk-profiler/
      eval-contract-designer/
      implementation-plan-builder/
      architecture-guideline-checker/
      adr-gap-detector/
      deterministic-test-author/
      source-control-config-capture/
      manual-config-evidence-capture/
      implementation-deviation-capture/
      model-drift-trigger-checker/
      live-eval-runner/
      eval-result-summarizer/
      eval-failure-classifier/
      high-risk-human-review-packager/
      regression-promotion-recommender/
      current-state-reconciler/
      manual-evidence-normalizer/
      documentation-consistency-validator/
      architecture-guideline-updater/
      traceability-matrix-builder/
      github-issue-drafter/
      closeout-package-builder/
      definition-of-done-validator/
      archive-package-preparer/
      slice-retro-and-lessons/
      strategic-doc-update-recommender/
      manual-config-debt-monitor/
      next-slice-recommender/
  standards/                                 # the three governance docs + AGENTS.md (reference)
    AGENTS.md
    gentech_slice_based_development_process_revised.md
    gentech_agent_skills_usage_and_requirements.md
    gentech_slice_lifecycle_orchestration_map.md
  docs/
    governance/                              # the 7 MVG docs (see 1.4)
      source-of-truth.md
      technical-architecture-guidelines.md
      slice-spec-template.md
      test-eval-strategy-and-dod.md
      github-issue-template.md
      manual-config-debt-policy.md
      release-authority-policy.md
    product-current-state/                   # empty for now; filled by reconciliation
    architecture/
      technical-architecture-guidelines.md   # (or symlink to governance copy)
      actual-technical-architecture.md       # empty for now
      adr-index.md
      adrs/
    delivery/
      slices/                                # per-slice working artifacts land under slices/<slice-id>/
      implementation-lessons.md
      process-lessons.md
  .github/ISSUE_TEMPLATE/
```

> **Why an installer rather than one source folder.** The canonical packages live under `Skills/.agents/skills/` in the standards repo — the *portable source form* both tools can vendor. But Claude Code discovers skills under `.claude/skills/` and Codex under `.agents/skills/`, so the installer syncs the same set into each. Auto-discovery (via the `SKILL.md` frontmatter) means you no longer *have* to force a skill by full path — naming it is enough — but this guide forces by path anyway so the stage-to-skill mapping stays unambiguous. (A proposal to un-hide the canonical `Skills/.agents/skills/` source folder is tracked as ADR-0005; the installer is the interim bridge.)

### 1.4 Create the minimum viable governance docs first

Per the process (§40), before slice 1 you author seven short docs. You can do this with Claude too — but they're policy, so you write/approve them as the human. They are: **Source-of-Truth Policy**, **Technical Architecture Guidelines** (for QuickTodo: React + TypeScript front end, Node/Express + TypeScript API, Postgres, Vitest for tests; later an LLM provider for the agentic feature), **Slice Specification Template**, **Test & Eval Strategy / Definition of Done**, **GitHub Issue Template**, **Manual-Config Debt Policy**, **Release Authority Policy** (for a solo project: you are primary release authority).

### 1.5 Seed `CLAUDE.md` so Claude operates the right way

`CLAUDE.md` is the one file Claude Code reads automatically for project context. Keep it short and point at the standards:

```markdown
# QuickTodo — how to work here

This project follows the slice-based standards in `standards/`. Read `standards/AGENTS.md`
first — it points into the three-document model (Process Doc, Skill Usage Guide, Orchestration Map).

- The lifecycle (21 stages, 0–20), stage order, gates, and which agent/skill runs each stage are
  defined in `standards/gentech_slice_lifecycle_orchestration_map.md`.
- Always operate one stage at a time. I (the human) will name the subagent and the skill
  to use in each prompt. Do not skip ahead or pick a different skill.
- Per-slice working artifacts live under `docs/delivery/slices/<slice-id>/`. The orchestrator
  tracks progress in `docs/delivery/slices/<slice-id>/slice-state.yaml` — read it to resume.
- Treat slice specs as intent, not truth. Current-state docs must stay slice-agnostic.
- STOP and ask for my approval at every human gate: ADR approval, residual-risk acceptance,
  GitHub issue creation, and any merge. Never merge on your own.
```

### 1.6 One concept before we build: risk tiers and the lite path

The lifecycle has 21 stages, but a slice does **not** run all 21 as separate passes. Stage 4's `eval-risk-profiler` assigns a **risk tier** — *low*, *standard*, or *high-assurance* — and the tier decides how much machinery turns on and how many of the stages collapse into single passes (the **governed "lite path"**, Orchestration Map §3.1):

- **Low / standard** — planning stages 0–2 fold into one pass; readiness review (Stage 3) may fold into the Stage 16 human gate at low risk; traceability + DoD (14–15) run as one closeout pass. QuickTodo slices 1 and 2 sit here.
- **High-assurance** — the full, un-collapsed path with adversarial evals, larger run counts, and stronger thresholds. QuickTodo's slice 3 (an LLM feature) escalates toward this.

Collapsing passes never removes a human gate. The three mandatory gates — ADR approval (Stage 6, if triggered), ambiguous eval-failure clarification (Stage 11, if triggered), and closeout/merge (Stage 16, always) — fire regardless of tier, and the orchestrator records the active tier in `slice-state.yaml` so the chosen collapse is auditable. The risk profiler is the switch; the rest of this guide shows it flipped low (slices 1–2) and high (slice 3).

That's setup. Now we build.

---

## 2. Slice 1 — "Create a todo and see it in a list"

### The first prompt — Stage 0: reconcile planning context

**Agent:** Slice Planning · **Skill:** `planning-context-reconciler`

**You type:**

```text
Use the slice-planning-agent subagent.
Have it follow .claude/skills/planning-context-reconciler/SKILL.md.

Task: produce a reconciled planning context for QuickTodo's FIRST slice.
Read from:
  - ../quicktodo-docs/ (product-vision, business/functional-requirements, user-journeys, roadmap)
  - docs/product-current-state/ (currently empty — note that nothing is built yet)
  - docs/architecture/technical-architecture-guidelines.md
  - docs/governance/source-of-truth.md
Write the reconciled context to docs/delivery/slices/slice-001/planning-context.md.
Do not write code or a slice spec yet.
```

**What you get back:** a `planning-context.md` that separates what's already built (nothing), what's aspirational, what the architecture allows, and candidate first-slice areas. Because the subagent is the *planning* role, it won't touch code.

### Stage 1: size the candidate slice

**Agent:** Slice Planning · **Skill:** `slice-sizer`

**You type:**

```text
Use the slice-planning-agent subagent.
Have it follow .claude/skills/slice-sizer/SKILL.md.

Candidate slice: "A user can create a todo (title only) and see it in a list."
Inputs: docs/delivery/slices/slice-001/planning-context.md.
Decide accept-as-one-slice / split / block, with rationale.
Write the verdict to docs/delivery/slices/slice-001/sizing.md.
```

**Result:** verdict = *accept*. One user-visible capability, one branch, one eval set. (If you'd proposed "create, edit, delete, complete, tag, and share todos," the skill would tell you to split.)

### Stage 2: write the slice spec

**Agent:** Slice Planning · **Skill:** `slice-spec-generator`

**You type:**

```text
Use the slice-planning-agent subagent.
Have it follow .claude/skills/slice-spec-generator/SKILL.md and the structure in
docs/governance/slice-spec-template.md.

Produce the slice spec for slice 001 (create + list todos).
Emphasize user/process behaviour and acceptance criteria; minimal implementation detail.
Include: business outcome, acceptance criteria, agent/no-agent behaviours, required deterministic
tests, out-of-scope (no edit/delete/complete yet), and open questions.
Write to docs/delivery/slices/slice-001/slice-spec.md.
```

**Result:** a spec like — *Outcome:* user can add a titled todo and see it persist in a list. *Acceptance criteria:* POST creates a todo; GET returns todos newest-first; empty title rejected; list survives refresh. *Out of scope:* completion, editing, deletion.

### Stage 3: independent readiness review (a verification gate)

**Agent:** Slice Planning · **Skill:** `slice-readiness-reviewer` (run as a **fresh** invocation — it's independent verification)

**You type:**

```text
Use the slice-planning-agent subagent as a FRESH reviewer (do not reuse the drafting context).
Have it follow .claude/skills/slice-readiness-reviewer/SKILL.md.

Independently review docs/delivery/slices/slice-001/slice-spec.md against the planning context and
docs/architecture/technical-architecture-guidelines.md.
Decide: ready-for-eval-design / needs-revision / blocked, with required fixes.
Write to docs/delivery/slices/slice-001/readiness.md.
```

**Result:** *ready* (or a short fix list you loop back on). This is the first place the "verification runs separately from authoring" idea shows up. In the Orchestration Map this is the `isolated-verification` execution model — and the skill enforces it for you: `slice-readiness-reviewer/SKILL.md` carries `context: fork` in its frontmatter, so Claude Code runs it in a fresh, isolated context that did not produce the spec. Saying "as a FRESH reviewer" in the prompt is the manual reinforcement of what the frontmatter already guarantees. (At *low* risk this stage may instead fold into the Stage 16 human gate per the lite path; QuickTodo runs it separately to show the pattern.)

### Stage 4: design the evals BEFORE coding

**Agent:** Eval Design · **Skills:** `eval-risk-profiler`, then `eval-contract-designer`

**You type (two skills, in order):**

```text
Use the eval-design-agent subagent.

Step 1 — have it follow .claude/skills/eval-risk-profiler/SKILL.md to produce the risk profile
for slice 001. Write to docs/delivery/slices/slice-001/eval-risk-profile.md.

Step 2 — have it follow .claude/skills/eval-contract-designer/SKILL.md to produce the eval
contract: deterministic test expectations, pass/fail criteria, and which regression evals (none
yet — this is slice 1). Write to docs/delivery/slices/slice-001/eval-contract.md.
```

**Result — and an important lesson:** the risk profiler classifies slice 1 as **standard / low** and the eval contract explicitly documents the **non-agentic carve-out**: no model, prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency. Stage 10 live eval execution is therefore not applicable, and Stage 11 must summarize that rationale beside the deterministic test results. Not every slice needs the heavy machinery; the risk profile and eval contract are what prove that. (Slice 3 will be different.)

### Stages 5–9: implement, on a feature branch

**Agent:** Coding · **Skills:** `implementation-plan-builder`, `architecture-guideline-checker`, `adr-gap-detector` (conditional), `deterministic-test-author`, `source-control-config-capture`, `implementation-deviation-capture` (conditional)

**5 — plan. You type:**

```text
Use the coding-agent subagent.
Have it follow .claude/skills/implementation-plan-builder/SKILL.md to turn
docs/delivery/slices/slice-001/slice-spec.md and eval-contract.md into a coding plan.
Constraints: obey docs/architecture/technical-architecture-guidelines.md (React+TS, Express+TS, Postgres, Vitest).
Create branch feature/slice-001-create-list-todos.
Write the plan to docs/delivery/slices/slice-001/impl-plan.md.
```

**6 — architecture compliance (and stop if a gap appears). You type:**

```text
Use the coding-agent subagent.
Have it follow .claude/skills/architecture-guideline-checker/SKILL.md to check the plan against
docs/architecture/technical-architecture-guidelines.md.
If you find a gap or conflict, follow .claude/skills/adr-gap-detector/SKILL.md, write a proposed
ADR to docs/architecture/adrs/, and STOP for my approval. Do not invent a new pattern on your own.
```

> **Human gate (conditional).** If an ADR is raised, you review and approve/reject it. If approved, you'd run the `documentation-and-architecture-reconciliation-agent` with `architecture-guideline-updater` to fold the decision into the guidelines, *then* resume. For slice 1, assume no gap.

**7–8 — implement + tests. You type:**

```text
Use the coding-agent subagent.
Implement slice 001 on feature/slice-001-create-list-todos per docs/delivery/slices/slice-001/impl-plan.md
(Express routes POST /todos and GET /todos, Postgres table, React list + add form).
Then follow .claude/skills/deterministic-test-author/SKILL.md to add unit + integration tests
mapped to each acceptance criterion in the slice spec.
Then follow .claude/skills/source-control-config-capture/SKILL.md to make sure DB schema/migration
and any config are represented in source control (no portal-only setup).
```

**9 — capture deviations (if any). You type:**

```text
Use the coding-agent subagent.
If the implementation diverged from the slice spec in any way, follow
.claude/skills/implementation-deviation-capture/SKILL.md and log it to
docs/delivery/slices/slice-001/deviations.md. If there were no deviations, say so explicitly.
```

### Stages 10–11: run and review evals

**Agent:** Eval Execution and Review · **Skill:** `eval-result-summarizer` (live eval not applicable under the non-agentic carve-out)

**You type:**

```text
Use the eval-execution-and-review-agent subagent.
Run the deterministic test suite (npm test / vitest).
Then follow .claude/skills/eval-result-summarizer/SKILL.md to write a concise summary
(pass/fail counts, coverage of acceptance criteria, versions) to docs/delivery/slices/slice-001/eval-summary.md.
Per the risk profile and eval contract, live eval is not applicable because the slice has no model,
prompt, tool-orchestration, agent behaviour, or behaviour-affecting model dependency. Record that
rationale explicitly in the eval summary.
```

**Result:** tests pass; summary written. If a test failed, you'd add `eval-failure-classifier` here to decide blocking vs. non-blocking.

### Stages 12–13: reconcile documentation, then validate it

**Agent:** Documentation and Architecture Reconciliation · **Skills:** `current-state-reconciler`, then `documentation-consistency-validator` (fresh)

**You type (reconcile):**

```text
Use the documentation-and-architecture-reconciliation-agent subagent.
Have it follow .claude/skills/current-state-reconciler/SKILL.md:
analyze the full diff of feature/slice-001-create-list-todos vs main, then update
docs/product-current-state/ and docs/architecture/actual-technical-architecture.md to describe
what the app NOW does. Keep it slice-agnostic — describe behaviour, not "slice 1 added…".
```

**You type (validate — fresh invocation):**

```text
Use the documentation-and-architecture-reconciliation-agent subagent as a FRESH validator.
Have it follow .claude/skills/documentation-consistency-validator/SKILL.md to check the updated
current-state docs against the code/tests/evidence. Report pass / blocking-mismatch / non-blocking-gap
to docs/delivery/slices/slice-001/doc-validation.md.
```

### Stages 14–15: traceability and closeout

**Agent:** Traceability and Closeout · **Skills:** `traceability-matrix-builder`, `github-issue-drafter`, `closeout-package-builder`, then `definition-of-done-validator` (fresh)

**You type:**

```text
Use the traceability-and-closeout-agent subagent.
1) Follow .claude/skills/traceability-matrix-builder/SKILL.md → docs/delivery/slices/slice-001/traceability.md
   (map each acceptance criterion to the test/evidence that proves it).
2) Follow .claude/skills/github-issue-drafter/SKILL.md to DRAFT issues for anything unresolved
   (draft only — do not create them).
3) Follow .claude/skills/closeout-package-builder/SKILL.md → docs/delivery/slices/slice-001/closeout.md
   with a merge-readiness recommendation.
Then, as a FRESH invocation, follow .claude/skills/definition-of-done-validator/SKILL.md →
docs/delivery/slices/slice-001/dod.md (done / not-done recommendation).
```

### Stage 16: the human gate — you approve and merge

No subagent here. **You** read `closeout.md` and `dod.md`, then act:

```text
I've reviewed the closeout and DoD. Approved. Create the drafted GitHub issues, then merge
feature/slice-001-create-list-todos into main.
```

This is the line agents won't cross on their own. Approving residual risk, creating issues, and merging are yours.

### Stages 17–19: archive, retro, debt

**You type (archive):**

```text
Use the traceability-and-closeout-agent subagent.
Follow .claude/skills/archive-package-preparer/SKILL.md to move slice-001 historical artifacts
out of main (to the archive location) and list which durable outputs stay in main.
```

**You type (retro + lessons + debt):**

```text
Use the governance-and-process-improvement-agent subagent.
1) Follow .claude/skills/slice-retro-and-lessons/SKILL.md → a short retro plus durable lessons,
   appended to docs/delivery/implementation-lessons.md and process-lessons.md (keep the two distinct).
2) Follow .claude/skills/manual-config-debt-monitor/SKILL.md → a debt report; tell me if anything
   would block the next slice.
```

### Stage 20: what next?

**You type:**

```text
Use the slice-planning-agent subagent.
Follow .claude/skills/next-slice-recommender/SKILL.md to score and recommend the next slice.
Present me the top options with rationale; I'll choose.
```

**Result:** it recommends, you pick. Slice 1 is done — and notice you invoked **six different role agents** and named the skill every single time. Claude never *chose* a skill.

---

## 3. Slice 2 — "Mark a todo complete and filter the list" (the deltas)

Same lifecycle. Rather than repeat all 21 stages (0–20), here is what *changes* the second time around — which is most of what you actually need to learn.

**Planning now reads real current-state docs.** Stage 0's prompt is identical, but the planning context is richer because `docs/product-current-state/` is no longer empty:

```text
Use the slice-planning-agent subagent.
Have it follow .claude/skills/planning-context-reconciler/SKILL.md to reconcile context for slice 002
("mark complete + filter"). This time read docs/product-current-state/ (now populated) and the slice-001
implementation lessons. Write to docs/delivery/slices/slice-002/planning-context.md.
```

**Eval design adds a re-eval/regression step.** Because slice 2 changes existing behaviour (the list now has a completion state and a filter), you explicitly invoke the drift check and make sure slice-1's tests are selected as regression:

```text
Use the eval-execution-and-review-agent subagent.
Before running new tests, follow .claude/skills/model-drift-trigger-checker/SKILL.md to decide what
must be re-run given slice-002's changes. Then run slice-002 tests PLUS the slice-001 regression tests.
Summarize with .claude/skills/eval-result-summarizer/SKILL.md → docs/delivery/slices/slice-002/eval-summary.md.
```

If a slice-1 test now fails (e.g., the list ordering changed), you'd add:

```text
Use the eval-execution-and-review-agent subagent.
Follow .claude/skills/eval-failure-classifier/SKILL.md on the failing test: blocking or non-blocking?
If a behaviour genuinely changed on purpose, follow .claude/skills/regression-promotion-recommender/SKILL.md
to recommend updating the regression scenario. Recommend only — I approve changes.
```

**Closeout is smaller.** A low-risk delta slice still goes through traceability → closeout → DoD → human approval → merge → archive → retro, but the packages are lighter. The *shape* is identical; you reuse the slice-1 prompts with `slice-002` paths.

**The point of slice 2:** the framework isn't heavier the second time — most stages are the same prompts with new paths, plus the explicit re-eval/regression handling that protects what you already shipped.

---

## 4. Slice 3 — "Natural-language quick add" (the agentic slice)

Now a user can type *"buy milk tomorrow"* and an LLM turns it into `{ title: "buy milk", dueDate: <tomorrow> }`. This is where the eval machinery earns its keep — and where the prompts differ most.

**Sizing/spec note it's agentic.** The slice spec must define *agent behaviour* and *unacceptable outputs* (e.g., must not invent a due date that wasn't implied; must not drop the task entirely).

**Eval design escalates the risk tier and REQUIRES live-model evals:**

```text
Use the eval-design-agent subagent.
Step 1 — follow .claude/skills/eval-risk-profiler/SKILL.md for slice 003 (LLM parses free text into a
structured todo). Expect a higher tier: user-facing model output that creates real data.
Identify unsafe failure modes (hallucinated dates, dropped tasks, wrong field mapping) and any
PHI/PII/data-residency concerns for the text sent to the model. Write to docs/delivery/slices/slice-003/eval-risk-profile.md.
Step 2 — follow .claude/skills/eval-contract-designer/SKILL.md to define LIVE-MODEL eval scenarios:
inputs like "buy milk tomorrow", "call dentist Friday 3pm", "" (empty), "asdfgh" (garbage);
expected structured outputs; pass threshold per Process §19.1 (Standard: 5-10 runs at >=80%; High-risk: 20+ runs at >=90% and zero critical failures);
repeated-run count; and which deterministic tests still apply. Write to docs/delivery/slices/slice-003/eval-contract.md.
```

**Coding is the same role, but the deterministic-test step is now joined by live evals at stages 10–11:**

```text
Use the eval-execution-and-review-agent subagent.
1) Follow .claude/skills/live-eval-runner/SKILL.md to run the live-model eval scenarios from
   docs/delivery/slices/slice-003/eval-contract.md against the configured model, recording model/prompt
   versions and keeping full artifacts external. Run the required number of repeats.
2) Follow .claude/skills/eval-result-summarizer/SKILL.md → docs/delivery/slices/slice-003/eval-summary.md.
3) Follow .claude/skills/eval-failure-classifier/SKILL.md on any miss (e.g., a wrong date) to decide
   blocking vs non-blocking.
```

**A new human-review packaging step appears because the tier is high:**

```text
Use the eval-execution-and-review-agent subagent.
Follow .claude/skills/high-risk-human-review-packager/SKILL.md to assemble the live-eval results,
unsafe-failure findings, and decision points into docs/delivery/slices/slice-003/human-review.md for my sign-off.
```

**Then the human gate is heavier.** You don't just approve a merge — you accept (or reject) the residual behavioural risk of an LLM feature, using that review package. Everything after (reconcile docs, traceability, closeout, DoD, archive, retro) follows the slice-1 pattern.

**The lesson of slice 3:** the *same* agents and the *same* prompt grammar scale up to an agentic feature simply by forcing the eval-design and eval-execution skills that slices 1–2 skipped. The risk profiler is the switch that decides which machinery turns on.

---

## 5. Cheat sheet — the prompt patterns

**Assign a role (every working prompt):**

```text
Use the <agent-name> subagent.
```

**Force a skill (every working prompt) — by name or by path:**

```text
Have it follow the <skill-name> skill to <task>.                        # name (frontmatter auto-discovers it)
Have it follow .claude/skills/<skill-name>/SKILL.md to <task>.          # full path (maximally explicit)
Write output to docs/delivery/slices/slice-NNN/<file>.md.
```

**Run a verification skill independently (the `isolated-verification` skills — readiness review, doc validation, DoD — carry `context: fork`, so the fork is automatic; the "FRESH" wording just reinforces it):**

```text
Use the <agent-name> subagent as a FRESH reviewer (don't reuse the drafting context).
Have it follow .claude/skills/<validator-skill>/SKILL.md ...
```

**Chain two skills in one role:**

```text
Use the <agent-name> subagent.
Step 1 — follow .claude/skills/<skill-a>/SKILL.md ...
Step 2 — follow .claude/skills/<skill-b>/SKILL.md ...
```

**Respect a human gate (you act, no subagent):**

```text
I've reviewed <closeout/ADR/review package>. Approved. <create issues / merge / accept risk>.
```

**Hand off to the next stage:** just send the next prompt naming the next agent + skill. The Orchestration Map's stage table tells you what comes next.

**Once fluent, let the orchestrator drive** (it reads/writes `slice-state.yaml` so the slice is resumable and the gate outcomes are auditable; run it in the main session if your tool version doesn't support nested subagents):

```text
Use the slice-orchestrator to drive slice 004 end to end. Track state in
docs/delivery/slices/slice-004/slice-state.yaml. Dispatch the correct role agent and skill for each
stage per the Orchestration Map, collapse stages per the slice's risk tier, and STOP at every human
gate for my approval.
```

---

## Quick reference — which agent owns which stage

| Stage(s) | Agent | Representative skills you force |
|---|---|---|
| 0–3, 20 | `slice-planning-agent` | planning-context-reconciler, slice-sizer, slice-spec-generator, slice-readiness-reviewer, next-slice-recommender |
| 4 | `eval-design-agent` | eval-risk-profiler, eval-contract-designer |
| 5–9 | `coding-agent` | implementation-plan-builder, architecture-guideline-checker, adr-gap-detector, deterministic-test-author, source-control-config-capture, implementation-deviation-capture |
| 10–11 | `eval-execution-and-review-agent` | live-eval-runner, eval-result-summarizer, eval-failure-classifier, high-risk-human-review-packager, model-drift-trigger-checker, regression-promotion-recommender |
| 12–13 | `documentation-and-architecture-reconciliation-agent` | current-state-reconciler, documentation-consistency-validator, manual-evidence-normalizer, architecture-guideline-updater |
| 14–15, 17 | `traceability-and-closeout-agent` | traceability-matrix-builder, github-issue-drafter, closeout-package-builder, definition-of-done-validator, archive-package-preparer |
| 16 | **human** (Release Authority) | — approve ADRs, residual risk, issue creation, merge |
| 18–19 | `governance-and-process-improvement-agent` | slice-retro-and-lessons, manual-config-debt-monitor, strategic-doc-update-recommender |
| all | `slice-orchestrator` | thin router (role file + `slice-orchestrator` skill) — dispatches the above and tracks `slice-state.yaml` |

Start from [`standards/AGENTS.md`](./AGENTS.md), which points into the three-document model: for the authoritative stage details see [`standards/gentech_slice_lifecycle_orchestration_map.md`](./gentech_slice_lifecycle_orchestration_map.md); for what each skill does see [`standards/gentech_agent_skills_usage_and_requirements.md`](./gentech_agent_skills_usage_and_requirements.md); for the rules see [`standards/gentech_slice_based_development_process_revised.md`](./gentech_slice_based_development_process_revised.md). The authoritative spec for any individual skill is its `SKILL.md` package under `.claude/skills/<skill-name>/` (canonical source: `Skills/.agents/skills/<skill-name>/`).
