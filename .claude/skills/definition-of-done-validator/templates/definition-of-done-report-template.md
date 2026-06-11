# Definition of Done Validation Report

**Slice ID:** `<slice-id>` | **Slice name:** `<slice-name>` | **Validation date:** `<YYYY-MM-DD>`
**By:** `definition-of-done-validator` (isolated verification) | **Closeout package ref:** `<path or ref>`

---

## 1. Per-Criterion Assessment

*All Process Doc §30 criteria — every one assessed, none omitted. Status: Met / Conditionally met / Not met / Not yet verifiable (or Not applicable where noted).*

| # | DoD Criterion (Process Doc §30) | Status | Evidence reference | Notes |
|---|---|---|---|---|
| 1 | Functionality works | | `<ref>` | |
| 2 | Deterministic tests pass | | `<ref>` | |
| 3 | Required live-model evals pass | | `<ref>` | |
| 4 | Cost and latency budgets reviewed where relevant | | `<ref>` | |
| 5 | High-risk behaviors reviewed by human | | `<ref>` | |
| 6 | Non-blocking failures approved and tracked | | `<ref>` | |
| 7 | Current-state documentation updated | | `<ref>` | |
| 8 | Architecture guidelines and ADRs consistent | | `<ref>` | |
| 9 | Traceability complete for the slice risk level | | `<ref>` | |
| 10 | Manual evidence reviewed | | `<ref>` | |
| 11 | Required GitHub Issues created (or drafts awaiting approval) | | `<ref>` | |
| 12 | Manual-config debt below defined ceiling | | `<ref>` | |
| 13 | Durable implementation lessons promoted | Met / Not yet verifiable (Stage 18) | `<ref>` | |
| 14 | Durable process lessons promoted | Met / Not yet verifiable (Stage 18) | `<ref>` | |
| 15 | Historical artifacts archived | Not yet verifiable (Stage 17 post-merge) | — | |
| 16 | Release Authority approved closeout | Not yet verifiable (Stage 16 gate) | — | Pending Stage 16 |

---

## 2. Discrepancies Found

*Any discrepancy between the closeout package's assertions and the underlying artifacts.*

| # | Package assertion | What the underlying artifact shows | Severity |
|---|---|---|---|
| 1 | `<assertion>` | `<actual>` | Blocking / Non-blocking |

*If none: "No discrepancies found between the closeout package and the underlying artifacts."*

---

## 3. Blocking Items

*DoD criteria Not met where the gap must be resolved before merge.*

| Item | Criterion # | Description | Stage to return to |
|---|---|---|---|
| `<description>` | `<#>` | `<detail>` | Stage `<N>` — `<stage name>` |

*If none: "No blocking items."*

---

## 4. Non-Blocking Items Requiring Release Authority Acceptance

*Conditionally met items — tracked as issues or accepted residual risks — needing explicit Stage 16 sign-off.*

| Item | Criterion # | Description | Issue ref or risk ID |
|---|---|---|---|
| `<description>` | `<#>` | `<detail>` | `#<issue>` or `RR-<N>` |

*If none: "No non-blocking items requiring separate acceptance."*

---

## 5. Overall Recommendation

**Recommendation:** Done / Conditionally done — pending Stage 16 / Not done — return to Stage `<N>`

**Reasoning:** `<concise. For "Not done", list each blocking item. For "Conditionally done", list items the Release Authority must explicitly accept.>`

---

## 6. Advisory Statement

This report is an advisory recommendation produced by `definition-of-done-validator` (isolated verification). Approval authority rests with the Release Authority at Stage 16. This skill does not approve the slice, waive any criterion, or accept residual risk.

Criteria 13–16 (lessons promoted, artifacts archived, Release Authority approval) are not verifiable at Stage 15 and are resolved in Stages 16–18. They are noted "Not yet verifiable" and do not drive a "Not done" recommendation unless the Release Authority explicitly requires them before merge.
