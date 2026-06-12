# Documentation Validation Report — Business Fixture Package (`fixpkg-e1-business` v1.0.0)

- **Slice:** `slice-e1-candidate-evaluation-council`
- **Stage:** 13 — Documentation validation (`documentation-consistency-validator`)
- **Date:** 2026-06-11
- **Validator:** fresh isolated-verification instance. This validator did not produce any of the
  artifacts checked below, read all documents cold, shared no session context with the curation
  or reconciliation work, and rewrote nothing — findings only.

---

## 1. Scope — files and evidence reviewed

**Fixture package (on disk, hash-verified):**

- `fixtures/business/e1-candidate-evaluation/` — full tree (35 files), `manifest.json`
  (33 artifact entries), `README.md`, `rejected/README.md`,
  `positions/senior-manager-digital-health/rubric.v1.json`.

**Slice reports:**

- `docs/delivery/slices/slice-e1-candidate-evaluation-council/test-data-inventory.md`
- `docs/delivery/slices/slice-e1-candidate-evaluation-council/fixture-selection-report.md`
- `docs/delivery/slices/slice-e1-candidate-evaluation-council/artifact-routing-map.md`
- `docs/delivery/slices/slice-e1-candidate-evaluation-council/fixture-validation-summary.md`
- `docs/delivery/slices/slice-e1-candidate-evaluation-council/fixture-curation-notes.md`

**Durable docs:**

- `docs/integration/business-fixture-routing.md`
- `docs/product-current-state/candidate-evaluation-fixtures.md`
- `docs/product-current-state/candidate-evaluation-council.md` (§18 Fixtures)
- `docs/architecture/candidate-evaluation-fixture-architecture.md`

**Implementation evidence checked directly:**

- `tests/test_business_fixtures.py` (test count + assertions), executed:
  `python3 -m pytest tests/test_business_fixtures.py -q -p no:cacheprovider`
- `src/hr_eval_lab/sources/fixture_store.py`, `.gitignore`, `fixtures/manifest.json`,
  `fixtures/positions/pos-sample-001/rubric.v1.json`,
  `fixtures/candidates/cand-sample-001/`.
- Programmatic manifest verification (Python): every `artifacts[].normalized_path` existence +
  sha256 recomputation + reverse sweep for unaccounted files.

Nothing live or networked was executed.

---

## 2. Verification results by check

| # | Check | Result |
|---|---|---|
| 1 | Curated structure: positions/ 4 files; candidates/primary/ 3 files; candidates/secondary/ 5 folders with `cand-a028-robin-kestrel` lacking `cover-letter.md` (intentional); policies/ 5 files; expected/ 2 files; `rejected/README.md`; `README.md`; `manifest.json` | **PASS** — exact match on disk |
| 2 | Manifest ↔ disk: all 33 `normalized_path`s exist; all 33 sha256 hashes recomputed and match; zero unaccounted files beyond the three documented exemptions (`README.md`, `manifest.json`, `rejected/README.md`) | **PASS** |
| 3 | Routing consistency (manifest ↔ routing map ↔ durable routing doc) | **PASS with one non-blocking gap** (NB-1 below). All 23 candidate-document manifest entries carry `copilot_usage: NO…`; all 5 policies carry `YES (later)`; rubric described as provisional/`approved: false` in manifest `approval_gaps`, routing map row + §3, durable routing doc, README, selection report, curation notes, validation summary, current-state and architecture docs |
| 4 | No claim of completed Azure/Copilot/Foundry configuration | **PASS** — every document states the opposite explicitly (manifest `live_configuration_status`, routing map header, `business-fixture-routing.md` "Implementation status", package README "Nothing here is wired to Azure", architecture doc §4 "future, not built", current-state doc §4) |
| 5 | Current-state docs vs. repo state | **PASS** — `tests/test_business_fixtures.py` has exactly 15 `def test_` functions and 15 pass; `FixtureStore` constants `POSITION_ID = "pos-sample-001"` / `CANDIDATE_REF = "cand-sample-001"` (lines 17–18) and hash-mismatch → `blocked` docstring match the docs; `.gitignore` line 58 contains `.local/`; root rubric `rub-sample-001` has 6 criteria as claimed; deterministic fixture paths exist; durable docs are present-tense and slice-agnostic (grep for "Slice N…", "this slice", "was added", "next slice" returned no hits in the three durable docs; §18 of the council doc is descriptive present tense) |
| 6 | Rejected/deferred explanation | **PASS** — `rejected/README.md` is documentation-only by design, summarizes 246 junk entries, the superseded 30-candidate pool, 8 templates/admin docs, and four deferral groups, and links to `test-data-inventory.md` + `fixture-selection-report.md`, which carry per-file dispositions |
| 7 | Gaps G-1..G-5 + rubric enforcement | **PASS** — G-1..G-5 tabulated in `fixture-selection-report.md` (gap table) and `fixture-curation-notes.md` (open-gaps table); `rubric.v1.json` carries `"approved": false`, `provisional: true`, `status: provisional_derived_fixture`, with derivation + PO-gate note; `test_rubric_is_anchored_and_explicitly_unapproved` asserts `approval.approved is False` |
| 8 | Test run | **PASS** — `15 passed, 1 warning in 0.08s` (warning is an unrelated starlette/httpx deprecation) |

