# Implementation Notes — Azure/Foundry Readiness Pack batch (slice-e1)

> Stage 12 artifact (`current-state-reconciler`), 2026-06-11. Slice-scoped
> implementation summary and working-tree diff analysis for the readiness-pack
> coding batch layered on the completed local deterministic E1 implementation.
> Plan: [`implementation-plan-readiness-pack.md`](./implementation-plan-readiness-pack.md).
> Deviations: [`implementation-deviations.md`](./implementation-deviations.md) (DEV-R01…R07).
> Architecture check: [`architecture-check-readiness-pack.md`](./architecture-check-readiness-pack.md) (verdict: Clear).
> Evidence: [`eval-summary-readiness-pack.md`](./eval-summary-readiness-pack.md)
> — 146 passed / 7 skipped (LE deferral stubs) / 0 failed; OpenAPI drift clean;
> CLI demo verified. Everything in this batch is local/deterministic by
> default; no Azure resource, live call, or secret exists.

## 1. What the batch built (verified against the working tree)

### Storage backend boundary (modified `persistence/store.py`; new `persistence/backend.py`, `persistence/azure_blob_backend.py`)

- `StorageBackend` ABC (write/read record, write/list artifacts, write/read
  metadata row) with `LocalFilesystemBackend` as the functional default.
- New artifact layout: `evaluations/{id}/record.json` plus projections
  (`request`, `source-documents`, `evidence-packet`, `council/{role}`,
  `synthesis`, `quality-gates`, `provider-metadata`, `human-review` `.json`)
  and `metadata/evaluations.jsonl` (text-free `RecordSummaryRow` per
  evaluation). The blob-equivalent path moved from `evaluations/{id}.json`
  (DEV-R01; DT-002/DT-010 updated to the new path).
- `LocalStore` keeps its facade API, delegates to the backend, projects
  per-role transcripts at persistence time, and still writes the legacy
  JSONL table-equivalents. Idempotency deliberately stayed on the store, not
  the ABC (DEV-R04).
- `AzureBlobBackend`: fail-closed scaffold — no SDK import, construction
  requires full config + `HRHA_ENABLE_LIVE_AZURE=true`, every operation
  raises `StorageNotConfiguredError` regardless.

### Provider registry (new `providers/registry.py`, `providers/foundry/`; modified `providers/base.py`, `config.py`)

- `provider_id` closed enum: `deterministic_mock` (default, only functional)
  | `foundry_project_responses` | `foundry_prompt_agent` |
  `foundry_hosted_agent` (fail-closed scaffolds; lazy import; no SDK).
- Server-side guards: `HRHA_PROVIDER_KILL_SWITCH` blocks all Foundry IDs;
  `HRHA_ENABLE_LIVE_AZURE` unset/false blocks them too (defense in depth).
- Legacy `ai_backend_type` retained and validated consistent with
  `provider_id` (pydantic model validator). Legacy `foundry_stub.py` retained
  but unreachable via `select_provider` (DEV-R05).

### Versioned prompt registry (new `prompts/registry.py` + `templates/<role>.v1.md`, 10 roles)

- Templates are **recorded, never executed** (DEV-R06): the mock stamps
  `prompt_template_id`/`prompt_template_version` into `ProviderMetadata`.
- Mandatory safety constraints embedded verbatim in every template and
  test-pinned (RP-009); no secrets/endpoints/tenant or subscription
  identifiers/real applicant data.

### Schemas (modified `domain/schemas/provider.py`, `request.py`; new `storage.py`, `transcript.py`)

- `ProviderMetadata` += `prompt_template_id`, `prompt_template_version`,
  `model_or_agent_ref`, `warnings`, `safe_error` (nullable/deterministic
  under the mock; live semantics owned by the deferred ADR).
- New `StorageArtifactRef`, `RecordSummaryRow` (no text-bearing field by
  construction) and `CouncilRoleInvocation` (provider output contract carried
  on the persisted transcript because validation is facade-owned — DEV-R03).
- `EvaluationRequest.idempotency_key` became `Optional` in the schema
  (header equivalence — DEV-R02).

### API (modified `api/app.py`, `api/routes_evaluations.py`; regenerated `openapi/evaluations-api.json`)

- Operation IDs `submitEvaluation` / `getEvaluation`.
- `Idempotency-Key` request header: equivalent to the body field; one
  required (neither → 400); both present must match (mismatch → 400).
