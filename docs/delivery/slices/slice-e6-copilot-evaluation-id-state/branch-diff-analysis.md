# Current-State Reconciliation: slice-e6-copilot-evaluation-id-state - Explicit Copilot `evaluation_id` Workflow State

| Field | Value |
|---|---|
| Slice ID | `slice-e6-copilot-evaluation-id-state` |
| Branch / Base | `slice-e6-copilot-evaluation-id-state` / `main` (`13b20fa6e3c393e462020ebf26b90e20caf34add`) |
| Date | `2026-06-13` |
| Produced By | `current-state-reconciler` |
| Status | `Applied` |

**Inputs reviewed:** `git diff main...HEAD`, `git status --short --branch`, `git log --oneline --decorate --max-count=12`, slice spec, implementation notes, deviation log, eval contract, eval summary, manual config evidence, `openapi/evaluations-api.json`, `openapi/copilot-studio/evaluations-tool.swagger.json`, and the current-state/integration/actual-architecture docs updated by this reconciliation.

---

## Branch-Diff Analysis

### Change Summary by Category

| Category | Area | Change Description | Source-Controlled? | Source Evidence |
|---|---|---|---|---|
| User-Visible / Agent Behaviour | Copilot Studio topic workflow | One synthetic topic workflow submits the sample candidate, stores the returned `evaluation_id` as `submitted_evaluation_id`, retrieves through `retrieveEvaluationForCopilot`, and renders an advisory/audit summary. | Partial | `manual-config-evidence.md`, `implementation-notes.md`, `eval-summary.md` |
| Backend / Service / API | Retrieve wrapper | `POST /api/evaluations/retrieve` with operationId `retrieveEvaluationForCopilot` accepts JSON body field `evaluation_id` and reuses the same retrieve envelope as `GET /api/evaluations/{evaluation_id}`. | Yes | `src/hr_eval_lab/api/routes_evaluations.py`, `src/hr_eval_lab/domain/schemas/request.py`, `openapi/evaluations-api.json` |
| Backend / Service / API | Canonical retrieve preservation | `GET /api/evaluations/{evaluation_id}` / `getEvaluation` remains available and is still the canonical explicit-ID HTTP read. | Yes | `src/hr_eval_lab/api/routes_evaluations.py`, `openapi/evaluations-api.json` |
| Infrastructure / IaC / Configuration | Local/system file instructions | Agent instructions now tell coding agents to ignore OS/editor/cache/generated metadata. | Yes | `AGENTS.md`, `CLAUDE.md`, `.claude/AGENTS.md` |
| Infrastructure / IaC / Configuration | Azure build overlay | A large Azure build overlay was added as future-oriented workflow architecture documentation. It is not current-state implementation truth. | Yes | `docs/hr_hiring_agent_mvp_workflow_azure_build_overlay_v0_1.md` |
| Power Platform / Copilot Studio / Foundry | Curated connector contract | The curated Swagger 2.0 artifact exposes exactly three actions: `submitEvaluation`, `getEvaluation`, `retrieveEvaluationForCopilot`. | Yes | `scripts/export_copilot_openapi.py`, `openapi/copilot-studio/evaluations-tool.swagger.json`, `tests/test_copilot_studio_openapi.py` |
| Power Platform / Copilot Studio / Foundry | Tool routing | `submitEvaluation` and `retrieveEvaluationForCopilot` are configured as `Only when referenced by topics or agents` so topic routing owns the workflow. | No | `manual-config-evidence.md`, `deviations.md`, `eval-summary.md` |
| Data / State / Persistence | Workflow state | Copilot holds only transient topic/workflow state; the stored `submitted_evaluation_id` is not durable system-of-record state. Persisted evaluation records remain in the facade store/Blob-backed hosted path. | Partial | `manual-config-evidence.md`, `candidate-evaluation-council.md`, `actual-technical-architecture.md` |
| Security / Permissions / Identity | Auth boundaries | Retrieve wrapper uses the same simulated lab `hr` authorization and authenticates before body parsing. No Entra, production identity, or new auth model is implemented. | Yes for API; No for portal state | `routes_evaluations.py`, `tests/test_dt009_authorization.py`, `manual-config-evidence.md` |
| Integration / External-System | Manual portal configuration | Connector import, topic variable assignment, retrieve binding, and final Copilot Studio test are note-evidenced manual configuration. | No | `manual-config-evidence.md`, `eval-summary.md` |
| Test and Eval | Deterministic tests | Route, auth, status vocabulary, OpenAPI, correlation header, and Copilot Swagger tests cover the retrieve wrapper and three-action artifact. | Yes | `tests/test_dt001_happy_path.py`, `tests/test_dt007_status_vocabulary.py`, `tests/test_dt009_authorization.py`, `tests/test_dt014_openapi.py`, `tests/test_copilot_studio_openapi.py`, `tests/test_rp004_openapi_and_headers.py` |
| Test and Eval | Live eval evidence | Accepted lab-scope smoke covers primary submit/store/retrieve; no repeated-run batch/exported transcript exists. | Partial | `eval-summary.md`, `manual-config-evidence.md` |
| Documentation-Only | Delivery evidence | Implementation notes, deviations, manual evidence, eval contract/risk/readiness/planning artifacts were added for E6. | Yes, except `eval-summary.md` was untracked at reconciliation start | `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/` |
| Documentation-Only | Current-state reconciliation | Current-state, actual-architecture, and integration docs now describe the implemented wrapper, preserved GET route, three-action Swagger, manual topic workflow, and evidence limits. | Yes | Files listed in the update plan below |

