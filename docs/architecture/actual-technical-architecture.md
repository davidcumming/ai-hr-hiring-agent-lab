# Actual Technical Architecture

This document describes **only what is physically built** in this repository
(Process Doc §9.2). Aspirational or planned components appear solely in the
"Not built" section, clearly labeled. Behavior details live in
[`../product-current-state/candidate-evaluation-council.md`](../product-current-state/candidate-evaluation-council.md).

## 1. System shape

A single local Python application: a FastAPI **facade** that owns the entire
deterministic business contract (identity, authorization, validation,
idempotency, source integrity, gates, schema validation of role outputs,
persistence, response envelope), driving a **council orchestrator** whose
model-backed roles execute only through a **provider seam**, persisting
through a **storage backend seam** to the local filesystem. There is no
deployed infrastructure of any kind; every Azure/Foundry-shaped component is
a fail-closed, non-functional scaffold.

```
CLI (httpx)        any HTTP client
      \               /
       v             v
  FastAPI facade (api/app.py, api/routes_evaluations.py)
   ├─ auth (api/auth.py — simulated header identity)
   ├─ envelope/errors (api/envelope.py, api/errors.py)
   ├─ X-Correlation-Id response middleware (api/app.py)
   ├─ idempotency (persistence/idempotency.py; body field or
   │              Idempotency-Key header)
   ├─ fixture/source integrity (sources/fixture_store.py)
   └─ council orchestrator (council/orchestrator.py)
        ├─ code roles (council/code_roles.py)
        ├─ composition / mode tables (council/composition.py)
        ├─ evidence packet builder (evidence/packet_builder.py)
        ├─ rigor resolver + triggers (rigor/)
        ├─ escalation policy (escalation/policy.py)
        ├─ quality gates (gates/quality_gates.py)
        └─ provider seam (providers/base.py → providers/registry.py)
             ├─ DeterministicMockProvider (providers/mock.py)   [active]
             ├─ Foundry scaffolds (providers/foundry/:
             │    project_responses, prompt_agent, hosted_agent)
             │    [non-functional; raise ProviderNotConfiguredError;
             │     blocked by env guards]
             └─ legacy FoundryAgentProvider stub
                  (providers/foundry_stub.py) [unreachable via select_provider]
   prompt registry (prompts/registry.py + prompts/templates/*.v1.md)
       [recorded into provider metadata; never executed]
   persistence: LocalStore (persistence/store.py)
       └─ StorageBackend seam (persistence/backend.py)
            ├─ LocalFilesystemBackend → var/lab-data/        [active]
            └─ AzureBlobBackend (persistence/azure_blob_backend.py)
                 [non-functional scaffold; fails closed]
   review queue row builder (review_queue.py)
   logging + never-log redaction (logging_setup.py)
   domain schemas (domain/schemas/: request, council, evaluation,
                   provider, audit, storage, transcript; domain/ids.py)
```

## 2. Module map (`src/hr_eval_lab/`)

| Package / module | Responsibility |
|---|---|
| `api/` | App factory, routes (POST/GET `/api/evaluations`, operation IDs `submitEvaluation`/`getEvaluation`), simulated auth, envelope, HTTP/error mapping, `Idempotency-Key` header handling, `X-Correlation-Id` request/response header. |
| `cli.py` | Thin HTTP client (stdlib + httpx only — no application imports). |
| `config.py` | Typed, validated view of `config/lab-config.toml` (pydantic, `extra="forbid"`); provider-ID/backend-family consistency validation; storage backend selection; the `HRHA_ENABLE_LIVE_AZURE` / `HRHA_PROVIDER_KILL_SWITCH` env-guard readers; `tomllib` with `tomli` fallback on Python 3.10. |
| `council/` | 11-role registry and Mode A/B/C tables, synchronous orchestrator, deterministic code roles. |
| `domain/` | Run-identity generation (`ids.py`) and all pydantic schema sources: request, per-role council outputs, advisory result, provider contract, audit record + table-row shapes, storage boundary (`storage.py`: `StorageArtifactRef`, `RecordSummaryRow`), per-role transcript (`transcript.py`: `CouncilRoleInvocation`). |
| `escalation/` | Escalation decision with recorded provenance (`none \| configured_escalated \| policy_triggered`). |
| `evidence/` | Evidence packet builder (stable segment addressing, rubric view, canonical serialization). |
| `gates/` | The six deterministic quality gates. |
| `logging_setup.py` | Central logger + defense-in-depth never-log redaction filter. |
| `persistence/` | `StorageBackend` ABC + `LocalFilesystemBackend` (active) + `AzureBlobBackend` fail-closed scaffold (`backend.py`, `azure_blob_backend.py`); `LocalStore` facade over the backend plus JSONL table-equivalents; idempotency records. |
| `prompts/` | Versioned prompt registry: `registry.py` + `templates/<role_id>.v1.md` for 10 roles; mandatory safety constraints test-pinned; templates are recorded into provider metadata, never executed. |
| `providers/` | `CouncilProvider` seam, provider registry (`registry.py` — lazy resolution + server-side guards), deterministic mock (active), three Foundry scaffolds under `foundry/` (non-functional), legacy `foundry_stub.py` (retained, unreachable via `select_provider`). |
| `review_queue.py` | Review-queue row construction (metadata-only). |
| `rigor/` | Pure-function rigor resolver; the six escalation-trigger computations. |
| `sources/` | Fixture resolution with per-run sha256 verification; inline-source wrapper. |