- `X-Correlation-Id`: documented request header on POST/GET; response
  middleware emits the envelope's server-assigned correlation id (or echoes
  the caller's value when no envelope id exists).
- OpenAPI regenerated; formally validated (openapi-spec-validator) and
  drift-checked clean.

### Scripts, infra, config

- `scripts/run_council_local.py` — facade-only local demo, safe stdout
  (ids/statuses/counts only).
- `scripts/smoke_foundry_config.py` / `smoke_storage_config.py` — disabled by
  default, double-guarded (`HRHA_ENABLE_LIVE_AZURE=true` + `--live`), safe
  failures; live checks intentionally unimplemented.
- `infra/` — placeholder-only IaC skeleton (README, Bicep, parameters, env
  sample); never deployed.
- `config/lab-config.toml` += `[provider] provider_id`, `[storage]` +
  `[storage.azure]` placeholders; new `config/azure.env.sample`,
  `config/role-agent-mapping.sample.json`.

### Tests

- New `tests/test_rp001_storage_backend.py` … `test_rp005_cli_and_smoke.py`
  (58 deterministic tests covering plan items RP-001…RP-015).
- `tests/test_dt002_determinism.py` and `tests/test_dt010_mandatory_flags.py`
  updated to the new record path only (assertion semantics unchanged).

## 2. Change categories (branch-diff analysis)

| Category | Changes |
|---|---|
| User-visible / API behavior | Idempotency-Key header equivalence (400 on mismatch/absence of any key); X-Correlation-Id response header; operation IDs. No change to envelope vocabulary or business outcomes. |
| Backend/service | Provider registry + guards; prompt provenance stamping in the mock. |
| Data/state/persistence | New artifact tree + summary rows behind the `StorageBackend` seam; record path moved (DEV-R01). |
| Security/identity | Two server-side env guards added; request surface still cannot select provider/model/etc. (test-pinned). No identity change. |
| Infra/IaC/config | Placeholder-only `infra/` skeleton; new config keys + samples. Nothing deployed. |
| Integration | None live. Scaffolds + readiness docs only. |
| Tests/evals | +58 RP tests; 2 DT tests path-updated; LE-001…007 still deferred stubs. |
| Docs | Stage-12 reconciliation updated current-state/architecture/integration docs (see §4). |

## 3. Design decisions of record

1. **Record as single source of truth** — all artifacts are projections
   emitted at persistence time; no second truth.
2. **Fail-closed scaffolds everywhere** — every Azure/Foundry-shaped module
   raises safe configuration errors; guards are server-side only.
3. **Recorded-not-executed prompts** — honest deterministic provenance
   instead of fake prompt execution (DEV-R06).
4. **Additive contract changes only** — body `idempotency_key` stays
   canonical; headers and metadata fields are additive; DT suite semantics
   unchanged.
5. **Option-neutral provider enumeration** — the three Foundry IDs keep all
   ADR options open and decide nothing (architecture check finding 4).

## 4. Stage-12 documentation reconciliation (this pass)

Durable docs updated to current state: `docs/product-current-state/README.md`,
`docs/product-current-state/candidate-evaluation-council.md`,
`docs/architecture/actual-technical-architecture.md`,
`docs/architecture/candidate-evaluation-council-architecture.md`,
`docs/architecture/provider-and-storage-seams.md` (stale claims removed:
"no prompt seam", concrete-`LocalStore`-only seam, old blob path, two-value
provider enum), `docs/integration/README.md`,
`docs/integration/copilot-studio-tool-readiness.md` (precision refinements).
Created: `docs/integration/azure-lab-wiring-tomorrow.md` (placeholder wiring
checklist, satisfying DEV-R07), this file, and
[`cloud-readiness-notes.md`](./cloud-readiness-notes.md).

## 5. Open items (references only — no issues created here)

- Deferred ADR approval + BQ-005 region approval (human gates) block the
  wiring slice.
- Follow-up candidates for Stage 14 issue drafting: remove or retire legacy
  `foundry_stub.py` (DEV-R05); record concrete `provider_id` in
  `RecordSummaryRow` at run time (today derived in `persistence/store.py`);
  retention/cleanup decisions for cloud storage.
- AC-019 (PO review), AC-020/FR-014 (CI evidence), BQ-EC-001 (latency
  thresholds ratification) remain human items per the eval contract.
