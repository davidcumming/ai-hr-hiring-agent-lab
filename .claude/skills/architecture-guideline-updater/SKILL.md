---
name: architecture-guideline-updater
description: "Updates forward-looking technical architecture guidelines after a human-approved ADR. Use only when an ADR has been approved and guidelines must reflect the new decision."
---

# Skill: Architecture Guideline Updater

**Used at:** Stage 6 — Architecture compliance & ADR check (Orchestration Map §3 stage table), after an approved ADR only
**Execution model:** `inline`
**Supports:** Process Doc §9 Architecture Guidelines Versus Actual Architecture

---

## 1. Purpose

Update the forward-looking technical architecture guidelines after a **human-approved** ADR. The guidelines are the intended Microsoft-stack mapping that all future slices must follow (Process Doc §9.1) — not historical records and not current-state descriptions. The approved ADR is the sole authority for any change; this skill obeys the recommend-never-approve and authority rules in AGENTS.md and acts only when an ADR has been approved.

---

## 3. Do Not Use This Skill For

- Updating guidelines without an approved ADR, or retroactively documenting an unreviewed change — there is no legitimate path here without an ADR.
- Updating actual architecture or current-state documentation — that is `current-state-reconciler` at Stage 12.
- Drafting or approving the ADR — drafting is `adr-gap-detector`; approval is a human gate.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Approved ADR | Yes | Must include ADR ID, decision, rationale, and human approval record |
| 2 | Current architecture guidelines | Yes | Full document; identify affected sections |
| 3 | User approval record | Yes | Confirmation the human release authority approved this specific ADR |
| 4 | Related implementation context | If exists | The slice/implementation that triggered the ADR (supporting evidence only) |

If the ADR is not yet approved, do not proceed. Raise a blocker: guideline update is blocked pending ADR approval.

---

## 6. Source Authority Rules

The approved ADR is the **only** authority for changing a guideline. Implementation context is supporting evidence — it does not authorize a change. If the ADR's human approval record is absent or ambiguous, block.

---

## 7. Process Steps

1. **Confirm ADR approval.** Verify a human approval record exists, that it explicitly covers the decision being implemented, and that the ADR ID is referenced in the slice's Stage 6 compliance report. If approval is absent or ambiguous, **block and request confirmation**.
2. **Identify affected guideline sections.** List every section that the ADR directly changes, contradicts, fills a gap in, or cross-references — before making any change.
3. **Plan the changes** per section: existing text, what the ADR requires instead, change type (replace/add/remove), and any downstream sections affected. Record the plan using the template before applying.
4. **Apply the changes.** Directive present-tense language ("Use…", "Require…", "Do not…", "All X must…"). Cross-reference the ADR by ID in every changed section. Do not expand beyond what the ADR authorizes, do not add rules the ADR does not address, and do not remove rules unless the ADR explicitly deprecates them. If the ADR is ambiguous about a section, do not update it — flag it for ADR clarification.
5. **Write the guideline change summary** — what changed, why (ADR reference), and impact on future slice planning. This summary supports future `planning-context-reconciler` and `architecture-guideline-checker` runs.
6. **Assess impact on future slices** — which planned slices, known limitations, or open GitHub Issues are affected by the new rule (note for the user; do not update issues here).

---

## 9. Output Format

Use `templates/architecture-guideline-update-template.md`. Update guidelines in place at `/docs/architecture/technical-architecture-guidelines.md`; write the change summary to `/docs/architecture/adrs/<adr-id>-guideline-update-summary.md`. Follow the project's paths if they differ. The final response includes: confirmed ADR ID and approval status, sections changed, change summary, updated text per section, future-slice impact, flagged ADR ambiguities, files changed, and confirmation that Stage 7 can proceed.

---

## 10. Quality Bar

Before handoff, confirm:

- An approved ADR with a human approval record exists and covers every section changed.
- No change exceeds ADR scope; no rule was removed that the ADR did not explicitly deprecate.
- The ADR ID is cited in every changed section.
- Guideline language is directive, present-tense, and forward-looking — no historical or retrospective framing.
- No actual-architecture, current-state, or aspirational documentation-repo content was introduced.
- Downstream guideline sections were reviewed for indirect impact.
- Flagged ambiguities (sections where the ADR is unclear) are listed explicitly.
- The change summary is complete and future-slice impact is assessed.
- Open GitHub Issues affected by the rule change are noted (not updated here).
- Files-changed list is complete; Stage 7 handoff confirmed.

---

## 11. Failure Modes to Avoid

- **Expanding beyond ADR scope** — map every change to a specific ADR statement; do not introduce unreviewed rules.
- **Treating implementation convenience as an approved rule** — only the ADR text is authority.
- **Removing rules not covered by the ADR** — this can silently unblock restricted behaviours; remove only explicitly deprecated rules.

---

## 13. Handoff to Next Skill

After this skill completes, Stage 6 continues to Stage 7 — Implementation & config capture. The coding agent picks up Stage 7 with the updated guidelines as the new active guardrails.

Pass forward: the updated guidelines file path; the ADR ID and confirmed approval record; the change-summary path; any flagged ambiguities that may need a follow-up ADR; notes on which planned slices the new rule affects.
