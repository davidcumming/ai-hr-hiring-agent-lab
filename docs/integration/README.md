# Integration — Current State

**No live Foundry, Entra, Copilot Studio, or Azure storage integration exists
in this repository.** The repo now contains an Azure Functions ASGI host
wrapper for the existing FastAPI facade, so the same deterministic API can be
published to the already-created lab Function App for a first hosted smoke
test. The repository still does not create or manage Azure resources, perform
external API calls by default, or contain credentials or secrets. Real
subscription IDs, tenant IDs, object IDs, client IDs, endpoints, keys, and
secrets must not be committed.

What exists is a deployment bridge plus planned integration seams:

| Scaffold | Where | Status |
|---|---|---|
| Azure Functions ASGI host wrapper | Root `function_app.py`, `host.json`, `.funcignore`, `requirements.txt` | Deployment bridge only. Wraps the existing FastAPI app with `func.AsgiFunctionApp` and uses Function-level auth. It keeps the deterministic mock provider and `local_filesystem` backend. Hosted local-filesystem persistence is redirected to `HRHA_PERSISTENCE_ROOT` or a temp directory and is temporary/ephemeral for this bridge slice. |
| Foundry provider scaffolds (three runtime shapes) | `src/hr_eval_lab/providers/foundry/` (`project_responses.py`, `prompt_agent.py`, `hosted_agent.py`), resolved by `provider.provider_id` via `providers/registry.py` | Non-functional by design: no Azure/Foundry SDK imports, no network code; any invocation raises `ProviderNotConfiguredError`. Resolution is additionally blocked server-side by `HRHA_PROVIDER_KILL_SWITCH=true` and by `HRHA_ENABLE_LIVE_AZURE` unset/false. No runtime shape is chosen — that is the deferred ADR's decision. |
| Legacy Foundry seam stub | `src/hr_eval_lab/providers/foundry_stub.py` | Retained for contract-shape reference but **unreachable** via `select_provider()` (the registry routes on `provider_id`); flagged for removal consideration when live wiring is undertaken. |
| Azure Blob storage backend scaffold | `src/hr_eval_lab/persistence/azure_blob_backend.py` (selected by `storage.backend = "azure_blob"`) | Fail-closed: no Azure SDK import, no network; construction and every operation raise `StorageNotConfiguredError` (live storage wiring deferred and human-gated). |
| Provider trace/eval metadata placeholders | `src/hr_eval_lab/domain/schemas/provider.py` | Nullable `trace_id`, `eval_run_id`, `agent_run_id`, `model_deployment`, `prompt_version`, `prompt_template_id`, `prompt_template_version`, `model_or_agent_ref`, `safe_error` fields (plus a `warnings` list) exist so a live backend can fill them; under the mock they are local placeholders, deterministic prompt provenance, or null. |
| Disabled-by-default smoke scripts | `scripts/smoke_foundry_config.py`, `scripts/smoke_storage_config.py` | Double-guarded (`HRHA_ENABLE_LIVE_AZURE=true` **and** `--live`); the default path performs no network I/O and imports no SDK; the live path fails safely — live checks are not implemented. |
| Infra-as-code skeleton | `infra/` (README, placeholder Bicep, sample parameters/env) | Placeholders only; this repo does not provision resources. Manually provisioned Azure lab resources exist out-of-band, but real IDs, endpoints, keys, and secrets are not committed. Durable Azure Blob/Table persistence remains a later slice. |
| Deferred ADR draft for live Foundry wiring | `docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md` | **Draft. NOT approved.** Records the open decisions (Agent Service vs Agent Framework, backend-type enumeration, live metadata contract, region/data residency). Human approval of this ADR is a hard gate before any live wiring, resource creation, model calls, or token spend. |
| Live-eval stubs LE-001…LE-007 | `tests/live_evals/test_le_stubs.py` | Skip unconditionally with a documented deferral rationale; they assert nothing until a live backend exists. |

Seam details and the swap analysis:
[`../architecture/provider-and-storage-seams.md`](../architecture/provider-and-storage-seams.md).
Copilot Studio tool-registration readiness (documentation only):
[`copilot-studio-tool-readiness.md`](./copilot-studio-tool-readiness.md).
Concrete values needed for future live wiring (placeholders only):
[`azure-lab-wiring-tomorrow.md`](./azure-lab-wiring-tomorrow.md).

The first deployed Function App smoke test remains deterministic and
mock-backed. Foundry, Entra auth, Copilot Studio registration, and live Azure
storage are still not enabled.
