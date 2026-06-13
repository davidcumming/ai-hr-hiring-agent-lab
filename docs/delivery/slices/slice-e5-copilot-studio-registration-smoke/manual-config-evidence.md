# Manual Config Evidence Summary

## 1. Report Metadata

| Field | Value |
|---|---|
| Slice ID | `slice-e5-copilot-studio-registration-smoke` |
| Slice Name | E5 Copilot Studio Registration Smoke |
| Created | 2026-06-12 |
| Agent / Author | Codex, using the `documentation-and-architecture-reconciliation-agent` role brief and `.claude/skills/manual-config-evidence-capture/SKILL.md` |
| Evidence Source | Human operator notes supplied for this slice |
| Source Control Capture Report | Not yet produced for this slice |
| Status | Partial - note-based evidence captured; screenshots and portal exports were not supplied |
| Redaction Concerns | None identified in this note-based evidence; no screenshots or secrets are included |

---

## 2. Evidence Register

| # | Item | Surface | Resource / Component Name | Environment | Evidence Status | Evidence File(s) | Notes Ref |
|---|---|---|---|---|---|---|---|
| 1 | Copilot Studio agent and environment setup | Copilot Studio / Power Platform | `HR Hiring Agent Lab` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.1 |
| 2 | Dataverse availability and maker/author privileges | Power Platform / Dataverse | Environment roles for `CHI-LAB-SANDBOX` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.2 |
| 3 | Agent settings for web search and model selection | Copilot Studio | `HR Hiring Agent Lab` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.3 |
| 4 | Power Apps custom connector API definition imported | Power Platform custom connector | `openapi/copilot-studio/evaluations-tool.swagger.json` | `CHI-LAB-SANDBOX` | Partial | `openapi/copilot-studio/evaluations-tool.swagger.json` | See Section 3.4 |
| 5 | Connector host and Function key auth configuration | Power Apps custom connector / Power Platform/Copilot connection | `func-hrha-lab-cac001-a4fpachkcgcug9cb.canadacentral-01.azurewebsites.net` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.5 |
| 6 | Stale Power Platform/Copilot connection refreshed or recreated | Power Platform/Copilot connection | Stored connector credentials and metadata | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.6 |
| 7 | `submitEvaluation` Copilot Studio tool/action mapping and smoke result | Copilot Studio tool/action | `submitEvaluation` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.7 |
| 8 | `getEvaluation` Copilot Studio tool/action mapping and smoke result | Copilot Studio tool/action | `getEvaluation` | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.8 |
| 9 | Idempotency key mapping correction | Copilot Studio tool/action | `submitEvaluation` input/header mapping | `CHI-LAB-SANDBOX` | Partial | None supplied | See Section 3.9 |

---

## 3. Notes

### 3.1 Copilot Studio Agent And Environment

**Resource:** `HR Hiring Agent Lab` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Copilot Studio agent | `HR Hiring Agent Lab` | Human operator reported that the agent was created. |
| Environment | `CHI-LAB-SANDBOX` | Environment name is recorded as non-secret configuration evidence. |
| Evidence type | Human operator note | No screenshot, export, or automated replay artifact was supplied. |

### 3.2 Dataverse And Maker/Author Privileges

**Resource:** `CHI-LAB-SANDBOX` role configuration - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Dataverse availability | Dataverse was initially missing and was later added to the environment. | Recorded as portal/low-code environment setup evidence. |
| Maker/author privileges | Required maker/author privileges were resolved using available Dataverse roles. | The expected Agent Author role was not visible. |
| Roles used | Environment Maker and Bot Author/system-admin-style access | Role names are recorded; no user identifiers, tenant identifiers, or privileged credential details are included. |

### 3.3 Agent Settings

**Resource:** `HR Hiring Agent Lab` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Web search | Disabled | Human operator reported this setting. |
| Model | GPT-4.1 selected | Human operator reported this setting. |

### 3.4 Power Apps Custom Connector API Definition

**Resource:** Power Apps custom connector - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Terminology | Power Apps custom connector = API definition | Use this term for the imported API definition, not for stored credentials. |
| Imported API definition | `openapi/copilot-studio/evaluations-tool.swagger.json` | This source-controlled file is the connector API definition used for import. |
| Exposed operations | `submitEvaluation`, `getEvaluation` | Imported from the curated Copilot Studio Swagger artifact. |
| Export evidence | Not supplied | No exported connector package or portal screenshot is claimed by this evidence file. |

