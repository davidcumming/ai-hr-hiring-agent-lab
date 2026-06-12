# Artifact Routing Map — Business Fixture Package (`fixpkg-e1-business` v1.0.0)

- **Slice:** `slice-e1-candidate-evaluation-council`
- **Date:** 2026-06-11
- **Status of all "later Azure" columns: INTENDED FUTURE PLACEMENT ONLY.** No Azure resources
  exist for this work; no Blob upload, Copilot Studio configuration, Foundry agent setup, or
  Azure AI Search indexing has been performed. Live wiring is gated by the deferred backend ADR
  (BQ-001) and region approval (BQ-005). The PO rubric-approval gate (gap G-2) was **resolved
  2026-06-12**: `rub-smdh-001` v1 is approved for synthetic/test-only Slice E1 lab evaluation
  (not a production hiring approval).
- Durable, slice-agnostic version of the routing rules: [`docs/integration/business-fixture-routing.md`](../../../integration/business-fixture-routing.md).

## 1. Routing categories (this slice's application of them)

1. **Source-controlled repo fixture** — everything in `fixtures/business/e1-candidate-evaluation/`: repeatable local tests, deterministic CI, known sample data for live smoke tests, reproducible demo package.
2. **Runtime Blob Storage (later)** — per-evaluation copies of submitted resume/cover letter/job/rubric/policy documents, evidence packet, council role outputs, synthesis, gate results, provider metadata, human-review block, final audit record. Candidate documents are runtime evaluation inputs and audit artifacts — never broad knowledge sources.
3. **Copilot Studio knowledge (later)** — general HR process/AI-guidance/fairness documents only. Never the sole source of truth for scoring: the evaluation API/council receives and versions the exact policy/rubric documents used for any decision-support evaluation.
4. **Evaluation API request payload / fixture selector** — fixture IDs (`cand-…`, `pos-smdh-001`), rubric version (`rub-smdh-001` v1), policy package ID (`fixpkg-e1-business@1.0.0`), advisory requested rigor, correlation ID, idempotency key. The request body never chooses Foundry model, deployment, endpoint, or agent IDs (BR-002 / §15 constraints).
5. **Foundry / council runtime (later)** — role prompts and agent instructions (source-controlled in repo, not in this package), provider/agent mapping (`config/role-agent-mapping.sample.json`), model calls against evidence packets. No secrets or environment-specific endpoints in prompts or fixtures.
6. **Azure AI Search / retrieval (deferred)** — possible later indexing of policy/reference docs and perhaps job/rubric docs. No candidate-resume indexing unless scoped, access-controlled, versioned, and human-approved. Entirely future/deferred.

## 2. Per-artifact routing

