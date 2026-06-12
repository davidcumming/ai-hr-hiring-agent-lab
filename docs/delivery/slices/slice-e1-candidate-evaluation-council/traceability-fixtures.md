# Traceability — Business Fixture Package (`fixpkg-e1-business` v1.0.0)

- **Date:** 2026-06-11
- **Role/skill:** traceability-and-closeout-agent role, `traceability-matrix-builder` conventions
- **Scope:** fixture artifacts only. This is **not** full slice closeout: no DoD run, no merge-readiness recommendation, no residual-risk acceptance — all remain human-gated.
- Coverage status vocabulary: Covered / Partial / Untested / Deferred / Untestable.

## 1. Fixture artifacts → requirements, tests, future evals

| Fixture artifact | Slice criterion / contract expectation | Local test evidence | Future live test (deferred) | Coverage |
|---|---|---|---|---|
| Primary candidate `cand-a001-nadia-belcourt` (resume, cover letter, metadata) | AC-001/AC-002-style happy path with realistic business content; AC-019 plausibility review input | `test_business_fixtures.py` (existence, hashes, completeness, loadability); inline-submission path exercised by existing DT suite contract (DT-001 uses `cand-sample-001`) | LE-001 (strong-fit live council run) | Covered (fixture integrity) / Deferred (live behaviour) |
| `cand-a013-bianca-rowan` (borderline) | AB-005 ambiguity handling; eval contract §10.5 | fixture-integrity tests | LE-002 (weak/borderline, moderated confidence) | Covered / Deferred |
| `cand-a020-arman-pike` (weak fit) | BR-013 missing evidence never invented; UFM-009 | fixture-integrity tests | LE-002 / LE-005 family | Covered / Deferred |
| `cand-a016-luca-fenwick` (proxy-signal trap) | BR-008 prohibited factors; AB-007; UFM-001 (blocking) | fixture-integrity tests incl. risky-content flagging in metadata/notes | LE-003 (fairness trap, zero-critical threshold) | Covered / Deferred |
| `cand-a018-jonah-pierce` (injection trap) | BR-012; AB-006; UFM-004 (blocking); DT-012 analogue with business content | fixture-integrity tests; injection string verified present and flagged in metadata/notes | LE-004 (injection trap, zero instruction-following) | Covered / Deferred |
| `cand-a028-robin-kestrel` (missing cover letter) | BR-013; missing-required-evidence escalation trigger (FR-011); UFM-003/009 | `test_cover_letter_present_unless_explicit_negative_test` (negative-test contract enforced) | LE-005 (missing-document scenario) | Covered / Deferred |
| `rub-smdh-001` v1 (derived rubric) | FR-007 anchored criterion-level scoring; BR-009 versioned/hashed sources | `test_rubric_is_anchored_and_approval_is_lab_scoped_only`; hash pinned in manifest | Live scoring runs (G-2 resolved 2026-06-12: PO-approved, synthetic/test-only lab scope, `production_hiring_approval: false`) | Covered (fixture + approval record) / Deferred (live behaviour) |
| Job posting / role profile / scoring guidance | FR-005 evidence-before-judgment source documents | existence + hash tests | Live evidence-packet construction | Covered / Deferred |
| Policy package (5 docs) | BR-007 advisory-only grounding; BR-008 fairness grounding; policy packet versioning rule (routing map §3) | categorization + routing tests (`hr_policy`, blob YES, Copilot YES-later); candidate-docs-never-Copilot test | Copilot knowledge configuration + policy-grounded live runs | Covered / Deferred |
| Expected-behaviour notes (2) | AC-019 human plausibility review aid; BR-007 flags | `test_expected_behavior_notes_carry_mandatory_flag_expectations` | PO validation against first real outputs (G-4) | Partial (provisional content) |
| Package manifest | BR-009 hash discipline; BR-011 synthetic-only; routing rules | manifest/hash/junk/secret/routing test battery (15 tests) | Hash re-verification at future Blob upload | Covered |

## 2. Deferred gaps → future work

| Gap | Traceability target | Status |
|---|---|---|
| G-2 rubric approval | AC-019-style PO review; live-wiring precondition | **Resolved 2026-06-12** — PO decision `po-2026-06-12-rubric-approval` (synthetic/test-only lab scope; not production hiring approval) |
| G-5 runtime FixtureStore registration | FR-001 fixture-reference submission for business IDs | Deferred — open implementation follow-up (no longer blocked by G-2) |
| Import edge cases (A011/A025/A026/A027/A029/A030, pool edge files) | Future applicant-import slice requirements | Deferred — reserved in source zip, documented in inventory |
| Copilot demo package (standouts + scenarios) | Future Copilot Studio slice | Deferred |
| LE-001…LE-006 live evals | Eval contract §12 (pre-drafted; not executable this slice) | Deferred with recorded rationale (mock backend) |

## 3. Orphan check

No orphan fixtures: every manifest artifact row in §1 traces to at least one slice requirement,
eval-contract expectation, or documented deferred gap. No GitHub Issues were created
(human-gated); follow-up candidates are listed in `fixture-curation-notes.md` and
`doc-validation-fixtures.md`.
