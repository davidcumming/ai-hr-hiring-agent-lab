# Eval Failure Classification Report

## 1. Classification Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Classification Date / Produced By | `<yyyy-mm-dd>` / `<agent-id — independent of the eval runner>` |
| Eval Summary Reference | `<path-or-id>` |
| Eval Contract Reference | `<path-or-id>` |
| Risk Tier | `<Low / Standard / High-risk / Safety-privacy-evidence-critical>` |
| Is Re-classification (after fix)? | `Yes / No` |
| Prior Classification Reference (if re-run) | `<path-or-id or N/A>` |

---

## 2. Per-Failure Classification

| Scenario ID | Name | Code | Primary Category | Rationale | Treatment Path |
|---|---|---|---|---|---|
| `SCN-XXX` | `<name>` | `BLOCK / NBC / AMB / FLAKY / EDD / IMP / MLM / FIX` | `<category>` | `<brief>` | `<path>` |

### Detailed Notes (one per failure)

#### `SCN-XXX` — `<scenario name>`
- **Category:** `<code>` — `<category name>`
- **Observed behaviour:** `<brief, no full outputs, no PHI/PII>`
- **Expected behaviour:** `<from eval contract>`
- **Consistency:** `<e.g., failed 2/8; failed all 8; inconsistent>`
- **Unsafe failure-mode register check:** `<Listed / Not listed — register ref>`
- **Rationale for this category:** `<key driving factors>`
- **Secondary factors:** `<optional>`
- **Treatment path:** `<per SKILL.md §7.2 Step 3>`
- **Regression promotion candidate?** `Yes / No / Maybe — reason`
- **GitHub Issue inputs:** `<title / type / severity / acceptance / re-test — or "Not required">`

---

## 3. Blocking Failures

*Prevent merge; require a fix loop.*

| Scenario ID | Name | Blocking Criterion (§22.1) | Required Fix Direction |
|---|---|---|---|
| `SCN-XXX` | `<name>` | `<§22.1 criterion>` | `<Stage 7 fix / Stage 4 re-design / Stage 2 requirement revision>` |

**Blocking failure count:** `<n>`

---

## 4. Non-Blocking Candidates

*Require human release authority approval, GitHub Issue, and re-test criteria before proceeding.*

| Scenario ID | Name | Residual Risk | Human Approval | GitHub Issue Inputs |
|---|---|---|---|---|
| `SCN-XXX` | `<name>` | `<risk remaining>` | `Yes — required` | `<title / type / severity / re-test>` |

**Non-blocking candidate count:** `<n>`

---

## 5. Ambiguous Failures

*Pause the slice; human must clarify before any agent proceeds.*

| Scenario ID | Name | Ambiguity | Clarification Question for Human |
|---|---|---|---|
| `SCN-XXX` | `<name>` | `<what is ambiguous>` | `<specific question>` |

**Ambiguous failure count:** `<n>`

---

## 6. Other Classifications

### Flaky
| Scenario ID | Failure Rate | Recommended Action |
|---|---|---|
| `SCN-XXX` | `<n/n>` | `<NBC with approval / escalate to IMP / escalate to BLOCK>` |

### Eval-Design Defect (EDD)
| Scenario ID | Defect | Recommended Rubric Correction |
|---|---|---|
| `SCN-XXX` | `<what is wrong>` | `<change to rubric or scenario>` |

### Implementation Defect (IMP)
| Scenario ID | Defect | Recommended Fix Area |
|---|---|---|
| `SCN-XXX` | `<what was wrong>` | `<prompt / tool / orchestration / workflow state>` |

### Model Limitation (MLM)
| Scenario ID | Limitation | Human Decision Required |
|---|---|---|
| `SCN-XXX` | `<what the model cannot do>` | `<accept / upgrade model / reduce scope / known-limitations register>` |

### Fixture Defect (FIX)
| Scenario ID | Fixture Issue | Recommended Fix |
|---|---|---|
| `SCN-XXX` | `<test data/environment issue>` | `<fix and re-run>` |

---

## 7. Aggregate Summary

| Category | Count |
|---|---|
| Blocking (`BLOCK`) | `<n>` |
| Non-blocking candidate (`NBC`) | `<n>` |
| Ambiguous requirement (`AMB`) | `<n>` |
| Flaky (`FLAKY`) | `<n>` |
| Eval-design defect (`EDD`) | `<n>` |
| Implementation defect (`IMP`) | `<n>` |
| Model limitation (`MLM`) | `<n>` |
| Fixture defect (`FIX`) | `<n>` |
| **Total failures classified** | `<n>` |

---

## 8. GitHub Issue Inputs

*For `github-issue-drafter`. Safe backlog issues may be created directly; sensitive, decision-needed, or tooling-blocked items remain drafts with a reason.*

| Scenario ID | Proposed Title | Type | Severity | Acceptance Criteria | Re-test Criteria | Slice Context |
|---|---|---|---|---|---|---|
| `SCN-XXX` | `<title>` | `<bug / tech-debt / eval-gap>` | `<critical / high / medium / low>` | `<what constitutes a fix>` | `<how to verify>` | `<slice-id>` |

---

## 9. Regression Promotion Candidates

*For `regression-promotion-recommender` to evaluate for the standing regression suite.*

| Scenario ID | Category | Reason for Consideration | Recommended Action |
|---|---|---|---|
| `SCN-XXX` | `<category>` | `<value to regression suite>` | `Refer to regression-promotion-recommender` |

---

## 10. Handoff Notes

**Gate recommendation:** `Proceed / Fix required / Pause for clarification / Human approval required`

**Explanation:** `<brief — e.g., "One blocking failure (SCN-003, IMP) requires a fix loop; two non-blocking candidates (SCN-007, SCN-009) ready for human approval review once resolved.">`

**Next skills required:**
- If blocking: fix loop → `live-eval-runner` re-run → `eval-failure-classifier` re-classification
- If ambiguous: human clarification → possibly `eval-contract-designer` rubric revision → `live-eval-runner` re-run
- If non-blocking only: human approval → `github-issue-drafter` → Stage 12 via orchestrator
- If regression candidates exist: `regression-promotion-recommender` (conditional)
- If high-risk tier: `high-risk-human-review-packager` (conditional)
