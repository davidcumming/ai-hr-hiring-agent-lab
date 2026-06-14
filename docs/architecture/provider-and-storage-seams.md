# Provider and Storage Seams

Describes the replacement seams that exist **in code today**, and what
swapping each for an Azure-backed implementation would touch. After E3, the
storage seam has one live-capable Azure path: Blob-backed evaluation
record/artifact persistence, selected only by explicit server-side
configuration. Foundry/provider paths remain fail-closed, non-functional
scaffolds. Live model wiring is still human-gated (deferred ADR + BQ-005
region approval — see §5).

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
  / `agent_run_id` / `model_deployment` / `prompt_version` /
  `prompt_template_id` / `prompt_template_version` / `model_or_agent_ref` /
  `safe_error`, a `warnings` list, `orchestration_version`
  (`council-composition-v1`), `role_schema_version` (`1.0`), `token_usage`,
  `latency_ms`. `safe_error` carries a safe error category only — never a raw
  provider error.
- The orchestrator, gates, and persistence depend only on this protocol plus
  the schema source — never on a concrete backend.

### Provider registry and selection (`src/hr_eval_lab/providers/registry.py`)

`select_provider()` (`providers/base.py`) delegates to
`resolve_provider()` in the provider registry, which resolves the configured
`provider.provider_id` lazily. The `provider_id` enumeration
(`config.py`, closed config literal):

| `provider_id` | Implementation | Status |
|---|---|---|
| `deterministic_mock` (default) | `DeterministicMockProvider` (`providers/mock.py`) | **Active — the only functional provider.** Fully deterministic, content-derived (criterion-keyword matching against rubric anchors; sha256-seeded identifiers; integer arithmetic). Schema-valid for all 8 model-backed role types; cites real packet segment / evidence ids so gates 3 and 6 are genuinely exercised. Stamps the role's prompt-registry template id/version into `ProviderMetadata` (templates are recorded, never executed — see §3). Test-only scenario scripting exists via constructor injection only — no API or config path reaches it. |
| `foundry_project_responses` | `providers/foundry/project_responses.py` | **Non-functional scaffold.** Fail-closed: any invocation raises `ProviderNotConfiguredError`. |
| `foundry_prompt_agent` | `providers/foundry/prompt_agent.py` | **Non-functional scaffold.** Same fail-closed behavior. |
| `foundry_hosted_agent` | `providers/foundry/hosted_agent.py` | **Non-functional scaffold.** Same fail-closed behavior. |

The three `foundry_*` IDs exist only so future wiring is a configuration
exercise; **none of them is chosen** — the live runtime shape
is an open question of the deferred, unapproved ADR. No module under
`providers/foundry/` imports any Azure/Foundry SDK at import time or performs
network I/O.

Resolution rules (all server-side; no request field can reach them):

- The default path imports only the mock — no Foundry module is imported.
- `HRHA_PROVIDER_KILL_SWITCH=true` blocks every Foundry provider
  (`ProviderBlockedError`, a `ProviderNotConfiguredError` subclass),
  regardless of any other configuration.
- `HRHA_ENABLE_LIVE_AZURE` unset or not `"true"` (case-insensitive,
  whitespace-trimmed; unset is the default) also blocks Foundry provider
  resolution. Even with both guards open, only the
  fail-closed scaffolds exist — no live call is possible.
- An unknown `provider_id` fails config validation (closed literal).

The legacy config key `provider.ai_backend_type` (`none | foundry_agents`)
is retained for audit-record compatibility. It is validated for consistency
with `provider_id` (`none` ↔ `deterministic_mock`; `foundry_agents` ↔ any
`foundry_*` id) — a mismatch is a configuration error. The legacy
`providers/foundry_stub.py` (`FoundryAgentProvider`) still exists in the tree
but is **no longer reachable** through `select_provider()`; the registry
routes exclusively on `provider_id`.

### What a live Azure AI Foundry swap would touch (planned, not implemented)

Sourced from the seam design and the deferred ADR draft
(`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`
— **draft, NOT approved; human approval is required before any live
wiring**). By design, wiring is intended to be configuration plus one real
provider implementation behind an existing scaffold, not restructuring:

