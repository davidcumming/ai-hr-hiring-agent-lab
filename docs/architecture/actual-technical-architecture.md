# Actual Technical Architecture

This document describes **only what is physically built** in this repository
(Process Doc §9.2). Aspirational or planned components appear solely in the
"Not built" section, clearly labeled. Behavior details live in
[`../product-current-state/candidate-evaluation-council.md`](../product-current-state/candidate-evaluation-council.md).

## 1. System shape

A Python application: a FastAPI **facade** that owns the entire
deterministic business contract (identity, authorization, validation,
idempotency, source integrity, gates, schema validation of role outputs,
persistence, response envelope), driving a **council orchestrator** whose
model-backed roles execute only through a **provider seam**, persisting
through a **storage backend seam** to the local filesystem by default or to
Azure Blob for explicitly configured hosted evaluation records/artifacts. The
repository now includes an Azure Functions ASGI host wrapper that can deploy
this same facade to the already-created lab Function App, but this codebase
does not create, manage, or configure Azure resources. Real subscription IDs,
tenant IDs, object IDs, client IDs, endpoints, keys, and secrets remain out
of source control. Foundry-shaped live components remain fail-closed.

A manual Copilot Studio lab configuration exists outside source control for
one synthetic topic workflow. It uses the curated Power Platform custom
connector contract, stores the returned `evaluation_id` in
`submitted_evaluation_id`, and calls the body-based retrieve wrapper. This is
actual manual portal configuration evidence, not source-controlled Copilot
ALM or production integration.

The repository also defines the E7/E8 workflow storage foundation as internal
contracts and adapters: Azure Table-shaped workflow entities, canonical Blob
path builders, Azure Queue-shaped message contracts, a deterministic
`LocalWorkflowStore`, and a guarded `AzureWorkflowStorageBackend` selected only
by explicit workflow-storage configuration. These contracts are not yet wired
into public API endpoints, workers, or Copilot topics.

```
CLI (httpx)        any HTTP client
      \               /
       v             v
  Azure Functions ASGI wrapper (function_app.py) [deployment bridge only]
                 |
                 v
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
            ├─ LocalFilesystemBackend → var/lab-data/        [active local default]
            │                         → temp/HRHA_PERSISTENCE_ROOT
            │                           [Function wrapper smoke path]
            └─ AzureBlobBackend (persistence/azure_blob_backend.py)
                 [explicit hosted record/artifact backend; guarded]
   workflow storage foundation (E7/E8, internal only)
       ├─ workflow Table schemas (domain/schemas/workflow.py)
       ├─ workflow Blob path contracts (domain/schemas/workflow_artifacts.py)
       ├─ workflow Queue message contracts (domain/schemas/workflow_queue.py)
       ├─ workflow storage protocols/selectors (persistence/workflow_storage.py)
       ├─ LocalWorkflowStore (persistence/workflow_store.py)
       │    [default local JSONL/filesystem adapter; no Azure SDK imports]
       └─ AzureWorkflowStorageBackend (persistence/azure_workflow_storage.py)
            [explicit guarded Table/Blob/Queue adapter; lazy Azure SDK imports]
   review queue row builder (review_queue.py)
   logging + never-log redaction (logging_setup.py)
   domain schemas (domain/schemas/: request, council, evaluation,
                   provider, audit, storage, transcript, workflow,
                   workflow_artifacts, workflow_queue; domain/ids.py)

Copilot Studio manual lab topic
   -> Power Platform custom connector (curated Swagger; manual portal config)
   -> Azure Functions ASGI wrapper / FastAPI facade
```

## 2. Module map (`src/hr_eval_lab/`)