### Documentation Impact Map

| Change Area | Affected Current-State Doc Sections | Affected Actual-Architecture Sections | Update Type |
|---|---|---|---|
| Body-based retrieve wrapper | `README.md`; `docs/product-current-state/README.md`; `candidate-evaluation-council.md` API sections; `copilot-studio-tool-readiness.md`; registration guide | System shape, module map, contracts | Additive |
| Preserved canonical GET | API endpoint tables and Copilot readiness docs | Contracts and "not built" boundaries | Corrective |
| Three-action curated Swagger | Product current-state, integration readiness, registration guide | Contracts | Corrective |
| Manual Copilot Studio topic workflow | Product current-state, integration overview/readiness/guide | System shape and not-built boundaries | Additive |
| Tool availability routing setting | Product current-state and integration docs | Manual configuration notes | Additive |
| Manual evidence limitations | Product current-state, integration docs, actual architecture limitations | Not-built and manual-config architecture notes | Corrective |
| Eval/test count drift | README and product-current-state docs | N/A | Corrective |

### Manual-Evidence Gaps

| Area / Surface | What Changed | Evidence Type Available | Follow-Up Required |
|---|---|---|---|
| Copilot Studio topic | Synthetic topic workflow stores and reuses `submitted_evaluation_id`. | Human operator notes plus chat-attached screenshot context; no repo-stored screenshot. | Human release authority decides whether notes are sufficient or requests redacted screenshots/export. |
| Power Apps custom connector | Connector imported the curated three-action Swagger. | Source Swagger in git plus manual notes. | Future ALM/export capture if the lab needs reproducible portal state. |
| Tool availability settings | `submitEvaluation` and `retrieveEvaluationForCopilot` set to `Only when referenced by topics or agents`. | Manual notes. | Future source-controlled runbook/export candidate. |
| Live eval transcript | Primary submit/store/retrieve smoke passed. | Eval summary and notes; no repeated-run batch or transcript. | Future regression/live-eval batch if confidence threshold must match the original contract. |
| Hosted deployment state | Deployed endpoint and connector test reported successful. | Manual notes. | Future deployment evidence/runbook candidate. |

### Known-Limitation Impacts

| Existing / New Limitation | Status After This Branch | Source Evidence |
|---|---|---|
| No Copilot Studio surface/configuration | Partially resolved for one manual synthetic lab workflow; still no production/source-controlled Copilot integration. | `manual-config-evidence.md`, `eval-summary.md` |
| Path-parameter retrieve binding | Platform limitation worked around by body-based retrieve; canonical GET remains available. | `deviations.md` D-001 |
| Broad standalone tool routing can pre-empt topics | Documented and mitigated manually for `submitEvaluation` and `retrieveEvaluationForCopilot`. | `deviations.md` D-002 |
| No live Foundry | Unchanged. | `actual-technical-architecture.md`, provider scaffold tests |
| Simulated lab identity only | Unchanged. | `api/auth.py`, `manual-config-evidence.md` |
| No Copilot ALM/source-control capture | New/explicitly documented manual-config limitation. | `manual-config-evidence.md`, `eval-summary.md` |
| No repeated-run live-eval batch | New/explicitly documented confidence limitation. | `eval-summary.md` |

### Deviations from Slice Spec

