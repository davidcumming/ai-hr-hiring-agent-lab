---
name: eval-contract-designer
description: "Converts slice requirements into a hardened eval contract defining how a slice is tested before coding begins. Use at Stage 4 to set deterministic and live-model expectations."
---

# Skill: Eval Contract Designer

**Used at:** Stage 4 — Eval design (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §13 Eval-Driven Requirements, §18 Testing and Eval Requirements, §19 Live-Model Eval Rules, §21 Mandatory Re-Eval Triggers, §24 Traceability

---

## 1. Purpose

Convert slice requirements into a hardened **eval contract**: the definitive record of how a slice will be tested and evaluated before coding begins — deterministic test expectations and live-model eval scenarios with clear pass/fail criteria, plus the selection of existing regression evals that must run for this slice. A slice is not ready for implementation until its expected behaviours are expressed this way. This skill produces a design artifact and enforces (never weakens) the tier and failure modes set by `eval-risk-profiler`; it does not approve residual risk (see AGENTS.md, Authority and human gates). The risk profile is a required input — if it is blocked or incomplete, do not proceed.

---

## 3. Do Not Use This Skill For

- Producing the risk profile — `eval-risk-profiler`.
- Running evals or summarizing/classifying actual results — `live-eval-runner`, `eval-result-summarizer`, `eval-failure-classifier`.
- Regression selection as a standalone activity outside Stage 4 — it is a section of this contract, not a separate document.

---

## 4. Required Inputs

Proceed only if a complete contract is achievable; mark gaps as blockers.

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Approved slice spec (Stage 3) | Mandatory | Source of behavioural requirements |
| 2 | Eval risk profile (from `eval-risk-profiler`) | Mandatory | Tier, failure modes, governance + cost/latency constraints |
| 3 | Test/eval strategy | Required | Structural conventions (location, naming, thresholds) |
| 4 | Current regression eval inventory | Required for regression selection | Names, descriptions, coverage areas |
| 5 | Privacy/eval-data guidance | Required | Confirms permitted eval-data types |
| 6 | Architecture guidelines + relevant ADRs | Required | Tools, memory, orchestration patterns to test |
| 7 | Model/prompt/tool/workflow change info | Required for regression selection | Determines triggered regressions |
| 8 | Reconciled planning context, known limitations, GitHub Issues | Recommended | May constrain what can be reliably tested |

---

## 7. Process Steps

### 7.1 Eval-Driven Requirements Rule (Process §13)

A slice is not ready for coding until: every major functional requirement has a deterministic test, a live eval scenario, or a documented reason neither applies; every unsafe failure mode from the profile has ≥1 detecting scenario; pass/fail criteria are observable (never "the output is good"); ambiguous requirements are flagged, not narrowed. For every significant behaviour the contract answers: what should the agent do / not do; what happens when required info is missing, ambiguous, conflicting, or out-of-scope/unsafe/unauthorized; which behaviours are deterministic vs agentic; whether the non-agentic carve-out applies; which failures block merge; which may be non-blocking only with human release authority + a tracked issue.

### 7.2 Contract Components

Build each section into `templates/eval-contract-template.md`.

- **Behavioural contract** — concise, evaluable statement of observable behaviour, tight enough to score pass/fail.
- **Deterministic test expectations** — `DT-NNN`, description, related FR/BR/AB, observable pass condition. Check systematically: state transitions/persistence, data validation + required fields, authorization/permission checks, tool-call routing, API response format + error codes, audit-event creation (field/timestamp/actor), export/notification format, configuration validation, error/exception handling.
- **Live-model eval scenarios** — `LE-NNN`, name, input pattern, expected behaviour, unacceptable behaviour, observable pass criteria, runs/threshold, risk level. Minimum categories: happy path; missing required info (agent asks, not assumes); ambiguous input (asks, not guesses); out-of-scope/unauthorized (refuses/redirects); each unsafe failure mode; conflicting info (surfaces, not arbitrarily resolves); evidence grounding (no assertion without source). High-Assurance: add adversarial scenarios.
- **Unsafe failure modes** — import Section B of the profile; map each to covering `LE` IDs, confirm sufficiency, add scenarios for any gap. Do not silently downgrade a blocking classification.
- **Pass/fail rubric** — use `rubrics/eval-pass-fail-rubric.md`, customize per slice. A partial pass must have an explicit per-scenario meaning (not "mostly ok"). A blocking fail prevents merge without human release authority sign-off and a tracked issue.
- **Repeated-run thresholds** — §7.3 table; defaults from Process §19.1, may be tightened by the profile.
- **Human review** — specify which scenarios need a reviewer, the review focus, and whether it must pass before the merge gate. High-Assurance slices always require ≥1 human-review point (§18).
- **Eval-data constraints** — import Section C; per scenario note data category, synthetic feasibility, fixtures. Never write scenarios requiring real PHI/PII without confirmed, documented governance approval.
- **Cost/latency expectations** — import Section D; per scenario note max response time, token/cost budget, max model/tool-call count, and what counts as a cost/latency failure. Mark thresholds needing human ratification as provisional.
- **Regression eval selection** — §7.4.
- **Traceability seed** — map every FR/BR/AB/AC to zero-or-more DT IDs, LE IDs, UFM IDs, and the expected evidence artifact. Any requirement with no DT and no LE must carry an explicit documented reason.

### 7.3 Repeated-Run Thresholds (Process §19.1)

| Scenario type | Runs / threshold |
|---|---|
| Low-risk | 3-5 runs, no critical failures, acceptable qualitative result |
| Standard | 5-10 runs, ≥80% pass |
| High-risk | 20+ runs, ≥90% pass, zero critical failures + human review |
| Safety/privacy/evidence-critical | 20+ runs, zero critical failures, stricter rubric-defined threshold + human review |
| Adversarial | Inherit applicable risk-tier minimum or stricter |
| Regression | Match original stored threshold; else applicable risk-tier minimum |

A single successful run is never evidence. Do not use a smaller high-risk sample unless the human release authority explicitly lowers the tier and records the rationale.

### 7.4 Regression Eval Selection

Triggers (Process §21): a regression eval must be included if the slice introduces any model-version, prompt-template, tool-schema, orchestration-logic, or permissions/memory/evidence-handling change; changes a behaviour an existing eval covers; or adds behaviour closely related to one's coverage area.

Method: for each eval in the inventory, decide whether the slice changes any behaviour it covers, and classify `Required` / `Optional` / `Not applicable`. Document the triggering change for each `Required`, and the exclusion rationale for each `Not applicable`. Do not invent evals absent from the inventory — note them as new regression candidates that promote after the slice closes via `regression-promotion-recommender`. Core regression evals cannot be skipped without documented human approval.

### 7.5 Requirement Ambiguity Rule

If a requirement cannot become a testable scenario because the expected behaviour is unclear, do not narrow or reinterpret it. Mark it `requirement-clarification-required` and block handoff to implementation planning. Block when: the expected agent decision is unspecified; the correct response depends on missing business policy; an acceptance criterion is not observable (e.g., "should be helpful"); the agent is to "use judgment" without a rubric; the acceptable/unacceptable boundary is unclear; or privacy/data-handling rules for an edge case are unresolved.

---

## 9. Output Format

Use `templates/eval-contract-template.md` — it contains the full contract structure plus the **Live-Eval Scenarios** section (for complex standalone scenario write-ups) and the **Regression-Eval Selection** section (for large inventories). Reference all eval data by governance-approved location; place no PHI/PII in the contract body, and confirm PHI-like artifacts are not committed to the repo. Store the contract where the Coding Agent and Eval Execution Agent can read it (typically `/docs/delivery/slices/<slice-id>/eval-contract.md`).

---

## 10. Quality Bar

Before handoff, confirm:

- Risk tier from the profile is confirmed and matches the contract; the behavioural contract is scoreable as pass/fail.
- Every major FR maps to ≥1 DT or LE, or has a documented no-coverage reason; every unsafe failure mode has ≥1 covering scenario.
- Every live scenario has an observable, non-vague pass criterion and separates expected from unacceptable behaviour, with runs/threshold and risk level.
- High-risk scenarios follow Process §19.1 (20+ runs, ≥90% pass, zero critical failures, human review); safety/privacy/evidence-critical require zero critical + stricter threshold.
- No failure mode silently downgraded from blocking; blocking-fail triggers are explicitly listed for this slice.
- Regression evals classified with documented Required/Not-Applicable rationale; skipped core evals carry human approval or a flag for it; new candidates listed.
- Eval-data constraints prohibit real PHI/PII without governance approval; synthetic plan confirmed; Canadian residency noted; PHI-like artifacts not committed.
- Cost/latency thresholds present for all applicable scenarios, marked Ratified or Provisional; none "no limit" without justification.
- Traceability seed covers all FR/BR/AB/AC; ambiguous requirements listed as blockers, not resolved.
- The contract does not claim evals have been run and does not approve residual risk.

---

## 13. Handoff to Next Skill

**Next skill:** `implementation-plan-builder` (Stage 5).

Pass the completed contract (path or inline), the risk tier + required test/eval package, deterministic test expectations (informs Stage 8 code tests), unsafe failure modes (what implementation must guard against), eval-data constraints (synthetic fixtures to prepare), cost/latency thresholds (implementation performance targets), required regression evals (must pass before the eval gate), and all open blockers marked for whether they require human action before coding. If any blocking ambiguity or governance blocker remains unresolved, `implementation-plan-builder` must be blocked until it clears.

Do not claim the slice is ready for merge or closeout — this skill produces only the eval contract.