## 3. Layering and data flow

1. **Facade layer** (`api/`) — the only entry point. Enforces order: auth →
   body validation (including idempotency-key presence/consistency across
   body field and `Idempotency-Key` header) → semantic validation →
   idempotency → source integrity → orchestration → persistence → envelope.
   A response middleware sets `X-Correlation-Id` from the envelope's
   server-assigned correlation id (or echoes a caller-supplied header when no
   envelope id exists). The CLI is strictly a client of this layer (verified
   by an import-graph test, DT-018).
2. **Council layer** (`council/`, `rigor/`, `escalation/`, `gates/`,
   `evidence/`) — deterministic pipeline; model-backed roles call only the
   provider seam; every output is schema-validated immediately with one
   bounded corrective retry; every execution is recorded with a sequence
   index (packet completion provably precedes the first provider call).
3. **Provider layer** (`providers/`) — `select_provider()` delegates to the
   registry's `resolve_provider()`, which resolves `provider.provider_id`
   lazily; the default path imports only the deterministic mock. Foundry IDs
   are blocked by `HRHA_PROVIDER_KILL_SWITCH=true` and by
   `HRHA_ENABLE_LIVE_AZURE` unset/false; even past the guards, only
   fail-closed scaffolds exist.
4. **Persistence layer** (`persistence/`) — `LocalStore` delegates record and
   artifact I/O to the `StorageBackend` seam and writes the append-only JSONL
   table-equivalents; the full record and its artifact projections are the
   only text-bearing artifacts; table and summary rows are metadata-first by
   schema construction.

## 4. Contracts and versioning

- **OpenAPI**: `openapi/evaluations-api.json`, generated from the app factory
  by `scripts/export_openapi.py`; `--check` exits non-zero on drift
  (verified clean 2026-06-11; also a CI step and a test). Stable operation
  IDs `submitEvaluation` / `getEvaluation`; documented request headers
  `Idempotency-Key` (POST) and `X-Correlation-Id` (POST/GET); the request
  schema exposes no provider/model/deployment/endpoint/agent field
  (test-pinned).
- **Provider contract**: single schema source for all backends
  (`domain/schemas/provider.py`): `PROVIDER_CONTRACT_VERSION = "1.0"`,
  `ORCHESTRATION_VERSION = "council-composition-v1"`; nullable
  `trace_id`/`eval_run_id` placeholders plus nullable `prompt_template_id`,
  `prompt_template_version`, `model_or_agent_ref`, `safe_error`, and a
  `warnings` list. No mock-only schema fork (DT-013).
- **Audit record**: `RECORD_SCHEMA_VERSION = "1.0"`
  (`domain/schemas/audit.py`); canonical-JSON serialization underpins the
  determinism baseline (DT-002).
- **Storage boundary**: `StorageArtifactRef` and `RecordSummaryRow`
  (`domain/schemas/storage.py`); per-role transcript `CouncilRoleInvocation`
  (`domain/schemas/transcript.py`) — a projection of the audit record, never
  a second source of truth.

## 5. Persistence design (local, storage-shape-mirrored)

`LocalStore` (over `LocalFilesystemBackend`) writes under the configured root
(default `var/lab-data/`, gitignored):

- `evaluations/{evaluation_id}/record.json` — the full audit record
  (`EvaluationRecord`, `domain/schemas/audit.py`) in canonical JSON (sorted
  keys, fixed separators, UTF-8). The record and its projections below are
  the only artifacts allowed to carry document/model text.
- Per-evaluation artifact projections beside the record, emitted from the
  record at persistence time: `request.json`, `source-documents.json`,
  `evidence-packet.json`, `council/{role}.json` (one `CouncilRoleInvocation`
  transcript per role execution), `synthesis.json`, `quality-gates.json`,
  `provider-metadata.json`, `human-review.json`.
- `metadata/evaluations.jsonl` — one `RecordSummaryRow` per evaluation:
  identifiers, enums, counts, hashes, and timestamps only; the schema has no
  text-bearing field. The row mirrors an Azure Table shape
  (`PartitionKey` = evaluation id, `RowKey` = `"summary"`).
- **Table-equivalent JSONL** under `tables/`: `EvaluationEvidence.jsonl`
  (PartitionKey = evaluation id, RowKey = zero-padded sequence index; no
  text-bearing fields by schema), `IdempotencyRecords.jsonl`
  (PartitionKey = idempotency key; fingerprint = sha256 of canonical request
  JSON), `ReviewQueue.jsonl` (one mandatory entry per evaluation).