| Spec Intent | Actual Implementation | Deviation Log Ref | Impact on Docs |
|---|---|---|---|
| Bind stored topic variable into `getEvaluation.evaluation_id` path parameter without app/API changes unless blocked. | Added `POST /api/evaluations/retrieve` / `retrieveEvaluationForCopilot` with body field `evaluation_id`; preserved `getEvaluation`. | D-001 | Docs now describe both retrieve shapes and prefer the body-based wrapper for Copilot topic workflows. |
| Topic workflow should own submit/store/retrieve routing. | `submitEvaluation` and `retrieveEvaluationForCopilot` availability set to `Only when referenced by topics or agents`. | D-002 | Integration docs now describe the routing setting and the manual evidence limitation. |

### Blockers / Assumptions

| ID | Item | Impact / Risk | Required Action / Basis |
|---|---|---|---|
| AS-001 | Manual portal evidence is note-based and partial. | Current-state docs can state the manual workflow exists, but cannot claim durable ALM/source-control reproducibility. | Basis: `manual-config-evidence.md` sections 4, 7, and 10. |
| AS-002 | Eval summary was untracked at reconciliation start. | Reviewed as Stage 10/11 input, but ownership/staging remains outside this Stage 12 edit. | Basis: `git status --short --branch`. |
| AS-003 | Large Azure build overlay is future-oriented. | Current-state docs must not promote its Table/Queue/Foundry/MVP workflow details as implemented reality. | Basis: overlay text and actual-architecture boundaries. |

---

## Current-State Doc Update Plan

### Affected Documentation Files

| File Path | Nature of Change | Priority |
|---|---|---|
| `README.md` | Corrective/additive: current scope, test count, curated Swagger, manual Copilot caveats | High |
| `docs/product-current-state/README.md` | Corrective/additive: at-a-glance behavior, tests, integration summary | High |
| `docs/product-current-state/candidate-evaluation-council.md` | Corrective/additive: API endpoints, body retrieve request, manual topic workflow, limitations, tests | High |
| `docs/architecture/actual-technical-architecture.md` | Corrective/additive: actual manual Copilot configuration, API/module/contracts, not-built boundaries | High |
| `docs/integration/README.md` | Corrective/additive: integration status and manual configuration table | High |
| `docs/integration/copilot-studio-tool-readiness.md` | Corrective rewrite: three-action current contract and manual workflow caveats | High |
| `docs/integration/copilot-studio/registration-guide.md` | Corrective rewrite: three-action registration and body-based retrieve workflow | High |

### Section-Level Update Plan

| Document / Section | Current content summary | Required change | Change type | Source evidence | Checks |
|---|---|---|---|---|---|
| `README.md` - Current Scope | Listed 176 passing tests and no Copilot Studio surface. | List 200 passing tests, source and curated API artifacts, and one manual synthetic Copilot workflow with caveats. | Corrective/additive | OpenAPI artifacts, eval summary, manual evidence | Present tense; no production claim; no multi-candidate claim |
| `docs/product-current-state/README.md` - At a glance / Integration | Claimed no portal configuration exists. | Add three-action API surface and manual lab workflow; keep no production/live Foundry/ALM caveats. | Corrective/additive | Manual evidence, implementation notes | Present tense; no slice-history language |
| `candidate-evaluation-council.md` - HTTP API | Listed only POST submit and GET retrieve. | Add `POST /api/evaluations/retrieve`, body schema, shared retrieve behavior, and preserved canonical GET. | Additive | Route code, OpenAPI, tests | Endpoint facts match source-controlled contracts |
| `candidate-evaluation-council.md` - Copilot workflow / limitations | No manual Copilot workflow or evidence caveat. | Add synthetic topic workflow, tool availability setting, and manual-evidence limitations. | Additive/corrective | Manual evidence, eval summary, deviations | No production, Entra, Foundry, real-data, or ALM claims |
| `actual-technical-architecture.md` - System shape/contracts/not-built | Described no Copilot configuration and older storage wording. | Add actual manual Copilot configuration and three-action contracts; correct Blob/fail-closed distinction; retain no source-controlled/prod Copilot boundary. | Corrective/additive | Code, OpenAPI, manual evidence | Actual architecture only; guidelines untouched |
| `docs/integration/README.md` - Current State | Claimed no Copilot integration exists. | Split production/source-controlled gaps from one manual lab configuration; add connector artifact and topic workflow rows. | Corrective | Manual evidence, Swagger | Manual evidence caveats explicit |
| `copilot-studio-tool-readiness.md` | E4/two-action readiness only. | Replace with current three-action contract and manual lab workflow evidence/gaps. | Corrective rewrite | Swagger, manual evidence, eval summary | No stale E4/two-action claims |
| `copilot-studio/registration-guide.md` | E4/two-action checklist and GET-only smoke. | Replace with three-action registration, body-based retrieve workflow, tool availability setting, and GET plus body-retrieve smoke. | Corrective rewrite | Swagger, implementation notes, manual evidence | Function key remains secure; no query-string key |

