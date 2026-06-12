# Business Fixture Package: e1-candidate-evaluation (`fixpkg-e1-business` v1.0.0)

Curated synthetic business fixtures for `slice-e1-candidate-evaluation-council`, selected from
the uploaded `hr-test-data.zip` on 2026-06-11. This package **supplements** — and does not
replace — the slice's bound deterministic fixtures (`fixtures/candidates/cand-sample-001`,
`fixtures/positions/pos-sample-001`), which the deterministic suite DT-001…DT-018 depends on.

**SYNTHETIC DATA ONLY (BR-011).** Every document is fictional sample content; source packages
declare this explicitly (fictional names/employers/schools, `.example` contact domains, 555
numbers). No real applicant data is present or permitted. No secrets.

**Nothing here is wired to Azure.** No Blob Storage upload, Copilot Studio knowledge
configuration, Foundry agent setup, or Azure AI Search indexing has been performed. Intended
future routing per artifact is recorded in `manifest.json` and
`docs/integration/business-fixture-routing.md`.

## Scenario

One position — **Senior Manager, Digital Health Strategy** — with one provisional rubric, one
evidence-rich primary candidate, and five targeted secondary cases:

| Fixture | What it is |
|---|---|
| `positions/senior-manager-digital-health/` | Job posting (assembled, gap G-1), role profile (verbatim), **derived rubric `rub-smdh-001` v1 — PO-approved 2026-06-12 for synthetic/test-only Slice E1 lab evaluation (not production hiring approval; gap G-2 resolved)**, scoring guidance |
| `candidates/primary/` | `cand-a001-nadia-belcourt` — strong-fit, clean, evidence-rich end-to-end candidate |
| `candidates/secondary/cand-a013-bianca-rowan/` | Borderline / mixed-evidence case |
| `candidates/secondary/cand-a016-luca-fenwick/` | ⚠ Proxy-signal fairness trap (deliberately risky content) |
| `candidates/secondary/cand-a018-jonah-pierce/` | ⚠ Prompt-injection trap (deliberately risky content) |
| `candidates/secondary/cand-a020-arman-pike/` | Weak-fit / insufficient-evidence case |
| `candidates/secondary/cand-a028-robin-kestrel/` | Missing-cover-letter case — **`cover-letter.md` intentionally absent** (explicit negative-test fixture) |
| `policies/` | Five HR policy/knowledge documents (verbatim): AI-in-recruitment guidance, fairness & assessment principles, screening rubric standard, recruitment process overview, roles & responsibilities |
| `expected/` | **Provisional** expected-behaviour notes (source-note restatements labelled *[source]*, eval-contract extrapolations labelled *[provisional]*) |
| `rejected/` | Documentation-only record of rejected/deferred source material |

## Conventions

- Stable fixture IDs: `pos-smdh-001`, `rub-smdh-001`, `cand-a###-firstname-lastname` (source
  applicant IDs preserved inside the ID).
- Filenames normalized to lowercase kebab-case (`resume.md`, `cover-letter.md`,
  `candidate-metadata.json`).
- `candidate-metadata.json` = source `metadata.json` verbatim **plus** added `fixture_id`,
  `synthetic`, and `provenance` fields (noted inside each file).
- `manifest.json` records, per artifact: source zip path, normalized path, document type,
  evaluation role, synthetic status, `sha256`, version, and intended runtime / council /
  Copilot / Blob / Foundry usage.
- Candidate documents are **never** Copilot knowledge sources; they are runtime evaluation
  inputs and audit artifacts only.
- Raw zip extract lives in gitignored `.local/incoming/hr-test-data/` and is never committed;
  no `.DS_Store` / `__MACOSX` content was copied.

## How this package is used

- **Now (local):** deterministic fixture-integrity tests (`tests/test_business_fixtures.py`)
  validate the manifest, file existence, hashes, junk/secret absence, and routing rules. The
  package is selectable sample data for local council runs via the facade API / CLI runner.
- **Tomorrow (live smoke tests):** known sample inputs for first live Azure lab testing —
  cleared by the PO rubric approval above (synthetic/test-only scope).
- **Later:** per-run copies to Blob Storage, policy docs as Copilot knowledge, council/Foundry
  evidence inputs, optional policy retrieval indexing — all deferred, see the routing map.
