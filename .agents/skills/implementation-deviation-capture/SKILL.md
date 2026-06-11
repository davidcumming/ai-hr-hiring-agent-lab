---
name: implementation-deviation-capture
description: Records, classifies, and explains every meaningful way an implementation diverged from the slice spec. Use when implementation differs from the spec (Stage 9) to produce a traceable deviation log.
---
# Skill: Implementation Deviation Capture

**Used at:** Stage 9 — Deviation capture (Orchestration Map §3 stage table), conditional — fires only when implementation diverged from the slice spec.
**Execution model:** `inline`
**Supports:** Process Doc §4 Slice Specs Are Intent, Not Truth, §16 Implementation Process

---

## 1. Purpose

Record, classify, and explain every meaningful way the implementation diverged from the slice spec, producing a deviation log that makes the gap between intent and result visible, traceable, and useful for future planning. Deviations are not failures — Azure, Power Platform, Copilot Studio, and Foundry reality often forces choices that differ from the plan; the goal is documentation, not criticism. The log feeds the closeout package (`closeout-package-builder`), current-state reconciliation (`current-state-reconciler`), and the retrospective (`slice-retro-and-lessons`). The slice spec is recorded intent and is never rewritten to match what was built; this skill recommends and flags, it does not approve deviations or modify the spec.

---

## 2. When to Use This Skill

Conditional. Use when implementation differs from any requirement, acceptance criterion, workflow, or architectural guidance in the spec — including features removed/deferred/rescoped, an approach substituted (different Azure service, connector, or Copilot Studio pattern), manual config used where source control was assumed (or vice versa), a platform constraint forcing a change, test/eval coverage differing from the contract, or an ambiguous requirement interpreted in practice. Do not use it when implementation matches the spec in all meaningful respects — a trivial naming or structural difference with no behavioural impact is not a deviation.

---

## 3. Do Not Use This Skill For

- Rewriting/amending the original spec to match implementation, approving deviations, or hiding them.
- Updating current-state docs (`current-state-reconciler`, Stage 12), creating GitHub Issues (recommend only), or producing implementation lessons (flag candidates; curated in `slice-retro-and-lessons`, Stage 18).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Original slice spec | Required | As it stood at the start of Stage 5 — not a version edited since. |
| 2 | Implementation branch changes | Required | PR diff, commit log, or file list. |
| 3 | Coding-agent notes / implementation summary | Recommended | If available. |
| 4 | Hardened eval contract | Required | To identify deviations in test/eval coverage. |
| 5 | Architecture guidelines and approved ADRs | Required | To assess whether deviations are compliance issues needing follow-up. |
| 6 | Source-control capture report + manual-config evidence summary | Required | To surface deviations in configuration strategy. |
| 7 | Team notes on known deviations / scope reductions / interpretations | Recommended | Decisions made during coding. |

If the original spec is unavailable or altered, note this as a process concern, work from the best available version, and flag the gap.

---

## 6. Source Authority Rules

| Question | Source of Truth |
|---|---|
| What was intended? | Original slice spec (as approved before implementation began) |
| What was actually built? | Branch changes, committed code/config/IaC, approved manual evidence |
| Is a deviation architecturally acceptable? | Architecture guidelines + approved ADRs (human approval required for new deviations) |
| Is a deviation a durable lesson? | Flagged here; curated in `slice-retro-and-lessons` |

The slice spec is not retroactively updated; deviations are recorded and the spec remains historical intent evidence (Process Doc §4).

---

## 7. Process Steps

1. **Compare spec to implementation** systematically, section by section: functional requirements and acceptance criteria; business rules (interpreted differently / reduced scope?); agent-behaviour requirements (Copilot Studio / Foundry actual vs. spec); integration requirements (deferred / substituted / modified?); data and state requirements (structures, workflow states, audit); manual-config expectations (spec assumed source control?); eval-contract coverage (acceptance criteria not covered?); privacy/residency/auditability; non-functional requirements (cost, latency, performance, reliability).
2. **Classify each deviation:**

   | Classification | Description |
   |---|---|
   | `requirement-removed` | A spec requirement not implemented and not deferred to an issue. |
   | `requirement-deferred` | Consciously deferred; a GitHub Issue recommendation exists or is being made. |
   | `approach-substituted` | Same requirement met by a different technical approach than specified. |
   | `scope-reduced` | Delivered a subset of specified scope; remainder deferred or dropped. |
   | `interpretation-applied` | An ambiguous requirement interpreted and implemented; may differ from intent. |
   | `platform-forced` | A Microsoft-stack constraint forced a different approach. |
   | `architecture-driven` | A guideline or approved ADR required a change from the spec. |
   | `eval-gap` | An acceptance criterion is not covered by the eval contract as executed. |

