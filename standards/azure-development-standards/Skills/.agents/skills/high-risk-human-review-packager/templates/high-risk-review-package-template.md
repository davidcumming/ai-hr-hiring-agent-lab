# High-Risk Eval Human Review Package

## 1. Package Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Package Date / Produced By | `<yyyy-mm-dd>` / `<agent-or-user>` |
| Risk Tier | `<High-risk / Safety-privacy-evidence-critical>` |
| Eval Summary Reference | `<path-or-id>` |
| Failure Classification Reference | `<path-or-id>` |
| Eval Contract Reference | `<path-or-id>` |
| Package Status | `Complete / Partial / Blocked` |

---

## 2. Instructions for the Reviewer

This package presents the high-risk eval evidence and the specific decisions required before the slice can proceed to documentation reconciliation and merge.

**Your responsibilities as release authority:** review each scenario in §4; answer each decision question; approve or reject each non-blocking candidate (§6); decide each model limitation (§7); record decisions in §9.

Skills have classified and packaged the evidence — they have not approved anything. Only you can approve.

**Full eval outputs** (transcripts, scoring logs) are stored externally; access references are in §4. Do not rely solely on the summaries here if you need the full output.

---

## 3. Scenarios Requiring Human Review

| Scenario ID | Name | Risk Designation | Classification | Decision Required |
|---|---|---|---|---|
| `SCN-XXX` | `<name>` | `<unsafe-mode / high-assurance / non-blocking candidate>` | `<BLOCK / NBC / MLM>` | `<brief decision statement>` |

---

## 4. Per-Scenario Evidence

### Scenario `SCN-XXX` — `<scenario name>`

- **Why high-risk:** `<from contract or unsafe-mode register — what could go wrong and why it matters>`
- **What was tested:** `<scenario description from eval contract>`
- **Observed behaviour (from eval summary):** `<brief — no raw outputs, no PHI/PII>`
- **Failure classification:** `<Code>` — `<Category name>`
- **Classification rationale (from `eval-failure-classifier`):** `<brief>`
- **Unsafe failure-mode register:** `Listed / Not listed`
- **External artifact reference:** `<URI or path for full transcript review>`
- **Decision question for reviewer:** `<specific, answerable, e.g., "Does the model skipping the approval confirmation in 3/20 runs represent unacceptable risk to approval-workflow integrity? [Yes, fix required / No, acceptable as documented residual risk with tracking issue]">`

---

## 5. Blocking Failures Summary

*For awareness. Blocking failures require a fix and cannot be approved for merge as-is.*

| Scenario ID | Classification | Blocking Criterion | Fix Direction |
|---|---|---|---|
| `SCN-XXX` | `BLOCK` | `<§22.1 criterion>` | `<Stage 7 fix / Stage 4 re-design / Stage 2 revision>` |

The fix loop must be completed and scenarios re-evaluated before this package is revisited.

---

## 6. Non-Blocking Candidates Requiring Approval

*Each requires explicit approval before the slice proceeds. If approved, a GitHub Issue must be created.*

| Scenario ID | Residual Risk | Failure Rate | Proposed GitHub Issue | Your Decision |
|---|---|---|---|---|
| `SCN-XXX` | `<risk remaining>` | `<n/n>` | `<proposed title>` | `[ ] Approve with issue  [ ] Reject — fix required` |

**Approval conditions (all required per Process Doc §22.2):**
- [ ] Severity classified.
- [ ] Failure documented (in the eval summary).
- [ ] GitHub Issue will be created.
- [ ] Re-test criteria defined.

---

## 7. Model Limitations Requiring Decision

| Scenario ID | Limitation | Options | Your Decision |
|---|---|---|---|
| `SCN-XXX` | `<what the model cannot do>` | `Accept / Upgrade model / Reduce scope / Add to known-limitations register` | `[ ] Decision: ___________` |

---

## 8. Risk Summary

| Item | If Approved | If Rejected |
|---|---|---|
| `<scenario or item>` | `<residual risk accepted, issue created, etc.>` | `<fix loop, scope change, etc.>` |

---

## 9. Reviewer Decisions and Approval Record

*Complete after reviewing the evidence. Your decisions are required to proceed.*

| Scenario ID | Decision | Notes | Date | Reviewer |
|---|---|---|---|---|
| `SCN-XXX` | `Approved / Rejected / Conditional` | `<notes>` | `<yyyy-mm-dd>` | `<name>` |

**Overall approval status:**
```
[ ] All items resolved — slice approved to proceed to Stage 12
[ ] One or more items rejected — fix loop required (specify scenarios above)
[ ] Conditional approval — conditions: ___________
```

**Reviewer signature / identity:** `<name, role, date>`

---

## 10. Handoff Notes

After review:
- Attach this document (decisions completed) to the closeout package.
- Non-blocking items approved: send to `github-issue-drafter`.
- Regression promotion recommended: send to `regression-promotion-recommender`.
- All items approved: orchestrator proceeds to Stage 12 (`current-state-reconciler`).
