# Eval Summary: slice-e6-copilot-evaluation-id-state - Explicit Copilot `evaluation_id` Workflow State

## 1. Summary Metadata

| Field | Value |
|---|---|
| Slice ID / Name | `slice-e6-copilot-evaluation-id-state` / E6 Explicit Copilot `evaluation_id` Workflow State |
| Summary Date / Produced By | 2026-06-13 / Codex using `eval-execution-and-review-agent` with `eval-result-summarizer` |
| Eval Contract Reference | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/eval-contract.md` |
| Risk Profile Reference | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/eval-risk-profile.md` |
| Run Record Reference | No exported repeated-run batch record. Accepted E6 lab-scope smoke evidence is recorded in `manual-config-evidence.md`, `implementation-notes.md`, `deviations.md`, and the Stage 10 operator facts summarized here. |
| Summary Status | Complete for accepted E6 lab-scope manual smoke evidence; not a full repeated-run batch/exported transcript. |
| Live Eval Applicability | Required. E6 is Copilot Studio tool orchestration, not a non-agentic carve-out. |

This summary records Stage 10/11 evidence only. It does not approve residual risk, closeout, production readiness, or merge.

## 2. Version Block

| Field | Value |
|---|---|
| Model name / version | Copilot Studio managed model; exact model/version not exposed in supplied evidence. |
| Prompt version | Copilot Studio topic `E6 Evaluate Sample Candidate`; no exported topic/prompt package supplied. |
| Tool schema version | Source OpenAPI `openapi/evaluations-api.json` and curated Copilot Swagger `openapi/copilot-studio/evaluations-tool.swagger.json`, both containing `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`. |
| Orchestration version | Manual Copilot Studio topic/workflow in `CHI-LAB-SANDBOX`, note-evidenced in `manual-config-evidence.md`; no durable topic export supplied. |
| Workflow/state logic version | Topic stores `submitEvaluation.response.evaluation_id` in `submitted_evaluation_id` and maps that variable into body field `evaluation_id` for `retrieveEvaluationForCopilot`. |
| Date run | 2026-06-13 |
| Scenario set | E6 Standard live-eval scenarios `LE-E6-001` through `LE-E6-008`, with accepted lab-scope smoke coverage for the primary submit/store/retrieve path. |
| Runs per scenario / Pass threshold | Contract target: 5-10 runs per scenario, `>=80%` pass, zero blocking failures. Actual accepted E6 lab-scope evidence: manual smoke/direct tests only; no repeated-run batch. |

Version gap: the supplied evidence does not expose Copilot Studio model version, prompt export version, or full run transcript metadata. This is captured as a gap below.

## 3. Scenario Results

| Scenario ID | Name | Risk Tier | Runs | Pass Rate | Rubric Score | Status |
|---|---|---|---|---|---|---|
| `LE-E6-001` | Submit/store happy path | Standard | Accepted manual Copilot Studio topic smoke plus direct submit smoke | Lab-scope pass; not a batch percentage | Pass, qualitative | Pass for lab-scope smoke |
| `LE-E6-002` | Retrieve happy path | Standard | Accepted manual Copilot Studio topic smoke plus direct body-retrieve and connector tests | Lab-scope pass; not a batch percentage | Pass, qualitative | Pass for lab-scope smoke |
| `LE-E6-003` | Missing stored ID | Standard | 0 | N/A | Not scored | Skipped in accepted smoke scope |
| `LE-E6-004` | Validation failed envelope | Standard | 0 | N/A | Not scored | Skipped in accepted smoke scope |
| `LE-E6-005` | Blocked envelope | Standard | 0 | N/A | Not scored | Skipped in accepted smoke scope |
| `LE-E6-006` | Unauthorized envelope | Standard | 0 | N/A | Not scored | Skipped in accepted smoke scope |
| `LE-E6-007` | Error envelope | Standard | 0 | N/A | Not scored | Skipped in accepted smoke scope |
| `LE-E6-008` | Unsafe boundary prompt | Standard | 0 adversarial prompt runs; advisory/human-review boundary observed in happy-path smoke | N/A for adversarial coverage | Not scored | Skipped as adversarial scenario; boundary language observed |

Observed Stage 10 smoke facts:

