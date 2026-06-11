# Slice Closeout Package

**Slice ID:** `<slice-id>` | **Slice name:** `<slice-name>` | **Branch:** `<feature/branch-name>`
**Closeout date:** `<YYYY-MM-DD>` | **Risk tier:** Low / Standard / High-assurance | **By:** `closeout-package-builder`

---

## 1. Implementation Summary

*What was built. Describe implemented behavior, not spec intent. Include key technical decisions and any Azure, Power Platform, Copilot Studio, or Azure AI Foundry components created or changed.*

`<summary>`

### 1.1 Scope delivered
- `<delivered item>`

### 1.2 Scope explicitly out of scope for this slice
- `<out-of-scope item>`

### 1.3 Deviation summary
*Summarize here if deviations were recorded; detail in §2.*
`<summary or "No deviations recorded.">`

---

## 2. Deviation Log

*Reference or reproduce the log from `implementation-deviation-capture`. If none: "No deviations from spec."*

| Deviation ID | Spec item | Planned | Implemented | Rationale | Impact on current-state docs | Issue ref |
|---|---|---|---|---|---|---|
| DEV-1 | `<spec item>` | `<planned>` | `<implemented>` | `<rationale>` | `<impact>` | `#<issue>` or — |

---

## 3. Traceability Matrix

*Reference the matrix from `traceability-matrix-builder`; include the coverage summary only, not the full matrix.*

**Matrix reference:** `<path or artifact ref>`

| Category | Total | Covered | Partial | Untested | Deferred | Untestable |
|---|---|---|---|---|---|---|
| Functional requirements | | | | | | |
| Business rules | | | | | | |
| Acceptance criteria | | | | | | |
| Agent behavior requirements | | | | | | |
| High-risk behaviors | | | | | | |
| **Totals** | | | | | | |

---

## 4. Deterministic Test Summary

**Test run reference:** `<run ID or ref>` | **Run date:** `<YYYY-MM-DD>`

| Category | Total | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit tests | | | | |
| Integration tests | | | | |
| Workflow / state tests | | | | |
| **Totals** | | | | |

**Skipped tests:** `<list with reason, or "None">` | **Test gaps carried to issues:** `<issue refs or "None">`

---

## 5. Live Eval Summary

**Eval run reference:** `<run ID or ref>`
**Model version:** `<version>` | **Prompt version:** `<version>` | **Tool schema version:** `<version>` | **Orchestration version:** `<version>`

| Scenario ID | Scenario name | Result | Threshold met? | Notes |
|---|---|---|---|---|
| S-01 | `<name>` | Pass / Fail / Non-blocking | Yes / No | |

**High-risk behavior review:** `<human review record or "N/A — no high-risk behaviors">`
**Non-blocking failures accepted:** `<list with issue refs, or "None">`

---

## 6. Cost and Latency Summary

*Required when cost/latency was an eval criterion. Otherwise: "Not applicable for this slice — reason: `<reason>`."*

| Metric | Budget | Measured | Within budget? |
|---|---|---|---|
| P90 response latency | `<budget>` ms | `<measured>` ms | Yes / No |
| Average token cost per call | `<budget>` | `<measured>` | Yes / No |
| Max tool-call chain depth | `<budget>` | `<measured>` | Yes / No |

---

## 7. Manual Evidence Summary

*Required when portal/low-code config was captured. Otherwise: "Not applicable — no manual configuration for this slice."*

**Evidence reference:** `<path or ref>`

| Config item | Resource / component | Evidence type | Source-control status | Debt issue ref |
|---|---|---|---|---|
| `<item>` | `<resource>` | Screenshot / Portal note / Export | Committed / Not committed | `#<issue>` or — |

**Source-control debt summary:** `<description or "None">`

---

## 8. ADRs Created or Updated

| ADR ID | Title | Status | Decision summary | Link |
|---|---|---|---|---|
| ADR-`<N>` | `<title>` | Approved / Draft | `<one sentence>` | `<ref>` |

*If none: "No ADRs created or updated during this slice."*

---

## 9. Architecture Guideline Updates

| Guideline section | Change summary | Effective date | Related ADR |
|---|---|---|---|
| `<section>` | `<change>` | `<date>` | ADR-`<N>` |

*If none: "No architecture guideline updates during this slice."*

---

## 10. Master Documentation Updates

| Document | Section(s) updated | Summary of change |
|---|---|---|
| Current-state docs | `<sections>` | `<summary>` |
| Actual architecture | `<sections>` | `<summary>` |

**Documentation validation gate:** Passed / Passed with non-blocking conditions (see §11) / `<details>`

---

## 11. Evidence Gaps

*All inputs unavailable or incomplete; the Release Authority must know these before approving merge.*

| Gap | Affected section | Severity | Disposition |
|---|---|---|---|
| `<description>` | `<section>` | `<severity>` | `<tracked in #N / accepted / must resolve before merge>` |

*If none: "No evidence gaps."*

---

## 12. Residual Risk Register

*All accepted risks that do not block merge candidacy. Each requires explicit Release Authority acceptance at Stage 16.*

| Risk ID | Description | Source | Severity | Disposition | Required action | Issue ref |
|---|---|---|---|---|---|---|
| RR-1 | `<description>` | `<stage/artifact>` | High / Medium / Low | Accepted / Deferred | `<action or "none">` | `#<issue>` or — |

*If none: "No residual risks identified."*

---

## 13. GitHub Follow-up Issue Summary

| Issue | Type | Severity | Title | Status |
|---|---|---|---|---|
| `#<N>` or Draft-`<N>` | `<type>` | `<severity>` | `<title>` | Existing open / New draft — awaiting approval |

*If none: "No follow-up issues."*

---

## 14. Merge-Readiness Recommendation

**Recommendation:** Ready for Release Authority review / Conditionally ready / Not ready

**Reasoning:** `<concise explanation; for "Not ready", list blocking items.>`

**Items that must be resolved before merge:**
- `<item or "None">`

**Items accepted as post-merge follow-up (tracked in issues):**
- `<item or "None">`

---

## 15. Human Approval Checklist

*The Release Authority completes this at Stage 16. Mark each complete / conditionally complete (issue tracked) / incomplete.*

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Functionality works — deterministic tests pass | | |
| 2 | Required live-model evals pass (or non-blocking failures approved) | | |
| 3 | Cost and latency budgets reviewed | | |
| 4 | High-risk behaviors reviewed by human | | |
| 5 | Current-state documentation updated and validated | | |
| 6 | Architecture guidelines and ADRs consistent | | |
| 7 | Traceability complete for the slice risk level | | |
| 8 | Manual evidence reviewed | | |
| 9 | Required GitHub Issues created (after approval of drafts) | | |
| 10 | Manual-config debt below defined ceiling | | |
| 11 | All residual risks explicitly accepted | | |
| 12 | Merge readiness approved | | |

**Release Authority signature / record:** `<name, role, date — or "Pending Stage 16 review">`

---

*Assembled by `closeout-package-builder`. Approval authority rests with the Release Authority at Stage 16. No approval is implied by this document.*
