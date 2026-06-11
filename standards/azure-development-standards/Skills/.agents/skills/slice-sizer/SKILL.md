---
name: slice-sizer
description: Determines whether a proposed slice is small enough to be implemented, tested, evaluated, documented, traced, and approved as one controlled delivery unit. Use before writing a spec.
---
# Skill: Slice Sizer

**Used at:** Stage 1 — Slice sizing (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §11 Slice Sizing Rules, §30 Definition of Done

---

## 1. Purpose

Determine whether a proposed slice is small enough to be implemented, tested, live-evaluated, documented, traced, reviewed, and approved as one controlled delivery unit — protecting the process from a "slice" that is really a milestone. The output is a sizing assessment, not a slice spec; that belongs to `slice-spec-generator`. The sizing question is not "can the coding agent technically implement this?" but "can this be implemented, tested, live-evaluated, documented, traced, reviewed, and approved as one coherent change?"

---

## 3. Do Not Use This Skill For

- Creating the full slice spec (`slice-spec-generator`) or detailed eval-risk profiling (`eval-risk-profiler`).
- Deciding business priority or approving a slice for coding.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Proposed slice name or capability area | Required | Starting point for sizing |
| 2 | Reconciled planning context from `planning-context-reconciler` | Recommended | Current-state baseline and candidate context |
| 3 | Brief description of the intended business/process outcome | Required | Core sizing anchor |
| 4 | Current-state documentation relevant to the area | Recommended | Confirms what already exists |
| 5 | Architecture constraints or guideline references | Recommended | Architecture risk signal |
| 6 | Known dependencies | Recommended | Ordering and split implications |
| 7 | Known GitHub Issues that may affect the slice | Recommended | Unresolved blocker signal |
| 8 | Privacy, data residency, audit, or security constraints | Recommended | High-assurance tier signal |
| 9 | Expected deterministic test/eval scope, if known | Optional | Eval tractability signal |
| 10 | User-provided deadline, size, or sequencing constraint | Optional | Guides split trade-offs |

If inputs are missing, continue only if a reasonable sizing assessment is still possible. Mark all assumptions.

---

## 6. Source Authority Rules

This skill reads from the reconciled planning context, which has already applied the AGENTS.md source-of-truth hierarchy. If a conflict surfaces during sizing, flag it as a blocker and refer back to `planning-context-reconciler`.

---

## 7. Process Steps

1. **Confirm the primary outcome.** Identify the single primary business/process/user outcome. More than one primary outcome strongly indicates a split.
2. **Apply the sizing scorecard** (§7.1). Rate each dimension. Note any `High`/`Poor` rating as a potential split trigger.
3. **Apply the split trigger rules** (§7.2). If any trigger fires, recommend a split.
4. **Estimate risk tier (rough)** (§7.3). If the slice is High-Assurance and broad, recommend a split to isolate the sensitive behaviour.
5. **Assess manual-config / source-control risk** (§7.4).
6. **Assess privacy, data residency, auditability** (§7.5).
7. **Determine the sizing decision** (§7.6) — exactly one category.
8. **If split-recommended, propose sub-slices.** For each: name, primary outcome, reason to be separate, dependencies, estimated risk tier, suggested order, and whether it is ready for `slice-spec-generator`.
9. **Record blockers and open questions.** Distinguish sizing blockers from spec-generation blockers.
10. **State the recommended next skill.**

### 7.1 Sizing Scorecard

| Dimension | Good Signal | Split / Block Signal |
|---|---|---|
| **Outcome coherence** | One clear primary outcome in one or two sentences | Multiple unrelated outcomes; unclear intent |
| **Workflow breadth** | One workflow or one transition within a workflow | Multiple independent workflows; multiple personas at once |
| **Architecture impact** | Fits existing guidelines; at most one ADR needed | Multiple unrelated ADRs; new service categories; many stack surfaces at once |
| **Data and state impact** | One well-defined data element or state transition | Multiple persistence systems; memory, audit, identity, permissions at once |
| **Deterministic testability** | Specific, verifiable acceptance criteria; understandable test scope | Vague criteria; very broad coverage across unrelated modules |
| **Live-eval tractability** | Focused behaviour set; few high-risk scenarios | Eval set too large/ambiguous; many separate high-risk areas |
| **Documentation impact** | One coherent current-state section updated | Many unrelated documentation areas need updating |
| **Privacy/data/audit risk** | Sensitive data isolated or not involved | High-risk data buried in a broad slice; multiple privacy surfaces at once |
| **Manual-config/source-control risk** | No portal config, or one well-understood surface | Multiple stack portal surfaces; source-control feasibility unclear |
| **Closeout complexity** | One reviewable closeout package; clear traceability | Unresolved items span unrelated areas; confusing traceability |

### 7.2 Split Trigger Rules

Recommend a split if any is true: more than one primary outcome; multiple independent workflows; multiple unrelated ADRs; several new services/stack surfaces at once; cannot be evaluated with a focused bounded eval set; would need more than one closeout package; acceptance criteria cannot fit a concise reviewable set; the live eval set becomes too broad to interpret; a high-assurance behaviour is mixed with lower-risk changes that could ship earlier; the slice is essentially a milestone.

Proposed sub-slices should each have one primary outcome, be independently testable/evaluable/documentable, preserve dependency order, avoid premature architecture expansion, avoid hiding high-risk behaviour, and allow useful progress without requiring everything at once.

### 7.3 Risk Tier Awareness (Rough Estimate)

For sizing only; full profiling belongs to `eval-risk-profiler`.

| Tier | Sizing Meaning |
|---|---|
| Low | Small internal behaviour; limited risk; no sensitive data; no authoritative decision output. |
| Standard | Normal workflow behaviour; manageable eval scope; limited sensitive-data exposure. |
| High-Assurance | Approvals; evidence claims; PHI/PII; external sharing; memory; permissions; irreversible state; user-facing authoritative outputs. |

If High-Assurance and broad, splitting is strongly preferred to isolate the sensitive behaviour.

### 7.4 Manual-Config / Source-Control Debt Awareness

If the slice likely introduces portal/low-code config (Azure, Power Platform, Copilot Studio, Azure AI Foundry), flag: which surfaces; whether config can be exported or IaC'd; evidence-capture need; potential follow-up issue; and whether unresolved manual-config debt from prior slices may hit the debt ceiling. Do not assume portal config appears in source control automatically.

### 7.5 Privacy, Data Residency, and Auditability Awareness

If the slice touches healthcare/PHI/PII, sensitive business data, Canadian residency, audit logs, retention, or external sharing: consider splitting to isolate the sensitive behaviour, do not bury high-risk data in a broad slice, and flag for `eval-risk-profiler` at Stage 4.

### 7.6 Sizing Decision Categories

Return exactly one:

| Decision | Meaning |
|---|---|
| `accept-as-one-slice` | Coherent, bounded, testable, live-evaluable, closeout-ready as one unit. |
| `split-recommended` | Multiple outcomes/workflows/architecture changes/eval areas/closeout units. Sub-slices follow. |
| `blocked-pending-clarification` | Requirements, architecture/privacy constraints, or expected behaviour are unclear. |
| `blocked-pending-adr` | An architecture decision is required first. |
| `blocked-pending-debt-burndown` | Manual-config/source-control debt, unresolved Issues, or known limitations make new planning unsafe. |

---

## 9. Output Format

Use `templates/slice-sizing-assessment-template.md`. The decision must be one of the five §7.6 categories; do not drift into a full slice spec.

---

## 10. Quality Bar

Before handoff, confirm:

- The primary outcome is identified, and the assessment checks for multiple primary outcomes / independent workflows / a milestone-in-disguise.
- The decision is one of the five approved categories with a specific rationale referencing the scoring dimensions.
- The recommendation considers tests, live evals, and closeout burden — not just coding effort.
- Architecture-guideline fit and ADR needs were considered; architecture risk is not hidden in a broad slice.
- Data/state and memory impact were considered.
- PHI/PII, Canadian residency, auditability, and external sharing were considered; high-assurance behaviour is not buried in a lower-risk slice.
- Portal/low-code config risk, source-control feasibility, evidence-capture needs, and debt-ceiling risk were considered.
- Split recommendations are practical, ordered by dependency, and explained.
- Blockers are explicit with blocking vs. non-blocking status for both sizing and spec generation.
- The recommended next skill is stated; the output is not a full slice spec.

---

## 11. Failure Modes to Avoid

- Accepting a slice because it is technically implementable while ignoring eval or closeout burden (fails at Stage 3, 4, or 15).
- Hiding high-risk behaviour inside a broad slice.
- Ignoring architecture-guideline gaps (blocked at Stage 6 after coding starts) or manual-config debt (debt-ceiling surprise at Stage 19).
- Splitting so aggressively that sub-slices are useless, or recommending an order without explaining dependencies.
- Referencing the retired `risk-tier-classifier` — use `eval-risk-profiler` at Stage 4.

---

## 13. Handoff to Next Skill

| Condition | Recommended Next Skill |
|---|---|
| `accept-as-one-slice` | `slice-spec-generator` |
| `split-recommended` | Back to candidate selection; then `slice-sizer` on each sub-slice in turn |
| `blocked-pending-adr` | `adr-gap-detector` |
| `blocked-pending-clarification` | Human clarification required |
| `blocked-pending-debt-burndown` | `manual-config-debt-monitor` |

Do not claim the slice is ready for coding. At most, state it is ready for `slice-spec-generator`.