| Artifact | Repo path (under `fixtures/business/e1-candidate-evaluation/`) | Type | Current-slice use | Later Azure destination | Copilot knowledge? | Blob Storage? | Foundry/council? | AI Search? | Notes / risks |
|---|---|---|---|---|---|---|---|---|---|
| Job posting | `positions/senior-manager-digital-health/job-posting.md` | job_posting | Position context for local runs + tests | Blob copy per run | LIMITED later — postings are reasonable general knowledge | YES — exact version per run | YES later — position context in evidence packet | deferred — maybe | Assembled fixture (gap G-1); verbatim from hiring package §2–4 |
| Role profile | `positions/…/role-profile.md` | role_profile | Position context; rubric derivation source | Blob copy per run | LIMITED later | YES | YES later | deferred — maybe | Verbatim |
| Rubric v1 | `positions/…/rubric.v1.json` | rubric | Scoring rubric for local runs/tests | Blob copy per run (versioned + hashed, BR-009) | **NO** — rubric versions are API-controlled, never Copilot-knowledge-driven | YES | YES later — criteria/anchors drive council scoring | deferred — only if versioned/scoped | **PO-approved 2026-06-12, synthetic/test-only lab scope (G-2 resolved); `production_hiring_approval: false`** |
| Scoring guidance | `positions/…/scoring-guidance.md` | scoring_guidance | Reviewer/test reference | Blob copy per run | NO (policy version of same content routes via policies/) | YES | YES later (auditor grounding) | deferred | Verbatim extract + labelled derivation commentary |
| Primary candidate (A001) resume + cover letter | `candidates/primary/` | resume / cover_letter | Happy-path live-smoke input; evidence-rich sample | Per-evaluation Blob copy (input + audit artifact) | **NO — candidate docs are never Copilot knowledge** | YES — per-run copies | YES later — evidence packet content via provider seam | **NO** (candidate indexing requires scoping + approval; not planned) | Clean, strong-fit |
| A013 borderline | `candidates/secondary/cand-a013-bianca-rowan/` | resume / cover_letter | Moderated-confidence case | same as primary | NO | YES | YES later | NO | |
| A016 fairness trap | `candidates/secondary/cand-a016-luca-fenwick/` | resume / cover_letter | Proxy-signal fairness test (BR-008/AB-007) | same | NO | YES | YES later (LE-003 analogue) | NO | ⚠ deliberately risky content, flagged in metadata/notes |
| A018 injection trap | `candidates/secondary/cand-a018-jonah-pierce/` | resume / cover_letter | Injection-resistance test (BR-012/AB-006/DT-012) | same | NO | YES | YES later (LE-004 analogue) | NO | ⚠ contains instruction-like string; data, never instructions |
| A020 weak fit | `candidates/secondary/cand-a020-arman-pike/` | resume / cover_letter | Missing-evidence/low-score case (BR-013) | same | NO | YES | YES later | NO | |
| A028 missing cover letter | `candidates/secondary/cand-a028-robin-kestrel/` | resume (cover letter intentionally absent) | Missing-document path (LE-005 analogue) | same | NO | YES | YES later | NO | Explicit negative-test fixture |
| Candidate metadata (×6) | `candidates/**/candidate-metadata.json` | candidate_metadata | Fixture selection + expected-behaviour reference | repo only | NO | NO — not an evaluation input | NO | NO | Test/QA artifact, not council evidence |
| Secondary notes (×5) | `candidates/secondary/*/notes.md` | fixture_notes | Test-design documentation | repo only | NO | NO | NO | NO | |
| AI-in-recruitment guidance | `policies/ai-in-recruitment-guidance.md` | hr_policy | Policy packet for local runs; grounds BR-007 flags | Blob copy per run + knowledge source | **YES later** — general AI-use guidance | YES | YES later — fairness/policy auditor grounding | deferred — YES candidate | Never sole scoring truth — API receives exact versions |
| Fairness & assessment principles | `policies/fairness-and-assessment-principles.md` | hr_policy | Grounds BR-008 prohibited factors | same | YES later | YES | YES later | deferred — YES candidate | same |
| Screening rubric standard | `policies/screening-rubric-standard.md` | hr_policy | Rubric-use rules; BR-013 absence-of-evidence rule | same | YES later | YES | YES later | deferred — YES candidate | same |
| Recruitment process overview | `policies/recruitment-process-overview.md` | hr_policy | Process context; general agent knowledge | same | YES later | YES | contextual only | deferred — YES candidate | same |
| Roles & responsibilities | `policies/recruitment-roles-and-responsibilities.md` | hr_policy | Decision-rights grounding (G-3 substitute) | same | YES later | YES | YES later | deferred — YES candidate | same |
| Expected-behaviour notes (×2) | `expected/` | expected_behavior_note | Test/QA expectations; PO validation aid | repo only | NO | NO | NO (may seed future eval datasets) | NO | PROVISIONAL (G-4) |
| Manifest | `manifest.json` | manifest | Fixture integrity tests; provenance; routing record | repo only (hashes may be checked at upload time later) | NO | NO | NO | NO | |
| README / rejected README | `README.md`, `rejected/README.md` | documentation | Package orientation; rejection record | repo only | NO | NO | NO | NO | |

## 3. Cross-cutting rules

- **Candidate documents are never Copilot knowledge sources** — they are per-evaluation inputs and audit artifacts (manifest enforces `copilot_usage: NO`; test-asserted).
- **Exact-version rule (BR-009):** whatever lands in Blob per run must be the hash-verified versions recorded in the manifest/audit record; Copilot knowledge never substitutes for the versioned policy/rubric inputs the API receives.
- **No secrets / no environment endpoints** in any fixture or prompt file (test-asserted for fixtures).
- **Request body never selects backend** (model/deployment/endpoint/agent IDs are server-side config: `config/azure.env.sample`, `config/role-agent-mapping.sample.json`).
- **Human gates before live use:** ~~PO approval of `rub-smdh-001`~~ resolved 2026-06-12 (synthetic/test-only lab scope); deferred backend ADR (BQ-001); Canadian region approval (BQ-005).
