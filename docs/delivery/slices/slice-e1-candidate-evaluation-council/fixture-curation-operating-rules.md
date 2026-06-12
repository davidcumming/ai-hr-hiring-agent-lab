# Fixture Curation Operating Rules — slice-e1-candidate-evaluation-council

- **Status:** binding for fixture-curation work in this slice.
- **Provenance note (2026-06-11):** this artifact was created retroactively, after the first
  curation pass of `hr-test-data.zip`, by distilling the canonical vendored standards, agent
  role prompts, and skill packages listed in §1. The completed pass was then validated against
  these rules; the result is recorded in
  [`doc-validation-fixtures.md`](./doc-validation-fixtures.md) (retroactive section).
- **No-fourth-copy rule:** this file operationalizes the canonical sources for fixture
  curation only. Lifecycle, gate, and skill rules are **not** restated authoritatively here —
  the linked sources win on any conflict.

## 1. Canonical sources

Process and governance: `standards/azure-development-standards/gentech_slice_based_development_process_revised.md`.
Skill index and role table: `standards/azure-development-standards/gentech_agent_skills_usage_and_requirements.md`.
Lifecycle control flow: `standards/azure-development-standards/gentech_slice_lifecycle_orchestration_map.md`.
Role prompts: `.claude/agents/documentation-and-architecture-reconciliation-agent.md` (inventory,
current-state, validation stages), `.claude/agents/coding-agent.md` (tests), `.claude/agents/eval-design-agent.md`
(eval-relevant fixture properties). Skills: `manual-evidence-normalizer`, `current-state-reconciler`,
`documentation-consistency-validator`, `deterministic-test-author`, `source-control-config-capture`,
`implementation-deviation-capture`, `traceability-matrix-builder` (under `.claude/skills/`).
Slice truth context: `slice-spec.md` (intent), `eval-contract.md`, AGENTS.md source-of-truth hierarchy
(code/tests/approved evidence/current-state docs are truth; specs are intent).

## 2. Data-safety rules (hard, from process §23.1 + AGENTS.md + BR-010/BR-011)

1. Synthetic or de-identified sample data only; no real applicant data, PHI, or PII. Every
   curated artifact must carry an explicit synthetic declaration (package and/or artifact level).
2. Treat resume-like content with real-PII discipline regardless: never-log, metadata-first
   rows, no full text where a reference suffices in eval/metadata artifacts.
3. No secrets, credentials, connection strings, SAS tokens, or private tenant details in any
   fixture, manifest, prompt, or doc. Secret-shape scanning must be test-enforced.
4. Unclear-provenance or privacy-ambiguous files are **not curated**. If the best available
   candidate/rubric/policy artifacts are not clearly synthetic/sample-safe, stop after the
   selection report and request Product Owner approval before copying anything into `fixtures/`.
5. Deliberately risky-by-design content (prompt-injection strings, proxy signals) may be
   curated only as explicitly flagged negative-test fixtures, with the risk named in metadata,
   notes, and manifest.

## 3. Intake and extraction rules (manual-evidence-normalizer discipline)

1. Raw uploads are inspected only in a gitignored scratch path (`.local/incoming/<name>/`);
   the raw extract is never committed and `.local/` must be verified gitignored.
2. Junk is never curated: `__MACOSX/`, AppleDouble `._*`, `.DS_Store`, resource forks, empty
   files. Corrupt/unreadable files only as explicit negative-test fixtures.
3. The inventory must classify every content file with normalized-evidence fields: original
   path, inferred document type, synthetic status, completeness (matching resume/cover
   letter/metadata), slice relevance, test value, recommended action
   (select / reserve / reject / defer), and reason. Risks classified
   (Critical/High/Medium/Low); references by file path only; follow-up issue candidates listed
   but never created (human gate).

## 4. Selection rules

1. Select the minimal set serving the current slice: one position package, one versioned
   rubric package, one complete primary candidate, a small targeted secondary set (3–5),
   policy package, expected-behaviour notes. Prefer completeness and documented expected
   behaviour over volume.