- Implement `invoke_role` in one (or more) of the `providers/foundry/`
  scaffolds, filling the metadata fields the contract already carries
  (`trace_id`, `eval_run_id`, `agent_run_id`, `model_deployment`,
  `model_or_agent_ref`, `prompt_template_id/version`, real token/latency
  values, `warnings`, `safe_error`).
- Confirm or revise the provider-ID enumeration — the final enumeration is an
  open ADR question; the current IDs decide nothing.
- Add endpoint/identity configuration (placeholders exist in
  `config/azure.env.sample` and `infra/env.sample`; no live value or secret
  exists anywhere in the repo) plus region/data-residency approval (BQ-005).
- Un-defer the live evals (LE-001…LE-007 stubs in
  `tests/live_evals/test_le_stubs.py`).
- The orchestrator, gates, schemas, persistence, and facade are designed to
  remain untouched; any contract drift would surface through the pinned
  `role_schema_version` / `orchestration_version` values. (Design intent —
  only the seam discipline itself is test-verified today, via DT-013.)

## 2. Storage seam (persistence)

### Backend contract (`src/hr_eval_lab/persistence/backend.py`)

`StorageBackend` is a formal abstract base class — the seam between the
facade's persistence layer and a physical store:

```python
write_evaluation_record(evaluation_id, record_payload)
read_evaluation_record(evaluation_id) -> Optional[dict]
write_artifact(evaluation_id, artifact_type, role_or_name, payload) -> StorageArtifactRef
list_artifacts(evaluation_id) -> list[StorageArtifactRef]
write_metadata_row(record_summary)
read_metadata_row(evaluation_id) -> Optional[dict]
```

Two implementations exist, resolved by `select_backend()` from
`[storage] backend` in config (closed literal `local_filesystem |
azure_blob`; the Azure module is imported only when explicitly selected):

| Backend | Status |
|---|---|
| `LocalFilesystemBackend` (default) | **Active local default.** Writes the artifact-per-evaluation layout below under the local persistence root. |
| `AzureBlobBackend` (`persistence/azure_blob_backend.py`) | **Functional for Slice E3 Blob record/artifact persistence only.** No Azure SDK import at module import time or on the local default path. Construction raises `StorageNotConfiguredError` unless Blob account URL + container are configured and `HRHA_ENABLE_AZURE_STORAGE=true`; `table_endpoint` is optional because Table Storage is deferred. Auth is identity-based (managed identity in hosted Azure; `DefaultAzureCredential` only for explicit developer live-storage smoke paths). Account keys, connection strings, SAS tokens, and SAS-in-URL query strings are rejected. |

Local artifact layout (mirrors the intended future blob layout so wiring is
configuration, not restructuring):

```
evaluations/{evaluation_id}/record.json            full audit record (canonical JSON)
evaluations/{evaluation_id}/request.json
evaluations/{evaluation_id}/source-documents.json
evaluations/{evaluation_id}/evidence-packet.json
evaluations/{evaluation_id}/council/{role}.json    per-role transcript (CouncilRoleInvocation)
evaluations/{evaluation_id}/synthesis.json
evaluations/{evaluation_id}/quality-gates.json
evaluations/{evaluation_id}/provider-metadata.json
evaluations/{evaluation_id}/human-review.json
metadata/evaluations.jsonl                          one text-free summary row per evaluation
```

Every artifact below `record.json` is a **projection of the audit record**,
emitted at persistence time — the record is the single source of truth; no
second truth exists. `StorageArtifactRef` and `RecordSummaryRow`
(`domain/schemas/storage.py`) are the boundary schemas; `RecordSummaryRow`
deliberately mirrors an Azure Table shape (`PartitionKey`/`RowKey` + typed
properties) and has **no text-bearing field** by construction.

### Store facade (`src/hr_eval_lab/persistence/store.py`)

