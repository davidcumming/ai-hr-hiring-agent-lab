# Cloud Readiness Notes — slice-e1 Azure/Foundry Readiness Pack

> Stage 12 artifact (`current-state-reconciler`, documentation-and-architecture-
> reconciliation-agent), 2026-06-11. Slice-scoped: slice language is allowed
> here. Classifies every readiness-pack surface as **cloud-ready (functional
> locally)**, **placeholder-only scaffold**, or **deferred (human-gated)**.
> Evidence: 146 passed / 7 skipped (LE deferral stubs) / 0 failed; OpenAPI
> drift check clean; CLI demo verified
> ([`eval-summary-readiness-pack.md`](./eval-summary-readiness-pack.md)).

## 1. Cloud-ready now (functional, local, deterministic — wiring becomes configuration)

| Surface | Why it is wiring-ready | Evidence |
|---|---|---|
| `StorageBackend` ABC + `LocalFilesystemBackend` (`persistence/backend.py`) | Formal seam; artifact layout `evaluations/{id}/record.json` + projections + `metadata/evaluations.jsonl` mirrors the intended blob/table layout name-for-name | RP-001 suite (`tests/test_rp001_storage_backend.py`); DT-002/DT-010 green on the new path |
| `RecordSummaryRow` / `StorageArtifactRef` (`domain/schemas/storage.py`) | Summary row is already Azure-Table-shaped (PartitionKey/RowKey) and text-free by schema | RP-001 suite |
| Per-role transcripts `CouncilRoleInvocation` (`domain/schemas/transcript.py`, persisted at `council/{role}.json`) | Carries the full provider output contract a live backend must fill; projection of the record, no second truth | RP-001/RP-014; CLI demo artifact listing |
| Extended `ProviderMetadata` (`prompt_template_id/version`, `model_or_agent_ref`, `warnings`, `safe_error`) | Live backend fills fields that already exist, deterministic/null under the mock | RP-008; DT-002 byte-identity retained |
| Provider registry (`providers/registry.py`) with `provider_id` enumeration + guards | Live provider lands behind an existing resolution path; guards (`HRHA_ENABLE_LIVE_AZURE`, `HRHA_PROVIDER_KILL_SWITCH`) already enforced server-side | RP-006/RP-007 (`tests/test_rp002_scaffolds_and_registry.py`) |
| Versioned prompt registry (`prompts/registry.py` + 10 `v1` templates) | Single versioned prompt source the live backend will execute; provenance already stamped into every audit record | RP-009 (`tests/test_rp003_prompt_registry.py`); RP-008 |
| API contract: `submitEvaluation`/`getEvaluation` operation IDs, `Idempotency-Key` + `X-Correlation-Id` headers | Copilot-/connector-registration-ready; no provider/model field in the request schema (test-pinned) | RP-010/RP-011 (`tests/test_rp004_openapi_and_headers.py`); drift check clean |
| `scripts/run_council_local.py` | Facade-only demo proves the full pipeline + artifact tree end-to-end with safe stdout | RP-012 (`tests/test_rp005_cli_and_smoke.py`); demo run in eval summary §3d |
| Config surfaces (`[provider] provider_id`, `[storage]`/`[storage.azure]`, `config/azure.env.sample`, `config/role-agent-mapping.sample.json`) | Wiring values have a committed, validated home; family-consistency validation prevents misconfiguration | Config validation in `config.py`; source-control capture report |

## 2. Placeholder-only scaffolds (committed, fail-closed, NON-functional)

| Surface | Fail-closed behavior |
|---|---|
| `AzureBlobBackend` (`persistence/azure_blob_backend.py`) | No SDK import, no network; `StorageNotConfiguredError` at construction without full config + `HRHA_ENABLE_LIVE_AZURE=true`, and on **every operation** even then. |
| Foundry provider scaffolds (`providers/foundry/`: `project_responses`, `prompt_agent`, `hosted_agent`) | No SDK import, no network; every `invoke_role` raises `ProviderNotConfiguredError`; registry refuses them while guards are closed. No runtime shape is chosen. |
| Legacy `providers/foundry_stub.py` | Retained but unreachable via `select_provider()` (DEV-R05); removal candidate at the wiring slice. |
| `scripts/smoke_foundry_config.py` / `smoke_storage_config.py` | Disabled by default; double-guarded (env flag + `--live`); live path fails safely (exit 2, no stack trace) — live checks intentionally unimplemented. |
| `infra/` skeleton (README, Bicep, parameters, env samples) | Documentation-grade only; never deployed, validated, or approved; placeholder values only; identity-first design (no keys/SAS/connstrings). |
| `[storage.azure]` config values, `HRHA_*` Azure/Foundry settings | Empty placeholders; populating them alone changes nothing (scaffolds still raise). |

## 3. Deferred — blocked on human gates

| Item | Gate |
|---|---|
| Live Foundry runtime shape choice + final provider-ID enumeration + live trace/eval metadata semantics | **Deferred ADR approval** ([`adr-deferred-foundry-wiring.md`](./adr-deferred-foundry-wiring.md) — draft, NOT approved). |
| Region/data-residency (any Canadian-region adoption, any deployment) | **BQ-005 human approval**. |
| Any Azure resource creation, any live call, any token spend | Both gates above, plus a scoped wiring slice with its own gates. |
| Live evals LE-001…LE-007 | Carried forward unweakened; gate the wiring slice (eval contract §7); stubs skip today. |
| Real identity (Entra groups for `hr`/`admin_lab`), Copilot Studio registration, hosted endpoint | Wiring-slice scope; simulated headers and local-only hosting today. |
| Concrete wiring values | Placeholder checklist: [`../../../integration/azure-lab-wiring-tomorrow.md`](../../../integration/azure-lab-wiring-tomorrow.md). |

## 4. Known wiring-slice work items (not gaps in this batch)

- Implement `AzureBlobBackend` operations and the live provider behind one
  scaffold; map JSONL table-equivalents (incl. idempotency, per DEV-R04) to
  Azure Tables.
- Record the concrete `provider_id` in `RecordSummaryRow` at run time
  (today derived: `deterministic_mock` vs `foundry_unresolved` in
  `persistence/store.py`).
- Decide retention/concurrency/cleanup for cloud storage (no behavior exists
  today).
- Reconsider/remove the legacy `foundry_stub.py` (DEV-R05).
