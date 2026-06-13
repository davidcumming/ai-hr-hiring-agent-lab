# Manual Config Evidence Summary

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `slice-e6-copilot-evaluation-id-state` |
| Slice Name | E6 Explicit Copilot `evaluation_id` Workflow State |
| Created | 2026-06-13 |
| Agent / Author | Codex, using the `documentation-and-architecture-reconciliation-agent` role brief in a constrained slice-local evidence pass |
| Evidence Source | Human operator notes and chat-attached screenshot context supplied for this slice |
| Source Control Capture Report | Not produced for this docs-only evidence update |
| Status | Partial - note-based evidence captured; chat screenshot context exists but no durable screenshot/export path was supplied |
| Redaction Concerns | None identified in this note-based evidence; no secrets or secret-bearing screenshots are included |

---

## 2. Evidence Register

| # | Item | Surface | Resource / Component Name | Environment | Evidence Status | Evidence File(s) | Notes Ref |
|---|---|---|---|---|---|---|---|
| 1 | Copilot Studio agent, environment, and topic | Copilot Studio | `HR Hiring Agent Lab` / `E6 Evaluate Sample Candidate` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.1 |
| 2 | Custom connector API definition update | Power Apps custom connector | `openapi/copilot-studio/evaluations-tool.swagger.json` | `CHI-LAB-SANDBOX` | Partial | `openapi/copilot-studio/evaluations-tool.swagger.json` | See Section 3.2 |
| 3 | Backend retrieve wrapper deployment and direct test | Azure Functions API facade | `POST /api/evaluations/retrieve` | Lab Function App | Partial | None supplied | See Section 3.3 |
| 4 | `retrieveEvaluationForCopilot` connector test | Power Apps custom connector | `retrieveEvaluationForCopilot` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.4 |
| 5 | Topic submit and variable storage | Copilot Studio topic/workflow | `submitEvaluation` -> `submitted_evaluation_id` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.5 |
| 6 | Topic retrieve action and stored-variable reuse | Copilot Studio topic/workflow | `retrieveEvaluationForCopilot` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.6 |
| 7 | Tool availability routing correction | Copilot Studio tools | `submitEvaluation`, `retrieveEvaluationForCopilot` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.7 |
| 8 | Final Copilot Studio test result | Copilot Studio test pane | `E6 Evaluate Sample Candidate` | `CHI-LAB-SANDBOX` | Partial | Chat-attached screenshot context only; no repo file path claimed | See Section 3.8 |

---

## 3. Notes

### 3.1 Copilot Studio Agent, Environment, And Topic

**Resource:** `HR Hiring Agent Lab` / `E6 Evaluate Sample Candidate` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Copilot Studio environment | `CHI-LAB-SANDBOX` | Environment name is recorded as non-secret configuration evidence. |
| Agent | `HR Hiring Agent Lab` | Human operator reported and screenshot context showed this agent in Copilot Studio. |
| Topic | `E6 Evaluate Sample Candidate` | Topic trace showed `E6 Evaluate Sample Candidate / Topic / Completed`. |
| Topic trigger | Agent-chosen topic for sample candidate evaluation | User prompt was `Evaluate the sample candidate.` |
| Evidence type | Human operator notes plus chat-attached screenshot context | No durable screenshot, export, transcript file, or automated replay artifact path was supplied for repository storage. |

### 3.2 Custom Connector API Definition Update

**Resource:** Power Apps custom connector - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Imported API definition | `openapi/copilot-studio/evaluations-tool.swagger.json` | Source-controlled curated Swagger artifact used to update the connector. |
| Exposed operations | `submitEvaluation`, `getEvaluation`, `retrieveEvaluationForCopilot` | Connector now exposes all three operations. |
| Existing retrieve operation preserved | `GET /api/evaluations/{evaluation_id}` / `getEvaluation` | Existing explicit-ID retrieve path remains available. |
| New retrieve operation | `POST /api/evaluations/retrieve` / `retrieveEvaluationForCopilot` | Body-based retrieve wrapper added for Copilot-friendly topic variable binding. |
| Export evidence | Not supplied | No exported connector package or portal screenshot is claimed by this evidence file. |

### 3.3 Backend Retrieve Wrapper Deployment And Direct Test

**Resource:** Azure Functions API facade - **Environment:** Lab Function App

