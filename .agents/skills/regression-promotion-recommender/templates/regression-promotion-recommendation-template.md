# Regression Promotion Recommendation

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Report Date / Produced By | `<yyyy-mm-dd>` / `<agent-or-user>` |
| Failure Classification Reference | `<path-or-id>` |
| Eval Contract Reference | `<path-or-id>` |
| Regression Inventory Reference | `<path-or-id or "Not available">` |

---

## 2. Per-Candidate Recommendation

| Scenario ID | Name | Classification | Recommendation | Brief Rationale |
|---|---|---|---|---|
| `SCN-XXX` | `<name>` | `<IMP / NBC / EDD / FIX / other>` | `Promote / Promote after fix / Do not promote / Clarify first` | `<brief>` |

---

## 3. Rewrite Suggestions (for "Promote after fix" candidates)

### Scenario `SCN-XXX` — `<name>`
- **Current scenario issue:** `<what is wrong with the definition, rubric, or test data>`
- **Recommended correction:** `<corrected definition, expected behaviour, or rubric adjustment>`
- **Requires `eval-contract-designer` revision?** `Yes / No — inline`
- **Data/fixture fix required?** `Yes — describe / No`

---

## 4. Fix Dependencies

*Scenarios that must not enter the regression suite until a related defect is fixed.*

| Scenario ID | Dependency | Blocking Fix | Expected Resolution |
|---|---|---|---|
| `SCN-XXX` | `<e.g., IMP fix loop for SCN-003 must complete and pass>` | `<fix loop / PR ref>` | `<e.g., promote after SCN-003 re-run passes>` |

---

## 5. Duplication Check

| Scenario ID | Existing Regression Scenario | Relationship | Action |
|---|---|---|---|
| `SCN-XXX` | `<REG-XXX or "None">` | `<Duplicate / Weaker exists / No overlap>` | `<Skip — already covered / Promote — strengthens / Promote — distinct>` |

---

## 6. GitHub Issue Draft Inputs

*For `github-issue-drafter`. One issue per promoted scenario.*

| Scenario ID | Proposed Title | Type | Priority | Acceptance Criteria | Related Slice |
|---|---|---|---|---|---|
| `SCN-XXX` | `<e.g., "Add SCN-003 clarification-gate scenario to regression suite">` | `eval-improvement` | `Medium` | `<reviewed, rewrite applied if needed, passes required run count>` | `<slice-id>` |

---

## 7. Handoff Notes

**Recommendation summary:** Total `<n>` · Promote `<n>` · Promote after fix `<n>` · Do not promote `<n>` · Clarify first `<n>`

**Next steps:**
- Promoted scenarios with fixes complete: `github-issue-drafter` for tracking issues.
- Scenarios requiring rewrite: refer to `eval-contract-designer`.
- Scenarios with fix dependencies: block until fix is verified.
- Ambiguous scenarios: refer to human for requirement clarification.

**Attach this report to the closeout package.**
