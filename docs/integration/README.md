# Integration — Current State

**No live integration of any kind exists in this repository.** There are no
Azure resources, no Azure AI Foundry connection, no Copilot Studio surface,
no Entra identity integration, no external API calls, and no credentials or
secrets. The application runs entirely locally against a deterministic mock
AI backend and local filesystem persistence.

What does exist is **planned integration seams only** — in-code scaffolding
that pins contract shapes without performing any integration:

| Scaffold | Where | Status |
|---|---|---|
| Foundry provider scaffolds (three runtime shapes) | `src/hr_eval_lab/providers/foundry/` (`project_responses.py`, `prompt_agent.py`, `hosted_agent.py`), resolved by `provider.provider_id` via `providers/registry.py` | Non-functional by design: no Azure/Foundry SDK imports, no network code; any invocation raises `ProviderNotConfiguredError`. Resolution is additionally blocked server-side by `HRHA_PROVIDER_KILL_SWITCH=true` and by `HRHA_ENABLE_LIVE_AZURE` unset/false. No runtime shape is chosen — that is the deferred ADR's decision. |
| Legacy Foundry seam stub | `src/hr_eval_lab/providers/foundry_stub.py` | Retained for contract-shape reference but **unreachable** via `select_provider()` (the registry routes on `provider_id`); flagged for removal consideration when live wiring is undertaken. |
| Azure Blob storage backend scaffold | `src/hr_eval_lab/persistence/azure_blob_backend.py` (selected by `storage.backend = "azure_blob"`) | Fail-closed: no Azure SDK import, no network; construction and every operation raise `StorageNotConfiguredError` (live storage wiring deferred and human-gated). |
| Provider trace/eval metadata placeholders | `src/hr_eval_lab/domain/schemas/provider.py` | Nullable `trace_id`, `eval_run_id`, `agent_run_id`, `model_deployment`, `prompt_version`, `prompt_template_id`, `prompt_template_version`, `model_or_agent_ref`, `safe_error` fields (plus a `warnings` list) exist so a live backend can fill them; under the mock they are local placeholders, deterministic prompt provenance, or null. |
| Disabled-by-default smoke scripts | `scripts/smoke_foundry_config.py`, `scripts/smoke_storage_config.py` | Double-guarded (`HRHA_ENABLE_LIVE_AZURE=true` **and** `--live`); the default path performs no network I/O and imports no SDK; the live path fails safely — live checks are not implemented. |
| Infra-as-code skeleton | `infra/` (README, placeholder Bicep, sample parameters/env) | Placeholders only; nothing deployed, validated, or approved. Deployment is gated on the deferred ADR + BQ-005 region approval. |
| Deferred ADR draft for live Foundry wiring | `docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md` | **Draft. NOT approved.** Records the open decisions (Agent Service vs Agent Framework, backend-type enumeration, live metadata contract, region/data residency). Human approval of this ADR is a hard gate before any live wiring, resource creation, model calls, or token spend. |
| Live-eval stubs LE-001…LE-007 | `tests/live_evals/test_le_stubs.py` | Skip unconditionally with a documented deferral rationale; they assert nothing until a live backend exists. |

Seam details and the swap analysis:
[`../architecture/provider-and-storage-seams.md`](../architecture/provider-and-storage-seams.md).
Copilot Studio tool-registration readiness (documentation only):
[`copilot-studio-tool-readiness.md`](./copilot-studio-tool-readiness.md).
Concrete values needed for future live wiring (placeholders only):
[`azure-lab-wiring-tomorrow.md`](./azure-lab-wiring-tomorrow.md).

This document must be updated when (and only when) a real integration lands.
