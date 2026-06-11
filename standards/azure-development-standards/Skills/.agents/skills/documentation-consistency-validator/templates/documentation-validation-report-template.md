# Documentation Validation Report: <Slice ID>

| Field | Value |
|---|---|
| Slice ID / Branch | `<slice-id>` / `<feature/branch-name>` |
| Validation Date | `<yyyy-mm-dd>` |
| Produced By | `documentation-consistency-validator` (isolated-verification) |
| Stage 12 Artifacts Reviewed | `<branch-diff path>, <doc update plan path>, <actual-architecture update path>` |
| Status | `Draft / Final` |

---

## Validation Scope

**Files validated:** `File | Type (current-state doc / actual architecture / known limitations / other) | Sections reviewed`

**Evidence reviewed:** branch diff analysis, implementation summary, test summary, eval summary, manual evidence summary `<or N/A>`, approved ADRs `<IDs or N/A>`, architecture guidelines, known limitations register, GitHub Issues.

---

## Blocking Mismatches

Must be resolved before Stage 14. Return to Stage 12 (`current-state-reconciler`).

| ID | File | Section | Mismatch (doc claim vs. evidence) | Evidence Gap | Required Action |
|---|---|---|---|---|---|
| BM-001 | `<path>` | `<section>` | `<claim vs. evidence>` | `<missing/contradicting evidence>` | `<specific correction>` |

**Count:** `<n>`

---

## Non-Blocking Gaps

Do not block Stage 14; should become follow-up issue candidates.

| ID | File | Section | Gap Description | Recommended Treatment |
|---|---|---|---|---|
| NB-001 | `<path>` | `<section>` | `<description>` | `Follow-up issue candidate / Accept as-is / Other` |

**Count:** `<n>`

---

## Observations

| ID | File | Section | Observation |
|---|---|---|---|
| OB-001 | `<path>` | `<section>` | `<observation>` |

---

## Architecture-Specific Findings

**Only-built-components:** `Component | Present in diff? / Present in docs? | Pass / Blocking mismatch / Non-blocking gap`

**Guideline consistency:** `Guideline Section | Architecture Claim | Consistent? (Yes / No — see BM-<n>) | Notes`

**Manual-configuration follow-up:** `Manual Config Item | Follow-Up Issue Ref Present? | Pass / Non-blocking gap`

**ADR cross-reference accuracy:** `<finding>`

---

## Slice-Language Check

| File | Slice-Specific Language Found? | Finding |
|---|---|---|
| `<path>` | `Yes (see BM-<n>) / No` | `Pass / Blocking mismatch` |

---

## Suggested Follow-Up Issue Candidates

For `github-issue-drafter` at Stage 14.

| Item | From Finding | Suggested Type | Priority |
|---|---|---|---|
| `<description>` | `NB-<n> / OB-<n>` | `documentation-gap / source-control-debt / other` | `High / Medium / Low` |

---

## Validation Recommendation

**Recommendation:** `PASS` / `CONDITIONAL-PASS` / `FAIL — return to Stage 12`

**Rationale:** `<blocking-mismatch count if FAIL; nature of gaps if CONDITIONAL-PASS; confirmation all checks passed if PASS>`

---

## Handoff

**If PASS or CONDITIONAL-PASS:** advance to Stage 14 — Traceability & closeout. Pass this report and follow-up issue candidates to `traceability-matrix-builder` and `closeout-package-builder`.

**If FAIL:** return to Stage 12 — Current-state reconciliation. Pass this report and the blocking mismatches list to `current-state-reconciler`. Do not advance to Stage 14 until Stage 13 passes on re-run.
