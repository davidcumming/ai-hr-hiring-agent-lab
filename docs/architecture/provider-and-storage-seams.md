# Provider and Storage Seams

Describes the two replacement seams that exist **in code today**, and what
swapping each for an Azure-backed implementation would touch. Nothing here is
wired to any cloud service; the swap analysis is forward-looking and labeled
as such.

## 1. Provider seam (AI backend)

### Contract (`src/hr_eval_lab/providers/base.py`)

`CouncilProvider` is an abstract base class with a single method:

```python
def invoke_role(role_id: str, packet: EvidencePacket,
                role_context: dict) -> ProviderResult
```

- One model-backed council role in, one schema-bearing result out.
- `role_context` carries prior validated role outputs, effective rigor,
  anomaly flags from the Deterministic Rules Validator, and (on a bounded
  corrective retry) a `corrective_hint`.
- `ProviderResult` (`domain/schemas/provider.py`) = `role_id` + `payload`
  (validated by the orchestrator against the role's declared schema) +
  `ProviderMetadata`: `ai_backend_type`, nullable `trace_id` / `eval_run_id`
  / `agent_run_id` / `model_deployment` / `prompt_version`,
  `orchestration_version` (`council-composition-v1`), `role_schema_version`
  (`1.0`), `token_usage`, `latency_ms`.
- The orchestrator, gates, and persistence depend only on this protocol plus
  the schema source — never on a concrete backend.

### Implementations

| Backend | Selected by | Status |
|---|---|---|
| `DeterministicMockProvider` (`providers/mock.py`) | `provider.ai_backend_type = "none"` (default) | **Active.** Fully deterministic, content-derived (criterion-keyword matching against rubric anchors; sha256-seeded identifiers; integer arithmetic). Schema-valid for all 8 model-backed role types; cites real packet segment / evidence ids so gates 3 and 6 are genuinely exercised. Test-only scenario scripting exists via constructor injection only — no API or config path reaches it. |
| `FoundryAgentProvider` (`providers/foundry_stub.py`) | `provider.ai_backend_type = "foundry_agents"` | **Non-functional scaffold.** No Azure SDK imports, no network code; any invocation raises `ProviderNotConfiguredError`. It exists to pin the seam contract shape against the same protocol and schema source as the mock (no mock-only schema fork — DT-013). |

### Selection (`select_provider`)

Resolution is lazy from validated config: the default path never imports the
Foundry stub module. `ai_backend_type` is a closed config literal
(`none | foundry_agents`); unknown values fail config validation.

### What a live Azure AI Foundry swap would touch (planned, not implemented)

Sourced from the seam design and the deferred ADR draft
(`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`
— **draft, NOT approved; human approval is required before any live
wiring**). By design, wiring is intended to be configuration plus one new
provider implementation, not restructuring:

- Implement `CouncilProvider.invoke_role` against Foundry Agents (Agent
  Service vs Agent Framework workflow is an open ADR question), filling the
  metadata placeholders (`trace_id`, `eval_run_id`, `agent_run_id`,
  `model_deployment`, `prompt_version`, real token/latency values).
- Possibly extend the `ai_backend_type` enumeration (config literal +
  `ProviderMetadata`) — an open ADR question.
- Add credential/endpoint configuration (none exists today; the current
  config file has no secret-bearing key) and region/data-residency approval.
- Un-defer the live evals (LE-001…LE-007 stubs in
  `tests/live_evals/test_le_stubs.py`).
- The orchestrator, gates, schemas, persistence, and facade are designed to
  remain untouched; any contract drift would surface through the pinned
  `role_schema_version` / `orchestration_version` values. (Design intent —
  only the seam discipline itself is test-verified today, via DT-013.)

There is **no prompt seam**: the mock derives outputs from the evidence
packet directly, and `prompt_version` is a nullable metadata placeholder. No
prompt templates exist in the repository.

## 2. Storage seam (persistence)

### Contract (`src/hr_eval_lab/persistence/store.py`)

`LocalStore` is the single storage abstraction the facade uses (constructed
once in `create_app` from `persistence.root`):

- `save_record(record)` — writes the blob-equivalent full audit record
  (canonical JSON) plus append-only metadata rows (evidence rows + review
  queue row).
- `load_record(evaluation_id)` — reads one full record.
- `read_table(table)` / `_append(table, row)` — JSONL table-equivalents:
  `EvaluationEvidence.jsonl`, `IdempotencyRecords.jsonl`,
  `ReviewQueue.jsonl`.

Row schemas (`domain/schemas/audit.py`) deliberately mirror an Azure Table
shape: `PartitionKey` / `RowKey` plus typed properties, and the evidence-row
schema has **no text-bearing field** by construction. Idempotency logic
(`persistence/idempotency.py`) is a thin layer over the same store.

Note: `LocalStore` is a concrete class, not an abstract interface — the seam
is the class boundary plus the storage-shaped row schemas, not a formal
protocol (observed from code).

### What an Azure storage swap would touch (planned, not implemented)

- Replace `LocalStore`'s file I/O with Blob Storage (full records) and Table
  Storage (the three JSONL tables) — the PartitionKey/RowKey and
  metadata-first row shapes are already aligned, so the intended change is an
  alternate store implementation behind the same method surface plus
  connection configuration.
- Idempotency lookup currently scans the whole JSONL table linearly; a table
  service would do a point query on PartitionKey — same semantics.
- Byte-identity determinism (DT-002) depends on the canonical-JSON
  serialization in `store.canonical_json`; a swap must preserve it.
- No retention, concurrency-control, or cleanup behavior exists today; a
  cloud-backed store would need those decisions (not specified anywhere in
  code).

## 3. Seams that do NOT exist

To prevent over-reading: there is no identity seam (auth is a single
header-parsing function in `api/auth.py`), no prompt/template seam, no
queue/messaging seam (the review queue is a JSONL file), no eval-harness
seam (live-eval stubs skip unconditionally), and no configuration service
seam (one TOML file read at startup).