`LocalStore` keeps the facade-facing API (`save_record` / `load_record` /
`read_table`), constructed once in `create_app` from `persistence.root`. It
delegates record and artifact I/O to the `StorageBackend` and additionally
writes the established append-only JSONL table-equivalents:
`tables/EvaluationEvidence.jsonl` (metadata-first rows, no text-bearing
field), `tables/IdempotencyRecords.jsonl`, `tables/ReviewQueue.jsonl`.
Idempotency logic (`persistence/idempotency.py`) remains a thin layer over
`LocalStore`'s table-equivalents — deliberately **not** part of the
`StorageBackend` ABC, to avoid a second source of truth (a future Azure
implementation would map the idempotency table to Azure Table directly).

### Workflow storage foundation (`src/hr_eval_lab/persistence/workflow_storage.py`)

E7 adds workflow storage contracts beside the existing evaluation persistence
seam. E8 adds guarded Azure SDK-backed adapters behind those contracts while
preserving the local deterministic default. E9 uses the Table portion of this
seam for the first public recruitment-case endpoints: `POST /api/cases`,
`GET /api/cases/{case_id}`, and `GET /api/cases/{case_id}/next-actions`.

- `domain/schemas/workflow.py` defines 18 Table-shaped MVP workflow entities
  (`RecruitmentCases`, `CaseParticipants`, `CaseTasks`, `CaseEvents`,
  `WorkflowGates`, `Notifications`, `SourceDocuments`, `ArtifactVersions`,
  `Approvals`, `Applicants`, `CandidatePackages`, `ModelAssessmentJobs`,
  `ModelCandidateAssessments`, `ModelCriterionRatings`,
  `HumanCandidateReviews`, `HumanCriterionReviewItems`,
  `FinalCandidateEvaluations`, and `FinalCriterionRatings`). All use
  `PartitionKey`, `RowKey`, `entity_type`, and `schema_version = "1.0"`.
  Case-partitioned entities enforce `PartitionKey == case_id`; Notification
  supports recipient actor inbox partitions and `case#{case_id}` partitions.
  Critical workflow RowKeys enforce their expected prefixes.
- `domain/schemas/workflow_artifacts.py` defines the canonical Blob paths for
  case documents, case artifacts, model assessment records, human reviews, and
  final evaluation reports. Path builders reject traversal, leading slashes,
  query strings, non-normalized paths, and unknown container prefixes.
- `domain/schemas/workflow_queue.py` defines Queue message contracts for
  `run-model-candidate-assessment`, `run-model-assessment-batch`, and
  `write-notification`; messages reject raw-content and secret markers even
  when injected into otherwise allowed string/list fields.
- `workflow_storage.py` defines the internal protocol seam:
  `WorkflowTableStore`, `WorkflowBlobStore`, `WorkflowQueueStore`, and the
  composed `WorkflowStorageBackend`. `select_workflow_storage()` resolves the
  backend lazily from `[workflow_storage]`.
- `cases/service.py` depends only on `WorkflowStorageBackend`. It creates and
  reads `RecruitmentCases`, `CaseParticipants`, `CaseTasks`, `WorkflowGates`,
  and `CaseEvents` rows for E9. It does not import concrete local/Azure
  adapters, Azure SDKs, provider code, Blob path writers, Queue writers, or
  Copilot tooling.
- `LocalWorkflowStore` persists these shapes under `<root>/workflow/` using
  JSONL Table rows, local files for Blob artifacts, and JSONL Queue messages.
  It imports no Azure SDKs, performs no network I/O, and remains the default.
- `AzureWorkflowStorageBackend` (`persistence/azure_workflow_storage.py`) is
  functional only when `[workflow_storage] backend = "azure"` is explicitly
  selected and `HRHA_ENABLE_AZURE_WORKFLOW_STORAGE=true`. It uses Azure Table
  Storage for E7 Table entities, Azure Blob Storage for canonical E7 artifact
  paths, and Azure Queue Storage for validated E7 Queue messages. It imports
  Azure SDKs only inside the real-client builder after configuration guards
  pass; deterministic tests inject fake clients.

E9 is a narrow public API use of the Table contracts only. It is **not** a
worker, resource-creation path, Copilot surface, notification API, document
API, applicant import path, model-assessment launcher, or live Azure smoke.
Future slices can wire more contracts into facade routes and workers without
rewriting the storage boundary.

### Azure storage status after E3

