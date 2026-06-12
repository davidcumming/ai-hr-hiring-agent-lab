# Fixture Validation Summary — `fixpkg-e1-business` v1.0.0

- **Date:** 2026-06-11
- **Role/skills:** coding-agent role; `deterministic-test-author` + `source-control-config-capture` conventions
- **Scope:** validation of the curated business fixture package only. No application logic was modified. No live Azure/Foundry/Copilot calls were made anywhere in this work.

## Tests added

`tests/test_business_fixtures.py` — 15 deterministic fixture-integrity tests, pure file/manifest checks (no app imports, no model calls):

| Test | Covers |
|---|---|
| `test_manifest_parses_with_required_package_fields` | Manifest parses; package ID/version/scenario/synthetic notice present |
| `test_manifest_artifacts_carry_required_fields` | Every artifact has source path, normalized path, type, role, sha256, routing fields; `synthetic: true` (BR-011) |
| `test_all_manifest_files_exist_with_matching_hashes` | All 33 manifest entries exist on disk; sha256 recomputation matches (BR-009 discipline) |
| `test_no_package_files_missing_from_manifest` | No orphan files in the package outside manifest + documented READMEs |
| `test_every_candidate_has_metadata_and_resume` | All 6 candidates complete |
| `test_cover_letter_present_unless_explicit_negative_test` | Cover letter required unless `cover_letter_missing: true` (A028), which must then have `notes.md` and no cover-letter file |
| `test_primary_scenario_is_complete` | Job posting + role profile + rubric + scoring guidance + 5 policies + primary resume/cover letter |
| `test_candidate_documents_are_loadable_nonempty_text` | Loadability floor for inline submission (FR-001); no unreadable-simulation content curated |
| `test_rubric_is_anchored_and_approval_is_lab_scoped_only` (named `…_explicitly_unapproved` until the 2026-06-12 PO approval) | 6 criteria, anchored 1–5 scale, required fields per criterion; **approval scope enforced**: `approved: true` (PO, 2026-06-12), `approval_scope` synthetic/test-only, `production_hiring_approval: false` (G-2 resolved) |
| `test_no_junk_files_in_curated_package` | No `.DS_Store`, `._*` AppleDouble, `__MACOSX` |
| `test_no_secret_looking_values_in_fixtures` | No API-key/SAS/connection-string/private-key/bearer-token shapes |
| `test_candidate_documents_never_marked_as_copilot_knowledge` | Routing rule: resume/cover-letter/metadata/notes all `copilot_usage: NO` |
| `test_policy_documents_categorized_and_routed_as_knowledge_candidates` | 5 policies typed `hr_policy`, Copilot-knowledge candidates, blob-per-run YES |
| `test_no_artifact_claims_live_configuration` | Manifest states no Azure/Copilot/Foundry configuration was performed |
| `test_expected_behavior_notes_carry_mandatory_flag_expectations` | `human_review_required` + `decision_support_only` + provisional labelling present (BR-007) |

## Commands run and results

| Command | Result |
|---|---|
| `python3 -m pytest tests/test_business_fixtures.py -q` | **15 passed** |
| `python3 -m pytest tests/ --ignore=tests/live_evals -q` (full deterministic suite) | **162 passed, 0 failed** (exit 0) — existing DT-001…DT-018 suite unaffected |
| Manifest JSON validation (`json.load` at generation + in tests) | valid |
| File-existence + hash checks | covered by tests above, all pass |

Note: the sandbox environment required installing test dependencies (`pytest`, `fastapi`, `pydantic`, `httpx`, `openapi-spec-validator`) — pre-existing repo dependencies, not new ones.

## Council-runner loadability finding

The runtime `FixtureStore` (`src/hr_eval_lab/sources/fixture_store.py`) is intentionally
hard-bound to the deterministic-suite fixtures (`cand-sample-001`, `pos-sample-001`,
`rub-sample-001`) and `fixtures/manifest.json`. The business package is therefore **not yet
selectable by fixture ID through the API/CLI runner**. This is deliberate: registering new
runtime fixtures would change validated application behaviour (DT-007 unknown-candidate
mapping) and is out of bounds for a curation task.

- **Available path today:** business candidate documents can be exercised end-to-end via inline
  `resume_text` + `cover_letter_text` submission (FR-001), which the facade already supports.
- **Follow-up (small, post-rubric-approval):** register business fixture IDs in the runtime
  store / root manifest so they are selectable by reference. Recorded as a gap in
  `fixture-curation-notes.md`; rubric PO approval gates this anyway.

## Outcome

**PASS** — package integrity, completeness, junk/secret hygiene, routing classification, and
advisory-flag expectations all validated deterministically; existing suite unaffected.
