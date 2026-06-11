---
name: adr-gap-detector
description: "Determines whether a proposed implementation choice requires a new ADR before coding begins. Use when architecture-guideline-checker flags a not-covered area or guideline conflict."
---

# Skill: ADR Gap Detector

**Used at:** Stage 6 — Architecture compliance & ADR check (Orchestration Map §3 stage table), conditional — fires only when `architecture-guideline-checker` identifies a not-covered area or guideline conflict.
**Execution model:** `inline`
**Supports:** Process Doc §9 Architecture Guidelines Versus Actual Architecture

---

## 1. Purpose

Determine whether a proposed implementation choice requires a new Architecture Decision Record (ADR) before coding begins, and produce a gap report that gives the human everything needed to decide. The skill answers one question: "Does this gap need an ADR?" If yes, it stops development — it does not write the ADR, approve the approach, or let coding proceed; it produces a structured gap report and hands control to the human release authority. If no (an existing ADR or guideline covers the area on closer inspection), it documents that and lets the orchestrator proceed to Stage 7.

---

## 2. When to Use This Skill

Conditional. Fires only when `architecture-guideline-checker` produced one or more "Not covered" findings, the implementation plan flagged an unresolved ADR concern, or the user asks whether a specific choice requires an ADR. Do not run speculatively on clear, compliant plans — it wastes context and creates false blockers.

---

## 3. Do Not Use This Skill For

- Writing or approving the final ADR (approval is a human gate), updating guidelines (`architecture-guideline-updater`, post-ADR), or checking compliance with existing guidelines (`architecture-guideline-checker`).
- Covering ADR gaps that arise after coding has started (`implementation-deviation-capture`).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Architecture guideline compliance report | Required | "Not covered" findings (Section 6) are the primary input. |
| 2 | Implementation plan | Required | Proposed-approach context for each gap. |
| 3 | Technical architecture guidelines | Required | To confirm the gap is real, not a misread. |
| 4 | Existing approved ADRs | Required | To check whether an existing ADR covers the gap under a different framing. |
| 5 | Slice spec | Required | Business/technical intent behind the choice. |
| 6 | Current-state documentation | Recommended | Whether the gap is a new pattern or an undocumented existing one. |
| 7 | Known limitations | Recommended | Why the gap cannot be resolved by existing patterns. |

---

## 6. Source Authority Rules

A gap that exists in the actual architecture but has no guideline or ADR coverage is still a gap. "We built this before" does not close an ADR gap. Gap existence is established by the compliance report; coverage is established only by a specific approved ADR.

---

## 7. Process Steps

1. **Confirm the gaps are real.** For each "Not covered" finding: re-read the relevant guideline sections to confirm the area is truly uncovered; search approved ADRs for any decision addressing it under a different title/framing. If an existing ADR covers it, document the finding, close the gap as "covered by existing ADR," and proceed. If confirmed real, continue.
2. **Characterize each confirmed gap.** Determine the **decision question** (frame as a concrete question the human must answer, e.g. "Should Azure Table Storage be the approved data store for lookup-only reference data, or should all data access use Cosmos DB / Azure SQL?"); **why the decision matters now** (risk if coding proceeds undecided); **options to consider** (2–4 concrete options with brief pros/cons in this Microsoft-stack context — do not recommend one); **impact on this slice** (which planned files/components are blocked); **impact on future slices**.
3. **Assess blocking severity** per gap:

   | Severity | Meaning |
   |---|---|
   | **Blocking** | Coding cannot start for affected components until an ADR is approved. |
   | **Conditionally blocking** | Unaffected components may proceed; components covered by this gap must wait. |
   | **Non-blocking recommendation** | Low-risk enough to proceed with documented intent pending a future formal ADR. Use sparingly. |

   Default to "Blocking" unless there is a strong, explicit reason to downgrade. Do not downgrade to avoid delay.
4. **Determine whether an ADR draft should be prepared.** Only if the user explicitly asks. Draft ADR input material (title, decision question, context, options) is allowed but must be labelled "draft input for human ADR author" — never marked approved. Do not produce an unsolicited draft.
5. **Produce the gap report** using `templates/adr-gap-report-template.md`.

If a blocking gap is confirmed, stop and escalate to the human — do not soften the blocker, frame options toward a preferred answer, or let coding proceed without an explicit human decision. See AGENTS.md cross-cutting rules (Authority and human gates; Evals and architecture).

---

## 8. Output Location

Gap report: `docs/delivery/slices/<slice-id>/adr-gap-report.md`. If a draft ADR is requested: `/docs/architecture/adr/ADR-NNN-draft-<short-title>.md` (next number in sequence), marked `DRAFT — AWAITING HUMAN APPROVAL`.

---

## 9. Output Format

Use `templates/adr-gap-report-template.md`. Gaps closed by existing ADRs are noted separately from confirmed gaps. Draft ADR material appears only if explicitly requested.

---

## 10. Quality Bar

Before handoff, confirm:

- The compliance report exists with at least one "Not covered" finding; this skill was not triggered speculatively.
- Guidelines reviewed are the current active version; all approved ADRs, the implementation plan, and the slice spec were consulted.
- Every "Not covered" finding was checked against all approved ADRs; any gap closed by an ADR cites the specific ADR ID and section (no vague "this seems covered").
- For each confirmed gap: the decision question is specific, answerable, and framed as a question; "why now" is concrete; 2–4 balanced options with pros/cons in this Microsoft-stack context are given; affected plan components and future-slice impact are listed.
- Blocking severity is stated, justified, and defaults to "Blocking" unless explicitly downgraded.
- No ADR was written and marked approved; any draft input is labelled "DRAFT — AWAITING HUMAN APPROVAL" and was produced only on explicit request; the report recommends no specific option.
- The development pause recommendation is explicit: every component depending on a confirmed gap is listed; any that may proceed are listed with their independence explained.
- The report is self-contained for a human who has not seen the conversation; handoff notes let the orchestrator pause and present it correctly.

---

## 11. Failure Modes to Avoid

- Writing and "approving" an ADR, or allowing coding past a blocking gap without explicit human instruction.
- Closing a gap without a specific ADR ("this seems covered"), or treating prior use as permission.
- Framing options to steer toward a preferred answer; producing an unsolicited ADR draft that anchors the human.
- Downgrading blocking severity to avoid delay — delay is the correct outcome when architecture clarity is absent.

---

## 13. Handoff to Next Skill

- **All gaps resolved (existing ADR found):** hand off to Stage 7 noting which ADRs cover the gaps; coding may proceed.
- **Blocking gaps confirmed:** STOP. The orchestrator presents the report to the human, who decides: approve a new ADR → `architecture-guideline-updater` → Stage 7; reject the approach → revise plan → return to Stage 5; or proceed at explicit risk → document the decision → Stage 7 with the risk noted.

Do not imply the gap is minor or that coding can start before the human decides. The orchestrator must not auto-proceed past this point.
