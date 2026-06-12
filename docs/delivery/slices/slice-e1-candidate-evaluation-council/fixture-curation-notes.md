# Fixture Curation Notes — `fixpkg-e1-business` v1.0.0

> **Operating rules:** this curation pass is governed by
> [`fixture-curation-operating-rules.md`](./fixture-curation-operating-rules.md) (created
> retroactively after the pass; the pass was validated against it and **accepted** — see the
> retroactive section of [`doc-validation-fixtures.md`](./doc-validation-fixtures.md)).

- **Date:** 2026-06-11
- **Activity:** curation of the uploaded `hr-test-data.zip` into the source-controlled business
  fixture package `fixtures/business/e1-candidate-evaluation/`.
- **Companion records:** [`test-data-inventory.md`](./test-data-inventory.md),
  [`fixture-selection-report.md`](./fixture-selection-report.md),
  [`artifact-routing-map.md`](./artifact-routing-map.md),
  [`fixture-validation-summary.md`](./fixture-validation-summary.md).

## Process followed

1. Zip extracted to gitignored `.local/incoming/hr-test-data/` (new `.gitignore` entry for
   `.local/`); raw extract never committed.
2. Full inventory and classification (364 entries → 159 content files, 246 junk excluded).
3. Minimal selection for the slice scenario; selection criteria and rejection/deferral
   rationale recorded per file.
4. Normalization: lowercase kebab-case filenames, stable fixture IDs, provenance + sha256 in
   the package manifest, source `metadata.json` preserved verbatim with added
   `fixture_id`/`synthetic`/`provenance` fields.
5. Deterministic validation: 15 new tests; full suite green (162 passed).
6. Durable docs updated (current-state, architecture, integration routing).

## Curation decisions worth remembering

- **Two-manifest design kept.** The business package has its own manifest and is *not*
  registered in `fixtures/manifest.json`, because the root manifest is the runtime hash
  authority bound to the deterministic suite. Registering business fixtures at runtime is a
  deliberate, small follow-up change — not a side effect of curation.
- **Derived rubric is the only non-verbatim content artifact.** `rub-smdh-001` v1 was derived
  because the zip contains no completed rubric (gap G-2). Derivation sources and the approval
  status are embedded in the artifact and enforced by test (initially `approved: false`;
  PO-approved 2026-06-12 with synthetic/test-only scope — see the PO decision record below).
- **Compound edge cases deferred.** A025 (missing cover letter + injection), duplicates
  (A011/A026), ambiguous matches (A027/A029), and the unreadable file (A030) were deferred:
  they test applicant-import behaviour that this slice does not implement, and compound cases
  blur first-live-test signals.
- **`rejected/` is documentation-only.** No rejected content is stored in the repo.

## Deviations (implementation-deviation-capture format)

| Required (task brief) | Implemented | Classification | Severity | Impact |
|---|---|---|---|---|
| Fixture structure with `policies/hiring-policy.md` and `policies/human-review-and-decision-authority.md` | Five policy files named for their actual sources; no standalone hiring-policy or human-review doc exists in the zip (gaps G-3) | interpretation-applied | Low | Decision-authority content is covered by roles-and-responsibilities §8/§10 + AI-guidance §5; creating placeholder policies would have invented unsourced policy text |
| "Fixture package can be loaded by existing local council runner" | Fixture-level loadability tested; runner-level loading by fixture ID not implemented (runtime `FixtureStore` bound to `cand-sample-001` by design) | scope-reduced | Medium | Business content runs via inline text submission (FR-001); ID-based selection is a small follow-up gated by rubric approval |
| `expected/` from existing expected-results material | Authored provisional notes from phase-6.1 review notes/metadata; `Demo-Expected-Results-Guide.md` not used (covers deferred candidates only) | interpretation-applied | Low | Notes are explicitly provisional and labelled by sourcing |

## Gaps and follow-up candidates (recommended, not created — human gates respected)

| ID | Gap / follow-up | Suggested owner action |
|---|---|---|
| G-1 | No finished job posting in source zip; `job-posting.md` assembled from hiring package §2–4 | Accept assembled fixture or supply a real sample posting |
| G-2 | ~~Rubric `rub-smdh-001` unapproved~~ **RESOLVED 2026-06-12** by PO decision `po-2026-06-12-rubric-approval` (see below) | None — decision recorded in rubric `approval` block, manifest, and docs |
| G-3 | No standalone hiring-policy / human-review-authority docs | Accept curated substitutes or author policy docs in the source documentation repo |
| G-4 | Expected council-output behaviour is provisional | PO validates notes against first real outputs (AC-019 analogue) |
| G-5 | Business fixtures not selectable by runtime fixture ID — **remains the open implementation follow-up** (G-2 no longer blocks it) | Register curated business fixture IDs in the runtime `FixtureStore` so the app/API can select the package by ID instead of inline-only submission; small change + tests |
| — | Import-slice fixture set (duplicates/ambiguous/unreadable) ready in reserve | Future applicant-import slice |
| — | Copilot demo package (standouts + scenarios + prompt pack) deferred | Future Copilot Studio slice |

## PO decision record — rubric approval (2026-06-12)

| Field | Value |
|---|---|
| Decision ID | `po-2026-06-12-rubric-approval` |
| Date | 2026-06-12 |
| Decider | Product Owner (human gate) |
| Decision | Approve rubric `rub-smdh-001` v1 as a **synthetic/test-only approved rubric for Slice E1 lab testing** |
| Scope limit | Approval is limited to synthetic fixture testing; it does **not** imply production hiring approval |
| Resolves | Gap G-2 (no approved role-specific rubric) |
| Recorded in | `rubric.v1.json` `approval` block (`approved: true`, `approval_scope`, `production_hiring_approval: false`); package `manifest.json` (`po_decisions`, updated `approval_gaps`); durable docs (current-state, architecture, routing); test `test_rubric_is_anchored_and_approval_is_lab_scoped_only` |
| Explicitly unchanged | G-5 runtime `FixtureStore` registration (implementation follow-up); no application logic changed; no Azure/Foundry/Copilot setup performed |

Fixture curation remains **complete and accepted** (see retroactive validation in
`doc-validation-fixtures.md`).

## Boundaries respected

Synthetic data only; no real applicant data; no secrets committed; no Azure resources created;
no live Foundry/model calls; no deployment or uploads; no Copilot Studio configuration; no
GitHub issues created; no merge performed; `hr-hiring` source repo untouched; no junk files
curated; future Azure/Copilot/Foundry placement everywhere documented as intent, not fact.