| Package / module | Responsibility |
|---|---|
| Root `function_app.py` | Azure Functions Python ASGI wrapper around the existing FastAPI app factory. It loads normal config, overrides `persistence.root` to `HRHA_PERSISTENCE_ROOT` or a temp directory, overlays Azure Blob storage app settings only when `HRHA_STORAGE_BACKEND=azure_blob`, and overlays guarded workflow storage only when `HRHA_WORKFLOW_STORAGE_BACKEND=azure`; no routes, business logic, or Foundry behavior are added here. |
| Root `host.json` / `.funcignore` / `requirements.txt` | Function host route-prefix config, deployment ignore hygiene, and Azure Functions deployment dependencies. |
| `api/` | App factory, routes (`POST /api/evaluations` / `submitEvaluation`, `GET /api/evaluations/{evaluation_id}` / `getEvaluation`, `POST /api/evaluations/retrieve` / `retrieveEvaluationForCopilot`), simulated auth, envelope, HTTP/error mapping, `Idempotency-Key` header handling, `X-Correlation-Id` request/response header. |
| `cli.py` | Thin HTTP client (stdlib + httpx only — no application imports). |
| `config.py` | Typed, validated view of `config/lab-config.toml` (pydantic, `extra="forbid"`); provider-ID/backend-family consistency validation; evaluation and workflow storage backend selection; Foundry/provider env guard readers (`HRHA_ENABLE_LIVE_AZURE`, `HRHA_PROVIDER_KILL_SWITCH`) plus storage-specific guards (`HRHA_ENABLE_AZURE_STORAGE`, `HRHA_ENABLE_AZURE_WORKFLOW_STORAGE`); `tomllib` with `tomli` fallback on Python 3.10. |
| `council/` | 11-role registry and Mode A/B/C tables, synchronous orchestrator, deterministic code roles. |
| `domain/` | Run-identity generation (`ids.py`) and all pydantic schema sources: request, per-role council outputs, advisory result, provider contract, audit record + table-row shapes, storage boundary (`storage.py`: `StorageArtifactRef`, `RecordSummaryRow`), per-role transcript (`transcript.py`: `CouncilRoleInvocation`), and E7 workflow contracts (`workflow.py`, `workflow_artifacts.py`, `workflow_queue.py`). |
| `escalation/` | Escalation decision with recorded provenance (`none \| configured_escalated \| policy_triggered`). |
| `evidence/` | Evidence packet builder (stable segment addressing, rubric view, canonical serialization). |
| `gates/` | The six deterministic quality gates. |
| `logging_setup.py` | Central logger + defense-in-depth never-log redaction filter. |
| `persistence/` | `StorageBackend` ABC + `LocalFilesystemBackend` (default local) + `AzureBlobBackend` (explicit Blob record/artifact backend); `LocalStore` facade over the backend plus JSONL table-equivalents; idempotency records; workflow storage protocols/selectors; `LocalWorkflowStore` for default E7 Table/Blob/Queue-shaped local workflow contracts; `AzureWorkflowStorageBackend` for explicit guarded SDK-backed workflow storage. |
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
5. **Workflow storage foundation** (`domain/schemas/workflow*.py`,
   `persistence/workflow_storage.py`, `persistence/workflow_store.py`,
   `persistence/azure_workflow_storage.py`) — internal E7/E8 contracts define
   the MVP case/workflow entity model, exact Blob paths, and async work request
   messages. The local adapter remains deterministic; the Azure adapter maps
   the same contracts to guarded Table/Blob/Queue SDK clients. No facade route
   or worker uses them yet.

## 4. Contracts and versioning

- **OpenAPI**: `openapi/evaluations-api.json`, generated from the app factory
  by `scripts/export_openapi.py`; `--check` exits non-zero on drift
  (verified clean 2026-06-13; also a CI step and a test). Stable operation
  IDs `submitEvaluation`, `getEvaluation`, and
  `retrieveEvaluationForCopilot`; documented request headers
  `Idempotency-Key` (submit POST) and `X-Correlation-Id` (submit POST, body
  retrieve POST, and GET); the request schema exposes no
  provider/model/deployment/endpoint/agent field (test-pinned).