### 3.5 Connector Host And Function Auth

**Resource:** Power Apps custom connector / Power Platform/Copilot connection - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Connector host | `func-hrha-lab-cac001-a4fpachkcgcug9cb.canadacentral-01.azurewebsites.net` | The Function App host is environment-specific configuration evidence and is not treated as a secret. |
| Previous placeholder host | `function-app-host.example` | Corrected from the placeholder in the imported API definition. |
| Function auth mechanism | Azure Function direct auth with `x-functions-key` confirmed | The key value is not recorded. |
| Terminology | Power Platform/Copilot connection = stored credentials for connector | Use this term for the stored credential/auth configuration, not for the API definition. |

### 3.6 Connection Refresh / Recreate

**Resource:** Power Platform/Copilot connection - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Connection refresh | Power Platform/Copilot connection was refreshed or recreated after connector host/security changes. | Human operator reported that stale connections continued using old metadata until refreshed or recreated. |
| Follow-up need | Runbook note recommended | This is backlog tracking only, not an approved architecture decision. |

### 3.7 `submitEvaluation` Copilot Studio Tool/Action

**Resource:** Copilot Studio tool/action `submitEvaluation` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Terminology | Copilot Studio tool/action = agent-level operation wiring/input mapping | Use this term for the agent-level operation configuration. |
| `X-Lab-Actor-Id` | `copilot-e5-lab-user` | Lab-only simulated actor header. |
| `X-Lab-Roles` | `hr` | Lab-only simulated role header. |
| `position_id` | `pos-sample-001` | Synthetic fixture identifier only. |
| `candidate_ref` | `cand-sample-001` | Synthetic fixture identifier only. |
| `idempotency_key` | `e5-copilot-submit-001` | Body field mapping. |
| `Idempotency-Key` | `e5-copilot-submit-001` | Header mapping. |
| Smoke result | `submitEvaluation` succeeded from Copilot Studio. | Human operator reported success; no automated replay artifact is included. |

### 3.8 `getEvaluation` Copilot Studio Tool/Action

**Resource:** Copilot Studio tool/action `getEvaluation` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| `X-Lab-Actor-Id` | `copilot-e5-lab-user` | Lab-only simulated actor header. |
| `X-Lab-Roles` | `hr` | Lab-only simulated role header. |
| `evaluation_id` | Dynamically filled with AI | Human operator reported that `getEvaluation` succeeded when supplied an explicit `evaluation_id`. |
| `X-Correlation-Id` / correlation id | `e5-copilot-retrieve` | Correlation value configured for retrieve smoke. |
| Smoke result | `getEvaluation` succeeded from Copilot Studio when given an explicit `evaluation_id`. | Human operator reported success; no automated replay artifact is included. |

### 3.9 Idempotency-Key Mapping Correction

**Resource:** Copilot Studio tool/action `submitEvaluation` - **Environment:** `CHI-LAB-SANDBOX`

| Setting Name | Value / Description | Notes |
|---|---|---|
| Failure observed | Missing `Idempotency-Key` caused `malformed_request_body`. | Human operator reported this failure mode. |
| Correction | Tool/action mapping was corrected to send both `idempotency_key` and `Idempotency-Key` as `e5-copilot-submit-001`. | This corrected the malformed request body issue. |
| E6 caveat | Copilot Studio does not reliably chain `submitEvaluation.evaluation_id` into `getEvaluation.evaluation_id` using only "Dynamically fill with AI." | This is an orchestration/state-management limitation, not an API failure. |
| E6 requirement | E6 must store `evaluation_id` explicitly in a Copilot topic/workflow variable. | Terminology: Copilot topic/workflow = orchestration/state management. |

---

## 4. Evidence Limitations

- This evidence is note-based from the human operator unless screenshots, portal exports, connector exports, or automated replay artifacts are later added.
- This file does not claim screenshot evidence.
- This file does not claim exported connector evidence.
- This file does not claim automated replay evidence.
- The source-controlled connector API definition exists at `openapi/copilot-studio/evaluations-tool.swagger.json`, but the actual portal import and connection configuration remain human-reported manual configuration evidence in this file.

---

## 5. Slice Boundary

- E5 proves Copilot Studio tool registration smoke only.
- E5 does not prove robust natural-language orchestration.
- E5 does not prove multi-candidate case workflow.
- E5 does not prove live Azure AI Foundry / Agent Framework council execution.
- E5 does not replace lab-only Function key/header auth.
- E5 does not approve manual configuration debt as permanent and does not close the slice.