| Setting Name | Value / Description | Notes |
|---|---|---|
| Deployed endpoint | `POST /api/evaluations/retrieve` | Human operator reported the new backend endpoint was deployed. |
| Operation ID | `retrieveEvaluationForCopilot` | Body-based retrieve wrapper for Copilot Studio. |
| Direct backend test | Succeeded | Human operator reported the deployed endpoint was directly tested. |
| Existing endpoint | `GET /api/evaluations/{evaluation_id}` / `getEvaluation` | Preserved; E6 did not remove or replace the existing route. |

### 3.4 `retrieveEvaluationForCopilot` Connector Test

**Resource:** Power Apps custom connector action `retrieveEvaluationForCopilot` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Connector operation | `retrieveEvaluationForCopilot` | Added to the custom connector and exposed to Copilot Studio. |
| Connector test result | HTTP 200 | Human operator reported the connector test succeeded. |
| Response status | `completed` | Reported connector result status. |
| ID check | `evaluation_id` matched the requested/stored ID | Confirms the wrapper can retrieve the intended persisted evaluation record. |

### 3.5 Topic Submit And Variable Storage

**Resource:** Copilot Studio topic/workflow `E6 Evaluate Sample Candidate` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Submit action | `submitEvaluation` | Topic calls `submitEvaluation` for the synthetic sample candidate workflow. |
| Stored variable | `submitted_evaluation_id` | The `submitEvaluation` output `evaluation_id` is stored in a topic/workflow variable and used/displayed under this name. |
| Confirmation message | `Stored evaluation ID: eval-a427db3ad61c4e8eac20` | Human operator reported and screenshot context showed the confirmation message. |
| Data scope | Synthetic sample candidate only | No real candidate data was used. |

### 3.6 Topic Retrieve Action And Stored-Variable Reuse

**Resource:** Copilot Studio topic/workflow `E6 Evaluate Sample Candidate` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Retrieve action | `retrieveEvaluationForCopilot` | Topic uses the body-based retrieve action instead of the path-parameter action for this workflow. |
| Input binding | Stored topic/workflow variable `submitted_evaluation_id` -> body field `evaluation_id` | Keeps identifier handoff explicit and avoids model-filled identifiers. |
| Stored value used | `eval-a427db3ad61c4e8eac20` | Final response displayed the stored evaluation ID. |
| Retrieved output | Advisory evaluation/audit summary | Copilot produced retrieved advisory evaluation/audit summary for the same stored ID. |

### 3.7 Tool Availability Routing Correction

**Resource:** Copilot Studio tools `submitEvaluation` and `retrieveEvaluationForCopilot` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Stale tool list | Agent-level tool list was stale until `retrieveEvaluationForCopilot` was added as a tool. | Human operator reported the stale-list behavior. |
| Initial routing issue | Standalone connector tools could pre-empt topic routing. | The standalone `submitEvaluation` tool initially pre-empted the E6 topic. |
| Tool usage setting | `Only when referenced by topics or agents` | Applied to `submitEvaluation` and `retrieveEvaluationForCopilot`. |
| Result | Topic routing completed successfully. | Topic-driven workflow completed after availability was narrowed. |

### 3.8 Final Copilot Studio Test Result

**Resource:** Copilot Studio test pane - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| User prompt | `Evaluate the sample candidate.` | Final Copilot Studio test prompt. |
| Topic trace | `E6 Evaluate Sample Candidate / Topic / Completed` | Human operator reported and screenshot context showed successful topic completion. |
| Displayed stored ID | `eval-a427db3ad61c4e8eac20` | Copilot response displayed the stored evaluation ID. |
| Retrieved summary | Copilot produced a retrieved advisory evaluation/audit summary. | Summary included advisory result content and audit-style criterion details. |
| Advisory boundary | Preserved | Final response preserved advisory-only and human-review-required language. |
| Screenshot handling | Chat-attached screenshot context exists; no durable path supplied | This evidence file does not copy the screenshot or invent a repository file path. |

---

## 4. Evidence Limitations

- This evidence is primarily note-based from the human operator, with chat-attached screenshot context.
- This file does not claim a repository-stored screenshot, exported connector package, exported topic package, or automated replay artifact.
- The source-controlled connector API definition exists at `openapi/copilot-studio/evaluations-tool.swagger.json`, but the actual portal connector import, topic configuration, tool availability settings, and final Copilot Studio test remain manual configuration evidence in this file.
- This file records the supplied final successful test only; it does not claim a full repeated-run live eval batch.

---

