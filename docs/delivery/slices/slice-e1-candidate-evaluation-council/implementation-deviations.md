# Implementation Deviations — Azure/Foundry Readiness Pack batch

> Stage 9 artifact (`implementation-deviation-capture`, coding-agent role), 2026-06-11.
> Baseline deviation log for the first E1 batch: [`deviation-log.md`](./deviation-log.md)
> (DEV-001..DEV-006, unchanged). This file records deviations of the readiness-pack
> batch relative to the slice spec and the readiness-pack plan. The spec is not amended.

| ID | Classification | Severity | What changed vs. intent | Rationale / impact |
|---|---|---|---|---|
| DEV-R01 | `approach-substituted` | Low | Spec/current-state docs recorded the blob-equivalent path as `evaluations/{id}.json`; the readiness pack moves it to `evaluations/{id}/record.json` plus per-artifact projections. Tests DT-002/DT-010 updated to the new path (assertion semantics unchanged: canonical JSON, flag invariants). | Required by the readiness-pack artifact layout (mirrors the future blob layout). Stage 12 must update current-state/architecture docs. Not a behaviour change at the API. |
| DEV-R02 | `interpretation-applied` | Low | The readiness instruction asks for an "idempotency key header for POST". Implemented as **additive**: `Idempotency-Key` header accepted; body field `idempotency_key` retained as canonical and now optional in the schema; both present must match (HTTP 400 otherwise); neither present → HTTP 400. | Avoids breaking the adopted body contract (DT-008) while satisfying the header requirement. Documented in OpenAPI; pinned by RP-011. |
| DEV-R03 | `interpretation-applied` | Low | Provider output contract fields `role`, `input_artifact_refs`, `output_json`, `validation_status` are carried on the persisted `CouncilRoleInvocation` transcript rather than on `ProviderResult`, because output validation is facade-owned (architecture constraint: agents/providers never self-certify validation). `ProviderMetadata` carries the remaining fields (`prompt_template_id/version`, `model_or_agent_ref`, `warnings`, `safe_error`, trace/token/latency). | Keeps the facade-owns-enforcement rule intact; full contract is persisted per role. Pinned by RP-008/RP-014. |
| DEV-R04 | `scope-reduced` (explicit) | Low | "Idempotency lookup/store" on the new `StorageBackend` ABC was not added; idempotency remains a thin layer over `LocalStore`'s existing table-equivalents (the established API pattern). | The task allowed it "if already part of the API pattern" — it is part of the store pattern, not the backend boundary; replicating it on the ABC would create a second source of truth. Wiring slice maps the idempotency table to Azure Table directly. |
| DEV-R05 | `approach-substituted` | Low | The legacy `foundry_stub.py` (`FoundryAgentProvider`) is retained but no longer reachable via `select_provider` (the registry routes `provider_id`; the legacy `ai_backend_type` is a validated-consistent family value). | Kept to avoid contract churn for any external reference; flagged for removal consideration at the wiring slice. |
| DEV-R06 | `interpretation-applied` | Low | "Versioned prompt registry" implemented as source-controlled templates **recorded, not executed**: the deterministic mock derives outputs from the evidence packet and stamps template id/version into provider metadata. | The mock executing prompt text would fake model behaviour; recording provenance is the honest deterministic equivalent. Stated in registry/docs; pinned by RP-008/RP-009. |
| DEV-R07 | `requirement-deferred` | Low | `docs/integration/azure-lab-wiring-tomorrow.md` (listed in the Stage 12 doc set) is produced at Stage 12 by the reconciliation agent, not during coding. | Sequencing only; no content gap. |

## Stage-13 fix-loop addendum (2026-06-11)

| ID | Classification | Severity | What changed |
|---|---|---|---|
| DEV-R08 | `implementation-defect-fixed` (Stage 13 BM-001 fix loop) | Low | The Stage-13 validator found that `create_app` never consulted `[storage] backend` (the documented app-level fail-closed behaviour for `azure_blob` did not occur). Fixed in code: `create_app` now resolves the backend via `select_backend(config)`, so selecting `azure_blob` without complete config (or without live Azure enabled) raises `StorageNotConfiguredError` at app construction. New pinning test `test_rp005_app_factory_fails_closed_when_azure_blob_selected` (suite: 147 passed / 7 skipped / 0 failed after fix). BM-002 and NB-001..NB-004 were documentation wording fixes only. |

No high-severity deviations; no compliance flags (privacy/residency/audit posture
unchanged: local-only, synthetic-only, advisory-only, never-log preserved and
extended to the new artifact and metadata surfaces). No spec requirement was
removed. Current-state doc sections requiring update are listed for Stage 12:
storage seam description ("no prompt seam", concrete-LocalStore wording, blob
path), provider seam enumeration, new config surfaces, scripts, infra skeleton.
