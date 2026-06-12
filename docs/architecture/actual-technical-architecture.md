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
model-backed roles execute only through a **provider seam**, persisting to a
**local filesystem store**. There is no deployed infrastructure of any kind.

```
CLI (httpx)        any HTTP client
      \               /
       v             v
  FastAPI facade (api/app.py, api/routes_evaluations.py)
   ├─ auth (api/auth.py — simulated header identity)
   ├─ envelope/errors (api/envelope.py, api/errors.py)
   ├─ idempotency (persistence/idempotency.py)
   ├─ fixture/source integrity (sources/fixture_store.py)
   └─ council orchestrator (council/orchestrator.py)
        ├─ code roles (council/code_roles.py)
        ├─ composition / mode tables (council/composition.py)
        ├─ evidence packet builder (evidence/packet_builder.py)
        ├─ rigor resolver + triggers (rigor/)
        ├─ escalation policy (escalation/policy.py)
        ├─ quality gates (gates/quality_gates.py)
        └─ provider seam (providers/base.py)
             ├─ DeterministicMockProvider (providers/mock.py)   [active]
             └─ FoundryAgentProvider stub (providers/foundry_stub.py)
                  [non-functional; raises ProviderNotConfiguredError]
   persistence: LocalStore (persistence/store.py) → var/lab-data/
   review queue row builder (review_queue.py)
   logging + never-log redaction (logging_setup.py)
   domain schemas (domain/schemas/: request, council, evaluation,
                   provider, audit; domain/ids.py)
```

## 2. Module map (`src/hr_eval_lab/`)

| Package / module | Responsibility |
|---|---|
| `api/` | App factory, routes (POST/GET `/api/evaluations`), simulated auth, envelope, HTTP/error mapping. |
| `cli.py` | Thin HTTP client (stdlib + httpx only — no application imports). |
| `config.py` | Typed, validated view of `config/lab-config.toml` (pydantic, `extra="forbid"`); `tomllib` with `tomli` fallback on Python 3.10. |
| `council/` | 11-role registry and Mode A/B/C tables, synchronous orchestrator, deterministic code roles. |
| `domain/` | Run-identity generation (`ids.py`) and all pydantic schema sources: request, per-role council outputs, advisory result, provider contract, audit record + table-row shapes. |
| `escalation/` | Escalation decision with recorded provenance (`none \| configured_escalated \| policy_triggered`). |
| `evidence/` | Evidence packet builder (stable segment addressing, rubric view, canonical serialization). |
| `gates/` | The six deterministic quality gates. |
| `logging_setup.py` | Central logger + defense-in-depth never-log redaction filter. |
| `persistence/` | `LocalStore` (blob-equivalent + JSONL table-equivalents, append-only) and idempotency records. |
| `providers/` | `CouncilProvider` seam, deterministic mock (active), Foundry seam stub (non-functional). |
| `review_queue.py` | Review-queue row construction (metadata-only). |
| `rigor/` | Pure-function rigor resolver; the six escalation-trigger computations. |
| `sources/` | Fixture resolution with per-run sha256 verification; inline-source wrapper. |

## 3. Layering and data flow

1. **Facade layer** (`api/`) — the only entry point. Enforces order: auth →
   body validation → semantic validation → idempotency → source integrity →
   orchestration → persistence → envelope. The CLI is strictly a client of
   this layer (verified by an import-graph test, DT-018).
2. **Council layer** (`council/`, `rigor/`, `escalation/`, `gates/`,
   `evidence/`) — deterministic pipeline; model-backed roles call only the
   provider seam; every output is schema-validated immediately with one
   bounded corrective retry; every execution is recorded with a sequence
   index (packet completion provably precedes the first provider call).
3. **Provider layer** (`providers/`) — `select_provider()` resolves the
   backend lazily from config; the default path never imports the Foundry
   stub module.
4. **Persistence layer** (`persistence/`) — append-only local writes; the
   full record is the only text-bearing artifact; table rows are
   metadata-first by schema construction.

## 4. Contracts and versioning

- **OpenAPI**: `openapi/evaluations-api.json`, generated from the app factory
  by `scripts/export_openapi.py`; `--check` exits non-zero on drift
  (verified clean 2026-06-11; also a CI step and a test, DT-014).
- **Provider contract**: single schema source for all backends
  (`domain/schemas/provider.py`): `PROVIDER_CONTRACT_VERSION = "1.0"`,
  `ORCHESTRATION_VERSION = "council-composition-v1"`, nullable
  `trace_id`/`eval_run_id` placeholders. No mock-only schema fork (DT-013).
- **Audit record**: `RECORD_SCHEMA_VERSION = "1.0"`
  (`domain/schemas/audit.py`); canonical-JSON serialization underpins the
  determinism baseline (DT-002).

## 5. Persistence design (local, storage-shape-mirrored)

`LocalStore` writes under the configured root (default `var/lab-data/`,
gitignored):

- `evaluations/{evaluation_id}.json` — blob-equivalent full audit record,
  canonical JSON.
- `tables/EvaluationEvidence.jsonl` — table-equivalent metadata rows
  (PartitionKey = evaluation id, RowKey = zero-padded sequence index; no
  text-bearing fields by schema).
- `tables/IdempotencyRecords.jsonl` — PartitionKey = idempotency key;
  fingerprint = sha256 of canonical request JSON.
- `tables/ReviewQueue.jsonl` — one mandatory entry per evaluation.

The shapes intentionally mirror a blob + table-storage layout so that a
future swap targets configuration rather than restructuring — but **no Azure
storage binding of any kind exists**; this is plain local filesystem I/O.

## 6. CI

`.github/workflows/ci.yml`: on PR and push to `main` — checkout, Python 3.10,
editable install with dev extras, `pytest -q`, OpenAPI drift check. No cloud
credentials, no deployment, no infrastructure provisioning.

## 7. Runtime requirements

Python ≥ 3.10 (`pyproject.toml`; CI pins 3.10 and the code avoids 3.11+-only
stdlib — `tomli` fallback in `config.py`), FastAPI, uvicorn, pydantic v2;
dev extras: pytest, httpx, openapi-spec-validator.

## 8. What is NOT built

None of the following exists in this repository; nothing below should be read
as implemented:

- **No Azure resources** — no IaC, no Bicep/Terraform, no deployment scripts,
  no resource definitions of any kind.
- **No live Azure AI Foundry integration** — the `foundry_agents` backend is
  a seam stub with no Azure SDK imports and no network code; any invocation
  raises `ProviderNotConfiguredError` (`providers/foundry_stub.py`). Live
  wiring is the subject of a **deferred, unapproved ADR draft**
  (`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`);
  it requires human approval before any live wiring begins.
- **No Copilot Studio** surface or configuration.
- **No Entra / real identity** — identity is simulated lab headers only.
- **No live model evaluations** — LE-001…LE-007 exist only as skipping stubs.
- **No admin configuration surface or config-change audit** — config is a
  source-controlled file.
- **No case entity / case-scoped authorization** — `case_id` is always null.
- **No data retention/cleanup** for the local store.

## 9. Companion documents

- [`candidate-evaluation-council-architecture.md`](./candidate-evaluation-council-architecture.md) — council subsystem detail.
- [`provider-and-storage-seams.md`](./provider-and-storage-seams.md) — seam contracts and what an Azure swap would touch.

There are no architecture guideline documents and no approved ADRs in this
repository's `docs/architecture/` tree at this time.
