# Source Document Inventory — slice-e1-candidate-evaluation-council

Stage 0 input record produced by the `planning-context-reconciler` skill (Slice Planning Agent).
Date: 2026-06-11.

## 1. Source-repo resolution

The read-only source documentation repo (`hr-hiring`) was located by checking the candidate paths in the order instructed:

| # | Candidate path | Result |
|---|---|---|
| 1 | `/Users/davidcumming/coding_projects/hr-hiring` | Does not exist |
| 2 | `/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab/reference/hr-hiring` | Does not exist |
| 3 | `/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab/source/hr-hiring` | Does not exist |
| 4 | `/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab/docs/source/hr-hiring` | Does not exist |
| 5 | `/Users/davidcumming/Library/Mobile Documents/iCloud~md~obsidian/Documents/Markdown Repo/0-Work/copilot-agents/hr-hiring` | **Resolved. Used as the source-doc root.** |

**Resolved source-doc root:** `/Users/davidcumming/Library/Mobile Documents/iCloud~md~obsidian/Documents/Markdown Repo/0-Work/copilot-agents/hr-hiring`

**Boundary:** this repo is SOURCE DOCUMENTATION ONLY. It was read, never edited. Its implementation artifacts (e.g. `api/`, `infra/`, `pyproject.toml`) were **not** read and must not be copied wholesale into the lab repo; only requirements, constraints, architecture intent, API expectations, fixtures, and acceptance criteria were extracted.

## 2. Document inventory (all paths relative to the source-doc root)

