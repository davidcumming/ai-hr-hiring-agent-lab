---
name: architecture-guideline-checker
description: "Verifies every implementation choice in the plan complies with active architecture guidelines before code is written. Use as the compliance gate between planning and coding."
---

# Skill: Architecture Guideline Checker

**Used at:** Stage 6 — Architecture compliance & ADR check (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §9 Architecture Guidelines Versus Actual Architecture, §16 Implementation Process

---

## 1. Purpose

Verify that every implementation choice in the Stage 5 plan complies with the active technical architecture guidelines before any code is written. This is the formal compliance gate between planning and coding: read the plan against the guidelines, identify violations or ambiguities, and determine whether any finding requires a new ADR. The output is a compliance report — it does not approve deviations, update guidelines, or write ADRs. When violations or ADR gaps are found, the orchestrator pauses for human input before coding proceeds.

---

## 3. Do Not Use This Skill For

- Approving deviations, updating guidelines (`architecture-guideline-updater`, post-ADR), or writing ADRs (surface gaps; `adr-gap-detector` characterizes them).
- Reviewing already-written code or documentation consistency (`documentation-consistency-validator`) — this skill checks the plan, before coding.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Stage 5 implementation plan | Required | The finalized plan from `implementation-plan-builder`. |
| 2 | Technical architecture guidelines | Required | Current active version; the rules document. |
| 3 | Approved ADRs | Required | Decisions that may extend or modify guidelines for specific areas. |
| 4 | Actual technical architecture document | Required | Records what was built — distinguishes "not in guidelines" from "not built yet". |
| 5 | Slice spec | Required | Clarifies intent so compliance is assessed in context. |
| 6 | Known limitations | Recommended | Areas where guidelines cannot currently be met. |

If guidelines are absent or outdated, surface a blocker — do not guess at them.

---

## 6. Source Authority Rules

Process Doc §9: guidelines prescribe rules for future implementation; the actual architecture document records what exists. These are different sources with different authority — do not conflate them. A pattern that exists in the codebase is not "approved" if it was never added to guidelines. "We did this before" is not a compliance justification unless covered by guidelines or an approved ADR.

| Question | Authority |
|---|---|
| What must future implementation follow? | Architecture guidelines + approved ADRs |
| What has been built so far? | Actual architecture document + code/config evidence |
| What is this slice trying to do? | Approved slice spec |
| What rules are proposed for change? | Only via a new ADR — not this skill |

---

## 7. Process Steps

1. **Identify the compliance surface.** From the plan, extract every file/component change; every Microsoft-stack surface (Copilot Studio, Azure AI Foundry, Power Platform, Azure services, API layer); every pattern/approach introduced (data access, agent invocation, authentication, API design, IaC); every new dependency (library, service, SDK, connector).
2. **Map each surface to guideline sections.** Locate the governing guideline section(s), note version and section number, and note whether an approved ADR extends or modifies that section.
3. **Assess compliance** per mapped item:

   | Finding Type | Meaning |
   |---|---|
   | **Compliant** | Matches active guideline and any relevant ADR. |
   | **Violation** | Contradicts an active guideline. Coding must not start for this item until resolved. |
   | **Not covered** | No guideline addresses this area — a potential ADR gap; flag for `adr-gap-detector`. |
   | **Ambiguous** | Guideline readable more than one way for this case; clarification needed. |
   | **ADR extends guideline** | An approved ADR explicitly permits/modifies the guideline here; record the ADR reference. |

4. **Check actual-architecture drift.** Flag cases where the plan matches existing architecture but is not covered by guidelines, or differs from existing architecture in a way the plan/spec does not explain. Not automatically violations, but must be flagged — may indicate guideline gaps or undocumented legacy patterns needing ADR coverage.
5. **Determine if `adr-gap-detector` is needed.** Any "Not covered" or substantial "Ambiguous" findings trigger it before coding starts for the affected areas. If all findings are "Compliant" or "ADR extends guideline," coding may proceed to Stage 7 (subject to other blockers).
6. **Produce the report** using `templates/architecture-guideline-compliance-report-template.md`.

This skill reports compliance; it never approves deviations and never modifies guidelines — those require the human and the ADR process. See AGENTS.md cross-cutting rules (Authority and human gates; Source of truth; Evals and architecture).

---

## 8. Output Location

`docs/delivery/slices/<slice-id>/architecture-compliance-report.md` — follow the project's slice folder convention if different and note the path used.

---

## 9. Output Format

Use `templates/architecture-guideline-compliance-report-template.md`. The verdict must be exactly one of: Clear / Violations found / ADR check required / Blocked pending clarification.

---

## 10. Quality Bar

Before handoff, confirm:

- The plan reviewed is the finalized Stage 5 plan; guidelines used are the current active version.
- All approved ADRs, the actual architecture document, and the slice spec were consulted.
- Every file/component change and every introduced pattern, approach, and new dependency has a finding — nothing skipped.
- Every Microsoft-stack surface is covered (Copilot Studio, Foundry, Power Platform, Azure services, API/connectors, IaC, data/state, app logic).
- Every "Violation" is marked blocking; every "Not covered" area is listed as an ADR gap candidate; every "Ambiguous" finding is specific; every "ADR extends guideline" entry cites the ADR ID.
- Actual architecture was used only to detect drift, not to grant compliance; existing patterns absent from guidelines are noted.
- No deviation was approved; no guideline was updated; no ADR was drafted in this report.
- The verdict is one of the four approved types with a specific rationale, and the recommended next step matches it.
- If verdict is "Clear," Sections 4–6 contain no violations, ambiguities, or not-covered areas.
- The report is self-contained for a reader who has not seen the conversation.

---

## 11. Failure Modes to Avoid

- Treating "we've done this before" as compliance when the pattern was never in guidelines — surface the gap.
- Skipping "Not covered" findings, letting architecture debt accumulate silently.
- Using the actual architecture as the authority for future rules, or treating documentation-repo aspirational material as enforceable guidelines.
- Conflating the guideline check with the ADR check — this skill checks compliance with existing guidelines; `adr-gap-detector` decides whether a new ADR is needed.

---

## 13. Handoff to Next Skill

- **Clear:** hand off to Stage 7 with the report; coding may begin.
- **ADR check required:** trigger `adr-gap-detector` with the not-covered areas; coding must not start until gaps resolve.
- **Violations found:** surface violations to the human; coding must not start; plan must be revised or guidelines changed via the ADR process.
- **Blocked pending clarification:** surface ambiguities to the human; coding must not start until intent is clarified.

Do not claim coding is cleared if any violation, blocking ambiguity, or not-covered area exists.
