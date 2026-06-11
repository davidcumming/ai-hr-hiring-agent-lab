---
name: planning-context-reconciler
description: Produces a concise reconciled planning-context package comparing documentation intent against current implementation. Use to prepare context before planning the next slice.
---
# Skill: Planning Context Reconciler

**Used at:** Stage 0 — Planning context reconciliation (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §3 Source-of-Truth Hierarchy, §12 Slice Planning, §35 Next-Slice Recommendation

---

## 1. Purpose

Produce a concise, reconciled planning-context package that downstream agents use to plan the next slice without reading stale, contradictory, or overly broad source material directly. It compares documentation-repo intent against the current implementation baseline (current-state docs, actual architecture, ADRs, lessons, known limitations, GitHub Issues, test/eval status) and classifies every material finding. The hard boundary: this skill does **not** create a slice spec — it prepares the context for slice planning.

---

## 3. Do Not Use This Skill For

- Creating a full slice specification (`slice-spec-generator`) or sizing/splitting candidates (`slice-sizer`).
- Updating current-state docs, actual architecture, or creating ADRs/GitHub Issues.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Documentation-repo material for the planning area | Required | Strategic intent source |
| 2 | Code repo current-state documentation | Required | What exists now |
| 3 | Technical architecture guidelines | Required | Active guardrails |
| 4 | Actual technical architecture | Recommended | What is built |
| 5 | Approved ADR index and relevant ADRs | Recommended | Supersedes guidelines where applicable |
| 6 | Implementation lessons register | Recommended | Durable technical lessons |
| 7 | Process lessons register | Optional | Durable process lessons |
| 8 | Known limitations | Recommended | Hard boundaries on planning |
| 9 | Relevant GitHub Issues | Required | Source of truth for unresolved work |
| 10 | Current test/eval strategy or eval summary references | Recommended | Verified behaviour baseline |
| 11 | User-provided planning priority, theme, or target capability | Optional | Focuses the reconciliation |

If inputs are missing, proceed only if the missing input is not essential. Mark all gaps and assumptions in the output.

---

## 7. Process Steps

1. **Gather inputs.** Locate all required and available inputs (§4); note missing ones explicitly.
2. **Establish the current-state baseline.** From current-state docs and implementation truth, identify what the product supports today in the planning area.
3. **Summarize strategic intent.** From the documentation repo, identify what is expected to eventually exist; label as intent, not current reality.
4. **Compare and classify findings.** Assign every material finding a reconciliation category (table below). Leave nothing unclassified.
5. **Resolve conflicts via the AGENTS.md source-of-truth hierarchy.** Do not silently resolve conflicts that require a human decision — surface them as blockers or open questions.
6. **Assess architecture/ADR implications.** Flag any area needing a new ADR, conflicting with guidelines, or showing a coverage gap.
7. **Flag eval-readiness gaps.** For each candidate area, check whether behaviour is defined well enough to design evals.
8. **Flag privacy / data residency / auditability.** Check PHI, PII, Canadian residency, audit trail, retention, external sharing.
9. **Flag manual-config / source-control risk.** Identify Azure Portal, Power Platform, Copilot Studio, Azure AI Foundry, or Entra surfaces that may escape source control.
10. **Identify candidate next-slice areas.** Assess each on: business/process clarity; current-state dependency clarity; architecture-guideline coverage; ADR completeness; known-limitation impact; open-Issue impact; testability; live-eval readiness; privacy/data-governance clarity; manual-config/source-control risk; sizing feasibility. Do not recommend spec generation where blocking ambiguity exists.
11. **Record blockers and open questions.** Distinguish blocking from non-blocking; assign an owner or next action to each.
12. **Recommend strategic documentation updates** where durable implementation reality should flow back to the documentation repo. Do not rewrite docs directly.
13. **State the recommended handoff** (§13).

### Reconciliation Categories

| Category | Meaning |
|---|---|
| `aligned` | Documentation-repo intent matches current-state docs and active guidelines. |
| `already-implemented` | Intent has already been implemented. |
| `partially-implemented` | Some intent exists, but gaps remain. |
| `planned-or-aspirational` | Intent exists in documentation repo but is not yet implemented. |
| `stale-or-contradicted` | Intent conflicts with current-state docs, ADRs, guidelines, or lessons. |
| `blocked` | Planning needs a decision, missing input, unresolved issue, or architecture update. |
| `requires-adr` | Area requires an architecture decision before it can become a slice. |
| `requires-eval-design` | Behaviour not defined enough until eval expectations are created. |
| `requires-privacy-review` | PHI/PII, residency, audit, retention, or sensitive eval-data concern needs review. |
| `manual-config-risk` | Intent likely depends on portal/low-code config that may escape source control. |
| `candidate-for-next-slice` | Area appears ready to be turned into a slice spec. |
| `strategic-doc-update-recommended` | Documentation repo should be selectively updated from durable implementation reality. |

If documentation-repo says a capability exists but current-state docs do not confirm it, mark `planned-or-aspirational`, not current. If current-state docs show a capability the documentation repo omits, mark `already-implemented` and flag a possible `strategic-doc-update-recommended`. Where an ADR changes a documentation-repo assumption, the ADR and updated guidelines win.

---

## 9. Output Format

Use `templates/reconciled-planning-context-template.md`. Keep implementation lessons and process lessons in distinct sections (AGENTS.md cross-cutting rule).

---

## 10. Quality Bar

Before handoff, confirm:

- Current-state claims are grounded in current-state docs or implementation evidence, not documentation-repo aspirations.
- Strategic intent is labelled as intent, never as built reality.
- Every material finding has a reconciliation category.
- Already-implemented capabilities are identified (avoids duplicate slices).
- Stale or contradicted assumptions are called out explicitly.
- Unresolved GitHub Issues affecting planning are flagged.
- Architecture-guideline gaps and ADR needs are flagged.
- Eval-readiness gaps are flagged.
- Privacy, data residency, audit, and manual-config risks are addressed.
- No source conflict was silently resolved — all surfaced as findings or blockers.
- Candidate slice areas are labelled candidates only; no slice spec was created here.
- Each candidate has a readiness assessment, main risk, and recommended next action.

---

## 11. Failure Modes to Avoid

- Creating a slice spec instead of a planning context (authority-boundary violation).
- Treating documentation-repo content as current reality (re-implements built features).
- Ignoring GitHub Issues or ADRs that invalidate a candidate.
- Recommending a next slice while blockers remain unresolved.

---

## 13. Handoff to Next Skill

| Condition | Recommended Next Skill |
|---|---|
| Context clean; one or more candidates ready | `slice-sizer` (confirm sizing before spec generation) |
| Candidate needs a spec and sizing is already obvious | `slice-spec-generator` |
| Architecture gap blocks any candidate | `adr-gap-detector` |
| Unresolved GitHub Issue blocks the candidate | Human clarification required |
| Strategic docs should be updated before next cycle | `strategic-doc-update-recommender` |
| Manual-config debt may block new planning | `manual-config-debt-monitor` |
| Privacy or residency concern is unclear | Human clarification required |

State explicitly whether the context is ready for `slice-sizer` or `slice-spec-generator`. Do not claim a slice is ready for coding — this skill only prepares planning context.