| # | Document | Status | Role for this slice | Key extractions |
|---|---|---|---|---|
| 1 | `docs/hr/slice-e1-candidate-evaluation-functional-spec.md` | Present (77 lines) | Primary functional spec for Slice E1 (draft for PO review, dated 2026-06-11). Records the PO slice-reorder decision: first functional slice is candidate evaluation, not job posting. | Business outcome; pre-seeded fixtures table; council pipeline; AI-backend seam (`none` / `foundry_model_endpoint`); proposed API surface (`POST /api/evaluations`, `GET /api/evaluations/{evaluation_id}`); persistence design (Blob `evaluations` + Table `EvaluationEvidence`); out-of-scope list; UAT success statement (6 criterion scores, evidence per score, disagreements, fairness block, `human_review_required: true`, deterministic with mock backend). |
| 2 | `docs/calibrated_evaluation_council.md` | Present (873 lines) | Council architecture spec — wins on council behaviour. | Full council component model (§4–§6): Request Normalizer, Source Ingestion/Versioning, Evidence Extraction Agent, Deterministic Rules Validator, Merit Advocate, Risk/Gaps Advocate, Neutral Scoring Judge, Policy/Fairness Auditor, Synthesis Judge, Quality Gates, Persistence/Audit; output JSON schemas; risk levels `standard \| high_impact \| regulated`; cost modes A (standard, ~4 calls), B (high-impact, ~6–7), C (escalated, ~8–9); escalation triggers (§10); calibration requirements (§11); shared prompting rules (§12); default council (§13). |
| 3 | `docs/architecture/foundry-agent-framework-architecture.md` | Present (194 lines) | AI-backend companion (subordinate to canonical architecture). | Backend options: Foundry model endpoint vs Foundry Agent Service / Agent Framework workflow; decision table — multi-agent rubric evaluation ⇒ Agent Service/workflow; facade-only call path; responsibility split; required trace/eval metadata (§8); security constraints (§9); open decisions incl. approved Canadian region/deployments and deterministic-mock equivalents for workflow-backed operations. |
| 4 | `docs/microsoft-stack-agentic-architecture.md` | Present (1412 lines; read selectively) | Canonical architecture pattern — wins on boundaries. | Copilot Studio-first front door; Azure Function/thin API facade owns the deterministic business contract; Azure Storage (Blob + Table) is the system of record; AI backends optional, advisory, facade-called only; lab PoC boundary (no production, no real applicant data). |
| 5 | `docs/architecture/azure-functions-api-contracts.md` | Present (1504 lines; read selectively) | Envelope/status vocabulary authority. | Standard response envelope (status, case_id, operation_id, state_version, evidence_event_id, correlation_id, user_message, safe_details, artifact_refs, required_inputs, allowed_actions, errors, warnings); fixed status vocabulary (`completed`, `blocked`, `needs_input`, `validation_failed`, `unauthorized`, `error`); HTTP mapping; idempotency. Note: doc enumerates only Slice 0/1 endpoints — the evaluation endpoints are *proposed* by the functional spec, to be confirmed at contract time. |
| 6 | `docs/architecture/azure-storage-and-evidence-design.md` | Present (517 lines; read selectively) | Storage / evidence design. | Blob container strategy; Table design (CaseState, IdempotencyRecords, ArtifactMetadata, EvidenceMetadata, CaseAcl); evidence event model; AI-backend provenance metadata; metadata-first evidence rows (no document text in Table rows or logs); hash/version rules for normalized AI input bundles. |
| 7 | `docs/architecture/identity-rbac-design.md` | Present (286 lines; read selectively) | Identity / RBAC design. | Lab roles: `hr`, `hiring_manager`, `reviewer`, `auditor`, `admin_lab`, `admin_prod`, `support`; two-layer authorization (global role + case scope via `CaseAcl`); facade validates identity/authorization before any AI-backend call; managed identity to backends. |
| 8 | `docs/prompts/model-generation-quality-controls.md` | Present (537 lines; read selectively) | Generation quality controls. | Mock-first rule with **mock parity** (deterministic mock returns the identical schema as the live backend, `ai_backend_type = none`); JSON-first generation; bounded single corrective retry; multi-agent validation requirements for future resume/rubric evaluation (proposer + validator, advisory-only, human gate, trace/eval capture, facade ownership, mock parity); telemetry never-log rule. |
| 9 | `docs/evaluation-response/functional/evaluation-council-calibration-set.md` | Present (151 lines) | Calibration gold-set spec (F6). | Human-labeled calibration dataset: minimum 60 synthetic cases, stratified (strong/weak/borderline/missing-doc/fairness-trap/conflicting-evidence); two-plus independent labelers; required before AI-backed evaluation is trusted. Out of scope for Slice E1 execution; immediate follow-up. |
| 10 | `docs/security/security-privacy-operating-rules.md` | Present (407 lines; read selectively) | Security/privacy operating rules. | Synthetic-only hard boundary; candidate-style materials are untrusted content (data, never instructions); never-log list (no raw resumes/prompts/model I/O in telemetry); facade validates identity/scope before any backend call; AI output never approves/rejects/ranks/mutates state; managed identity + Key Vault; Canadian region/residency pause-for-decision rule. |
| 11 | `fixtures/sample-position/job-description.md` | Present (38 lines) | Pre-seeded sample position. | `pos-sample-001` — Program Coordinator, Digital Health Initiatives (synthetic), Toronto ON. |
| 12 | `fixtures/sample-position/rubric.v1.json` | Present (73 lines) | Pre-approved versioned rubric. | `rub-sample-001` v1, `approved_fixture`; 1–5 anchored scale; 6 criteria (C1 coordination, C2 healthcare/public-sector, C3 written communication, C4 risk/issue tracking — required; C5 PM certification, C6 bilingual EN/FR — preferred); disqualifier D1 work eligibility (absence = missing evidence, never disqualification); prohibited-factors note. Note: fixture carries `version` but the functional spec also requires a `sha256` field — the fixture as inspected has no hash field; hash must be computed/recorded when the fixture is vendored into this repo. |
| 13 | `fixtures/candidates/jordan-rivera/resume.md` | Present (35 lines) | Synthetic candidate resume. | `cand-sample-001`, Jordan Rivera (synthetic); 4 years public-sector digital program coordination incl. provincial health agency. |
| 14 | `fixtures/candidates/jordan-rivera/cover-letter.md` | Present (19 lines) | Synthetic candidate cover letter. | Synthetic; references RAID log ownership, status reporting, stakeholder work. |

**Missing documents:** none — all 14 instructed source documents were found and read (large architecture documents were read selectively for the sections governing this slice; their full text remains available read-only at the source root).

## 3. Inputs the skill requires that do not exist yet (working repo)

| Skill input | Status |
|---|---|
| Code-repo current-state docs | Absent — repo has no current-state documentation (greenfield) |
| Actual technical architecture | Absent — nothing built |
| Approved ADR index / ADRs | Absent — no ADRs exist in the working repo |
| Implementation / process lessons registers | Absent |
| Known-limitations doc | Absent (lab boundaries exist in `AGENTS.md`) |
| GitHub Issues | None exist for this repo (fresh repo, single commit) |
| Test/eval strategy or eval summaries | Absent — no tests or evals exist |

These absences are recorded as current-state facts in the planning context; per the skill, the reconciliation proceeds with the gaps marked rather than fabricating inputs.
