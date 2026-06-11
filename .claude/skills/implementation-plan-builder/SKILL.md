---
name: implementation-plan-builder
description: Converts an approved slice spec and hardened eval contract into a concrete coding plan for the Coding Agent. Use during implementation planning (Stage 5) to map files, tests, evals, and ADR checks.
---
# Skill: Implementation Plan Builder

**Used at:** Stage 5 — Implementation planning (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §14 Branching Model, §16 Implementation Process

---

## 1. Purpose

Convert the approved slice spec and hardened eval contract into a concrete coding plan the Coding Agent can follow through Stages 6–9: which files change, how the test suite expands, how eval scenarios integrate with the runner, and which architecture/ADR checks are needed before coding. It bridges the "what" (slice spec) and the "how" (branch changes, test additions, config captures). It does not write code, decide architecture, or approve the plan — it produces the plan and surfaces blockers.

---

## 3. Do Not Use This Skill For

- Writing application code, IaC, or configuration; hardening eval scenarios; approving architecture deviations.
- Creating GitHub Issues (`github-issue-drafter`), deviation capture (`implementation-deviation-capture`), or selecting the next slice (`next-slice-recommender`).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Approved slice spec | Required | Approved version, not a draft. |
| 2 | Hardened eval contract | Required | Deterministic test expectations, live-model scenarios, regression eval list. |
| 3 | Technical architecture guidelines | Required | Active guidelines for the Microsoft stack in use. |
| 4 | Current-state documentation | Required | What the application currently does and how it is structured. |
| 5 | Approved ADRs | Required | Architecture decisions already made. |
| 6 | Existing test structure / conventions | Required | Layout, naming, framework (pytest, xUnit, Vitest, Power Apps Test Studio). |
| 7 | Known limitations | Recommended | Constraints on implementation choices. |
| 8 | GitHub Issues for this slice | Recommended | Open issues affecting approach. |
| 9 | Implementation lessons from prior slices | Recommended | Recurring patterns, Microsoft-stack gotchas. |

If the eval contract is not hardened or the spec is still a draft, do not proceed — surface a blocker ("Stage 4 eval design is required before Stage 5 implementation planning") and stop.

---

## 7. Process Steps

1. **Confirm inputs.** Verify spec is approved and eval contract is hardened. If not, blocker and stop.
2. **Map requirements to implementation areas.** For each functional requirement, business rule, agent-behaviour requirement, and acceptance criterion, identify affected code/IaC/config areas; which Microsoft-stack surfaces are involved (Copilot Studio topics/actions/agents, Azure AI Foundry prompts/models/tools, Power Platform flows/connectors, Azure services, API layers); and whether manual portal configuration is expected (flag for Stage 7 `manual-config-evidence-capture`).
3. **Produce the file and change plan.** List files/components expected to change, grouped by layer: app logic / agent orchestration / prompts; data/state/workflow-state; API/connectors/integrations; IaC (Bicep, ARM, Terraform); Power Platform / Copilot Studio / Foundry exports or config records; tests (unit, integration, workflow-state); eval scenario files; documentation stub notes (full update is Stage 12).
4. **Produce the test plan.** For every deterministic test expectation in the eval contract: identify test file, type, and framework; map it to the requirement/criterion it covers; flag new infrastructure or fixtures; list gaps (requirements with no mapped test).
5. **Produce the eval-integration plan.** For live-model scenarios: identify trigger mechanism (CI/CD hook, manual step, Prompt Flow / Azure AI Foundry evaluation run); identify eval-data fixtures or synthetic-data needs; note environment variables, model versions, and dataset references the runner will need.
6. **Check architecture and ADR flags.** For each area, verify fit with active guidelines and approved ADRs. Flag any deviation or uncovered approach as a required ADR check (input to Stage 6 `adr-gap-detector`). Do not resolve gaps here — flag them and note the Stage 6 gate.
7. **Identify risks and blockers.** Implementation (unclear requirements, missing precedent, untested integration, known limitations); architecture (guideline violations, ADR gaps, multi-surface coordination); test/eval (unclear pass/fail, data availability); manual-config (non-source-controllable portal config); privacy/residency (PHI/PII, Canadian residency, audit obligations); sequencing dependencies.
8. **Assemble the plan** using `templates/implementation-plan-template.md`.

This skill flags architecture and ADR gaps for Stage 6; it never resolves them and never authorizes coding to start. If requirements are unclear, surface a blocker — do not quietly simplify the spec to fit an implementation preference. See AGENTS.md cross-cutting rules (Authority and human gates; Source of truth).

---

## 8. Output Location

`docs/delivery/slices/<slice-id>/implementation-plan.md` — follow the project's slice folder convention if different and note the deviation.

---

## 9. Output Format

Use `templates/implementation-plan-template.md`. Copy the slice intent summary verbatim — do not rephrase requirements. The plan contains no code: list files and describe changes at the intent level.

---

## 10. Quality Bar

Before handoff, confirm:

- Slice spec is the approved version and the eval contract is hardened (not drafts).
- Every layer is represented in the change plan (logic, data/state, API/connectors, IaC, tests, eval scenarios).
- Every Microsoft-stack surface involved has a change-plan entry, with source-control feasibility noted.
- Portal/low-code config surfaces are flagged for Stage 7 evidence capture.
- Every acceptance criterion has a mapped test or an explicit gap flag; every deterministic test expectation from the eval contract is represented.
- Every live-model eval scenario is accounted for in the eval-integration plan, with model/prompt/tool/orchestration versions noted.
- Eval-data governance (PHI/PII, Canadian residency, synthetic-data needs) is addressed.
- All architecture and ADR flags are explicit and marked blocking / non-blocking / unknown — none silently assumed resolved.
- Privacy, residency, and audit risks are called out where relevant; sequencing dependencies and open blockers are listed.
- The plan contains no code and does not change requirements from the slice spec.
- The recommended next step is Stage 6 (or a specific blocker resolution).
- The plan is self-contained for a reader who has not seen this conversation.

---

## 11. Failure Modes to Avoid

- Treating the plan as approval to start coding — Stage 6 must clear architecture compliance first.
- Silently assuming architecture compliance, or adding patterns not covered by guidelines without flagging the ADR need.
- Omitting eval-integration details, leaving evals unwired even when tests exist.
- Ignoring manual-config surfaces that will not auto-export (Azure, Power Platform, Copilot Studio, Foundry).

---

## 13. Handoff to Next Skill

On completion, hand off to Stage 6 with the finalized plan, the list of architecture/ADR flags, and any open blockers human review must resolve first. Do not claim implementation is ready to start. Next skills: `architecture-guideline-checker` (always) and `adr-gap-detector` (only if ADR flags are present).
