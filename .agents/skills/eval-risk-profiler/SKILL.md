---
name: eval-risk-profiler
description: Characterizes the full eval risk surface of a Stage 3-approved slice in one pass. Use when designing evals (Stage 4) to set risk tier, failure modes, data governance, and cost/latency criteria.
---
# Skill: Eval Risk Profiler

**Used at:** Stage 4 — Eval design (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §18 Testing and Eval Requirements, §19 Live-Model Eval Rules, §20 Cost and Latency as Eval Dimensions, §23 Privacy, Data Residency, and Auditability

---

## 1. Purpose

Characterize the full eval risk surface of a Stage 3-approved slice in a single pass, before `eval-contract-designer` hardens the contract. The output is an **eval risk profile** with four sections: (A) risk tier + required test/eval package, (B) unsafe failure-mode register, (C) eval-data governance assessment, (D) cost/latency criteria. This skill recommends a tier and flags blockers; it never approves residual risk — that is a human gate (see AGENTS.md, Authority and human gates).

---

## 3. Do Not Use This Skill For

- Hardening the eval contract or writing scenarios/tests — `eval-contract-designer`, `deterministic-test-author`.
- Classifying actual eval failures — `eval-failure-classifier`.
- Deciding slice-spec readiness — `slice-readiness-reviewer` (Stage 3).

---

## 4. Required Inputs

Proceed only if a defensible profile is achievable; mark missing inputs as assumptions or blockers.

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Slice spec (Stage 3 approved) | Mandatory | Source of behaviour and indicators |
| 2 | Draft eval contract | Optional | Use slice-spec seeds if absent |
| 3 | Reconciled planning context | Recommended | Current-state reality, lessons, known limitations |
| 4 | Architecture guidelines + relevant ADRs | Required | Residency, tool-use, authorization risk |
| 5 | Privacy/data-governance/auditability policy | Required | Drives Section C; if absent, escalate as blocker — do not assume permissive defaults |
| 6 | Current-state documentation | Required | Distinguishes new risk from continuation of existing behaviour |
| 7 | Known limitations and GitHub Issues | Required | Existing debt may elevate tier |
| 8 | Model/tool usage assumptions | Required | Drives Section D |
| 9 | Cost/latency budgets | Optional | If absent, produce recommendations for human ratification |
| 10 | Test/eval strategy | Required | Calibrates tier-appropriate package |

---

## 7. Process Steps

Each section applies its named rubric (in `rubrics/`); do not restate rubric content here, work through it. Begin by listing which inputs are present, absent, or assumed.

### Section A — Risk Tier (`risk-tier-rubric.md`)

1. Work through every indicator in the scorecard; determine whether any high-assurance trigger applies.
2. Assign `Low`, `Standard`, or `High-Assurance`. Under uncertainty use `Standard with unresolved risk`, `High-Assurance pending clarification`, or `Blocked pending clarification`.
3. Apply the **highest** applicable tier — never average down. Tier is about behavioural consequence, not coding complexity.
4. If the high-assurance element is separable, recommend splitting the slice.
5. Specify the required test/eval package for the tier (§7.1).

### Section B — Unsafe Failure-Mode Register (`unsafe-failure-mode-rubric.md`)

For each candidate failure mode (drawn from functional requirements, business rules, agent behaviours, edge cases): describe the unacceptable behaviour; state why it creates risk (safety/privacy/trust/workflow/evidence/compliance); recommend blocking vs non-blocking; recommend covering eval scenarios; recommend whether human review is needed. Do not omit high-risk modes because they seem unlikely. If a mode cannot be evaluated with available eval data, flag it as a blocker.

### Section C — Eval-Data Governance Assessment (`privacy-residency-audit-rubric.md`)

1. Determine whether live eval scenarios are required. A deterministic-only path is allowed only if the slice has no model, prompt, tool-orchestration, agent-behaviour, or behaviour-affecting model dependency (the non-agentic carve-out).
2. Inventory every data type live scenarios would represent; assess each for PHI, PII, sensitive business data, Canadian residency, and audit retention.
3. Determine whether synthetic data is sufficient, partial, or insufficient. Where real/production-like data may be required, flag a blocker pending explicit governance approval.
4. Address external-artifact handling (storage + residency) and auditability (what must be logged/retained).
5. For Canadian projects, confirm eval infrastructure and storage stay in approved Canadian Azure regions. Residency is a hard constraint, not informational.

### Section D — Cost/Latency Criteria (`cost-latency-rubric.md`)

For each scenario type (standard, high-risk, regression) identify the response-time envelope, token budget (per call and per workflow run), and max model/tool-call count for normal and degraded paths. Propose a measurement approach (Azure Monitor, Application Insights, Foundry metrics, or equivalent) and recommend threshold values. If no budget exists, flag for human ratification — "fast enough" is not a threshold. Note disproportionately expensive/slow scenarios.

### Compile and review

Compile into `templates/eval-risk-profile-template.md`. Resolve inter-section inconsistencies (e.g., a failure mode implying a higher tier than assigned, or a governance blocker that prevents a required eval scenario). Confirm the profile is complete enough for `eval-contract-designer`; list blockers that must clear first.

---

### 7.1 Required Test/Eval Package by Tier

| Package element | Low | Standard | High-Assurance |
|---|---|---|---|
| Relevant deterministic tests | Required | Required | Required |
| Slice-specific live evals | Required unless non-agentic carve-out | Required unless non-agentic carve-out | Required (expanded) |
| Core regression evals | Optional/N/A with rationale | Required unless N/A with rationale | Required |
| Repeated-run thresholds (Process §19.1) | 3-5 runs, no critical failures, acceptable qualitative result | 5-10 runs, ≥80% pass | 20+ runs, ≥90% pass + zero critical failures; safety/privacy/evidence-critical: zero critical + stricter rubric threshold |
| Adversarial scenarios | Not required | Recommended for key risks | Required |
| Human review (high-risk) | Not required | Conditional | Required |
| Unsafe failure-mode analysis | Lightweight | Required | Required (exhaustive) |
| Privacy/data governance review | Only if data involved | Required if data involved | Required |
| Auditability review | Not required | Conditional | Required |
| Cost/latency evals | Optional | Recommended | Required |
| Residual-risk human approval | Not required | Conditional | Required |
| GitHub Issues for accepted non-blocking failures | Not required | Required | Required |
| Traceability | Lightweight | Standard | Full |

---

## 9. Output Format

Use `templates/eval-risk-profile-template.md`. Reference any eval data by governance-approved location; do not place real PHI/PII in the profile body. If live evals are not applicable, record the non-agentic carve-out statement explicitly.

Place the profile where `eval-contract-designer` can read it in the same Stage 4 session (typically `/docs/delivery/slices/<slice-id>/eval-risk-profile.md`).

---

## 10. Quality Bar

Before handoff, confirm:

- All risk indicators assessed; any `Unknown` flagged as assumption or blocker.
- Tier is explicit and follows the **highest** applicable indicator (not averaged down).
- Required package matches the tier and follows Process §19.1 thresholds.
- Any deterministic-only completion documents the non-agentic carve-out.
- Failure-mode register is complete for the tier (≥3 for Standard, ≥6 for High-Assurance) and exhaustive for high-risk behaviours.
- Every data type inventoried; PHI/PII/residency assessed; no real PHI/PII proposed without documented governance approval.
- Governance issues are flagged as blockers, not informational notes.
- Cost/latency thresholds are measurable or explicitly marked for human ratification; none left as "no limit" without justification.
- Sections are internally consistent; all blockers listed and marked blocking vs non-blocking for eval-contract design.
- Profile does not approve residual risk; implementation and process lessons are not mixed in.

---

## 13. Handoff to Next Skill

**Next skill:** `eval-contract-designer`.

Pass the completed profile (path or inline), the risk tier + rationale, the failure-mode register (Section B → contract's unsafe-failure section), the governance assessment (Section C → constrains permissible scenarios), the cost/latency criteria (Section D → contract thresholds), and all open blockers marked as eval-contract blockers vs human-gate items. If hard blockers remain (no governance basis, missing cost/latency approval, high-assurance with no human-review plan), `eval-contract-designer` must not proceed until they clear.

Do not claim the eval contract is ready — this skill produces only the risk profile.
