# Slice Spec: E7 MVP Workflow Data Model and Azure Storage Foundation

> Intent, not truth. Implementation truth comes from code, tests, and
> current-state docs. The buildout source of truth is
> `docs/hr_hiring_agent_mvp_workflow_azure_build_overlay_v0_1.md`, even though
> the filename says `v0_1` and the document header refers to v0.2.

## Summary

E7 defines the source-controlled storage/workflow foundation for the HR Hiring
Agent MVP without creating cloud resources or public workflow APIs. It adds:

- Azure Table-shaped workflow entity schemas for the core MVP case,
  participant, task, event, gate, notification, document, artifact, approval,
  applicant, package, model assessment, human review, and final evaluation
  records.
- Canonical Blob path builders for case documents, case artifacts, model
  assessment records, human review forms, and final evaluation reports.
- Azure Queue-shaped message contracts for model-assessment and notification
  work requests.
- A deterministic local adapter that persists those shapes as JSONL rows,
  local files, and JSONL queue messages.

## In Scope

- Internal Pydantic schema contracts only.
- Deterministic local Table/Blob/Queue-shaped adapter.
- Focused tests that pin schema shape, path shape, queue message shape, local
  adapter behavior, and E7 non-goals.
- Current-state documentation updates that describe what is now built.

## Explicit Non-Goals

- No Azure resource creation, deployment, portal work, Copilot Studio changes,
  GitHub issue changes, committing, pushing, or merging. Git index state is an
  operational handoff detail, not an E7 product behavior.
- No live Foundry/model assessment, worker execution, human review UI, final
  score aggregation implementation, candidate contact, or hiring decision.
- No real applicant data, secrets, tenant IDs, subscription IDs, connection
  strings, SAS tokens, Function keys, or secret-bearing screenshots.
- No case-management API endpoints, notification APIs, assessment-status APIs,
  OpenAPI changes, Copilot Swagger changes, or Copilot topic wiring.
- No SDK-backed Azure Table or Azure Queue adapter in E7.

## Acceptance Criteria

- The 18 planned logical Table entities exist as strict Pydantic schemas with
  `PartitionKey`, `RowKey`, `entity_type`, `schema_version = "1.0"`, and
  Table-compatible serialization. Case-partitioned entities enforce
  `PartitionKey == case_id`; Notification supports actor-inbox partitions and
  `case#{case_id}` partitions.
- Critical workflow entities enforce the E7 RowKey prefixes for tasks, gates,
  documents, artifacts, approvals, candidates, packages, jobs, model
  assessments, human reviews, and final evaluations.
- The required Blob path builders return the exact overlay paths and reject
  unsafe path segments, traversal, and non-normalized paths.
- The three Queue message types validate required IDs, correlation IDs, schema
  version, retry metadata, and reject raw-content/secret markers inside
  otherwise allowed fields.
- `LocalWorkflowStore` round-trips Table rows, Blob artifacts, and Queue
  messages without importing Azure SDKs or performing network I/O.
- The default app still exposes only the existing evaluation API surface.
