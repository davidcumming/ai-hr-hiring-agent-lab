# Traceability Matrix

**Slice ID:** `<slice-id>` | **Slice name:** `<slice-name>` | **Matrix date:** `<YYYY-MM-DD>` | **By:** `traceability-matrix-builder`

## Inputs used

| Input | Version / reference | Available? |
|---|---|---|
| Slice spec | `<ref>` | Yes / No / Partial |
| Eval contract | `<ref>` | Yes / No / Partial |
| Deterministic test summary | `<ref>` | Yes / No / Partial |
| Live eval summary | `<ref>` | Yes / No / Partial |
| Manual evidence summary | `<ref>` | Yes / No / N/A |
| Implementation summary / deviation log | `<ref>` | Yes / No / Partial |
| Open GitHub Issues at construction time | `<snapshot date or list>` | Yes / No |

---

## 1. Full Coverage Table

Status values: Covered / Partial / Untested / Deferred / Untestable. Evidence type: Test / Eval / Manual / —. Issue ref: `#<issue>` or —.

### 1.1 Functional Requirements

| ID | Requirement summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| FR-1 | `<short text>` | | | `<test name / eval scenario ID / evidence ID>` | |

### 1.2 Business Rules

| ID | Rule summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| BR-1 | `<short text>` | | | | |

### 1.3 Acceptance Criteria

| ID | Criterion summary | Status | Evidence type | Evidence reference | Issue ref |
|---|---|---|---|---|---|
| AC-1 | `<short text>` | | | | |

### 1.4 Agent Behavior Requirements

| ID | Behavior summary | Status | Eval scenario ID | Eval result | Issue ref |
|---|---|---|---|---|---|
| AB-1 | `<short text>` | | `<scenario-id>` | Pass / Fail / Non-blocking | |

*A live eval scenario reference is required; deterministic tests alone are insufficient for agent behavior items.*

### 1.5 High-Risk Behaviors

| ID | Behavior summary | Risk tier | Status | Eval scenario ID | Human review record | Issue ref |
|---|---|---|---|---|---|---|
| HRB-1 | `<short text>` | High-assurance | | | `<review ref or "none">` | |

---

## 2. Coverage Summary

| Category | Total | Covered | Partial | Untested | Deferred | Untestable |
|---|---|---|---|---|---|---|
| Functional requirements | | | | | | |
| Business rules | | | | | | |
| Acceptance criteria | | | | | | |
| Agent behavior requirements | | | | | | |
| High-risk behaviors | | | | | | |
| **Totals** | | | | | | |

**Overall coverage rate (informational):** `<(covered + partial) / total>`% — every gap is listed below regardless of percentage.

---

## 3. Gap List

*Every item with status Partial, Untested, Deferred, or Untestable.*

### 3.1 Untested

| Item ID | Item summary | Gap reason | Blocking? | Issue candidate? |
|---|---|---|---|---|
| `<ID>` | `<text>` | `<reason>` | Yes / No | Yes / No |

### 3.2 Partial (non-blocking failures accepted)

| Item ID | Item summary | Passing scenarios | Failing scenarios | Issue ref |
|---|---|---|---|---|
| `<ID>` | `<text>` | `<list>` | `<list>` | `#<issue>` |

### 3.3 Deferred

| Item ID | Item summary | Deferral reason | Deviation log ref | Issue ref |
|---|---|---|---|---|
| `<ID>` | `<text>` | `<reason>` | `<ref>` | `#<issue>` or — |

### 3.4 Untestable

| Item ID | Item summary | Untestable rationale | Human review record | Issue ref |
|---|---|---|---|---|
| `<ID>` | `<text>` | `<rationale>` | `<ref or "none">` | `#<issue>` or — |

---

## 4. Issue Candidate List

*Structured input for `github-issue-drafter`; one row per candidate.*

| # | Traceable item ref | Suggested type | Severity | Summary sentence | Notes for drafter |
|---|---|---|---|---|---|
| 1 | `<item ID>` | `test-gap` / `eval-failure` / `technical-debt` / `documentation-gap` / `security-risk` / other | High / Medium / Low | `<one sentence>` | `<context>` |

*If none: "No new issue candidates. All gaps are covered by existing open issues."*

---

## 5. Caveats and Limitations

*Any input unavailable, incomplete, or assumed.*

- `<caveat>`

---

## 6. Matrix Status

| Check | Result |
|---|---|
| All traceable items present | Yes / No — `<detail>` |
| All gaps explicitly listed | Yes / No |
| Issue references for unresolved items only | Yes / No |
| No untested agent behavior items without rationale | Yes / No |
| Ready to pass to `closeout-package-builder` | Yes / Blocked — `<reason>` |