### Sections Confirmed Unchanged

| File Path | Section | Reason No Change Required |
|---|---|---|
| `docs/product-current-state/candidate-evaluation-council.md` | Council orchestration, rigor, gates, evidence packet, prompt registry | E6 did not change council behavior or model/provider execution. |
| `docs/architecture/actual-technical-architecture.md` | Foundry provider scaffolds, CI, runtime requirements | E6 did not enable Foundry or change CI/runtime dependency boundaries. |

### Known Limitations - Updates

| Register Path | Action | Description | Source Evidence |
|---|---|---|---|
| `docs/product-current-state/candidate-evaluation-council.md` | Add/update | Manual Copilot Studio evidence is partial and narrow; no ALM/export/transcript/production identity/live Foundry. | `manual-config-evidence.md`, `eval-summary.md` |
| `docs/product-current-state/candidate-evaluation-council.md` | Update | Storage limitation is narrow Blob durability, not local-only persistence. | Existing architecture/storage docs, branch context |
| `docs/architecture/actual-technical-architecture.md` | Update | No production/source-controlled Copilot integration, but one manual lab workflow exists. | `manual-config-evidence.md` |

### Gaps, Assumptions, and Follow-Up Issue Candidates

| ID | Item | Affected Section | Risk | Treatment |
|---|---|---|---|---|
| DG-001 | No source-controlled Copilot ALM export or unpacked topic/connector state. | Integration and architecture docs | Medium | Follow-up issue candidate for Stage 14 only if release authority wants tracking. |
| DG-002 | No durable screenshot/export/transcript or repeated-run live-eval batch. | Integration docs and eval caveats | Medium | Documented limitation; release authority decides whether additional evidence is required. |
| DG-003 | Portal tool availability settings can drift. | Integration docs | Medium | Documented manual-config limitation; future export/runbook candidate. |

Follow-up issue candidates for Stage 14 (not created here): `Copilot Studio ALM/source-control capture` (`source-control-debt`, Medium), `Durable redacted evidence/export capture for manual Copilot workflow` (`documentation-gap`, Medium), `Repeated-run live-eval batch for Copilot state handoff` (`eval-debt`, Medium).

---

## Actual-Architecture Update

| Field | Value |
|---|---|
| Actual Architecture Document | `docs/architecture/actual-technical-architecture.md` |
| Status | `Applied` |

**Architecture change summary:** The system now has two retrieve shapes over the same persisted evaluation record: the canonical `GET /api/evaluations/{evaluation_id}` and a Copilot-friendly `POST /api/evaluations/retrieve` with body field `evaluation_id`. The curated Copilot Swagger exposes three actions. A manual Copilot Studio lab topic/custom-connector configuration exists outside source control for one synthetic submit/store/retrieve workflow, while production Copilot integration, Entra, live Foundry, Copilot ALM export, durable portal evidence, and multi-candidate workflow remain not built.

### Components Added

| Component | Type | Description | Source Evidence | Source-Controlled? |
|---|---|---|---|---|
| `retrieveEvaluationForCopilot` | API / Connector action | Body-based retrieve operation for Copilot Studio topic-variable binding; accepts `evaluation_id` in JSON body and reuses the same retrieve envelope as `getEvaluation`. | `routes_evaluations.py`, `openapi/evaluations-api.json`, Swagger artifact | Yes |
| `EvaluationRetrieveRequest` | Schema | Request schema with required `evaluation_id` and `extra="forbid"`. | `src/hr_eval_lab/domain/schemas/request.py` | Yes |
| Manual Copilot Studio synthetic workflow | Agent / Connector configuration | Topic calls `submitEvaluation`, stores `submitted_evaluation_id`, then calls `retrieveEvaluationForCopilot`; tool availability narrowed for topic routing. | `manual-config-evidence.md`, `eval-summary.md` | No |

### Components Modified