- **Copilot Swagger**:
  `openapi/copilot-studio/evaluations-tool.swagger.json`, generated by
  `scripts/export_copilot_openapi.py`; `--check` exits non-zero on drift. It
  is a Swagger 2.0 custom-connector artifact separate from the OpenAPI 3.1
  source contract. It exposes exactly three Copilot-facing actions:
  `submitEvaluation`, `getEvaluation`, and
  `retrieveEvaluationForCopilot`. The retrieve wrapper accepts only body
  field `evaluation_id`; the canonical GET route remains available.
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
- **Workflow storage foundation**: `WorkflowTableEntity` and the 18 E7 table
  schemas (`domain/schemas/workflow.py`); canonical Blob path builders and
  `WorkflowBlobArtifactRef` (`domain/schemas/workflow_artifacts.py`); Queue
  message schemas for `run-model-candidate-assessment`,
  `run-model-assessment-batch`, and `write-notification`
  (`domain/schemas/workflow_queue.py`); workflow storage protocols
  (`persistence/workflow_storage.py`). These are internal contracts only and
  do not change the OpenAPI/Copilot contracts.

## 5. Persistence design (local, storage-shape-mirrored)

`LocalStore` (over `LocalFilesystemBackend`) writes under the configured root
(default `var/lab-data/`, gitignored, for normal local FastAPI/dev use):

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
future swap targets configuration rather than restructuring. The current
narrow Azure storage path lets `AzureBlobBackend` persist the full evaluation
record and artifact projections to Blob when explicitly selected and
`HRHA_ENABLE_AZURE_STORAGE=true`. It does not import Azure SDKs on the local
default path and rejects connection strings, account keys, SAS tokens, and
SAS-in-URL query strings.

When imported through `function_app.py`, `persistence.root` is overridden to
`HRHA_PERSISTENCE_ROOT` or `<tempdir>/hrha-lab-data` for local JSONL
table-equivalent rows. If the wrapper also sees
`HRHA_STORAGE_BACKEND=azure_blob`, it overlays Blob account URL/container
settings and uses Blob for record/artifact I/O. Hosted POST-then-GET is
durable for the full audit record. Azure Table-backed idempotency, evidence
rows, review queue rows, summary rows, concurrency, retention/recovery, and
reconciliation remain deferred.

`select_workflow_storage()` resolves the workflow storage backend from
`[workflow_storage]`. With committed defaults it returns `LocalWorkflowStore`,
which writes E7 workflow foundation data under `<root>/workflow/`:

- `tables/<TableName>.jsonl` — Azure Table-shaped rows for the MVP workflow
  entities. List/dict properties are serialized as canonical JSON strings at
  the Table boundary. Case-partitioned workflow entities enforce
  `PartitionKey == case_id`, while Notification supports recipient actor inbox
  partitions and `case#{case_id}` partitions. Critical workflow RowKeys
  enforce their E7 prefixes.
- `blobs/<container>/cases/...` — local files using the canonical E7 Blob
  paths, including role source documents, candidate source documents,
  rubric artifacts, candidate packages, model assessment records, human review
  forms, and final evaluation reports. Blob path validation rejects traversal,
  query/fragment markers, and non-normalized paths.
- `queues/workflow-jobs.jsonl` — Queue-shaped async work request envelopes for
  model assessment and notification messages. Queue schemas reject raw-content
  and secret markers even inside otherwise allowed identifier fields.

The local adapter imports no Azure SDK modules and is selected by
`create_app()` as `app.state.workflow_storage`. It is a deterministic
foundation for future case/workflow facade slices.

`AzureWorkflowStorageBackend` is available only when `[workflow_storage]
backend = "azure"` is explicitly selected and
`HRHA_ENABLE_AZURE_WORKFLOW_STORAGE=true`. It maps the same contracts to Azure
Table Storage, Azure Blob Storage, and Azure Queue Storage using identity-based
auth. The Azure SDK imports occur only inside the real-client builder after
guards pass; deterministic tests inject fake clients. It does not create
tables, containers, queues, resources, routes, or workers.

## 6. Configuration and guards