The layout intentionally mirrors a blob + table-storage design so that a
future swap targets configuration rather than restructuring. The
`AzureBlobBackend` scaffold documents that mapping but performs no I/O: it
fails closed (`StorageNotConfiguredError`) at construction unless fully
configured **and** `HRHA_ENABLE_LIVE_AZURE=true`, and every operation raises
even then. **No Azure storage binding of any kind exists**; the active path
is plain local filesystem I/O.

## 6. Configuration and guards

- `config/lab-config.toml` — the only runtime configuration file:
  `[rigor]`, `[escalation]`, `[provider]` (`provider_id` +
  validated-consistent legacy `ai_backend_type`), `[persistence]`,
  `[storage]` (`backend = "local_filesystem"` default) and `[storage.azure]`
  (empty placeholders; no secrets).
- Server-side environment guards (read at resolution time, never stored in
  records): `HRHA_ENABLE_LIVE_AZURE` (default false — every live path
  disabled) and `HRHA_PROVIDER_KILL_SWITCH` (`true` blocks all Foundry
  providers).
- Source-controlled samples, placeholders only: `config/azure.env.sample`,
  `config/role-agent-mapping.sample.json`.

## 7. Scripts

| Script | Role |
|---|---|
| `scripts/export_openapi.py` | OpenAPI generation + drift check (CI step). |
| `scripts/vendor_fixtures.py` | Dev-time fixture vendoring/hash refresh. |
| `scripts/run_council_local.py` | Local deterministic council demo: one synthetic candidate strictly through the in-process HTTP facade; writes the artifact tree; prints a safe summary only (ids, statuses, counts — never document or prompt text). |
| `scripts/smoke_foundry_config.py` | Disabled-by-default config smoke scaffold; double-guarded (`HRHA_ENABLE_LIVE_AZURE=true` **and** `--live`); no SDK import and no network in the default path; fails safely (exit 2, clear config error) if the live path is requested — live checks are not implemented. |
| `scripts/smoke_storage_config.py` | Same double-guarded pattern; the default path additionally sanity-checks the local filesystem backend in a temp dir. |

## 8. Infrastructure-as-code skeleton (placeholders only — nothing deployed)

`infra/` contains a documentation-grade IaC skeleton: `README.md`,
`bicep/main.bicep`, `parameters.sample.json`, `env.sample`. Placeholder
values only (`<...>` / `TODO-...`); no real tenant/subscription IDs,
endpoints, object IDs, or secrets; identity-based access (managed identity +
RBAC) is the documented pattern — never keys, connection strings, or SAS
tokens. **Nothing in `infra/` has been deployed, validated against a
subscription, or approved**; deployment is gated on the human-approved
Foundry-wiring ADR and the BQ-005 region approval.

## 9. CI

`.github/workflows/ci.yml`: on PR and push to `main` — checkout, Python 3.10,
editable install with dev extras, `pytest -q`, OpenAPI drift check. No cloud
credentials, no deployment, no infrastructure provisioning.

## 10. Runtime requirements

Python ≥ 3.10 (`pyproject.toml`; CI pins 3.10 and the code avoids 3.11+-only
stdlib — `tomli` fallback in `config.py`), FastAPI, uvicorn, pydantic v2;
dev extras: pytest, httpx, openapi-spec-validator.

## 11. What is NOT built

None of the following exists in this repository as working capability;
nothing below should be read as implemented:

- **No deployed Azure resources** — the `infra/` skeleton is placeholders
  only; no deployment has ever been executed; no subscription, resource
  group, storage account, Function App, or Foundry resource exists for this
  lab.
- **No live Azure AI Foundry integration** — the three Foundry provider
  scaffolds and the legacy stub contain no Azure SDK imports and no network
  code; any invocation raises `ProviderNotConfiguredError`, and server-side
  guards block resolution by default. Live wiring is the subject of a
  **deferred, unapproved ADR draft**
  (`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`)
  and the BQ-005 region approval; both are human gates before any live
  wiring begins.
- **No live Azure storage** — the `AzureBlobBackend` is a fail-closed
  scaffold; all persistence is local filesystem.
- **No prompt execution** — prompt templates are recorded provenance only;
  no prompt text is ever sent to any model.
- **No Copilot Studio** surface or configuration (a registration-readiness
  doc exists: `docs/integration/copilot-studio-tool-readiness.md`).
- **No Entra / real identity** — identity is simulated lab headers only.
- **No live model evaluations** — LE-001…LE-007 exist only as skipping stubs.
- **No admin configuration surface or config-change audit** — config is a
  source-controlled file.
- **No case entity / case-scoped authorization** — `case_id` is always null.
- **No data retention/cleanup** for the local store.

## 12. Companion documents

- [`candidate-evaluation-council-architecture.md`](./candidate-evaluation-council-architecture.md) — council subsystem detail.
- [`provider-and-storage-seams.md`](./provider-and-storage-seams.md) — seam contracts and what an Azure swap would touch.

There are no architecture guideline documents and no approved ADRs in this
repository's `docs/architecture/` tree at this time.