## 5. Slice Boundary

- E6 proves one synthetic Copilot Studio topic-driven submit -> store `evaluation_id` -> retrieve workflow.
- E6 uses `retrieveEvaluationForCopilot` for the Copilot-friendly retrieve path and preserves `getEvaluation`.
- E6 does not prove multi-candidate case workflow, arbitrary uploads, production identity, Entra delegated identity, replacement of lab-only auth, live Azure AI Foundry / Agent Framework council execution, production readiness, or final hiring decisions.
- E6 does not approve manual configuration debt as permanent and does not close the slice.
- E6 does not update current-state docs in this requested evidence-capture pass.

---

## 6. Implementation Lesson Candidate

For Copilot Studio, standalone connector tools can pre-empt topic routing unless their availability is set to `Only when referenced by topics or agents`. For topic-driven workflows, set connector actions to topic/agent referenced use rather than broad direct agent use.

---

## 7. Risk Summary

| # | Item | Risk Level | Risk Rationale | Source-Control Migration Feasible? | Expected Timeline |
|---|---|---|---|---|---|
| 1 | Copilot Studio agent, environment, and topic | Medium | Topic routing and trigger state affect reproducibility and are only note/screenshot-context evidenced here. | Partially | Future Copilot/Power Platform ALM export or runbook slice |
| 2 | Custom connector API definition update | Medium | Source Swagger is in git, but portal import state is manual and can drift. | Yes | Future solution export/unpack or connector ALM work |
| 3 | Backend retrieve wrapper deployment and direct test | Medium | Hosted deployment state affects the manual workflow and is not captured as an artifact here. | Partially | Deployment evidence/runbook or release evidence package |
| 4 | `retrieveEvaluationForCopilot` connector test | Medium | Connector behavior depends on portal configuration and connection state. | Partially | Future connector ALM/runbook work |
| 5 | Topic submit and variable storage | Medium | Variable assignment controls the core E6 state handoff and is manual portal configuration. | Partially | Future topic/workflow export or runbook |
| 6 | Topic retrieve action and stored-variable reuse | Medium | Retrieve behavior depends on explicit body binding from the stored variable. | Partially | Future topic/workflow export or runbook |
| 7 | Tool availability routing correction | Medium | Tool routing precedence can bypass the intended topic if availability is too broad. | Partially | Future Copilot tool configuration export/runbook |
| 8 | Final Copilot Studio test result | Medium | Final success is note/screenshot-context evidenced, not represented by a durable replay artifact. | Partially | Future live-eval artifact capture |

---

## 8. Recommended GitHub Issues

No issues recommended for this slice evidence capture. The user explicitly requested no GitHub issue creation or closure.

---

## 9. Redaction Concerns

| File / Note | Concern | Status | Action Required |
|---|---|---|---|
| This note-based evidence file | Function key, connection secret, tenant ID, subscription ID, raw applicant data, or secret-bearing screenshot could be accidentally added later | Resolved for current file | Keep secrets and private tenant details out of future evidence; redact screenshots before repository storage |

No Function key, connection secret, tenant ID, subscription ID, raw applicant data, connection string, SAS token, or secret-bearing screenshot is recorded in this file.

---

## 10. Handoff Summary

### To `manual-evidence-normalizer` (Stage 12)

- Evidence summary: `docs/delivery/slices/slice-e6-copilot-evaluation-id-state/manual-config-evidence.md`
- Screenshots: chat-attached screenshot context only; no repository-stored screenshot path supplied
- Exports: none supplied
- Source-controlled API definition reference: `openapi/copilot-studio/evaluations-tool.swagger.json`
- Pending redaction concerns: none identified in the current note-based evidence
- Evidence Pending items: screenshot/export/replay evidence for manual portal configuration, if the team requires durable artifacts for closeout

### Closeout Blockers

This file does not close the slice or approve closeout. Human release authority must decide whether note-based plus chat-screenshot-context evidence is sufficient or whether additional redacted screenshots/exports are required before closeout.

| # | Item | Reason | Required Action |
|---|---|---|---|
| 1 | Portal/manual configuration evidence depth | Evidence is note-based, with no durable screenshot/export path supplied | Human release authority decides whether to accept this evidence or request redacted screenshots/exports before closeout |

### Evidence Counts

| Status | Count |
|---|---|
| Complete | 0 |
| Partial | 8 |
| Evidence Pending | 0 |
| **Total items** | 8 |
