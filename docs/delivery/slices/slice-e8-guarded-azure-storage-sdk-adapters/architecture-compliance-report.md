# Architecture Compliance Report: E8 Guarded Azure Storage SDK Adapters

Verdict: **Clear for guarded implementation under explicit human instruction**

## Inputs

- Implementation plan: user-provided E8 plan in the Codex implementation turn.
- Buildout authority: `docs/hr_hiring_agent_mvp_workflow_azure_build_overlay_v0_1.md`.
- Current-state architecture: `docs/architecture/actual-technical-architecture.md`.
- Storage seam detail: `docs/architecture/provider-and-storage-seams.md`.
- Approved ADRs: none in `docs/architecture/`; the Foundry ADR remains draft and unrelated to storage-only E8.

## Compliance Surface

E8 introduces internal workflow storage protocols, a deterministic local default,
a guarded Azure SDK-backed workflow storage adapter, workflow-specific config,
a disabled-by-default live smoke, deterministic tests, and current-state docs.
It does not add public APIs, Copilot Studio/Power Platform changes, Foundry
execution, workers, Azure resource creation, or production identity.

## Findings

| Area | Finding | Rationale |
|---|---|---|
| Workflow state in Azure Table Storage | Compliant | The overlay identifies Azure Table Storage as the workflow system of record for case state, gates, tasks, notifications, reviews, and audit/event ledger. E7 already created strict Table-shaped contracts. |
| Workflow artifacts in Azure Blob Storage | Compliant | The overlay identifies Blob as the document/artifact store. E7 already created canonical Blob path contracts. E8 stores those paths as blob names in a configured container without creating containers. |
| Async work in Azure Queue Storage | Compliant | The overlay identifies Queue Storage as async orchestration. E7 already created identifier-only queue message contracts. E8 only sends/peeks/receives/deletes these contracts; no worker is introduced. |
| Guarded Azure SDK usage | Compliant | Existing storage precedent uses lazy SDK imports, identity-based auth, explicit storage guard, no connection strings/account keys/SAS/query strings, and no Azure imports on the default path. E8 mirrors that posture with a workflow-specific guard. |
| Public/API/Copilot surface | Compliant | E8 wires only internal `app.state.workflow_storage`; no routes, OpenAPI, Copilot Swagger, connector, topic, or worker surface is added. |
| Architecture guideline gap | Recorded non-blocking gap | The repo currently records no formal architecture guideline docs or approved storage ADRs in `docs/architecture/`. The user explicitly requested implementation after the plan caveat, and the overlay plus current-state docs already establish the target storage services and guard style. No new service category or live model path is introduced. |

## ADR Gap Disposition

No blocking ADR is required before E8 because the decision to use Azure Table,
Blob, and Queue for workflow foundation is already captured in the overlay and
E8 remains guarded, internal, storage-only, and non-public. A future ADR may
still be useful before production-grade concurrency, retention, resource
provisioning, worker execution, or identity/authorization decisions.

## Handoff

Proceed with E8 implementation under these constraints:

- Keep `LocalWorkflowStore` as the default deterministic backend.
- Require `HRHA_ENABLE_AZURE_WORKFLOW_STORAGE=true` and explicit Azure workflow config before SDK-backed construction.
- Import Azure SDKs lazily only after guards pass.
- Do not create resources, mutate portal state, run Foundry, add case APIs, or change OpenAPI/Copilot artifacts.
