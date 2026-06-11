# Deterministic Test Plan: <Slice Name>

## 1. Plan Metadata

| Field | Value |
|---|---|
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Plan Date | `<yyyy-mm-dd>` |
| Plan Author | `<agent/user>` |
| Linked Slice Spec | `<path or reference>` |
| Linked Eval Contract | `<path or reference>` |
| Test Framework(s) | `<e.g., pytest 8.x, xUnit 2.x, Vitest 2.x, Power Apps Test Studio>` |
| Status | `Draft / Final / Tests Written` |

---

## 2. Test Framework and Conventions Summary

Directory layout, naming conventions, fixture management, how external dependencies are mocked, CI/CD trigger, coverage tooling: `<description>`

---

## 3. Test Coverage Map

One row per requirement, business rule, or acceptance criterion.

| Requirement / Criterion ID | Description | Test File | Test Name(s) | Test Type | Status |
|---|---|---|---|---|---|
| `<AC-01>` | `<description>` | `<path>` | `<test name(s)>` | `Unit / Integration / Workflow-state` | `Covered / Gap — see §5 / Gap — deferred` |

**Coverage summary:**

| Type | Total | Covered | Gap |
|---|---|---|---|
| Eval contract deterministic expectations | `N` | `N` | `N` |
| Slice spec acceptance criteria | `N` | `N` | `N` |
| Slice spec business rules | `N` | `N` | `N` |

---

## 4. Tests Added

### 4.1 Unit Tests

| Test File | Test Name | What It Verifies | Mocked Dependencies |
|---|---|---|---|
| `<path>` | `<test_name>` | `<behaviour>` | `<mocked calls>` |

### 4.2 Integration Tests

| Test File | Test Name | What It Verifies | External Dependencies Mocked |
|---|---|---|---|
| `<path>` | `<test_name>` | `<behaviour>` | `<list>` |

### 4.3 Workflow-State Tests

| Test File | Test Name | State Transition Tested | What It Verifies |
|---|---|---|---|
| `<path>` | `<test_name>` | `<FROM_STATE → TO_STATE>` | `<behaviour>` |

---

## 5. New Test Infrastructure

| Item | Type | Location | Purpose |
|---|---|---|---|
| `<name>` | `Fixture / Mock / Helper / Factory` | `<path>` | `<what it provides>` |

---

## 6. Model and Prompt Call Verification

| Test File | Mocked Call | Mock Type | Notes |
|---|---|---|---|
| `<path>` | `<e.g., AzureOpenAI.chat.completions.create>` | `<Mock / Patch / Stub>` | `<notes>` |

> If none: "No model/prompt calls in scope for deterministic tests. Model-dependent scenarios are live-model eval scenarios."

---

## 7. Test Gap Report

Every requirement/criterion with no deterministic coverage; be specific about why.

| Requirement / Criterion ID | Gap Reason | Better Suited To | Resolution Plan |
|---|---|---|---|
| `<criterion>` | `<why no deterministic test>` | `Live-model eval / Future slice / Unclear requirement / Implementation not ready` | `<eval contract scenario ref or planned resolution>` |

> If none: "All requirements and acceptance criteria have deterministic test coverage. No gaps found."

---

## 8. Traceability Confirmation

Every test traces to at least one requirement/criterion.

| Test File | Test Name | Traces To |
|---|---|---|
| `<path>` | `<test_name>` | `<requirement ID or criterion>` |

> Confirm every test has a traceability link. Untraced tests are noise (remove) or must be traced to a known requirement.

---

## 9. Deviation Flags

Cases where production code does not match the slice spec, discovered during test writing.

| # | File / Component | Expected Behaviour (Spec) | Actual Behaviour | Severity | Recommended Action |
|---|---|---|---|---|---|
| DF-001 | `<path>` | `<spec>` | `<code>` | `Blocking / Non-blocking / Minor` | `Raise for Stage 9 / Fix before tests / Accept` |

> If none: "No deviations from the slice spec found during test writing."

---

## 10. Recommended Next Step

| Condition | Next Step |
|---|---|
| All tests pass, no deviations | Stage 9 check (if no deviation, proceed to Stage 10 live eval) |
| Tests fail | Return to Stage 7 — Implementation; do not proceed to Stage 10 with failing tests |
| Deviations found | Trigger Stage 9 `implementation-deviation-capture` before live evals |

### Current Recommendation

`<specific next step for this slice>`

### Handoff Notes

`<what Stage 9 / Stage 10 / the human needs to know>`