2. The secondary set should cover, where available: strong/direct evidence, borderline,
   weak/insufficient evidence, a fairness/prohibited-factor trap, an injection trap, and a
   malformed/incomplete case — single-behaviour cases preferred over compound ones.
3. Materials targeting out-of-slice behaviour (import, dedupe, shortlist, interview stages,
   Copilot demos) are deferred with rationale, not curated.
4. No facts may be invented. Derived artifacts (anything not verbatim) are permitted only
   when a required input is missing from sources, must embed their derivation sources and an
   explicit approval status (`approved: false` until a human approves), and are listed as gaps.

## 5. Normalization and manifest rules (source-control-config-capture discipline)

1. Stable fixture IDs; lowercase kebab-case filenames; original source paths and versions
   preserved in provenance fields; `sha256` recorded per file.
2. The package manifest must record per artifact: source zip/path, normalized path, document
   type, evaluation role, synthetic status, version, hash, and intended runtime / council /
   Copilot / Blob / Foundry routing. Package level: package ID + version, scenario, source
   packages, approval gaps, and an explicit statement of live-configuration status.
3. The business package must not be registered as runtime hash authority
   (`fixtures/manifest.json` stays bound to the deterministic suite); runtime registration is
   a separate, deliberate change.

## 6. Routing rules (architecture constraints, council spec)

1. Candidate resumes/cover letters: runtime evaluation inputs and audit artifacts only —
   **never Copilot knowledge sources**, never broadly indexed; future per-run Blob copies.
2. Rubrics and policies: exact, versioned, hash-verified evaluation inputs delivered through
   the API/council (BR-009). Copilot knowledge may carry general HR guidance later but is
   never the authoritative scoring source.
3. Request bodies never select backend (model/deployment/endpoint/agent IDs); rigor and
   escalation configuration is server-side and source-controlled.
4. All Azure/Copilot/Foundry/Search placement is documented intent until live wiring is
   approved; docs must never claim completed cloud configuration.

## 7. Test rules (deterministic-test-author discipline)

1. Deterministic fixture-integrity tests are required: manifest parse + required fields,
   manifest↔disk existence and hash agreement, no orphan files, candidate completeness with an
   explicit negative-test escape hatch, primary-scenario completeness, junk-file scan,
   secret-pattern scan, routing-rule enforcement (candidate docs never Copilot knowledge),
   derived-artifact approval status enforcement, advisory-flag expectations present.
2. Test naming `test_<unit>_<condition>_<expected_outcome>`; no live LLM/Azure/network calls;
   the existing deterministic suite must remain green.
3. Application logic is not modified for curation unless necessary for fixture loading, small,
   local, and test-covered; otherwise record as a scoped deviation
   (implementation-deviation-capture format: required vs implemented, classification, severity,
   impact).

## 8. Documentation rules (current-state-reconciler discipline)

1. Durable current-state docs: present tense, slice-agnostic, no aspirational claims, explicit
   known-limitations section; architecture docs describe only what is built, with future
   placement clearly marked future.
2. Slice-folder reports required: inventory, selection report, routing map, validation
   summary, curation notes (including deviations and gaps), and a documentation-consistency
   validation report.
3. Validation must be performed by a **fresh** validator instance (isolated verification) and
   reported as: scope → blocking mismatches → non-blocking gaps → observations →
   recommendation (PASS / CONDITIONAL-PASS / FAIL). Blocking criteria include false claims,
   contradictions with approved decisions, unsupported claims, and slice-specific language in
   durable docs.

## 9. Human gates (recommend, never approve)

Curation work never approves: derived-rubric approval (Product Owner), residual risk, ADRs,
GitHub Issue creation, merge, deployment, or any live Azure/Copilot/Foundry configuration.
Gaps and follow-up candidates are recorded for humans; the `hr-hiring` source repo is
read-only.
