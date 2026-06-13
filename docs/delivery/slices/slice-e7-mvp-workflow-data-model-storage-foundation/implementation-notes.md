# Implementation Notes: E7 Workflow Storage Foundation

## What Changed

- Added `src/hr_eval_lab/domain/schemas/workflow.py` with strict
  Azure Table-shaped schemas for the 18 MVP workflow entities.
- Added `src/hr_eval_lab/domain/schemas/workflow_artifacts.py` with canonical
  Blob path builders and `WorkflowBlobArtifactRef`.
- Added `src/hr_eval_lab/domain/schemas/workflow_queue.py` with the three
  E7 Queue message contracts.
- Added `src/hr_eval_lab/persistence/workflow_store.py`, a local deterministic
  adapter that writes:
  - `workflow/tables/<TableName>.jsonl`
  - `workflow/blobs/<canonical-blob-path>`
  - `workflow/queues/workflow-jobs.jsonl`
- Added focused E7 tests for schemas, paths, queue messages, local store
  behavior, and non-goals.

## Boundaries Preserved

- No public API route was added.
- `openapi/evaluations-api.json` and
  `openapi/copilot-studio/evaluations-tool.swagger.json` were intentionally
  left unchanged.
- No Azure Table, Blob, Queue, Foundry, Power Platform, or Copilot Studio live
  action is performed by the new E7 code.
- `LocalWorkflowStore` is not selected by `create_app()` and does not alter
  the existing evaluation persistence path.

## Design Notes

- Table entity list/dict properties serialize to canonical JSON strings at the
  adapter boundary, matching Azure Table property constraints while preserving
  ergonomic Python models.
- Queue messages are work requests only. They carry identifiers and retry
  metadata, not document text, prompt text, model outputs, keys, SAS tokens, or
  tenant/subscription identifiers.
- Blob path helpers validate identifiers before joining paths, rejecting empty
  values, leading slashes, traversal, query strings, fragments, and unknown
  container prefixes.
- Actual Azure Table/Queue SDK adapters, worker orchestration, case APIs, and
  notification APIs are deferred to later slices.

## Operational Handoff Note

- During the follow-up hardening pass, the E7 file set was already present in
  the local Git index. This note does not claim the working tree is unstaged.
- No commit, push, merge, Azure resource creation, portal change, Copilot
  Studio change, or live Foundry action was performed by E7.