3. **Assess impact** per deviation: does it affect current-state docs `current-state-reconciler` will produce? does it need a GitHub Issue (deferred requirement / unacceptable scope reduction)? is it a durable implementation lesson for `slice-retro-and-lessons`? does it suggest a strategic-doc update (spec'd approach not viable on this stack)? is it a compliance concern (privacy, security, data residency)?
4. **Produce the deviation log** using `templates/deviation-log-template.md`.
5. **Recommend follow-up:** deferred requirements → recommend a GitHub Issue; significant approach substitutions → flag for `current-state-reconciler`; platform constraints → note for the retro as an implementation lesson; interpretations of ambiguous requirements → flag for the retro and consider annotating the (historical) spec with a note.

Document deviations honestly — do not hide them because they seem minor or embarrassing, and do not approve or declare any deviation acceptable; human and governance processes determine acceptability. See AGENTS.md cross-cutting rules (Authority and human gates; Source of truth; Evidence, privacy, context).

---

## 8. Output Location

`docs/delivery/slices/<slice-id>/deviations.md` — follow the project's convention if different. Referenced in the closeout package and current-state reconciliation.

---

## 9. Output Format

Use `templates/deviation-log-template.md`. Use only the approved classification values; assign High/Medium/Low severity to each deviation.

---

## 10. Quality Bar

Before handoff, confirm:

- Every spec section was reviewed for deviations (functional, business rules, agent behaviour, integration, data/state, manual config, eval coverage, privacy/residency/audit, non-functional).
- No deviation was omitted as minor or embarrassing; trivial structural differences with no behavioural impact are correctly excluded; eval-gap deviations are identified.
- Each deviation uses an approved classification, consistently applied, with a severity assigned.
- Each entry clearly states what the spec intended vs. what was implemented, with specific rationale (what exactly was unsupported, not just "the platform didn't support it").
- Current-state doc impact is assessed per deviation; Section 4 lists all sections `current-state-reconciler` must update (or states none).
- Lesson flags are set for platform-forced and architecture-driven deviations and for substitutions where the spec's approach proved unviable on this stack.
- Every deferred requirement and scope reduction has a GitHub Issue recommendation (recommended, not created) with an appropriate type.
- Every deviation touching privacy, PHI/PII, residency, security, or audit is surfaced in the compliance-flags section, not buried.
- The original spec was not amended or rewritten; the log neither approves deviations nor produces lessons (candidates only); doc updates and lesson curation are deferred to their owning skills.
- Handoff identifies eval-gap deviations, doc sections needing updates, and lesson candidates; closeout summary counts are correct.

---

## 11. Failure Modes to Avoid

- Hiding deviations (they become undocumented debt) or rewriting the spec to match implementation (erases intent history, violates Process Doc §4).
- Treating all deviations as failures — most are expected adaptations; the classification and rationale are what matter.
- Missing eval-contract gaps (uncovered acceptance criteria are deviations even if the code is correct) or not flagging compliance deviations (privacy, PHI/PII, residency, audit, security).
- Conflating deviation capture with the retro — record deviations here; do not write lessons.

---

## 13. Handoff to Next Skill

- **Primary:** `live-eval-runner` (Stage 10) — pass the deviation log; if any `eval-gap` deviation changes what should be evaluated, the eval contract may need revisiting before the run.
- **Stage 12 consumer:** `current-state-reconciler` — required input; tells the reconciler which doc sections must reflect actual implementation rather than the spec.
- **Stage 18 consumer:** `slice-retro-and-lessons` — receives the lesson flags as inputs for lesson curation.

Downstream: `closeout-package-builder` (Stage 14), `traceability-matrix-builder` (Stage 14, deferred/unimplemented requirements and issue references), `definition-of-done-validator` (Stage 15, confirms deviations are documented and high-severity ones have human-acknowledged treatment). Recommend proceeding to Stage 10, or pausing for human review if there are high-severity deviations or compliance flags that may affect the eval contract. The agent must not approve deviations or claim the implementation satisfies the spec if it does not.
