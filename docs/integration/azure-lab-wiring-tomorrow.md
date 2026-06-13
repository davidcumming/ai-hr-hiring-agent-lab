# Azure Lab Wiring — Exact Values Needed (Placeholders Only)

Checklist of every concrete value that future live Azure/Foundry wiring
needs, so that wiring day is a configuration exercise. **This document contains
placeholders only — no real subscription, tenant, endpoint, object ID, agent
ID, or secret values exist anywhere in this repository, and none may be
committed.** Real values arrive through an approved channel at wiring time.

## 0. Human gates that must pass FIRST

No Foundry value below may be acted on — no Foundry setting flipped to live
mode and no Foundry/model call attempted — until **both** of these human gates
pass. Slice E3's Azure Blob storage path is the narrow exception for
already-created lab resources: it is storage-only, deterministic/mock-backed,
and still requires explicit app settings plus identity-based auth.

1. **Foundry-wiring ADR approval** —
   [`../delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`](../delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md)
   is a **draft, NOT approved**. It owns the live runtime-shape decision
   (project Responses API vs prompt agent vs hosted agent), the final
   provider-ID enumeration, and the live trace/eval metadata contract.
2. **BQ-005 region/data-residency approval** — Canadian-region adoption
   (e.g. Canada Central) requires explicit human approval; never adopt a
   region silently.

Additional standing gates: any merge, any GitHub Issue creation, any Azure
resource creation, and residual-risk acceptance are human decisions. The
deterministic ASGI wrapper may be published to the already-created Function
App while `HRHA_ENABLE_LIVE_AZURE=false` and `HRHA_PROVIDER_KILL_SWITCH=true`;
Blob storage is enabled separately by `HRHA_ENABLE_AZURE_STORAGE=true`.

## 1. Azure subscription and resource group

| Value | Placeholder | Notes |
|---|---|---|
| Subscription ID | `<azure-subscription-id>` | Never committed. |
| Entra tenant ID | `<entra-tenant-id>` | Never committed; Bicep resolves `subscription().tenantId` at deploy time. |
| Resource group | `rg-hrha-lab-cac` (suggested default) | Created out-of-band; see `infra/parameters.sample.json`. |
| Region | `<approved-canadian-region>` (e.g. `canadacentral`) | Only after BQ-005 approval (`infra/bicep/main.bicep` `location` param). |
| Resource name prefix | `hrhalab` (sample default) | `infra/bicep/main.bicep` `namePrefix` param. |

## 2. Storage (records + artifact tree now; metadata tables later)

| Value | Placeholder | Maps to |
|---|---|---|
| Storage account name | `<storage-account>` (3–24 lowercase alphanumerics; sample `hrhalabstor`) | `infra/bicep/main.bicep`; shared-key access disabled (`allowSharedKeyAccess: false`). |
| Blob account URL | `https://<storage-account>.blob.core.windows.net` | `config/lab-config.toml` `[storage.azure] account_url` / app setting `HRHA_STORAGE_ACCOUNT_URL`. |
| Blob container name | `hrha-evaluations` (suggested) | `[storage.azure] container` / `HRHA_STORAGE_CONTAINER`. Blob layout mirrors the local tree: `evaluations/{evaluation_id}/record.json` + artifact projections. |
| Table endpoint | `https://<storage-account>.table.core.windows.net` | Optional/future live adapter target. E7 defines local Table-shaped workflow contracts for `RecruitmentCases`, gates, notifications, source documents, packages, model assessments, human reviews, and final evaluations; no Azure Table SDK path uses this endpoint yet. |
| Queue endpoint | `https://<storage-account>.queue.core.windows.net` | Future live async target. E7 defines local Queue message contracts for `run-model-candidate-assessment`, `run-model-assessment-batch`, and `write-notification`; no Azure Queue SDK path or worker exists yet. |

## 3. Facade host

| Value | Placeholder | Notes |
|---|---|---|
| Function App name | `func-hrha-lab-cac001` (already created out-of-band for this lab) | Facade host target for the ASGI wrapper smoke test. This repo can publish code to it, but does not create or manage the resource. |
| Application Insights resource | `hrhalab-appi` (sample) | Safe-metadata telemetry only; never-log rules apply. |
| Key Vault name | `hrhalab-kv` (sample) | For secrets that managed identity cannot eliminate; none known today. |