---

## 6. Risk Summary

| # | Item | Risk Level | Risk Rationale | Source-Control Migration Feasible? | Expected Timeline |
|---|---|---|---|---|---|
| 1 | Copilot Studio agent and environment setup | Medium | Portal-created agent/environment state affects reproducibility and is only note-evidenced here. | Partially | Future Copilot/Power Platform ALM export or runbook slice |
| 2 | Dataverse availability and maker/author privileges | High | Environment provisioning and elevated role choices affect access, auditability, and repeatability. | Partially | Future environment setup/runbook or ALM governance work |
| 3 | Agent settings for web search and model selection | Medium | Model and search settings affect agent behavior and should be replayable. | Partially | Future Copilot configuration export/runbook |
| 4 | Power Apps custom connector API definition imported | Medium | The source API definition is in git, but the portal import state is note-evidenced only. | Yes | Future solution export/unpack or connector ALM work |
| 5 | Connector host and Function key auth configuration | High | Endpoint and credential binding determine production of tool calls; key value must remain secret. | Partially | Future Entra delegated identity and connector ALM work |
| 6 | Stale Power Platform/Copilot connection refreshed or recreated | Medium | Stale connection metadata can make smoke results misleading after connector host/security changes. | Yes | Runbook follow-up |
| 7 | `submitEvaluation` Copilot Studio tool/action mapping and smoke result | Medium | Tool/action input mapping controls whether the API receives the intended synthetic fixture request. | Partially | Future topic/workflow export or runbook |
| 8 | `getEvaluation` Copilot Studio tool/action mapping and smoke result | Medium | Retrieve behavior depends on explicit `evaluation_id` state handoff that is not robustly orchestrated yet. | Partially | E6 topic/workflow state slice |
| 9 | Idempotency key mapping correction | Medium | Missing header/body mapping causes malformed requests; this is critical for repeatable smoke behavior. | Partially | E6 topic/workflow state slice plus runbook |

---

## 7. Created Follow-Up GitHub Issues

These follow-up issues were created as non-destructive backlog tracking records. They are not approved architecture decisions, residual-risk acceptance, committed delivery scope, or slice closeout approval.

| Issue | Title | URL | Related Evidence Item # |
|---|---|---|---|
| #1 | E6: Add explicit Copilot topic/workflow variable storage for `evaluation_id` | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/1 | 8, 9 |
| #2 | Document Power Platform connection staleness / recreate-after-connector-change runbook | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/2 | 5, 6 |
| #3 | Replace lab-only Function key plus fake `X-Lab-*` headers with Entra delegated identity and role mapping | https://github.com/davidcumming/ai-hr-hiring-agent-lab/issues/3 | 5, 7, 8 |

---

## 8. Redaction Concerns

| File / Note | Concern | Status | Action Required |
|---|---|---|---|
| This note-based evidence file | Function key, connection secret, tenant ID, subscription ID, or secret-bearing screenshot could be accidentally added later | Resolved for current file | Keep secrets out of future evidence; redact screenshots before repository storage |

No Function key, connection secret, tenant ID, subscription ID, raw applicant data, or secret-bearing screenshot is recorded in this file.

---

## 9. Handoff Summary

### To `manual-evidence-normalizer` (Stage 12)

- Evidence summary: `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md`
- Screenshots: none supplied
- Exports: none supplied
- Source-controlled API definition reference: `openapi/copilot-studio/evaluations-tool.swagger.json`
- Pending redaction concerns: none identified in the current note-based evidence
- Evidence Pending items: screenshot/export evidence for the manual portal and low-code configuration, if the team requires it for closeout
- Follow-up GitHub issues created: #1, #2, #3.

### Closeout Blockers

This file does not close the slice or approve closeout. Human release authority must decide whether note-based evidence is sufficient or whether additional screenshots/exports are required before closeout.

| # | Item | Reason | Required Action |
|---|---|---|---|
| 1 | Portal/manual configuration evidence depth | Evidence is note-based only | Human release authority decides whether to accept note-based evidence or request redacted screenshots/exports before closeout |

### Evidence Counts

| Status | Count |
|---|---|
| Complete | 0 |
| Partial | 9 |
| Evidence Pending | 0 |
| **Total items** | 9 |
