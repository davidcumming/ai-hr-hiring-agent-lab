# Azure Lab Wiring — Exact Values Needed (Placeholders Only)

Checklist of every concrete value that future live Azure/Foundry wiring
needs, so that wiring day is a configuration exercise. **This document contains
placeholders only — no real subscription, tenant, endpoint, object ID, agent
ID, or secret values exist anywhere in this repository, and none may be
committed.** Real values arrive through an approved channel at wiring time.

## 0. Human gates that must pass FIRST

No value below may be acted on — no resource created, no setting flipped, no
live call attempted — until **both** of these human gates pass:

1. **Foundry-wiring ADR approval** —
   [`../delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`](../delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md)
   is a **draft, NOT approved**. It owns the live runtime-shape decision
   (project Responses API vs prompt agent vs hosted agent), the final
   provider-ID enumeration, and the live trace/eval metadata contract.
2. **BQ-005 region/data-residency approval** — Canadian-region adoption
   (e.g. Canada Central) requires explicit human approval; never adopt a
   region silently.

Additional standing gates: any merge, any GitHub Issue creation, any Azure
resource deployment, and residual-risk acceptance are human decisions.

## 1. Azure subscription and resource group

| Value | Placeholder | Notes |
|---|---|---|
| Subscription ID | `<azure-subscription-id>` | Never committed. |
| Entra tenant ID | `<entra-tenant-id>` | Never committed; Bicep resolves `subscription().tenantId` at deploy time. |
| Resource group | `rg-hrha-lab-cac` (suggested default) | Created out-of-band; see `infra/parameters.sample.json`. |
| Region | `<approved-canadian-region>` (e.g. `canadacentral`) | Only after BQ-005 approval (`infra/bicep/main.bicep` `location` param). |
| Resource name prefix | `hrhalab` (sample default) | `infra/bicep/main.bicep` `namePrefix` param. |

## 2. Storage (records + artifact tree + metadata tables)

| Value | Placeholder | Maps to |
|---|---|---|
| Storage account name | `<storage-account>` (3–24 lowercase alphanumerics; sample `hrhalabstor`) | `infra/bicep/main.bicep`; shared-key access disabled (`allowSharedKeyAccess: false`). |
| Blob account URL | `https://<storage-account>.blob.core.windows.net` | `config/lab-config.toml` `[storage.azure] account_url` / app setting `HRHA_STORAGE_ACCOUNT_URL`. |
| Blob container name | `hrha-evaluations` (suggested) | `[storage.azure] container` / `HRHA_STORAGE_CONTAINER`. Blob layout mirrors the local tree: `evaluations/{evaluation_id}/record.json` + artifact projections. |
| Table endpoint | `https://<storage-account>.table.core.windows.net` | `[storage.azure] table_endpoint` / `HRHA_STORAGE_TABLE_ENDPOINT`. Targets: summary rows (`RecordSummaryRow`, PartitionKey = evaluation id, RowKey = `summary`), evidence rows, idempotency records, review queue. |

## 3. Facade host

| Value | Placeholder | Notes |
|---|---|---|
| Function App name | `<function-app-name>` (sample `hrhalab-func`) | Candidate facade host (`infra/bicep/main.bicep`); HTTPS only. |
| Application Insights resource | `hrhalab-appi` (sample) | Safe-metadata telemetry only; never-log rules apply. |
| Key Vault name | `hrhalab-kv` (sample) | For secrets that managed identity cannot eliminate; none known today. |

## 4. Foundry (per the ADR-selected runtime shape)

| Value | Placeholder | Used by |
|---|---|---|
| Foundry project endpoint | `https://<foundry-resource>.services.ai.azure.com/api/projects/<project>` | All shapes; app setting `HRHA_FOUNDRY_PROJECT_ENDPOINT`. |
| Model deployment name | `<model-deployment-name>` | `foundry_project_responses` shape; `HRHA_FOUNDRY_MODEL_DEPLOYMENT`. |
| Agent IDs / ID prefix | `<agent-id-or-prefix>` | `foundry_prompt_agent` / `foundry_hosted_agent` shapes; `HRHA_FOUNDRY_AGENT_ID_PREFIX`. Per-role mapping placeholders: `config/role-agent-mapping.sample.json` (`future_agent_ref` per council role). |
| Runtime shape decision | one of `foundry_project_responses \| foundry_prompt_agent \| foundry_hosted_agent` | **The deferred ADR's human decision** — the current enumeration decides nothing. |

## 5. Identity and access

| Value | Placeholder | Notes |
|---|---|---|
| Managed identity vs client identity decision | `<decision>` | Intended path is a **user-assigned managed identity** (`hrhalab-mi` sample) with `DefaultAzureCredential`; never account keys, connection strings, or SAS tokens. A client-identity (service principal) fallback would be an explicit, recorded decision. |
| Managed identity client ID | `<managed-identity-client-id>` | App setting `HRHA_MANAGED_IDENTITY_CLIENT_ID`. |
| RBAC role assignments | Storage Blob Data Contributor + Storage Table Data Contributor (scoped to the lab storage), Key Vault Secrets User, plus the Foundry data-plane role the ADR selects | Placeholder TODOs in `infra/bicep/main.bicep`. |
| Entra group object ID — `hr` role | `<object-id-hr-group>` | Real authorization design replaces the simulated `X-Lab-Roles` headers; never committed. |
| Entra group object ID — `admin_lab` role | `<object-id-admin-lab-group>` | Same. |

## 6. App settings (from `config/azure.env.sample` / `infra/env.sample`)

```
HRHA_ENABLE_LIVE_AZURE=false          # flip to true ONLY after both human gates pass
HRHA_PROVIDER_KILL_SWITCH=false       # leave available as the emergency stop
HRHA_STORAGE_ACCOUNT_URL=             # https://<storage-account>.blob.core.windows.net
HRHA_STORAGE_CONTAINER=               # hrha-evaluations
HRHA_STORAGE_TABLE_ENDPOINT=          # https://<storage-account>.table.core.windows.net
HRHA_FOUNDRY_PROJECT_ENDPOINT=        # https://<foundry-resource>.services.ai.azure.com/api/projects/<project>
HRHA_FOUNDRY_MODEL_DEPLOYMENT=        # <model-deployment-name>
HRHA_FOUNDRY_AGENT_ID_PREFIX=         # <agent-id-or-prefix>
HRHA_MANAGED_IDENTITY_CLIENT_ID=      # <managed-identity-client-id>
```

Server-side config to flip at wiring time (`config/lab-config.toml`):
`[provider] provider_id` to the ADR-selected shape (with the matching legacy
`ai_backend_type = "foundry_agents"`), `[storage] backend = "azure_blob"`,
and the `[storage.azure]` values above.

## 7. First live smoke-test commands

Run only after the gates pass, the values are configured, and live wiring is
implemented (today both scripts fail safely by design — live checks are
intentionally unimplemented):

```bash
HRHA_ENABLE_LIVE_AZURE=true python3 scripts/smoke_storage_config.py --live
HRHA_ENABLE_LIVE_AZURE=true python3 scripts/smoke_foundry_config.py --live
```

Both scripts are double-guarded (env flag **and** `--live`), print no
secrets, and exit 2 with a clear configuration error rather than a stack
trace when anything is missing. `HRHA_PROVIDER_KILL_SWITCH=true` blocks the
Foundry check (and all Foundry providers) regardless of everything else.

## 8. Out of scope for this document

Real values, secrets, deployment commands, portal steps, and any change to
the deterministic local default. The lab remains synthetic-data-only and
advisory-only at every stage; live wiring does not change those invariants.
