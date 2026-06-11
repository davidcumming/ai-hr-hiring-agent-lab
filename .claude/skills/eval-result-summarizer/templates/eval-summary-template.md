# Eval Summary

## 1. Summary Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Summary Date / Produced By | `<yyyy-mm-dd>` / `<agent-or-user>` |
| Eval Contract Reference | `<path-or-id>` |
| Run Record Reference | `<path-or-id or N/A — non-agentic carve-out>` |
| Summary Status | `Complete / Partial / Blocked / Not Applicable — Non-Agentic` |
| Live Eval Applicability | `Required / Not Applicable — Non-Agentic Carve-Out` |

---

## 2. Version Block

*All fields required per Process Doc §19.2. If live evals are not applicable, set model/prompt/tool fields to `N/A — non-agentic carve-out` and complete §6.*

| Field | Value |
|---|---|
| Model name / version | `<model-name>` / `<model-version>` |
| Prompt version | `<prompt-version>` |
| Tool schema version | `<tool-schema-version>` |
| Orchestration version | `<orchestration-version>` |
| Workflow/state logic version | `<workflow-version>` |
| Date run | `<yyyy-mm-dd>` |
| Scenario set | `<eval-suite-version or description>` |
| Runs per scenario / Pass threshold | `<n>` / `<threshold>` |

---

## 3. Scenario Results

| Scenario ID | Name | Risk Tier | Runs | Pass Rate | Rubric Score | Status |
|---|---|---|---|---|---|---|
| `SCN-001` | `<name>` | `<tier>` | `<n>` | `<n/n (%)>` | `<score>` | `Pass / Fail / Error / Skipped` |

---

## 4. Threshold Summary

| Risk Tier | Required Threshold (§19.1) | Actual Pass Rate | Zero Critical Failures? | Threshold Met? |
|---|---|---|---|---|
| `<tier>` | `<threshold>` | `<rate>` | `Yes / No` | `Pass / Fail / N/A` |

**Overall threshold result:** `Met / Not met / Partial`

---

## 5. Failure Summary

*Describe observed behaviour only. Do not classify here — that is `eval-failure-classifier`. No full outputs, no PHI/PII; references only.*

| Scenario ID | Name | Observed Behaviour (brief: actual vs. expected) | Artifact Reference |
|---|---|---|---|
| `SCN-XXX` | `<name>` | `<brief>` | `<external-artifact-uri>` |

If live evals are not applicable: `N/A — no live eval failures; eval contract documented the non-agentic carve-out.`

---

## 6. Non-Agentic Carve-Out Rationale

*Complete only if live evals are not applicable.*

| Required statement | Evidence |
|---|---|
| No model behaviour | `<eval contract reference>` |
| No prompt changes | `<eval contract reference>` |
| No tool-orchestration behaviour | `<eval contract reference>` |
| No agent behaviour | `<eval contract reference>` |
| No behaviour-affecting model dependency | `<eval contract reference>` |

**Live eval not applicable rationale:** `<brief>`

---

## 7. Cost and Latency Summary

*Complete only if the eval contract specified thresholds (Process Doc §20); else state "Not tracked" with reason.*

| Scenario ID | Avg Latency (ms) | Latency Threshold | Latency Pass? | Avg Tokens | Token Budget | Token Pass? | Est. Cost | Cost Envelope | Cost Pass? |
|---|---|---|---|---|---|---|---|---|---|
| `SCN-001` | `<ms>` | `<ms>` | `Pass / Fail / N/A` | `<tokens>` | `<tokens>` | `Pass / Fail / N/A` | `<$>` | `<$>` | `Pass / Fail / N/A` |

**Cost/latency overall:** `Met / Not met / Not tracked`

---

## 8. External Artifact References

| Scenario ID | Artifact Type | URI / Location | Access Notes |
|---|---|---|---|
| `SCN-001` | Response transcripts | `<uri>` | `<access group>` |
| `SCN-001` | Scoring log | `<uri>` | `<access group>` |

Full artifacts stored externally per Process Doc §23.3. References only.

---

## 9. Gap and Discrepancy Flags

*Differences between what the eval contract required and what the run record shows.*

| ID | Description | Impact | Action Required |
|---|---|---|---|
| GAP-001 | `<e.g., SCN-005 required by contract but not in run record>` | `<impact>` | `<action>` |

---

## 10. Human-Review Notes

*Notes from reviewers, if provided. Leave blank if none.*

| Source | Note |
|---|---|
| `<reviewer>` | `<note>` |

---

## 11. Reviewer Notes (Process Doc §19.2)

*Additional reviewer notes required by Process Doc §19.2.*

> `<free text>`

---

## 12. Handoff Notes

**Summary status:** `Complete / Partial / Blocked / Not Applicable — Non-Agentic`

**Counts:** Total `<n>` · Passed `<n>` · Failed `<n>` · Error/Skipped `<n>` · Threshold met `Yes / No / Partial` · Applicability `Required / Not Applicable — Non-Agentic Carve-Out`

**Failures present?** `Yes / No`

**Recommended next skill:**
- If failures exist: `eval-failure-classifier`
- If high-risk tier: also `high-risk-human-review-packager` (conditional)
- If no failures and threshold met: orchestrator proceeds to Stage 12
