# Business Fixture Routing

How curated business fixtures (synthetic candidate, position, rubric, and HR policy documents)
are routed between the repo, the evaluation runtime, and the intended future Azure / Copilot /
Foundry surfaces. This document is durable and slice-agnostic; per-package detail lives in each
fixture package's `manifest.json` and the owning slice's `artifact-routing-map.md`.

**Implementation status.** The repo contains source-controlled fixture packages and a local
evaluation runtime only. No Blob Storage upload, Copilot Studio knowledge configuration,
Foundry agent wiring, or Azure AI Search indexing has been performed. Every "later" routing
below is intent, recorded so live wiring is a copy/configuration exercise rather than a design
exercise.

## Routing categories

### 1. Source-controlled repo fixtures (implemented)

Synthetic job postings, role profiles, rubrics, resumes/cover letters, policy documents,
expected-behaviour notes, and fixture manifests live under `fixtures/`. Purpose: repeatable
local tests, deterministic CI, known sample data for live smoke tests, reproducible demo
packages. Every artifact carries provenance (source zip/repo + path), `sha256`, version, and a
synthetic declaration in its package manifest.

### 2. Runtime Blob Storage (later)

Per-evaluation copies of the exact submitted/selected documents (resume, cover letter, job,
rubric, policy versions), the evidence packet, council role outputs, synthesis output, quality
gate results, provider metadata, the human-review block, and the final audit record. The local
persistence layer already mirrors these blob-equivalent shapes (`src/hr_eval_lab/persistence/`),
so the move to Blob is a backend swap, not a remodel.

**Rule:** candidate resumes and cover letters are runtime evaluation inputs and audit
artifacts. They are never broad knowledge sources.

### 3. Copilot Studio knowledge sources (later)

Only general HR knowledge: process explanations, AI-in-recruitment guidance, fairness and
assessment principles, and instructions about what users can ask the agent.

**Rules:** candidate documents are never Copilot knowledge. Copilot knowledge is never the
sole source of truth for scoring — the evaluation API/council must receive and version the
exact policy/rubric documents used for any decision-support evaluation.

### 4. Evaluation API request payload / fixture selector (implemented locally)

Requests reference fixtures by stable ID: candidate fixture ID, position fixture ID, rubric
version, policy package ID, advisory requested rigor, correlation ID, idempotency key. The
request body never chooses the Foundry model, deployment, endpoint, or agent IDs — backend
selection is server-side, source-controlled configuration.

### 5. Foundry / council runtime (later)

Role prompts and role-specific agent instructions (source-controlled in the repo),
provider/agent mapping (`config/role-agent-mapping.sample.json` shape), model calls against
controlled evidence packets, council role outputs, and possible future evaluation datasets.
No secrets or environment-specific endpoints in prompts or fixture files.

### 6. Azure AI Search / retrieval layer (deferred)

Possible future indexing of policy/reference documents, and perhaps job/rubric documents.
Candidate resumes are not indexed unless the indexing is scoped, access-controlled, versioned,
and human-approved. This entire layer is future/deferred.

## Document-type routing summary

| Document type | Repo fixture | Blob (per-run) | Copilot knowledge | Foundry/council | AI Search |
|---|---|---|---|---|---|
| Resume / cover letter (synthetic) | yes | yes — input + audit copy | **never** | yes — evidence packet content | no (requires scoped approval) |
| Job posting / role profile | yes | yes — exact version per run | limited, later | yes — position context | deferred |
| Rubric (versioned, hashed) | yes | yes — exact version per run | **no** — API-controlled versions only | yes — scoring criteria/anchors | deferred, only if versioned/scoped |
| HR policy / guidance docs | yes | yes — exact version per run | yes, later (general knowledge) | yes — policy/fairness grounding | deferred — primary indexing candidates |
| Expected-behaviour notes, candidate metadata, fixture notes, manifests | yes | no | no | no | no |
| Evidence packet, council outputs, synthesis, gate results, audit record | produced at runtime | yes — canonical home | no | produced/consumed by council | no |

## Current fixture packages

- `fixtures/` (root `manifest.json`): deterministic-suite fixtures `cand-sample-001`,
  `pos-sample-001`, `rub-sample-001` — bound to tests DT-001…DT-018; do not replace.
- `fixtures/business/e1-candidate-evaluation/` (`fixpkg-e1-business` v1.0.0): curated business
  scenario (Senior Manager, Digital Health Strategy) — one primary candidate, five secondary
  cases, five policy documents, derived rubric `rub-smdh-001` v1 (PO-approved 2026-06-12 for
  synthetic/test-only Slice E1 lab evaluation; `production_hiring_approval: false` — never a
  production hiring approval).
