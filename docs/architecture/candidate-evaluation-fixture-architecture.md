# Candidate Evaluation Fixture Architecture

How synthetic fixture data is structured, pinned, validated, and routed in this repo, and how
it is intended to map onto the future Azure/Copilot/Foundry runtime. Only the repo-local parts
are built; every cloud placement in §4 is documented intent, not implementation.

## 1. Two-package design

| | Deterministic-suite fixtures | Business fixture package |
|---|---|---|
| Root | `fixtures/` (+ root `manifest.json`) | `fixtures/business/e1-candidate-evaluation/` (+ package `manifest.json`) |
| Package ID | (root, unversioned) | `fixpkg-e1-business` v1.0.0 |
| Contents | `pos-sample-001`, `rub-sample-001` v1, `cand-sample-001` | `pos-smdh-001`, `rub-smdh-001` v1 (PO-approved for synthetic/test-only lab evaluation; `production_hiring_approval: false`), 1 primary + 5 secondary candidates, 5 HR policy docs, expected-behaviour notes |
| Role | Bound to the deterministic test suite and the runtime `FixtureStore`; **runtime hash authority** (BR-009: hash mismatch → `blocked`) | Curated business scenario for realistic local runs and future live smoke tests; validated by `tests/test_business_fixtures.py` |
| Runtime resolvable by ID | Yes (`sources/fixture_store.py`) | Not yet (known limitation; inline text submission is the path today) |

The separation is deliberate: the deterministic suite's byte-stable expectations stay isolated
from evolving business content, and business curation can never silently change runtime
behaviour.

## 2. Manifest schema (business package)

Each artifact entry carries: `artifact_id` (stable fixture ID), `normalized_path`,
`source_zip` + `source_path` (provenance), `document_type` (`resume`, `cover_letter`,
`candidate_metadata`, `fixture_notes`, `job_posting`, `role_profile`, `rubric`,
`scoring_guidance`, `hr_policy`, `expected_behavior_note`), `evaluation_role`, `synthetic`
(always `true`), `version`, `sha256`, and four intent fields (`copilot_usage`, `blob_usage`,
`foundry_usage`, `runtime_destination`). Package-level fields record the selected scenario,
source packages, approval gaps, and an explicit `live_configuration_status` statement that no
cloud configuration has been performed.

## 3. Validation layer

`tests/test_business_fixtures.py` is a pure file/manifest test module (no app imports, no
network): manifest↔disk agreement including sha256 recomputation, candidate completeness with
an explicit negative-test escape hatch (`cover_letter_missing: true` requires `notes.md` and
forbids a cover-letter file), junk-file and secret-pattern scans, routing-rule enforcement
(candidate documents are never Copilot knowledge), and enforcement that the rubric's approval
stays explicitly scoped to synthetic/test-only lab evaluation with
`production_hiring_approval: false`.

## 4. Intended runtime mapping (future, not built)

Per `docs/integration/business-fixture-routing.md`:

- **Blob Storage** receives per-evaluation copies of the exact document versions used, plus
  the evidence packet, council outputs, gate results, and audit record — mirroring the local
  persistence shapes already implemented under `src/hr_eval_lab/persistence/`.
- **Copilot Studio** receives only general HR policy/process documents as knowledge; never
  candidate documents; never as the source of truth for scoring (the API receives and versions
  the exact policy/rubric inputs).
- **Foundry/council runtime** consumes fixture content only through the provider seam's
  controlled evidence packets; role prompts and agent mappings are source-controlled
  separately (`config/role-agent-mapping.sample.json` shape); the request body never selects
  models, deployments, endpoints, or agent IDs.
- **Azure AI Search** is deferred entirely; policy documents are the only near-term indexing
  candidates, and candidate resumes are excluded absent scoped, access-controlled, versioned,
  human-approved design.

## 5. Curation pipeline (repeatable pattern)

Raw uploads land in gitignored `.local/incoming/<name>/` and are never committed. Curation
selects a minimal slice-relevant subset, normalizes filenames (lowercase kebab-case) and IDs,
preserves source paths and versions in the manifest, computes sha256 per file, and documents
rejections/deferrals (`rejected/README.md` + the owning slice's inventory and selection
reports). Derived artifacts (anything not verbatim from a source) are labelled with their
derivation sources and approval status inside the artifact itself.