---

## 3. Blocking mismatches

None found.

- No false or evidence-unsupported capability claims.
- No slice-specific language in durable current-state/architecture/integration docs.
- No aspirational text presented as current behaviour — all Azure/Copilot/Foundry/AI Search
  placements are uniformly labelled future intent.
- No contradiction with the deferred-Foundry direction
  (`adr-deferred-foundry-wiring.md`) or the synthetic-data rule (BR-011).
- Known limitations (unapproved rubric, business fixtures not FixtureStore-resolvable,
  provisional expected-behaviour notes, no Azure surface) are classified as limitations, not
  capabilities, in `candidate-evaluation-fixtures.md` §4.

---

## 4. Non-blocking gaps

| ID | Location | Gap | Recommended treatment |
|---|---|---|---|
| NB-1 | `manifest.json` artifact `rub-smdh-001` (`copilot_usage` field) vs. `artifact-routing-map.md` §2 "Rubric v1" row and `business-fixture-routing.md` routing table | The manifest field reads `"LIMITED (later) — job posting/role profile may be exposed as knowledge; rubric versions remain API-controlled"`, while both routing docs state the rubric's Copilot-knowledge answer as **NO** ("rubric versions are API-controlled, never Copilot-knowledge-driven"). Substantively aligned — all three agree rubric versions stay API-controlled, and the "LIMITED" text actually describes the job-posting/role-profile artifacts, not the rubric — but the field value on the rubric entry diverges from the documented routing answer, and no test pins the rubric's `copilot_usage` (tests cover candidates = NO and policies = YES only) | Follow-up issue candidate: set the rubric entry's `copilot_usage` to `NO — …` (or align the routing-map cell to LIMITED if that is the intent) and optionally extend `test_business_fixtures.py` to assert rubric routing. Not false today, but the divergence invites drift |

---

## 5. Observations (informational)

1. The validation layer is unusually strong for fixture work: manifest↔disk agreement including
   sha256 recomputation is itself test-asserted, so check #2 is enforced in CI, not just by this
   report.
2. The missing-cover-letter negative fixture (A028) is consistently handled at every layer:
   absent on disk, absent from the manifest, escape-hatched in tests
   (`cover_letter_missing: true` requires `notes.md` and forbids the file), and called out in
   README, routing map, and current-state docs.
3. G-5 (business fixtures not selectable by runtime fixture ID) is honestly carried as a known
   limitation in both durable docs and is consistent with `fixture_store.py` evidence; it is a
   ready-made follow-up issue once the G-2 rubric approval gate clears.
4. `manifest.json` carries a package-level `live_configuration_status` field — a good durable
   pattern; future fixture packages should replicate it.
5. The two `approval_gaps` entries in the manifest match G-1/G-2 wording in the selection
   report and curation notes verbatim in substance.

---

## 6. Recommendation

**CONDITIONAL-PASS** — advance to Stage 14 (traceability & closeout).

Rationale: zero blocking mismatches across all eight requested checks; the only finding (NB-1)
is a wording/field-value divergence between the manifest's rubric `copilot_usage` and the two
routing documents that is substantively consistent and not false, classified non-blocking per
the skill's criteria ("improvable but not false"). NB-1 becomes a follow-up issue candidate
(human gate applies to issue creation).

**Follow-up issue candidates:**

1. Align `rub-smdh-001` `copilot_usage` wording with the routing map / durable routing doc and
   add a test assertion for rubric routing (NB-1).