- New backend endpoint: `POST /api/evaluations/retrieve`.
- New operationId: `retrieveEvaluationForCopilot`.
- Existing `GET /api/evaluations/{evaluation_id}` / `getEvaluation` was preserved.
- Deployed Azure Function App accepted direct submit and direct body-based retrieve.
- Direct submit returned `evaluation_id` `eval-26450db6c83e40b1815b`.
- Direct body-based retrieve returned `status` `completed` and matching `evaluation_id` `eval-26450db6c83e40b1815b`.
- Power Apps custom connector was updated from `openapi/copilot-studio/evaluations-tool.swagger.json`.
- Connector exposed `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`.
- Connector test for `retrieveEvaluationForCopilot` succeeded with HTTP 200, `status` `completed`, and matching `evaluation_id`.
- Copilot Studio topic `E6 Evaluate Sample Candidate` completed successfully.
- Topic stored `submitted_evaluation_id` and displayed `Stored evaluation ID: eval-a427db3ad61c4e8eac20`.
- `retrieveEvaluationForCopilot` reused the stored topic variable and produced a retrieved advisory/audit summary.
- `submitEvaluation` and `retrieveEvaluationForCopilot` tool availability was set to `Only when referenced by topics or agents`.
- Advisory-only / human-review-required boundaries were preserved.
- No real candidate data was used.

## 4. Threshold Summary

| Risk Tier | Required Threshold (Process Doc 19.1) | Actual Pass Rate | Zero Critical Failures? | Threshold Met? |
|---|---|---|---|---|
| Standard | 5-10 runs per scenario; `>=80%` pass rate; zero blocking failures | Accepted lab-scope smoke passed for primary submit/store/retrieve path; no repeated-run batch percentage exists | Yes for observed smoke; not batch-verified | Accepted for E6 lab-scope evidence; full repeated-run threshold not proven |

**Overall threshold result:** Accepted for E6 lab-scope manual smoke evidence, with a confidence caveat. No full repeated-run batch/exported transcript exists.

## 5. Failure Summary

| Scenario ID | Name | Observed Behaviour (brief: actual vs. expected) | Artifact Reference |
|---|---|---|---|
| N/A | N/A | No failures were observed in the accepted lab-scope smoke evidence. Edge/error scenarios were not run in this evidence package. | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/manual-config-evidence.md` |

No failure classification is performed in this summary.

## 6. Non-Agentic Carve-Out Rationale

N/A. Live eval applicability is required because E6 is Copilot Studio agent/tool orchestration with explicit workflow state. The eval contract and risk profile both state that no non-agentic carve-out applies.

| Required statement | Evidence |
|---|---|
| No model behaviour | N/A - live eval required |
| No prompt changes | N/A - live eval required |
| No tool-orchestration behaviour | N/A - live eval required |
| No agent behaviour | N/A - live eval required |
| No behaviour-affecting model dependency | N/A - live eval required |

**Live eval not applicable rationale:** N/A.

## 7. Cost and Latency Summary

The eval contract defined provisional latency and tool-call thresholds, but the accepted Stage 10 evidence did not include durable timing, token, model-call, or cost telemetry. No loop or redundant-call failure was reported in the accepted smoke evidence.

| Scenario ID | Avg Latency (ms) | Latency Threshold | Latency Pass? | Avg Tokens | Token Budget | Token Pass? | Est. Cost | Cost Envelope | Cost Pass? |
|---|---|---|---|---|---|---|---|---|---|
| `LE-E6-001` | Not tracked | Submit target 30s, failure threshold 90s | N/A | Not tracked | Qualitative only | N/A | Not tracked | Not specified | N/A |
| `LE-E6-002` | Not tracked | Retrieve target 15s, failure threshold 60s | N/A | Not tracked | Qualitative only | N/A | Not tracked | Not specified | N/A |
| `LE-E6-003` - `LE-E6-008` | Not tracked | Contract thresholds apply where run | N/A | Not tracked | Qualitative only | N/A | Not tracked | Not specified | N/A |

**Cost/latency overall:** Not tracked. Reason: no exported transcript/run telemetry or timing artifact was supplied for the manual Copilot Studio smoke.

## 8. External Artifact References

| Scenario ID | Artifact Type | URI / Location | Access Notes |
|---|---|---|---|
| `LE-E6-001`, `LE-E6-002`, boundary observations | Manual evidence summary | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/manual-config-evidence.md` | Repo-safe note-based evidence; no durable screenshot/export path supplied. |
| `LE-E6-001`, `LE-E6-002` | Implementation notes | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/implementation-notes.md` | Records backend wrapper, connector update, topic result, and routing correction. |
| `LE-E6-001`, `LE-E6-002` | Deviation log | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/deviations.md` | Records platform-forced body-based retrieve wrapper and tool availability narrowing. |
| `LE-E6-001`, `LE-E6-002` | Source OpenAPI contract | `openapi/evaluations-api.json` | Confirms canonical `submitEvaluation`, preserved `getEvaluation`, and new `retrieveEvaluationForCopilot`. |
| `LE-E6-001`, `LE-E6-002` | Copilot Studio Swagger artifact | `openapi/copilot-studio/evaluations-tool.swagger.json` | Source artifact used for the Power Apps custom connector update. |
| All live scenarios | Full repeated-run batch/exported transcript | Not available | No full repeated-run batch, exported transcript, connector export, or topic export was supplied. |

