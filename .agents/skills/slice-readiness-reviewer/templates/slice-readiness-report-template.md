# Slice Readiness Report: <Slice ID> — <Slice Name>

## 1. Review Metadata

| Field | Value |
|---|---|
| Report ID | `<report-id>` |
| Slice ID | `<slice-id>` |
| Slice Name | `<slice-name>` |
| Date Reviewed | `<yyyy-mm-dd>` |
| Reviewed By | `<agent-id — must differ from spec author>` |
| Draft Spec Reference | `<path/link>` |
| Execution Model | `isolated-verification` |
| Status | `Complete` |

## 2. Inputs Reviewed

| Input | Reference | Notes |
|---|---|---|
| Draft slice spec | `<reference>` | Primary artifact under review |
| Reconciled planning context | `<reference>` | Baseline consistency check |
| Architecture guidelines | `<reference>` | Constraint citation check |
| Approved ADRs | `<reference>` | Override check |
| Known limitations | `<reference>` | Scope boundary check |
| GitHub Issues | `<reference>` | Blocker check |
| Test/eval strategy | `<reference>` | Eval draft quality context |

Findings in §3–§10 use `Type` = `Required fix / Recommended improvement / Note`.

## 3. Scope Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| SCO-001 | `<finding>` | `<type>` | `<fix>` |

**Scope summary:** `<pass / concerns>`

## 4. Functional Requirements Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| FR-001 | `<finding>` | `<type>` | `<fix>` |

**Requirements summary:** `<pass / concerns>`

## 5. Agent Behaviour Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| AB-001 | `<finding>` | `<type>` | `<fix>` |

**Behaviour summary:** `<pass / concerns>`

## 6. Eval Contract Draft Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| EC-001 | `<finding>` | `<type>` | `<fix>` |

**Eval contract summary:** `<pass / concerns>`

## 7. Architecture Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| ARC-001 | `<finding>` | `<type>` | `<fix>` |

**Architecture summary:** `<pass / concerns>`

## 8. Privacy and Governance Review

| Concern | Addressed in Spec? | Finding | Type |
|---|---|---|---|
| PHI | `Yes / No / Partial` | `<finding>` | `<type>` |
| PII | `Yes / No / Partial` | `<finding>` | `<type>` |
| Canadian data residency | `Yes / No / Partial` | `<finding>` | `<type>` |
| Audit trail | `Yes / No / Partial` | `<finding>` | `<type>` |
| Sensitive eval data | `Yes / No / Partial` | `<finding>` | `<type>` |
| External sharing | `Yes / No / Partial` | `<finding>` | `<type>` |
| Manual configuration | `Yes / No / Partial` | `<finding>` | `<type>` |

**Privacy/governance summary:** `<pass / concerns>`

## 9. Consistency Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| CON-001 | `<finding>` | `<type>` | `<fix>` |

**Consistency summary:** `<pass / concerns>`

## 10. Open Questions Review

| Finding ID | Finding | Type | Recommended Fix |
|---|---|---|---|
| OQ-001 | `<finding>` | `<type>` | `<fix>` |

**Open questions summary:** `<pass / concerns>`

## 11. Required Fixes (Blocking)

Must be resolved before the spec can be approved.

| Fix ID | Finding Reference | Description | Required Action |
|---|---|---|---|
| FIX-001 | `<finding-id>` | `<description>` | `<action>` |

**Total required fixes:** `<count>`

## 12. Recommended Improvements (Non-Blocking)

| Improvement ID | Finding Reference | Description | Recommendation |
|---|---|---|---|
| IMP-001 | `<finding-id>` | `<description>` | `<recommendation>` |

## 13. Readiness Decision

**Decision** — one of: `ready-for-eval-design / needs-revision / blocked`

**Decision Rationale** — two to four sentences; reference the specific required fixes or blockers.

**If Blocked — Blocking Reason** — `<specific blocker and owner>`

## 14. Handoff Recommendation

| Decision | Recommended Next Action |
|---|---|
| `ready-for-eval-design` | Proceed to `eval-risk-profiler` and `eval-contract-designer` at Stage 4. |
| `needs-revision` | Return spec to `slice-spec-generator` with the required-fixes list in §11. |
| `blocked` | Resolve the blocker identified above, then return to `slice-spec-generator`. |

**Recommendation:** `<next action>`