2. (Already documented as G-5) register business fixture IDs in the runtime `FixtureStore`
   after PO rubric approval.

**Handoff:** documentation is cleared for closeout; pass this report path, NB-1, and the issue
candidates to `traceability-matrix-builder` / `closeout-package-builder`.

---

## Post-validation resolution (2026-06-11, curation agent)

NB-1 resolved after validation: `manifest.json` entries `rub-smdh-001` and
`rub-smdh-001:scoring_guidance` changed from `copilot_usage: "LIMITED (later)…"` to explicit
`NO`, matching the routing map and `business-fixture-routing.md` (rubric versions are
API-controlled, never Copilot knowledge). `tests/test_business_fixtures.py` re-run: 15 passed.
G-5 (runtime FixtureStore registration) remains an open follow-up candidate, human gate applies.

---

## Retroactive operating-rules validation (2026-06-11)

The binding rules artifact [`fixture-curation-operating-rules.md`](./fixture-curation-operating-rules.md)
did not exist when the curation pass ran; it was created retroactively from the canonical
standards, role prompts, and skills, and the completed pass was then validated against it.

**Scope:** all curation outputs (inventory, selection report, curated package + manifest,
routing maps, tests, durable docs, prior validation report) checked against rules §2–§9.

**Checks and results:**

| Rule area | Check | Result |
|---|---|---|
| §2 data safety | Synthetic declarations present (package READMEs, manifest `synthetic_notice`, per-artifact `synthetic: true`); risky-by-design fixtures (A016/A018) explicitly flagged; secret-pattern scan test passes | PASS |
| §3 intake | Raw extract only in `.local/` (git check-ignore confirms ignored; 0 tracked entries); 0 junk files in curated package; inventory carries normalized-evidence fields incl. risk classification §8 and follow-up candidates §9 | PASS |
| §4 selection | Minimal set (1 position, 1 rubric, 1 primary, 5 single-behaviour secondary cases, 5 policies); out-of-slice material deferred with rationale; only derived artifact (`rub-smdh-001`) embeds derivation sources + `approved: false`, listed as gap G-2 | PASS |
| §5 manifest | Manifest↔disk existence + sha256 agreement test-verified; required per-artifact and package fields present; business package not registered as runtime hash authority | PASS |
| §6 routing | 0 candidate-doc Copilot violations (re-checked programmatically); rubric `copilot_usage: NO` (post-NB-1 fix); `live_configuration_status` explicit; completed-config-claim grep across all new/updated docs found only a compliant negation sentence | PASS |
| §7 tests | 15 deterministic fixture tests; `tests/test_business_fixtures.py` 15 passed; full suite re-run 162 passed / 0 failed (exit 0); no app logic modified — FixtureStore non-registration recorded as scoped deviation | PASS |
| §8 docs | Durable docs present-tense/slice-agnostic with known-limitations sections; all required slice reports exist; fresh-validator consistency report exists (CONDITIONAL-PASS → NB-1 resolved) | PASS |
| §9 human gates | No issues created, no merge, no cloud configuration, no rubric approval claimed; PO gate G-2 stated everywhere the rubric appears | PASS |

**Validation result: PASS.** The existing curation pass is **accepted** under the
retroactively-created operating rules. No blocking mismatch; no re-curation required.
Unresolved (by design, human-gated): G-2 rubric approval, G-5 runtime fixture-ID
registration, deferred ADR BQ-001 and region approval BQ-005 before live wiring.

---

## Status update (2026-06-12): G-2 resolved by PO decision

PO decision `po-2026-06-12-rubric-approval` (recorded in `fixture-curation-notes.md`):
`rub-smdh-001` v1 is approved as a **synthetic/test-only rubric for Slice E1 lab testing**;
the approval does not imply production hiring approval. The "unresolved" G-2 references in the
sections above are historical. Updated accordingly: rubric `approval` block, package manifest
(`po_decisions`, `approval_gaps`, refreshed sha256 for the three touched artifacts), package
README/scoring-guidance/expected notes, durable docs, routing maps, traceability, and the
renamed test `test_rubric_is_anchored_and_approval_is_lab_scoped_only`. G-5 (runtime
`FixtureStore` registration of business fixture IDs) remains the open implementation
follow-up. No application logic changed; no cloud configuration performed.