| Component | What Changed | Reason | Source Evidence | ADR Reference |
|---|---|---|---|---|
| Evaluation API routes | GET retrieve logic was shared with the new body-based retrieve route. | Preserve semantics while supporting Copilot body binding. | `routes_evaluations.py`, tests | N/A |
| Curated Copilot Swagger generator/artifact | Expected paths/actions changed from two to three and added `EvaluationRetrieveRequest`. | Keep connector artifact deterministic and source-controlled. | `scripts/export_copilot_openapi.py`, Swagger artifact | N/A |
| Current-state/integration/architecture docs | Stale no-Copilot/two-action claims corrected. | Match implemented and note-evidenced reality. | This reconciliation | N/A |

### Components Removed or Deprecated

| Component | Status | Reason | Source Evidence |
|---|---|---|---|
| Path-parameter-only Copilot topic retrieve pattern | Deprecated for topic-driven workflow | Copilot Studio did not reliably preserve the path-parameter variable binding. | `deviations.md` D-001 |

### Integration / Data Flow Changes

| Integration / Flow | Change Description | Direction | Source Evidence |
|---|---|---|---|
| Copilot Studio synthetic topic | `submitEvaluation` -> store `submitted_evaluation_id` -> `retrieveEvaluationForCopilot` body field `evaluation_id` -> advisory/audit summary. | Added | `manual-config-evidence.md`, `eval-summary.md` |
| Custom connector action set | Curated Swagger exposes three actions instead of two. | Modified | Swagger artifact, tests |
| API retrieve flow | GET and body-POST retrieve share persisted record lookup and envelope behavior. | Added/modified | Route code, tests |

### Security, Identity, and Permissions Changes

| Area | Change Description | Source Evidence |
|---|---|---|
| API authorization | New body-based retrieve route requires the same simulated lab `hr` authorization and runs auth before body parsing. | `routes_evaluations.py`, `tests/test_dt009_authorization.py` |
| Function key / lab headers | Curated Swagger still represents Function key auth as secure header `x-functions-key` and exposes temporary `X-Lab-*` headers; no Entra identity is implemented. | Swagger artifact, registration guide |
| Evidence redaction | Manual evidence records no Function key, connection secret, tenant ID, subscription ID, real applicant data, or secret-bearing screenshot. | `manual-config-evidence.md` |

### Manual-Configuration Architecture Notes

Components that are part of actual architecture but **not yet source-controlled** - each needs release-authority treatment before closeout or future ALM work.

| Component / Configuration | Surface | Description | Follow-Up Issue Ref |
|---|---|---|---|
| Copilot Studio topic `E6 Evaluate Sample Candidate` | Copilot Studio | Manual synthetic workflow for submit/store/retrieve. | Candidate for Stage 14 drafter if required |
| Power Apps custom connector import state | Power Platform | Portal connector updated from the curated Swagger artifact. | Candidate for Stage 14 drafter if required |
| Tool availability settings | Copilot Studio tools | `submitEvaluation` and `retrieveEvaluationForCopilot` set to `Only when referenced by topics or agents`. | Candidate for Stage 14 drafter if required |
| Final Copilot Studio smoke evidence | Copilot Studio test pane | Note-evidenced completion; no durable transcript/export stored. | Candidate for Stage 14 drafter if required |

### Known Architecture Limitations (Updated)

| Limitation | Description | Guideline Gap? | Follow-Up Issue Candidate |
|---|---|---|---|
| Copilot ALM/source-control gap | Manual portal topic/connector/tool state is not exported or unpacked into source control. | Yes | Yes, if release authority wants tracking |
| Evidence durability gap | Current evidence is notes plus chat screenshot context, not durable repo-safe screenshot/export/transcript. | No | Yes, if closeout requires stronger evidence |
| No production identity | Simulated lab headers and Function key auth remain; no Entra delegated identity exists. | No, within lab scope | No for E6 |
| No live Foundry | Council still uses deterministic mock provider; Foundry provider scaffolds remain fail-closed. | No, within lab scope | No for E6 |
| No multi-candidate workflow | Workflow is one synthetic sample candidate only. | No, within E6 scope | No for E6 |

### Architecture Guideline Cross-References (read-only)

Guidelines were **not** changed here. No ADR or architecture-guideline update was performed.

| Guideline Section | Compliance Status | Notes |
|---|---|---|
| Copilot as front door / tool orchestrator | Compliant for lab scope | Manual topic orchestrates one synthetic workflow; durable workflow state remains outside Copilot. |
| Facade owns controls and envelopes | Compliant | Copilot retrieves facade envelopes and does not own evaluation decisions. |
| Manual configuration evidence | Partial gap | Evidence exists but is note-based and not source-controlled ALM. |
| Identity and authorization | Lab-limited | No production/Entra claim; simulated lab auth remains documented. |
