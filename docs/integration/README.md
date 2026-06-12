# Integration — Current State

**No live Foundry, Entra, or Copilot Studio integration exists in this
repository.** The repo contains an Azure Functions ASGI host wrapper for the
existing FastAPI facade, and E3 adds a narrow Azure Blob storage path for
durable evaluation audit records/artifacts when the Function App explicitly
sets `HRHA_STORAGE_BACKEND=azure_blob` and
`HRHA_ENABLE_AZURE_STORAGE=true`. The repository still does not create or
manage Azure resources, perform external API calls by default, or contain
credentials or secrets. Real subscription IDs, tenant IDs, object IDs, client
IDs, endpoints, keys, and secrets must not be committed.

What exists is a deployment bridge plus planned integration seams:

| Scaffold | Where | Status |
|---|---|---|
| Azure Functions ASGI host wrapper | Root `function_app.py`, `host.json`, `.funcignore`, `requirements.txt` | Wraps the existing FastAPI app with `func.AsgiFunctionApp` and uses Function-level auth. It keeps the deterministic mock provider. The normal default remains `local_filesystem`; the wrapper overlays Azure Blob storage only from Function App settings. |
| Foundry provider scaffolds (three runtime shapes) | `src/hr_eval_lab/providers/foundry/` (`project_responses.py`, `prompt_agent.py`, `hosted_agent.py`), resolved by `provider.provider_id` via `providers/registry.py` | Non-functional by design: no Azure/Foundry SDK imports, no network code; any invocation raises `ProviderNotConfiguredError`. Resolution is additionally blocked server-side by `HRHA_PROVIDER_KILL_SWITCH=true` and by `HRHA_ENABLE_LIVE_AZURE` unset/false. No runtime shape is chosen — that is the deferred ADR's decision. |
| Legacy Foundry seam stub | `src/hr_eval_lab/providers/foundry_stub.py` | Retained for contract-shape reference but **unreachable** via `select_provider()` (the registry routes on `provider_id`); flagged for removal consideration when live wiring is undertaken. |
| Azure Blob storage backend | `src/hr_eval_lab/persistence/azure_blob_backend.py` (selected by `storage.backend = "azure_blob"` after wrapper env overlay or explicit test config) | Functional for Blob-backed evaluation records/artifacts only. No Azure SDK import on the local default path; construction fails closed without `HRHA_ENABLE_AZURE_STORAGE=true`, Blob account URL, and container. Table Storage, idempotency rows, evidence rows, and review queue durability are deferred. |
| Provider trace/eval metadata placeholders | `src/hr_eval_lab/domain/schemas/provider.py` | Nullable `trace_id`, `eval_run_id`, `agent_run_id`, `model_deployment`, `prompt_version`, `prompt_template_id`, `prompt_template_version`, `model_or_agent_ref`, `safe_error` fields (plus a `warnings` list) exist so a live backend can fill them; under the mock they are local placeholders, deterministic prompt provenance, or null. |
| Disabled-by-default smoke scripts | `scripts/smoke_foundry_config.py`, `scripts/smoke_storage_config.py` | Default paths perform no network I/O and import no Azure Storage SDK. Foundry remains double-guarded by `HRHA_ENABLE_LIVE_AZURE=true` and `--live`; storage config checks use `HRHA_ENABLE_AZURE_STORAGE=true` and `--live`. |
| Infra-as-code skeleton | `infra/` (README, placeholder Bicep, sample parameters/env) | Placeholders only; this repo does not provision resources. Manually provisioned Azure lab resources exist out-of-band, but real IDs, endpoints, keys, and secrets are not committed. Complete Table-backed Azure system-of-record behavior remains a later slice. |
| Deferred ADR draft for live Foundry wiring | `docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md` | **Draft. NOT approved.** Records the open decisions (Agent Service vs Agent Framework, backend-type enumeration, live metadata contract, region/data residency). Human approval of this ADR is a hard gate before any live wiring, resource creation, model calls, or token spend. |
| Live-eval stubs LE-001…LE-007 | `tests/live_evals/test_le_stubs.py` | Skip unconditionally with a documented deferral rationale; they assert nothing until a live backend exists. |

Seam details and the swap analysis:
[`../architecture/provider-and-storage-seams.md`](../architecture/provider-and-storage-seams.md).
Copilot Studio tool-registration readiness (documentation only):
[`copilot-studio-tool-readiness.md`](./copilot-studio-tool-readiness.md).
Concrete values needed for future live wiring (placeholders only):
[`azure-lab-wiring-tomorrow.md`](./azure-lab-wiring-tomorrow.md).

The deployed Function App smoke path remains deterministic and mock-backed.
Foundry, Entra auth, Copilot Studio registration, and complete Azure
Table-backed system-of-record behavior are still not enabled.

## Deployment and hosted smoke

Use the Azure CLI zip deployment path used by the successful E2 deployment,
not `func azure functionapp publish`:

```bash
cd "/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab"
rm -rf ".deploy/stage" ".deploy/hrha-functionapp.zip"
mkdir -p ".deploy/stage"
rsync -a ./ ".deploy/stage/" \
  --exclude ".git/" --exclude ".venv/" --exclude "venv/" \
  --exclude ".local/" --exclude "var/" --exclude ".deploy/" \
  --exclude "__pycache__/" --exclude "**/__pycache__/" --exclude "*.pyc" \
  --exclude "local.settings.json" --exclude ".env" --exclude ".env.*" \
  --exclude "logs/" --exclude "*.log" --exclude ".DS_Store" --exclude "**/.DS_Store"
(cd ".deploy/stage" && zip -qr "../hrha-functionapp.zip" .)

az functionapp deployment source config-zip \
  --resource-group rg-hrha-lab-cac \
  --name func-hrha-lab-cac001 \
  --src .deploy/hrha-functionapp.zip \
  --build-remote true
```

Derive the hosted URL dynamically because Flex Consumption may use a generated
regional hostname:

```bash
HOST="$(az resource show \
  --resource-group rg-hrha-lab-cac \
  --resource-type Microsoft.Web/sites \
  --name func-hrha-lab-cac001 \
  --query 'properties.defaultHostName' \
  -o tsv)"
APP_URL="https://$HOST"
```

The hosted smoke extraction should read `evaluation_id` from either
`post["result"]["evaluation_id"]` or top-level `post["evaluation_id"]`, and
print the available JSON keys if neither exists.