- `config/lab-config.toml` — the only runtime configuration file:
  `[rigor]`, `[escalation]`, `[provider]` (`provider_id` +
  validated-consistent legacy `ai_backend_type`), `[persistence]`,
  `[storage]` (`backend = "local_filesystem"` default) and `[storage.azure]`
  (empty placeholders; no secrets), plus `[workflow_storage]`
  (`backend = "local"` default).
- Server-side environment guards (read at resolution time, never stored in
  records): `HRHA_ENABLE_LIVE_AZURE` (default false — live model/provider
  paths disabled), `HRHA_PROVIDER_KILL_SWITCH` (`true` blocks all Foundry
  providers), and `HRHA_ENABLE_AZURE_STORAGE` (`true` required for the
  explicitly selected Azure Blob storage backend). E8 adds
  `HRHA_ENABLE_AZURE_WORKFLOW_STORAGE` for the explicitly selected Azure
  workflow Table/Blob/Queue backend.
- Azure Functions wrapper-only persistence override:
  `HRHA_PERSISTENCE_ROOT` (optional; defaults to the process temp directory).
  Storage app-setting overlay (`HRHA_STORAGE_BACKEND`,
  `HRHA_STORAGE_ACCOUNT_URL`, `HRHA_STORAGE_CONTAINER`, optional
  `HRHA_STORAGE_TABLE_ENDPOINT`, optional `HRHA_STORAGE_QUEUE_ENDPOINT`) is
  applied only by `function_app.py`. Workflow storage app-setting overlay
  (`HRHA_WORKFLOW_STORAGE_BACKEND`, `HRHA_WORKFLOW_BLOB_CONTAINER`,
  `HRHA_WORKFLOW_TABLE_PREFIX`, `HRHA_WORKFLOW_QUEUE_NAME`) is also wrapper
  only. This does not alter `config/lab-config.toml` or the normal local app
  default.
- Source-controlled samples, placeholders only: `config/azure.env.sample`,
  `config/role-agent-mapping.sample.json`.

## 7. Scripts

| Script | Role |
|---|---|
| `scripts/export_openapi.py` | OpenAPI generation + drift check (CI step). |
| `scripts/vendor_fixtures.py` | Dev-time fixture vendoring/hash refresh. |
| `scripts/run_council_local.py` | Local deterministic council demo: one synthetic candidate strictly through the in-process HTTP facade; writes the artifact tree; prints a safe summary only (ids, statuses, counts — never document or prompt text). |
| `scripts/smoke_foundry_config.py` | Disabled-by-default config smoke scaffold; double-guarded (`HRHA_ENABLE_LIVE_AZURE=true` **and** `--live`); no SDK import and no network in the default path; fails safely (exit 2, clear config error) if the live path is requested — live checks are not implemented. |
| `scripts/smoke_storage_config.py` | Disabled-by-default storage config smoke. The default path performs no network I/O and sanity-checks the local filesystem backend in a temp dir. The explicit live-storage config path requires `HRHA_ENABLE_AZURE_STORAGE=true` and `--live`, checks `HRHA_STORAGE_BACKEND=azure_blob` plus Blob account URL/container, and does not require Table endpoint for the current Blob-only storage path. |
| `scripts/smoke_workflow_storage_config.py` | Disabled-by-default E8 workflow storage smoke. The default path performs no network I/O, imports no Azure SDK, and exercises local workflow Table/Blob/Queue operations in a temp dir. The explicit live path requires `HRHA_ENABLE_AZURE_WORKFLOW_STORAGE=true`, `--live`, `HRHA_WORKFLOW_STORAGE_BACKEND=azure`, Blob/Table/Queue service URLs, a workflow Blob container, and a dedicated empty workflow Queue. |

## 8. Infrastructure-as-code skeleton (placeholders only — nothing deployed)

`infra/` contains a documentation-grade IaC skeleton: `README.md`,
`bicep/main.bicep`, `parameters.sample.json`, `env.sample`. Placeholder
values only (`<...>` / `TODO-...`); no real tenant/subscription IDs,
endpoints, object IDs, or secrets; identity-based access (managed identity +
RBAC) is the documented pattern — never keys, connection strings, or SAS
tokens. Manually provisioned Azure lab resources exist out-of-band, including
the target Function App for the wrapper smoke test and one Copilot Studio lab
topic/custom-connector configuration; this repository still does not
provision or manage those resources. Complete Azure Table-backed storage,
Foundry, Entra auth, source-controlled Copilot ALM/export, and production
Copilot Studio integration remain later human-gated slices.

