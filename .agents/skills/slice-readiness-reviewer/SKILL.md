---
name: slice-readiness-reviewer
description: Independently reviews a draft slice spec and decides whether it is ready for eval design. Use after a spec is drafted, run by an agent that did not author it.
context: fork
---
# Skill: Slice Readiness Reviewer

**Used at:** Stage 3 — Slice readiness review (Orchestration Map §3 stage table)
**Execution model:** `isolated-verification`
**Supports:** Process Doc §12 Slice Planning, §13 Eval-Driven Requirements

---

## 1. Purpose

Independently review a draft slice spec and decide whether it is ready to hand off to eval design at Stage 4. The output is a readiness report with a three-way decision: **ready for eval design**, **needs revision**, or **blocked**. This skill approves eval-design readiness only — never coding readiness (which is a human gate at Stage 16) — and must be run by an agent that did not author the spec, so the author does not grade their own work. It does not rewrite the spec unless the user explicitly asks.

---

## 3. Do Not Use This Skill For

- Rewriting or substantially revising the spec (unless the user explicitly asks).
- Hardening eval scenarios (`eval-contract-designer`, Stage 4).
- Approving coding readiness or residual risk.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Draft slice spec | Required | Primary artifact under review |
| 2 | Reconciled planning context from `planning-context-reconciler` | Required | Baseline for intent vs. current state |
| 3 | Technical architecture guidelines | Required | Check constraints are correctly cited |
| 4 | Known limitations | Recommended | Confirm spec does not plan against hard limits |
| 5 | Relevant GitHub Issues | Recommended | Confirm open issues are reflected in spec blockers |
| 6 | Approved ADRs index | Recommended | Confirm architecture constraints are grounded |
| 7 | Test/eval strategy | Optional | Context for judging eval-contract-draft quality |

Do not read raw application code, old slice specs, or archived branch artifacts. Ground the review in the same documentation-level inputs the planning agent used, plus the draft spec.

---

## 7. Process Steps

1. **Read the draft spec end to end.** Form an initial impression of scope coherence, requirement completeness, and eval-draft quality.
2. **Review each dimension** (§7.1), flagging findings.
3. **Classify every finding** as a required fix (blocks the readiness decision), recommended improvement (non-blocking), or note.
4. **Determine the readiness decision** (§7.2).
5. **Write the readiness report** using the template.

### 7.1 Review Dimensions

**Scope** — one clear primary outcome; explicit/adequate out-of-scope list; bounded enough to implement, test, evaluate, document, and close out as one unit; not a milestone in disguise.

**Functional requirements** — behaviourally testable; not implementation steps disguised as requirements; business rules specific enough to implement; no requirement gaps that would block the coding agent.

**Agent behaviour** — explicit; ambiguity handling addressed; acceptable and unacceptable outputs stated; unsafe failure modes listed with blocking status.

**Eval contract draft** — behavioural-contract summary present and meaningful; unsafe failure modes listed; expected/unacceptable outputs defined; ambiguity handling covered; human-review requirements identified; cost/latency present where relevant; eval-data governance addressed; sufficient for `eval-contract-designer` to harden at Stage 4 without significant guessing.

**Architecture** — constraints cite approved guidelines or ADRs; gaps flagged not silently resolved; no implementation design smuggled in as constraints; no constraint contradicts an active ADR.

**Privacy / governance** — PHI, PII, Canadian residency, audit trail, sensitive eval data, and external sharing each explicitly addressed (even if "not applicable"); manual-config surfaces identified where applicable; any unresolved privacy concern raised as a blocker.

**Consistency** — current-state context aligns with the reconciled planning context; documentation-repo intent not treated as current reality; no contradiction of known limitations, active GitHub Issues, or superseded architecture assumptions.

**Open questions** — all explicit; must-resolve-before-coding marked as such; hidden assumptions surfaced as open questions; unresolved Issues flagged as blockers where relevant.

### 7.2 Readiness Decision Rules

**`ready-for-eval-design`** — requires all of: no required fixes outstanding; one clear primary outcome; testable requirements; eval-contract draft sufficient for `eval-contract-designer`; architecture constraints cite approved sources and gaps are flagged; privacy/residency/auditability addressed; must-resolve-before-coding questions explicit and marked; no unresolved Issue blocking scope.

**`needs-revision`** — required fixes exist but no fundamental scope/architecture blocker (e.g. vague/untestable requirements, eval-draft gaps, unaddressed governance, ambiguous blocking status, consistency issues). Return to `slice-spec-generator` with a specific required-fixes list.

**`blocked`** — cannot be made ready without resolving something outside the planning agent's authority (architecture decision needed; privacy/residency governance decision needed; key open question the planning agent cannot resolve alone; unresolved Issue fundamentally constrains scope; scope too broad and must be re-split). Return with a clear explanation of what blocks and who must resolve it.

---

## 9. Output Format

Use `templates/slice-readiness-report-template.md`. Required fixes must be specific and actionable, not vague warnings. Do not rewrite the spec inside the report.

---

## 10. Quality Bar

Before handoff, confirm:

- The review was performed by an agent that did not author the spec, using independent documentation-level inputs.
- Every review dimension was checked and documented.
- One primary outcome confirmed; the slice is not a milestone in disguise.
- Requirements checked for behavioural testability; no implementation steps disguised as requirements; no material gaps.
- Agent-behaviour ambiguity handling and unsafe-failure-mode coverage checked.
- Eval-contract draft judged sufficient for `eval-contract-designer` to harden.
- Architecture constraints cite approved sources; no gap silently accepted; no constraint contradicts an active ADR.
- PHI, PII, Canadian residency, audit, sensitive eval data, external sharing, and manual-config each addressed.
- Consistency with the planning context, known limitations, and active Issues verified.
- All open questions explicit; must-resolve-before-coding marked.
- The decision is one of the three approved categories with a specific rationale; required fixes are specific and actionable.
- The report does not rewrite the spec and does not approve coding readiness (eval-design readiness only).

---

## 11. Failure Modes to Avoid

- Approving a spec as ready while required fixes exist (broken gate).
- Rewriting the spec instead of flagging issues (violates the isolated-verification boundary).
- Vague warnings instead of specific required fixes (planning agent cannot act).
- Marking an ambiguous open question non-blocking (hidden assumption enters coding).

---

## 13. Handoff to Next Skill

| Decision | Recommended Next Action |
|---|---|
| Ready for eval design | `eval-risk-profiler` and `eval-contract-designer` at Stage 4 |
| Needs revision | Return spec to `slice-spec-generator` with the required-fixes list |
| Blocked — architecture gap | `adr-gap-detector`, then return to `slice-spec-generator` |
| Blocked — privacy/governance | Human clarification required |
| Blocked — scope too broad | `slice-sizer` to re-scope, then `slice-spec-generator` |

This skill approves eval-design readiness only. Coding readiness requires human approval at Stage 16.
