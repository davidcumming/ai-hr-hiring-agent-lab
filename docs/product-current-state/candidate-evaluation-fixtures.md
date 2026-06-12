# Candidate Evaluation Fixtures — Current State

Present-tense reference for the synthetic fixture data that exists in this repo and how it is
used. Sources: `fixtures/`, `tests/test_business_fixtures.py`, the deterministic suite, and the
fixture package manifests. Companion architecture view:
[`docs/architecture/candidate-evaluation-fixture-architecture.md`](../architecture/candidate-evaluation-fixture-architecture.md).
Routing rules: [`docs/integration/business-fixture-routing.md`](../integration/business-fixture-routing.md).

## 1. What exists

Two synthetic fixture packages are source-controlled. Everything is fictional sample data; the
repo permits no real applicant data and no secrets.

### 1.1 Deterministic-suite fixtures (`fixtures/`, root manifest)

One synthetic position (`pos-sample-001`: job description + approved-fixture rubric
`rub-sample-001` v1, 6 anchored criteria) and one synthetic candidate (`cand-sample-001`,
resume + cover letter), pinned by `fixtures/manifest.json` (artifact id, version, path,
sha256, provenance, `synthetic: true`). This manifest is the **runtime hash authority**: the
evaluation service resolves and hash-verifies these artifacts on every run
(`src/hr_eval_lab/sources/fixture_store.py`); a mismatch yields envelope status `blocked`.
The deterministic test suite is bound to this package.

### 1.2 Business fixture package (`fixtures/business/e1-candidate-evaluation/`, `fixpkg-e1-business` v1.0.0)

A curated business scenario for the position **Senior Manager, Digital Health Strategy**,
selected from an uploaded synthetic HR test-data zip (curation record:
`docs/delivery/slices/slice-e1-candidate-evaluation-council/fixture-selection-report.md`):

- **Position package:** assembled job posting, verbatim role profile, scoring guidance, and a
  **derived rubric `rub-smdh-001` v1, PO-approved (2026-06-12) for synthetic/test-only Slice
  E1 lab evaluation** — the approval is recorded in the rubric's `approval` block
  (`production_hiring_approval: false`) and never implies production hiring approval.
- **Candidates:** one evidence-rich primary candidate (`cand-a001-nadia-belcourt`) and five
  targeted secondary cases — borderline evidence, weak fit, a proxy-signal fairness trap, a
  prompt-injection trap, and a missing-cover-letter case (the cover letter file is
  intentionally absent and the manifest/notes say so).
- **Policies:** five verbatim HR policy/knowledge documents (AI-in-recruitment guidance,
  fairness and assessment principles, screening rubric standard, recruitment process overview,
  roles and responsibilities).
- **Expected-behaviour notes:** provisional, with source-derived statements labelled
  *[source]* and eval-contract extrapolations labelled *[provisional]*.
- **Package manifest** (`manifest.json`): per artifact — source zip path, normalized repo
  path, document type, evaluation role, `sha256`, version, synthetic status, and intended
  runtime/council/Copilot/Blob/Foundry routing.

## 2. How fixtures are used today

- The deterministic suite (DT-001…DT-018) runs the council pipeline against the
  deterministic-suite fixtures.
- `tests/test_business_fixtures.py` (15 tests) validates the business package: manifest/file/
  hash agreement, candidate completeness (cover letter required unless explicitly a
  negative-test fixture), primary-scenario completeness, no junk files, no secret-shaped
  values, candidate documents never marked as Copilot knowledge, policy categorization, the
  lab-only scope of the rubric approval (`production_hiring_approval: false` enforced), and advisory-flag expectations in the
  expected-behaviour notes.
- Business candidate documents are usable end-to-end **today** via inline
  `resume_text`/`cover_letter_text` submission through the facade API. They are **not yet
  selectable by fixture ID**: the runtime `FixtureStore` is bound to the deterministic-suite
  fixtures (known limitation, §4).

## 3. What is safe to commit, and why

All fixture content is synthetic by construction (fictional names/employers/schools,
`.example` contact domains, 555 numbers) and declared synthetic in both package manifests.
Two fixtures intentionally contain risky-by-design content for safety testing — a
prompt-injection string and proxy-signal details — and are flagged as such in their metadata,
notes, and manifest entries. Tests assert the absence of junk files and secret-shaped values.

## 4. Known limitations

- The business package's rubric is approved for **synthetic/test-only lab evaluation** (PO
  decision 2026-06-12); it carries no production hiring approval and must not be presented
  as one.
- Business fixtures are not registered in the runtime `FixtureStore`; selection by fixture ID
  is a small follow-up change (inline submission is the available path).
- Expected-behaviour notes for the business package extrapolate council-output expectations
  beyond the source material and are labelled provisional pending human validation.
- No Azure surface exists for any fixture: nothing has been uploaded to Blob Storage, exposed
  to Copilot Studio as knowledge, wired to Foundry, or indexed for retrieval. All such
  placements are documented intent only (`docs/integration/business-fixture-routing.md`).
