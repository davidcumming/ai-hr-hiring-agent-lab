# Live Eval Run Record

## 1. Run Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `<slice-id>` / `<slice-name>` |
| Run Date / Executor | `<yyyy-mm-dd>` / `<agent-or-user>` |
| Eval Contract Reference / Status | `<path-or-id>` / `Approved` |
| Environment / Azure Region | `<dev / staging / production-mirror>` / `<region>` |

### Version Manifest

| Artifact | Version / Ref | Source File |
|---|---|---|
| Model name | `<model-name>` | `<manifest file>` |
| Model version | `<model-version>` | `<manifest file>` |
| Prompt version | `<prompt-version>` | `/prompts/prompt-manifest.json` |
| Tool schema version | `<tool-schema-version>` | `/tools/tool-schema-version.json` |
| Orchestration version | `<orchestration-version>` | `/orchestration/orchestration-version.json` |
| Workflow/state logic version | `<workflow-version>` | `<manifest file>` |
| Eval suite version | `<eval-suite-version>` | `/evals/eval-suite-version.json` |

---

## 2. Pre-Run Verification

| Check | Status | Notes |
|---|---|---|
| Eval contract status is `approved` | `Pass / Fail / N/A` | `<notes>` |
| Eval-data governance approval located | `Pass / Fail / N/A` | `<reference>` |
| All version manifests readable and current | `Pass / Fail / N/A` | `<notes>` |
| Deployment target matches contract environment | `Pass / Fail / N/A` | `<notes>` |
| Required run count per scenario confirmed | `Pass / Fail / N/A` | `<notes>` |

**Pre-run overall result:** `Pass / Blocked` — if blocked, describe and do not proceed: `<blocker>`

---

## 3. Scenario Results

| Scenario ID | Name | Risk Tier | Required Runs | Completed | Passes | Fails | Errors | Aggregate Pass Rate | Rubric Score | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `SCN-001` | `<name>` | `<tier>` | `<n>` | `<n>` | `<n>` | `<n>` | `<n>` | `<n/n (%)>` | `<score>` | `Pass / Fail / Error / Skipped` |

### Failure Detail (one per failing scenario)

#### `SCN-XXX` — `<scenario name>`
- **Observed behaviour:** `<what the model did>`
- **Expected behaviour (from rubric):** `<what was required>`
- **Failure mode (initial observation — do not classify here):** `<brief>`
- **Run indices that failed:** `<run 2, run 4, …>`
- **External artifact ref:** `<location>`

---

## 4. Threshold Summary

| Risk Tier | Required Threshold (§19.1) | Required Runs | Actual Pass Rate | Zero Critical Failures? | Threshold Met? |
|---|---|---|---|---|---|
| Low | No critical failures; acceptable qualitative result | 3–5 | `<rate>` | `Yes / No` | `Pass / Fail / N/A` |
| Standard | ≥ 80% pass rate | 5–10 | `<rate>` | `Yes / No` | `Pass / Fail / N/A` |
| High-risk | ≥ 90% pass rate + zero critical failures | 20+ | `<rate>` | `Yes / No` | `Pass / Fail / N/A` |
| Safety/privacy/evidence-critical | Zero critical failures + stricter rubric | 20+ | `<rate>` | `Yes / No` | `Pass / Fail / N/A` |

**Overall threshold result:** `Met / Not met / Partial`

---

## 5. Cost and Latency Summary

Complete only if the eval contract specified cost/latency thresholds (Process Doc §20).

| Scenario ID | Avg / Max Latency (ms) | Latency Threshold | Latency Pass? | Avg Token Usage | Token Budget | Token Pass? | Est. Cost | Cost Envelope | Cost Pass? |
|---|---|---|---|---|---|---|---|---|---|
| `SCN-001` | `<ms>` / `<ms>` | `<ms>` | `Pass / Fail / N/A` | `<tokens>` | `<tokens>` | `Pass / Fail / N/A` | `<$>` | `<$>` | `Pass / Fail / N/A` |

---

## 6. External Artifact References

| Scenario ID | Artifact Type | Location / URI | Access Notes | Retention Policy |
|---|---|---|---|---|
| `SCN-001` | Full response transcript | `<blob-url or path>` | `<access group / key>` | `<retention>` |
| `SCN-001` | Scoring log | `<blob-url or path>` | `<access group / key>` | `<retention>` |

Full outputs stored externally per Process Doc §23.3 Durable Audit Archive. References only.

---

## 7. Errors and Skipped Scenarios

| Scenario ID | Status | Reason | Action Required |
|---|---|---|---|
| `SCN-XXX` | `Error / Skipped` | `<reason>` | `<action>` |

---

## 8. Eval-Data Governance

| Item | Status |
|---|---|
| Data governance approval reference | `<document ref or link>` |
| Scenario data classification | `Synthetic / De-identified / Approved production data` |
| PHI present? / PII present? | `Yes / No` / `Yes / No` |
| Canadian residency requirements apply? | `Yes / No / N/A` |

---

## 9. Handoff Notes

**Run status:** `Complete / Partial / Blocked`

**Summary counts:** Scenarios `<total>` · Passed `<n>` · Failed `<n>` · Error/Skipped `<n>` · Threshold met `Yes / No / Partial`

**Recommended next skill:** `eval-result-summarizer`

**Notes for Stage 11:** `<context needed to interpret results: environmental anomalies, quota limits, partial re-run context>`
