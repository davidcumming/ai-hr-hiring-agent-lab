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
| Foundry Agents provider seam stub | `src/hr_eval_lab/providers/foundry_stub.py` (selected by `provider.ai_backend_type = "foundry_agents"`) | Non-functional by design: no Azure SDK imports, no network code; any invocation raises `ProviderNotConfiguredError`. Pins the `CouncilProvider` contract shape against the same schemas as the active mock. |
| Provider trace/eval metadata placeholders | `src/hr_eval_lab/domain/schemas/provider.py` | Nullable `trace_id`, `eval_run_id`, `agent_run_id`, `model_deployment`, `prompt_version` fields exist so a live backend can fill them; under the mock they are local placeholders or null. |
| Deferred ADR draft for live Foundry wiring | `docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md` | **Draft. NOT approved.** Records the open decisions (Agent Service vs Agent Framework, backend-type enumeration, live metadata contract, region/data residency). Human approval of this ADR is a hard gate before any live wiring, resource creation, model calls, or token spend. |
| Live-eval stubs LE-001…LE-007 | `tests/live_evals/test_le_stubs.py` | Skip unconditionally with a documented deferral rationale; they assert nothing until a live backend exists. |

Seam details and the swap analysis:
[`../architecture/provider-and-storage-seams.md`](../architecture/provider-and-storage-seams.md).

This document must be updated when (and only when) a real integration lands.