The bridge host is root `function_app.py`, which wraps the existing FastAPI
facade with Azure Functions. The hosted path remains deterministic/mock-backed.
By default it can still use temporary local-filesystem persistence via
`HRHA_PERSISTENCE_ROOT` or the process temp directory. When the Function App
has `HRHA_STORAGE_BACKEND=azure_blob` and `HRHA_ENABLE_AZURE_STORAGE=true`,
the wrapper overlays Azure Blob persistence for the evaluation audit record
and artifact projections. Complete Table-backed system-of-record behavior is
a later slice. E7 adds local deterministic Table/Blob/Queue-shaped workflow
contracts and adapters only; the Function wrapper does not select them and no
portal or cloud configuration is required for them.

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
HRHA_ENABLE_LIVE_AZURE=false          # Foundry/model live switch; leave false for E3 Blob storage
HRHA_PROVIDER_KILL_SWITCH=true        # keep the emergency stop on for deterministic hosted smoke
HRHA_PERSISTENCE_ROOT=                # optional temp/writable path for hosted local_filesystem smoke state
HRHA_STORAGE_BACKEND=azure_blob       # Function wrapper overlay only; local TOML default remains local_filesystem
HRHA_ENABLE_AZURE_STORAGE=true        # narrow storage gate; does not enable Foundry/model calls
HRHA_STORAGE_ACCOUNT_URL=             # https://<storage-account>.blob.core.windows.net
HRHA_STORAGE_CONTAINER=               # hrha-evaluations
HRHA_STORAGE_TABLE_ENDPOINT=          # future live Table adapter target
HRHA_FOUNDRY_PROJECT_ENDPOINT=        # https://<foundry-resource>.services.ai.azure.com/api/projects/<project>
HRHA_FOUNDRY_MODEL_DEPLOYMENT=        # <model-deployment-name>
HRHA_FOUNDRY_AGENT_ID_PREFIX=         # <agent-id-or-prefix>
HRHA_MANAGED_IDENTITY_CLIENT_ID=      # <managed-identity-client-id>
```

Do not flip `config/lab-config.toml` for the deployed E3 storage path. The
normal local FastAPI app reads the committed local defaults. The Azure
Functions wrapper applies the storage app-setting overlay only in
`function_app.py`. Foundry wiring later would require the ADR-selected
provider shape plus the matching legacy `ai_backend_type = "foundry_agents"`.

## 7. First live smoke-test commands

Storage config-only smoke for E3:

```bash
HRHA_STORAGE_BACKEND=azure_blob \
HRHA_ENABLE_AZURE_STORAGE=true \
HRHA_STORAGE_ACCOUNT_URL=https://<storage-account>.blob.core.windows.net \
HRHA_STORAGE_CONTAINER=hrha-evaluations \
python3 scripts/smoke_storage_config.py --live
```

Hosted connectivity is validated by POST then GET against the Function App,
deriving the hostname dynamically from Azure:

```bash
HOST="$(az resource show \
  --resource-group rg-hrha-lab-cac \
  --resource-type Microsoft.Web/sites \
  --name func-hrha-lab-cac001 \
  --query 'properties.defaultHostName' \
  -o tsv)"

APP_URL="https://$HOST"
```

Foundry smoke remains separately gated and disabled by default:

```bash
python3 scripts/smoke_foundry_config.py
```

Only run `HRHA_ENABLE_LIVE_AZURE=true python3 scripts/smoke_foundry_config.py --live`
after the Foundry ADR and region/data-residency gates pass. Both smoke
scripts print no secrets and exit 2 with a clear configuration error rather
than a stack trace when required values are missing. `HRHA_PROVIDER_KILL_SWITCH=true`
blocks the Foundry check and all Foundry providers regardless of everything
else.

## 8. Out of scope for this document

Real subscription IDs, tenant IDs, object IDs, client IDs, endpoints, keys,
secrets, portal steps, and any change to the deterministic local default. The
lab remains synthetic-data-only and advisory-only at every stage; live wiring
does not change those invariants. Foundry, live model calls, Entra auth,
Copilot Studio registration, Azure Queue workers, and complete live
Table-backed Azure Storage system-of-record behavior remain later slices.
Slice E3 only makes Blob evaluation records/artifacts durable enough for POST
then GET; E7 only adds source-controlled workflow storage contracts and a
local deterministic adapter.
