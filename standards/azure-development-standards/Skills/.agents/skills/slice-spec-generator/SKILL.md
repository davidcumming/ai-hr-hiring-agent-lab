---
name: slice-spec-generator
description: Creates a functional, business/process-oriented implementation-intent slice spec for a Microsoft-stack agentic solution. Use after slice-sizer accepts a candidate as one slice.
---
# Skill: Slice Spec Generator

**Used at:** Stage 2 — Slice specification (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §12 Slice Planning, §13 Eval-Driven Requirements

---

## 1. Purpose

Create a functional, business/process-oriented implementation-intent slice specification for a Microsoft-stack agentic solution: it tells the coding agent what user behaviour, workflow change, business rule, and eval contract the next slice should support. The spec is a planning artifact describing intent, not a technical design document and not implementation truth (per the AGENTS.md source-of-truth hierarchy). Normally called after `slice-sizer` returns `accept-as-one-slice`.

---

## 3. Do Not Use This Skill For

- Designing detailed implementation mechanics or writing code.
- Fully hardening eval scenarios (`eval-contract-designer`, Stage 4).
- Producing a sizing assessment — if the slice looks too large, hand back to `slice-sizer`.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Reconciled planning context from `planning-context-reconciler` | Required | Current-state baseline and strategic intent |
| 2 | Documentation-repo source material for the slice area | Required | Intent source |
| 3 | Code repo current-state documentation | Required | What exists now |
| 4 | Technical architecture guidelines | Required | Constraint source |
| 5 | Approved ADR index and relevant ADRs | Recommended | Supersedes guidelines |
| 6 | Implementation lessons relevant to the area | Recommended | Avoids repeating past mistakes |
| 7 | Process lessons, if available | Optional | Process-level guidance |
| 8 | Known limitations | Recommended | Hard planning boundaries |
| 9 | Open GitHub Issues relevant to the proposed slice | Required | Unresolved work that may constrain scope |
| 10 | Current testing and eval strategy | Recommended | Eval section anchor |
| 11 | Sizing assessment from `slice-sizer` | Recommended | Scope confirmation |
| 12 | User-provided priority, constraint, or target outcome | Optional | Focuses the spec |

If inputs are missing, continue only if the missing input is not essential. Mark all assumptions and gaps.

---

## 7. Process Steps

1. **Confirm scope from sizing assessment.** If none is available, defer to `slice-sizer`'s split-trigger rules; if the slice appears too large, produce a split recommendation instead of a bloated spec.
2. **Identify the primary business/process outcome.** State it in one or two sentences. Everything else serves it.
3. **Establish current-state context.** From current-state docs, describe what already exists. Do not use historical slice specs as current-state truth.
4. **Write functional requirements** (FR-NNN). Behaviourally testable; avoid implementation mechanics.
5. **Write business rules** (BR-NNN). Explicit rules governing data, state, decisions, constraints.
6. **Write agent behaviour requirements** (AB-NNN). How the agent behaves under normal conditions and under ambiguity/risk; state acceptable and unacceptable behaviours explicitly.
7. **Write acceptance criteria** (AC-NNN). Specific, verifiable, linked to requirements, each with a verification method (deterministic test / live eval / human review / manual evidence).
8. **Draft the eval contract.** Behavioural contract summary; unsafe failure modes; expected/unacceptable outputs; ambiguity handling; human-review requirements; cost/latency; eval-data governance constraints. Draft only — `eval-contract-designer` hardens it at Stage 4.
9. **Write deterministic test expectations.** Unit, integration, workflow-state tests, linked to requirements/acceptance criteria.
10. **Write live-model eval expectations.** Draft scenarios with expected behaviour, pass criteria, run thresholds (Process §19.1), and risk level.
11. **Address privacy/architecture-gap/manual-config concerns** (§7.1).
12. **State architecture constraints.** Only approved, active constraints from guidelines or ADRs; no implementation design.
13. **Record dependencies, blockers, open questions.** Mark which open questions must be resolved before coding begins.
14. **Create the traceability seed.** Initial mapping of requirements → acceptance criteria → tests → evals → expected evidence.
15. **Write handoff notes for the coding agent.** Primary outcome; must-follow architecture constraints; required tests/evals; known blockers; what not to build.

### 7.1 Privacy, Architecture-Gap, and Manual-Config Handling

The spec must explicitly state whether the slice touches PHI, PII, sensitive business data, data residency / Canadian hosting, audit logs, evidence retention, external sharing, human approval, or eval data that could contain sensitive information; where the governance approach is unclear, mark a blocker rather than proceeding as if resolved. If the slice needs functionality not covered by, or conflicting with, the architecture guidelines (or a new stack service category), mark an `architecture-guideline-gap` and recommend `adr-gap-detector` — do not silently resolve it or write the ADR here. Identify likely portal/low-code surfaces (Azure Portal, Power Platform, Copilot Studio, Azure AI Foundry, Microsoft Entra) and require evidence capture plus source-control follow-up where feasible; do not assume portal changes appear in source control automatically.

### 7.2 Technical Content Rule

The spec is primarily functional/business/process-oriented; the 80/20 functional-to-technical ratio is guidance, not a gate. Include technical content only where it constrains implementation (e.g. must follow the existing Copilot-front-door pattern; approved workflow-state storage pattern; current memory guidelines; a current security/audit rule; no new architecture pattern without ADR approval). No detailed implementation design unless it is already an approved constraint.

---

## 9. Output Format

Use `templates/slice-spec-template.md`. Write the spec as intent, never as current-state truth. Live-eval thresholds reference Process §19.1.

---

## 10. Quality Bar

Before handoff, confirm:

- One clear primary business/process outcome; out-of-scope items explicit; not a milestone in disguise.
- Requirements are behaviourally testable (not implementation steps); business rules and agent behaviours are specific, with acceptable/unacceptable outcomes and ambiguity handling stated.
- Acceptance criteria each state a verification method.
- Draft live-model eval expectations are included; unsafe failure modes listed with blocking status; pass/fail clear enough for `eval-contract-designer` to harden; human-review and eval-data governance constraints addressed.
- Technical content is limited to constraints/context; architecture constraints cite guidelines/ADRs; guideline gaps are flagged, not silently resolved.
- Manual-config expectations identified; privacy, residency, and auditability addressed for all applicable concerns.
- A traceability seed links requirements → acceptance criteria → tests → evals.
- The coding agent can understand the user/process outcome from the spec alone.
- Open questions marked must-resolve-before-coding or non-blocking.
- The spec does not claim to be implementation truth, and does not claim coding readiness (eval design still required at Stage 4).

---

## 11. Failure Modes to Avoid

- Writing a milestone, or a slice too large to evaluate (blocked at Stage 3 readiness review).
- Omitting live-model eval expectations (eval design cannot proceed at Stage 4).
- Vague acceptance criteria that cannot set pass/fail thresholds.
- Writing detailed code design into the spec, or ignoring architecture-guideline gaps (blocked at Stage 6 after coding starts).

---

## 13. Handoff to Next Skill

| Condition | Recommended Next Skill |
|---|---|
| Spec complete and well-formed | `slice-readiness-reviewer` (Stage 3) |
| Architecture gap found during spec creation | `adr-gap-detector` (resolve before readiness review) |
| Slice proved too large during spec writing | `slice-sizer` (re-scope first) |
| Privacy concern unresolved | Human clarification required |
| Open questions block coding | Human clarification required before `slice-readiness-reviewer` |

State whether the slice is ready for `slice-readiness-reviewer` at Stage 3. Do not claim coding readiness until eval-design review (Stage 4) is complete unless the user explicitly skips it.