## 9. CI

`.github/workflows/ci.yml`: on PR and push to `main` — checkout, Python 3.10,
editable install with dev extras, `pytest -q`, OpenAPI drift check. No cloud
credentials, no deployment, no infrastructure provisioning.

## 10. Runtime requirements

Python ≥ 3.10 (`pyproject.toml`; CI pins 3.10 and the code avoids 3.11+-only
stdlib — `tomli` fallback in `config.py`), Azure Functions Python library,
Azure Identity, Azure Storage Blob, Azure Data Tables, Azure Storage Queue,
FastAPI, uvicorn, pydantic v2; dev extras: pytest, httpx,
openapi-spec-validator.

## 11. What is NOT built

None of the following exists in this repository as working capability;
nothing below should be read as implemented:

- **No repo-managed Azure resources** — the `infra/` skeleton is placeholders
  only; this repository does not contain real tenant/subscription IDs,
  endpoints, object IDs, client IDs, keys, or secrets and does not create or
  manage Azure infrastructure.
- **No live Azure AI Foundry integration** — the three Foundry provider
  scaffolds and the legacy stub contain no Azure SDK imports and no network
  code; any invocation raises `ProviderNotConfiguredError`, and server-side
  guards block resolution by default. Live wiring is the subject of a
  **deferred, unapproved ADR draft**
  (`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`)
  and the BQ-005 region approval; both are human gates before any live
  wiring begins.
- **No complete live Azure Storage system of record** — `AzureBlobBackend` can
  persist full evaluation records and artifact projections to Blob when
  explicitly enabled for the Azure Functions host. E8 adds guarded
  SDK-backed workflow Table/Blob/Queue adapters behind the E7 contracts, but
  evaluation idempotency rows, evidence JSONL rows, review queue rows,
  Azure Table summaries, queue processing, concurrency, retention/recovery,
  and reconciliation remain local/deferred.
- **No case-management or notification API** — E7/E8 add internal workflow
  data contracts and adapters only. There is no `POST /api/cases`, case
  search/open endpoint, notification endpoint, assessment-status endpoint,
  worker, or Copilot topic wiring for those contracts.
- **No prompt execution** — prompt templates are recorded provenance only;
  no prompt text is ever sent to any model.
- **No source-controlled or production Copilot Studio integration** — one
  manual lab topic workflow exists for the synthetic
  `submitEvaluation` -> `submitted_evaluation_id` ->
  `retrieveEvaluationForCopilot` path, with `submitEvaluation` and
  `retrieveEvaluationForCopilot` available only when referenced by topics or
  agents. There is no Copilot ALM export, durable screenshot/export/transcript
  artifact, general multi-candidate workflow, production identity, or
  production readiness claim.
- **No Entra / real identity** — identity is simulated lab headers only.
- **No live model evaluations** — LE-001…LE-007 exist only as skipping stubs.
- **No admin configuration surface or config-change audit** — config is a
  source-controlled file.
- **No case entity / case-scoped authorization** — `case_id` is always null.
- **No data retention/cleanup** for the local store.

## 12. Companion documents

- [`candidate-evaluation-council-architecture.md`](./candidate-evaluation-council-architecture.md) — council subsystem detail.
- [`provider-and-storage-seams.md`](./provider-and-storage-seams.md) — seam contracts and what an Azure swap would touch.
- [`candidate-evaluation-fixture-architecture.md`](./candidate-evaluation-fixture-architecture.md) — fixture package structure, manifests/hashing, validation tests, and the (future-only) routing intent toward Blob/Copilot/Foundry/Search.

There are no architecture guideline documents and no approved ADRs in this
repository's `docs/architecture/` tree at this time.