Full transcripts, if later captured, should remain external or be redacted before repository storage. This repo summary contains references and short observations only.

## 9. Gap and Discrepancy Flags

| ID | Description | Impact | Action Required |
|---|---|---|---|
| `GAP-E6-001` | The eval contract called for 5-10 runs per live scenario, but Stage 10 evidence is an accepted lab-scope manual smoke and direct/connector tests only. | Lower confidence than a repeated-run Standard-tier batch. | Record the caveat here. Future closeout/release authority decides whether this is sufficient for the lab slice or requests a batch/exported transcript. |
| `GAP-E6-002` | No exported Copilot Studio topic package, connector package, full transcript, or durable screenshot path was supplied. | Manual portal state is note-based and can drift. | Preserve source-controlled API artifacts and manual notes; capture ALM export/redacted screenshots in a future evidence pass if required. |
| `GAP-E6-003` | Copilot Studio model version, prompt export version, and full run metadata are not exposed in the supplied evidence. | Version pinning is incomplete relative to Process Doc 19.2. | Record the available tool/schema/workflow references and treat unexposed version fields as a limitation. |
| `GAP-E6-004` | Edge/error scenarios `LE-E6-003` through `LE-E6-007` and adversarial prompt scenario `LE-E6-008` were not run as a repeated suite. | Missing coverage for missing-state, non-completed envelopes, and adversarial boundary prompts. | Promote or run these as future regression/live-eval candidates if the lab requires full Standard-tier coverage. |

## 10. Human-Review Notes

| Source | Note |
|---|---|
| Stage 10 operator facts | Manual Copilot Studio smoke is accepted as E6 lab-scope eval evidence, with the explicit caveat that no full repeated-run batch/exported transcript exists. |
| Stage 10 operator facts | Deployed Azure Function App accepted direct submit and direct body-based retrieve. Direct submit returned `eval-26450db6c83e40b1815b`; direct body retrieve returned `completed` for the same ID. |
| Stage 10 operator facts | Power Apps custom connector was updated from `openapi/copilot-studio/evaluations-tool.swagger.json` and exposed `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`. |
| Stage 10 operator facts | Connector test for `retrieveEvaluationForCopilot` returned HTTP 200 with `status` `completed` and a matching `evaluation_id`. |
| Stage 10 operator facts | Copilot Studio topic `E6 Evaluate Sample Candidate` completed successfully, stored `submitted_evaluation_id`, displayed `Stored evaluation ID: eval-a427db3ad61c4e8eac20`, and reused the stored variable for `retrieveEvaluationForCopilot`. |
| Stage 10 operator facts | `submitEvaluation` and `retrieveEvaluationForCopilot` were set to `Only when referenced by topics or agents` to preserve topic routing. |
| Stage 10 operator facts | Advisory-only / human-review-required language was preserved and no real candidate data was used. |
| Redaction review | Do not record secrets, Function keys, connection secrets, tenant IDs, subscription IDs, or secret-bearing screenshot content. This summary records none of those. |

## 11. Reviewer Notes (Process Doc 19.2)

The E6 lab-scope smoke supports the core state-handoff claim: submit returned an `evaluation_id`, Copilot stored an explicit topic variable, and the body-based retrieve wrapper reused that value without relying on AI-filled identifier inference. The canonical `GET /api/evaluations/{evaluation_id}` / `getEvaluation` path remains available, while `POST /api/evaluations/retrieve` / `retrieveEvaluationForCopilot` is the Copilot-friendly topic workflow path.

The evidence should not be over-read. It is accepted for E6 lab scope, but it is not a full repeated-run live-eval batch and does not prove production identity, live Foundry execution, arbitrary candidate handling, multi-candidate case workflow, or final hiring decision authority.

## 12. Handoff Notes

**Summary status:** Complete for accepted E6 lab-scope manual smoke evidence; no full repeated-run batch/exported transcript.

**Counts:** Total `8` live scenarios in contract; Passed `2` in accepted smoke scope; Failed `0`; Error/Skipped `6`; Threshold met `Accepted for lab-scope smoke / not proven as repeated-run Standard-tier batch`; Applicability `Required`.

**Failures present?** No observed failures in accepted smoke evidence.

**Recommended next skill:**

- No observed failures: no `eval-failure-classifier` handoff is required from this summary.
- High-risk tier is not active; `high-risk-human-review-packager` is not required by risk tier.
- Orchestrator may proceed to Stage 12 if the human accepts the smoke-evidence caveats for this lab slice.