- Implemented: `AzureBlobBackend` methods persist the full record and artifact
  projections as block blobs under
  `{container}/evaluations/{evaluation_id}/...` (same names as the local
  layout). `read_evaluation_record` retrieves `record.json` by evaluation id,
  which is enough for hosted POST-then-GET durability.
- Implemented as Blob compatibility, not Table Storage: `write_metadata_row`
  writes `metadata/evaluations/{evaluation_id}.json` so the current
  `StorageBackend` contract can complete without requiring Table Storage.
- Implemented for workflow foundation only: E8 maps E7 workflow entities,
  workflow artifacts, and workflow queue messages to guarded Azure
  Table/Blob/Queue adapters.
- Deferred: map the evaluation summary row and the three legacy evaluation
  JSONL table-equivalents to Azure Table Storage; idempotency lookup becomes
  a point query on PartitionKey — same semantics.
- Byte-identity determinism (DT-002) depends on the canonical-JSON
  serialization (`backend.canonical_json`); a swap must preserve it.
- No retention, concurrency-control, or cleanup behavior exists today; a
  cloud-backed store would need those decisions (not specified anywhere in
  code).

## 3. Prompt seam (versioned prompt registry)

A source-controlled prompt registry exists at `src/hr_eval_lab/prompts/`:

- `registry.py` — `get_template(role_id, version=None) -> PromptTemplate`
  (latest version by default) and `list_roles()`. Template files live at
  `prompts/templates/<role_id>.v<N>.md`; the stable template id is
  `prompt-<role_id>` and the version is `v<N>`.
- Ten roles have a `v1` template (the eight model-backed roles plus
  `request_normalizer` and `quality_gate_evaluator`).
- Every template embeds the mandatory safety-constraint block
  (`MANDATORY_CONSTRAINTS` in `registry.py`: evidence-packet-only reasoning,
  no unsupported inference, evidence-relation discipline, no protected
  characteristics or proxies, rubric-as-written, structured JSON only,
  advisory-only, human review required). Test-pinned (RP-009), which also
  pins the absence of secret-bearing patterns, GUID-like tenant/subscription
  identifiers, and non-example Azure/Microsoft endpoints; the absence of real
  applicant data is maintained by review convention (the templates contain
  none) rather than by a dedicated test pattern.

**Templates are recorded, never executed.** The deterministic mock derives
outputs from the evidence packet directly and stamps the role's
`prompt_template_id` / `prompt_template_version` into `ProviderMetadata`, so
the audit trail already carries prompt provenance. No prompt text is ever
sent anywhere; there is no model to send it to. A role-to-template /
role-to-future-agent mapping sample (placeholders only) is committed at
`config/role-agent-mapping.sample.json`.

## 4. Seams that do NOT exist

To prevent over-reading: there is no identity seam (auth is a single
header-parsing function in `api/auth.py`), no case-scoped authorization seam
(E9 case endpoints still require the global simulated `hr` lab role), no live
Azure Queue/worker seam (E7 defines Queue message contracts and local/Azure
adapters only; E9 does not enqueue), no eval-harness seam (live-eval stubs
skip unconditionally), and no configuration service seam (one TOML file read
at startup, plus server-side environment guards and the Azure Functions
wrapper-only storage overlay).

## 5. Live-wiring gates (status, not architecture)

Live Foundry/model wiring is **deferred and human-gated**: the Foundry-wiring
ADR
(`docs/delivery/slices/slice-e1-candidate-evaluation-council/adr-deferred-foundry-wiring.md`)
is a draft and NOT approved, and BQ-005 (Canadian-residency region/deployment
approval) is pending. Until both human gates pass, every Foundry-shaped
component in this document remains a fail-closed scaffold and no live model
call, resource creation, or token spend is possible from this codebase.
Azure Blob storage is the narrow exception: it may persist evaluation records
and artifacts when `HRHA_STORAGE_BACKEND=azure_blob` and
`HRHA_ENABLE_AZURE_STORAGE=true`, while `HRHA_ENABLE_LIVE_AZURE=false` and
`HRHA_PROVIDER_KILL_SWITCH=true` continue to keep model paths disabled.
