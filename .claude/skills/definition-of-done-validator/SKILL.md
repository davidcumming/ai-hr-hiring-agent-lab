---
name: definition-of-done-validator
description: "Independently validates whether a slice satisfies every definition-of-done criterion with explicit evidence. Use at Stage 15 as the last automated gate before human review."
context: fork
---

# Skill: Definition of Done Validator

**Used at:** Stage 15 — Definition-of-done validation (Orchestration Map §3 stage table)
**Execution model:** `isolated-verification`
**Supports:** Process Doc §30 Definition of Done

---

## 1. Purpose

Independently validate whether the slice satisfies every criterion in the agreed definition of done (Process Doc §30), producing a per-criterion assessment with explicit evidence and an overall done / not-done recommendation. This skill recommends done or not-done; it never approves merge — that is the human Release Authority at Stage 16. It is the last automated gate before that human review, and its core job is to surface any criterion the `closeout-package-builder` missed, softened, or left ambiguous. It must run as an isolated subagent that did not assemble the package it is checking, so the agent that built the evidence cannot grade its own work.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Closeout package | Yes | Primary input; all others verified against it |
| 2 | Traceability matrix | Yes | Cross-checked against the closeout coverage summary |
| 3 | Deterministic test summary | Yes | Verify pass counts match; check skipped tests |
| 4 | Live eval summary | Yes | Verify threshold table; confirm non-blocking failures are accepted |
| 5 | Documentation validation report | Yes | Confirm pass gate reached; no blocking mismatches remain |
| 6 | GitHub Issue summary | Yes | Verify all gaps are tracked; check type and severity |
| 7 | Manual evidence summary | Conditional | Verify debt tracked; check ceiling compliance |
| 8 | Human approval records | Conditional | High-risk reviews (Stage 11), ADR approvals (Stage 6) |

---

## 6. Source Authority Rules

Verify against the underlying artifacts, not the package's own assertions. Code, configuration, tests, evals, and approved manual evidence are implementation truth; GitHub Issues are the source of truth for unresolved work; Process Doc §30 is the authoritative DoD — do not add or remove criteria.

| Criterion | How to verify |
|---|---|
| Functionality works | Deterministic test summary — required tests pass |
| Agent behavior verified | Live eval summary — scenarios pass or non-blocking failures accepted |
| Cost / latency reviewed | Cost/latency section — budgets met or acknowledged |
| High-risk review done | Human approval record from Stage 11 |
| Non-blocking failures approved | Residual risk register — each accepted or a new draft pending Stage 16 |
| Docs updated | Documentation validation report — gate passed |
| ADRs / guidelines consistent | ADR section + guideline updates |
| Traceability complete | Matrix coverage summary — no blocking gaps |
| Manual evidence reviewed | Manual evidence section — present or explicitly N/A |
| Issues created | Issue summary — all gaps tracked; drafts exist for untracked gaps |
| Manual-config debt below ceiling | Debt register or referenced debt monitor |
| Lessons promoted | Closeout or retro note (may be conditional on Stage 18) |
| Historical artifacts archived | Not verifiable at Stage 15 — done post-merge by `archive-package-preparer` |
| Release Authority approved | Not verifiable at Stage 15 — this is the Stage 16 gate; note "pending" |

---

## 7. Process Steps

### Step 1 — Load inputs without contamination
Receive the closeout package and supporting artifacts as provided by the orchestrator. Do not import any memory, notes, or reasoning from the agent that assembled the package.

### Step 2 — Validate each DoD criterion (Process Doc §30)
For every criterion: identify the expected evidence; check it is present and sufficient; record **Met** / **Conditionally met** / **Not met** / **Not yet verifiable at Stage 15**; note the evidence reference. For any Not met, state whether it is a blocker (resolve before merge) or a non-blocking gap (trackable as an issue).

### Step 3 — Cross-check traceability matrix
Independently verify the coverage summary in the package matches the matrix artifact. Flag any numerical discrepancy.

### Step 4 — Cross-check issue tracking
Verify every residual risk in the package is referenced by an existing open issue or by a new draft awaiting approval. Flag any with no tracking.

### Step 5 — Assess the overall state
All Met or Conditionally met (tracked) → **Done**. One or more Not met (blocking) → **Not done** + identify the stage to return to. Conditionally met with items pending Release Authority acceptance → **Conditionally done — pending Stage 16**.

---

## 10. Quality Bar

Before handoff, confirm:

- [ ] This validation was run by an agent that did not assemble the closeout package, with no imported context from it.
- [ ] All 16 Process Doc §30 criteria are present in the per-criterion table — none omitted, even where evidence is missing.
- [ ] Criteria 15 (archived) and 16 (Release Authority approved) are marked "Not yet verifiable", not Met; criteria 13–14 (lessons) are "Not yet verifiable" if Stage 18 has not run, or Met with a reference.
- [ ] Each "Met" cites a specific artifact reference, not "the package says so".
- [ ] Each "Conditionally met" names the condition and tracking issue/risk ID; each "Not met" states what is missing and the stage to return to.
- [ ] The package's merge-readiness recommendation was not treated as verification — each criterion was assessed independently against underlying artifacts.
- [ ] The coverage summary was verified against the traceability matrix; any discrepancy is listed, not silently resolved.
- [ ] Every residual risk has an existing-issue reference or a pending draft; any without tracking is flagged.
- [ ] The overall recommendation is one of three explicit states (not hedged); "Conditionally done" is not used to mask a blocking item.
- [ ] The stage to return to is specified for any "Not done".
- [ ] The advisory statement is included and correctly states the Release Authority approves at Stage 16.
- [ ] The report waives no criterion, accepts no residual risk, approves no closeout, and contains no PHI/PII/Canadian-residency-restricted data.

---

## 11. Failure Modes to Avoid

| Failure mode | Why it matters |
|---|---|
| Treating the package's own summary as verification | Self-reporting is not independent verification; cross-check underlying artifacts |
| Marking "Release Authority approved" as Met before Stage 16 | That criterion is the Stage 16 gate; it is not verifiable here |
| Waiving criteria because the slice is low-risk | All §30 criteria apply; risk tier affects evidence depth, not which criteria exist |
| Omitting criteria not addressed in the package | Omissions are the primary failure mode this validator exists to catch |
| Contaminating from the assembling agent's context | Any leakage invalidates the independence guarantee |

---

## 13. Handoff to Next Skill

If Done or Conditionally done, pass both the closeout package and this report to the Release Authority at Stage 16. If Not done, the `slice-orchestrator` routes back to the identified stage (e.g., Stage 12 for documentation gaps, Stage 11 for eval gaps, Stage 14 for traceability gaps). The Release Authority's Stage 16 decision is informed by but not bound by this recommendation. After merge, `archive-package-preparer` (Stage 17) includes this report in the archive manifest. The skill response must include the per-criterion table (all §30 criteria), an explicit blocking-items list (or "No blocking items"), a non-blocking-items list requiring Release Authority acceptance (or "None"), any discrepancies between package assertions and underlying artifacts, and the overall recommendation (Done / Conditionally done — pending Stage 16 / Not done — return to Stage `<N>`). Obeys the recommend-never-approve and source-of-truth rules in AGENTS.md.
