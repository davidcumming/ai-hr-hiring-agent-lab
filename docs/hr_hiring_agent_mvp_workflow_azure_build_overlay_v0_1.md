# HR Hiring Agent — MVP Workflow with Azure Build Implementation Overlay v0.2

**Purpose:** This is an updated Azure Build overlay for the core MVP workflow. It keeps the business workflow intact, but adds the Microsoft-stack implementation view after each stage: Copilot Studio topics, API tools, Azure Table entities, Azure Blob artifacts, Azure Queue jobs, Azure AI Foundry / Agent Framework participation, actors, gates, and slice implications.

**Source basis:** `mvp_workflow.md` describes the complete HR Hiring Agent MVP from recruitment-case intake through final advisory recommendation/export. This overlay does not replace that document; it translates its workflow into the concrete Azure Build implementation model.

**Current build reality as of E6:** Copilot Studio can run a topic-driven tool workflow, store a returned `evaluation_id` in an explicit topic/workflow variable, and call a second tool using a body-bindable `evaluation_id` input. Azure Functions exposes a FastAPI facade. Blob persistence already exists for evaluation records. The next product-level slices need to formalize the full MVP data model, generalize Blob storage for documents/artifacts, make Azure Table Storage the workflow system of record, add Azure Queue-backed asynchronous assessment, and replace the deterministic council with live Azure AI Foundry / Agent Framework execution.

---

## 0. Cross-Cutting Azure Build Model

### 0.1 Primary Microsoft-stack components

| Layer | Product / Component | Role in final solution |
|---|---|---|
| Business-user front door | Copilot Studio | Guided conversational workflow, topic orchestration, tool invocation, business-language rendering, user prompts, and task guidance. |
| API facade | Azure Functions + FastAPI | Thin controlled service layer. Owns API contracts, validation, authorization, workflow gates, envelope responses, and calls to storage / Foundry. |
| Workflow system of record | Azure Table Storage | Case state, workflow state, artifact indexes, version records, approvals, review records, task state, assignments, evidence index, audit/event ledger. |
| Document and artifact store | Azure Blob Storage | Source documents, generated artifacts, exports, evaluation records, prompt/eval artifacts, redacted evidence packs, report packages. |
| Async orchestration | Azure Queue Storage | Background jobs for document processing, candidate assessment batches, package generation, export generation, retryable long-running work. |
| Live AI execution | Azure AI Foundry / Agent Framework | Drafting, extraction, rubric assistance, advisory evaluation council, synthesis, fairness/policy review, interview-package generation, final package drafting. |
| Secret and configuration control | Key Vault + managed identity | Function keys eventually replaced by Entra/managed identity. Secrets stay outside repo and evidence. |
| Observability | Application Insights / Log Analytics | API telemetry, workflow events, Foundry call traces, latency/cost measurements, failures, audit-support diagnostics. |
| Power Platform governance | Power Platform solution / custom connector / connection | Custom connector API definition, connection credential binding, Copilot tool availability, topic configuration, eventually export/import ALM. |

### 0.2 Durable stores and naming model

These names are draft logical names, not final implementation commitments.

#### Azure Tables

| Table | Purpose |
|---|---|
| `RecruitmentCases` | One entity per recruitment case. Current state, owner, role context, hiring manager, status, current gate, active artifact versions. |
| `CaseParticipants` | Case-scoped actors and permissions: HR, hiring manager, interviewers, reviewers, auditors. |
| `CaseTasks` | Pending/completed workflow tasks and next actions shown by Copilot. |
| `CaseEvents` | Business-readable activity trail: created, updated, approved, blocked, exported, cancelled, reviewed. |
| `ArtifactVersions` | Version records for intake, posting, rubric, import summary, assessment package, shortlist, interview package, final recommendation. |
| `Approvals` | Version-specific approval records, actor, role, decision, timestamp, comments. |
| `SourceDocuments` | Index of uploaded/imported source documents stored in Blob, with document type, hash, version, synthetic flag, case/candidate linkage. |
| `Applicants` | Applicant/candidate set records for a case; candidate identity/reference, import status, duplicate/incomplete flags. |
| `CandidatePackages` | Candidate package assembly state: resume, cover letter, required docs, source refs, package completeness. |
| `Assessments` | Advisory assessment status and metadata by case/candidate/rubric version. Full records live in Blob. |
| `HumanReviews` | HR/hiring-manager/interviewer comments, corrections, overrides, acknowledgement, review status. |
| `Shortlists` | Provisional and official internal advisory shortlist packages, status, version, approvals. |
| `InterviewAssignments` | Candidate/interviewer assignment records and visibility boundaries. |
| `InterviewFeedback` | Human-entered interview feedback index and status; full forms can live in Blob if large. |
| `Exports` | Export package metadata, status, Blob link, generated timestamp, export type. |

#### Azure Blob containers / path conventions

| Container / path | Purpose |
|---|---|
| `case-artifacts/cases/{case_id}/intake/{version}/...` | Structured intake and source-derived artifacts. |
| `case-artifacts/cases/{case_id}/posting/{version}/...` | Job posting drafts, approved versions, exports. |
| `case-artifacts/cases/{case_id}/rubric/{version}/...` | Rubric drafts, approved rubric JSON/Markdown/PDF. |
| `case-documents/cases/{case_id}/candidates/{candidate_id}/...` | Resume, cover letter, uploaded applicant materials, source evidence documents. |
| `case-artifacts/cases/{case_id}/candidate-packages/{candidate_id}/{version}/...` | Assembled candidate evidence packets for evaluation. |
| `evaluations/cases/{case_id}/candidates/{candidate_id}/evaluations/{evaluation_id}/record.json` | Full advisory evaluation/audit records. |
| `case-artifacts/cases/{case_id}/shortlists/{version}/...` | Provisional and official shortlist packages. |
| `case-artifacts/cases/{case_id}/interviews/{version}/...` | Interview questions, scorecards, package exports. |
| `case-artifacts/cases/{case_id}/feedback/{candidate_id}/...` | Interview feedback forms and attachments if needed. |
| `case-artifacts/cases/{case_id}/final/{version}/...` | Final advisory recommendation package and export. |
| `evidence/cases/{case_id}/events/{event_id}/...` | Redacted evidence packs, screenshots/exports where repo-safe, and evidence summaries. |

### 0.3 Common API envelope pattern

Every tool-facing endpoint should return a standard envelope:

- `status`: `completed`, `validation_failed`, `blocked`, `unauthorized`, or `error`
- `case_id`
- `candidate_id` or `candidate_ref` where applicable
- `artifact_id` / `artifact_version` / `evaluation_id` where applicable
- `correlation_id`
- `user_message`
- `safe_details`
- `result`
- `errors`
- `warnings`
- `next_actions`

This keeps Copilot Studio rendering consistent and prevents the conversation layer from deciding business state.

### 0.4 Core actor model

| Actor | Role in solution |
|---|---|
| HR Specialist | Case owner / workflow operator. Can create cases, upload/import docs, initiate drafts, request assessments, coordinate reviews, generate packages, export artifacts. |
| Hiring Manager | Business owner/reviewer/approver. Can confirm role details, approve posting/rubric/shortlist/interview package, review assessments, comment/override. |
| Interviewer / Reviewer | Scoped reviewer. Can view assigned materials and enter interview feedback. |
| Auditor / Governance Reviewer | Read-only. Can inspect case activity, evidence, artifact versions, approvals, and audit trails. |
| Administrator | Environment/setup role. Manages configuration, identities, policy, and emergency governed reopen/cancel operations. |

### 0.5 Product boundaries to preserve

The agent remains advisory, human-in-the-loop, and not an ADP replacement. It does not contact candidates, schedule interviews, send offers/rejections, write back to ADP, make final hiring decisions, or use unapproved criteria. Those boundaries are not optional; they should be encoded into system prompts, API gates, response templates, eval contracts, and closeout criteria.


### 0.6 Technical decisions captured after v0.1 review

These decisions refine the buildout direction for the complete MVP, not only the first stakeholder demo.

| Decision area | Decision | Implementation consequence |
|---|---|---|
| Complete data model | Define a complete MVP data model now, even if later slices refine it. | This document now includes Appendix A as the first complete logical data model for Tables, Blobs, Queues, Foundry runs, notifications, model assessments, human reviews, and final candidate evaluations. |
| Document storage | Store source documents and generated artifacts in Azure Blob Storage. | Blob paths become first-class artifact references; Table rows store metadata, hashes, versions, and links rather than large document bodies. |
| Workflow state | Store workflow state in Azure Table Storage. | Copilot topic variables are transient orchestration state only. Case state, gates, tasks, approvals, reviews, and assessment status are Table entities. |
| Model assessment execution | Run LLM-backed model candidate assessment asynchronously using Azure Queue Storage. | Copilot starts an assessment job; workers invoke Foundry/Agent Framework; Table state and notifications tell users when assessments are complete. |
| User notification | Provide an explicit notification mechanism when async candidate assessment completes. | MVP stores notifications in a `Notifications` table and exposes `getMyNotifications` / `getCaseNotifications`; future channels may add Teams/Outlook/Power Automate proactive messages. |
| Foundry placement | Foundry / Agent Framework runs behind the controlled API/worker layer, not directly inside Copilot. | The facade/worker validates gates, assembles candidate packages, invokes Foundry, persists outputs, and returns advisory envelopes. |
| Terminology | Separate model candidate assessment from human candidate review. | The model assessment is a prerequisite for human review. Human review records agreements/overrides and rationales. The final candidate evaluation is a derived consolidated record, not simply the model output. |
| Human reviewer cardinality | Allow multiple HR specialists, hiring managers, and other authorized reviewers per candidate. | Review tables must support many reviewers per candidate/evaluation/criterion, role-specific required coverage rules, and aggregation across all submitted human reviews. |
| Score aggregation | Final candidate scores are derived from human review decisions over model ratings. | If all required humans agree with the model rating, the model score stands. If exactly one human override exists for a criterion, final score averages model score and that human override. If two or more human overrides exist, final score averages the human override scores and excludes the model score. All model and human rationale text remains in the final report. |
| Gates | Use workflow gates to block premature assessment, human review, shortlist, interview-package, and final recommendation actions. | Gate status and blocked attempts are stored as Table state and CaseEvents, with business-readable messages returned to Copilot. |
| Copilot ALM | Add a near-term Copilot Studio ALM/source-control capture slice. | Future topic/tool configuration should be exported/unpacked where feasible so the UI is not the only source of truth. |

### 0.7 Terminology: model assessment, human review, and final evaluation

The MVP must consistently distinguish these concepts:

| Term | Meaning | Source of truth |
|---|---|---|
| **Model Candidate Assessment** | The AI/Foundry council's advisory assessment of one candidate package against the approved rubric. It includes per-criterion scores, rationales, evidence, gaps, fairness/policy review, quality gates, and model metadata. | `ModelCandidateAssessments` table row plus full Blob audit record. |
| **Human Candidate Review** | A human review of the model candidate assessment. The reviewer sees one candidate at a time, reviews the model's full assessment, then agrees with or overrides each criterion rating and provides rationale for any override. | `HumanCandidateReviews` and `HumanCriterionReviewItems` table rows plus optional detailed review Blob artifact. |
| **Final Candidate Evaluation** | The consolidated candidate evaluation after required human reviews. It contains final per-criterion ratings derived from the aggregation rule, all model and human rationales, disagreement notes, reviewer coverage, caveats, and evidence links. | `FinalCandidateEvaluations` / `FinalCriterionRatings` plus Blob final evaluation report. |
| **Candidate assessment set** | The set of model assessments for all confirmed applicants in a case. | `ModelAssessmentJobs`, `ModelCandidateAssessments`, `CandidatePackages`. |
| **Human review coverage** | The required set of human reviewers/roles who must complete review before shortlist/final stages. | `ReviewRequirements`, `HumanCandidateReviews`, `WorkflowGates`. |

Recommended naming rule: avoid using “assessment” for human activity unless the surrounding text is explicit. Use **model assessment** for the AI council output and **human review** for human agreement/override work.

### 0.8 Human review and final-rating aggregation rule

For each candidate and rubric criterion:

1. The model council produces a model rating and model rationale.
2. Each required human reviewer is shown the model rating, model rationale, evidence, gaps, and caveats for one candidate at a time.
3. For each criterion, each reviewer records either:
   - `agree_with_model = true`, with optional comment; or
   - `agree_with_model = false`, with an override rating and required override rationale.
4. The final criterion rating is derived as follows:
   - if zero human overrides exist, use the model rating;
   - if exactly one human override exists, average the model rating and the single override rating;
   - if two or more human overrides exist, average the human override ratings only and exclude the model rating;
   - preserve decimal precision in storage and round only for display/export according to the report template.
5. The final report must preserve all subjective evaluation language: the model rationale, every human agreement comment, every override rationale, and a calculation explanation.

Example report language:

> The model rated Criterion X as 8/10. The hiring manager overrode the rating to 7/10 and provided rationale. The HR specialist overrode the rating to 6/10 and provided rationale. Because two human reviewers overrode the model rating, the final criterion rating is the average of the two human override ratings: 6.5/10. The model rationale and both human rationales are preserved below.

This aggregation rule is an MVP policy decision and should be implemented as deterministic backend logic, not left to Copilot or the model.

### 0.9 Async assessment and notification pattern

Model candidate assessment should be asynchronous for the MVP, especially once a case contains multiple candidates or live Foundry council execution is enabled.

| Step | Component | Behaviour |
|---|---|---|
| Start assessment | Copilot topic calls API facade | User requests assessment for one candidate or a confirmed set. API validates gates and creates `ModelAssessmentJob` rows. |
| Queue work | API facade writes Azure Queue messages | Queue messages identify case, candidate package, rubric version, requested action, actor, correlation ID, and retry metadata. |
| Run council | Worker / Function processor | Worker loads package/rubric from Blob/Table, invokes Foundry council, validates outputs, and persists full audit records. |
| Update state | Worker writes Tables/Blob | `ModelCandidateAssessments` status changes from `queued` to `running` to `completed` or `failed`; full record is stored in Blob. |
| Notify user | Worker/API writes `Notifications` | HR/hiring manager notification rows are created when an assessment or batch completes, fails, or needs human attention. |
| User sees result | Copilot topic calls notification/status APIs | User can ask “what’s ready?” or “show completed assessments.” Future proactive Teams/Outlook notification can be added without changing the workflow model. |

For the first demo, notification may be pull-based through Copilot (`getMyNotifications`, `getAssessmentBatchStatus`). For the complete MVP, the data model should allow proactive notification channels later.

---

# 1. Stage 1 — Start or Continue a Recruitment Case

## Existing business workflow summary

Create or retrieve a structured recruitment case with owner, role context, participants, current state, and recommended next action.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose | Primary users |
|---|---|---|
| `Start recruitment case` | Guided topic to create a new case from minimal role/hiring-need information. | HR Specialist |
| `Open recruitment case` | Retrieve case by ID/name/recent activity and show state, tasks, artifacts, and next action. | HR Specialist, Hiring Manager |
| `Where are we in this hiring process?` | Case status summary and pending-task topic. | HR Specialist, Hiring Manager, Auditor |

Topic variables:

- `Topic.active_case_id`
- `Topic.case_status`
- `Topic.next_action`
- `Topic.actor_role`
- `Topic.selected_case_id` when user picks from search results

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `createRecruitmentCase` / `POST /api/cases` | Create a case and initial workflow state. |
| `searchRecruitmentCases` / `GET or POST /api/cases/search` | Find cases by title, department, hiring manager, or recent cases. |
| `getRecruitmentCase` / `GET /api/cases/{case_id}` or body-friendly wrapper | Retrieve case state and allowed actions. |
| `getCaseNextActions` / `GET /api/cases/{case_id}/next-actions` | Return pending tasks and blocked gates in business language. |

### Azure Table entities

- `RecruitmentCases`: new case row with `case_id`, title, department, role title, status `intake_pending`, owner actor, hiring manager reference, created timestamps.
- `CaseParticipants`: HR owner and proposed hiring manager.
- `CaseTasks`: tasks such as `complete_role_intake`, `attach_source_documents`, `confirm_hiring_manager`.
- `CaseEvents`: `case_created`, `case_opened`, `case_status_viewed`.

### Azure Blob artifacts

Optional at this stage. If source documents are provided during creation, store them under:

`case-documents/cases/{case_id}/source-intake/{document_id}`

### Queue jobs

Usually none. If uploaded documents are included at case creation, enqueue `process-source-document`.

### Foundry / AI usage

Optional and low risk. Foundry may summarize a role brief or propose missing intake questions, but the case state itself is created by the API facade, not by the model.

### Actors and permissions

- HR Specialist can create and own cases.
- Hiring Manager can view attached cases after being added.
- Auditor can search/read, but not create or modify.

### Gates and evidence

No downstream assessment can start from this stage. Evidence records case creation, actor, role, and initial status.

### Slice implications

Early product slice: implement Table-backed case creation/opening and a Copilot topic that can create/open a case. This is the gateway to replacing sample-only workflows with case-based workflows.

---

# 2. Stage 2 — Role Intake and Source Document Collection

## Existing business workflow summary

Collect role details, source documents, and business context, then produce a structured intake record used by posting, rubric, assessment, interviews, and final recommendation.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Complete role intake` | Guided form-like conversation to capture role purpose, responsibilities, qualifications, risks, interview participants, and open questions. |
| `Upload role source documents` | Attach source materials such as ADP exports, business notes, prior postings, org docs, or job descriptions. |
| `Review role intake gaps` | Show missing/weak sections and ask HR/hiring manager to clarify. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `upsertRoleIntake` / `POST /api/cases/{case_id}/intake` | Save structured intake draft/version. |
| `registerSourceDocument` / `POST /api/cases/{case_id}/documents` | Register uploaded/source documents and Blob metadata. |
| `getRoleIntake` / `GET /api/cases/{case_id}/intake/current` | Retrieve current intake. |
| `analyzeRoleSourceDocuments` / `POST /api/cases/{case_id}/intake/analyze` | Extract draft intake fields from source documents. |
| `listIntakeGaps` / `GET /api/cases/{case_id}/intake/gaps` | Return missing or weak intake fields. |

### Azure Table entities

- `SourceDocuments`: document metadata, type, Blob URI, hash, source, synthetic flag, origin (`manual_upload`, `adp_export`, `business_doc`).
- `ArtifactVersions`: `role_intake` version records.
- `CaseTasks`: track `role_intake_in_progress`, `source_docs_pending`, `hiring_manager_confirmation_pending`.
- `CaseEvents`: `source_document_uploaded`, `role_intake_drafted`, `intake_gap_flagged`.

### Azure Blob artifacts

- Source documents in `case-documents/cases/{case_id}/role-source/{document_id}`.
- Extracted intake draft JSON/Markdown in `case-artifacts/cases/{case_id}/intake/{version}/intake.json`.
- Optional redacted evidence pack in `evidence/cases/{case_id}/events/{event_id}`.

### Queue jobs

- `process-source-document`: extract text, hash, document type, source segments.
- `generate-intake-draft`: if Foundry is used asynchronously for long source docs.

### Foundry / AI usage

Foundry can extract and organize intake fields from uploaded source documents, flag ambiguity, and propose missing questions. The API facade validates and versions the structured intake before it becomes case state.

### Actors and permissions

- HR Specialist uploads and edits.
- Hiring Manager confirms or clarifies role criteria.
- Auditor can inspect source references and version history.

### Gates and evidence

Posting/rubric generation should be blocked until minimum required intake fields exist. Evidence records document hashes, extraction outputs, missing fields, and confirmations.

### Slice implications

This is where Blob document storage becomes mandatory. Build `SourceDocuments` and `ArtifactVersions` before serious arbitrary-document candidate workflows.

---

# 3. Stage 3 — Job Posting Draft, Review, and Approval

## Existing business workflow summary

Draft and version a job posting from approved intake/source material, then require HR and hiring-manager approval of the same current version before it is official.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Draft job posting` | Generate a draft posting from current intake and source documents. |
| `Revise job posting` | Apply human-requested revisions and create a new version. |
| `Review job posting` | Show current version, source references, fairness warnings, and approval status. |
| `Approve job posting` | Record HR or hiring-manager approval for the current version. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `draftJobPosting` / `POST /api/cases/{case_id}/posting/draft` | Generate a draft via templates and Foundry. |
| `reviseJobPosting` / `POST /api/cases/{case_id}/posting/revise` | Create a new version from human instructions. |
| `getJobPosting` / `GET /api/cases/{case_id}/posting/current` | Retrieve current version and approval state. |
| `approveArtifactVersion` / `POST /api/cases/{case_id}/approvals` | Approve current posting version. |
| `exportJobPosting` / `POST /api/cases/{case_id}/posting/export` | Generate exportable artifact. |

### Azure Table entities

- `ArtifactVersions`: `job_posting` draft/approved versions.
- `Approvals`: HR and hiring-manager approvals tied to exact version.
- `CaseEvents`: `job_posting_drafted`, `job_posting_revised`, `job_posting_approved`, `posting_exported`.
- `CaseTasks`: pending approvals.

### Azure Blob artifacts

- `case-artifacts/cases/{case_id}/posting/{version}/posting.md`
- `posting.json` with structured fields/source refs
- `posting_export.docx` or `posting_export.pdf` when implemented

### Queue jobs

- `generate-posting-draft` if long-running.
- `generate-posting-export` for Word/PDF.

### Foundry / AI usage

Foundry drafts posting text from approved intake and templates, checks wording, and highlights potentially unfair or unclear language. The service stores drafts only after validating structure and source references.

### Actors and permissions

- HR Specialist can draft, edit, submit for approval, and approve as HR.
- Hiring Manager can review and approve business accuracy.
- Auditor can inspect versions and approvals.

### Gates and evidence

Approval must be version-specific and require both HR and hiring-manager approvals on the same version. Any material revision invalidates prior approval and creates a new approval task.

### Slice implications

This can be delayed until after first demo if the first demo starts from pre-approved rubric/posting. For full MVP, it needs Table-backed artifact versioning and approvals.

---

# 4. Stage 4 — Screening Rubric Creation and Approval

## Existing business workflow summary

Draft and approve a screening rubric before candidate assessment. The rubric defines required/preferred/disqualifying criteria, evidence expectations, follow-up areas, and scoring guidance.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Draft screening rubric` | Generate rubric from approved intake/posting and HR standards. |
| `Review rubric risks` | Show unclear criteria, proxy-risk concerns, and missing evidence expectations. |
| `Revise screening rubric` | Apply human edits and version rubric. |
| `Approve screening rubric` | Record HR/hiring-manager approval of current rubric version. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `draftScreeningRubric` / `POST /api/cases/{case_id}/rubric/draft` | Generate structured rubric. |
| `reviseScreeningRubric` / `POST /api/cases/{case_id}/rubric/revise` | Create new version. |
| `getCurrentRubric` / `GET /api/cases/{case_id}/rubric/current` | Retrieve current rubric and approval state. |
| `approveArtifactVersion` | Record version-specific approval. |
| `validateRubricForAssessment` / `POST /api/cases/{case_id}/rubric/validate` | Check suitability before assessment. |

### Azure Table entities

- `ArtifactVersions`: `screening_rubric` versions, status, hash.
- `Approvals`: rubric approvals by HR and hiring manager.
- `CaseEvents`: rubric drafted/revised/approved.
- `CaseTasks`: `rubric_approval_pending`.

### Azure Blob artifacts

- `case-artifacts/cases/{case_id}/rubric/{version}/rubric.json`
- `rubric.md`
- optional fairness/proxy-risk review output

### Queue jobs

Optional `generate-rubric-draft`.

### Foundry / AI usage

Foundry can draft rubric criteria and flag proxy-risk concerns. The API validates schema, prohibited factor checks, scoring anchors, and evidence expectations before saving.

### Actors and permissions

- HR Specialist and Hiring Manager both approve.
- Auditor reads.

### Gates and evidence

Applicant assessment is blocked until rubric is approved. Assessment records must carry `rubric_version` and rubric hash. If the rubric changes, existing assessments become stale until regenerated/reconciled.

### Slice implications

For first demo, start from a pre-approved synthetic rubric in Blob/Table, then later build full rubric drafting/approval.

---

# 5. Stage 5 — Applications Received and Applicant Import

## Existing business workflow summary

After applications are received through existing processes such as ADP exports, HR imports applicant materials into the agent workflow as untrusted evidence, resolves findings, and confirms the applicant set.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Import applicants` | Upload/register candidate materials for a case. |
| `Review import findings` | Show missing documents, duplicates, unsupported file types, and candidate package status. |
| `Confirm applicant set` | HR confirms imported candidates are ready for assessment. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `registerApplicant` / `POST /api/cases/{case_id}/applicants` | Create candidate/applicant row. |
| `registerCandidateDocument` / `POST /api/cases/{case_id}/candidates/{candidate_id}/documents` | Register resume, cover letter, or uploaded materials. |
| `processApplicantImport` / `POST /api/cases/{case_id}/applicant-imports` | Process import batch. |
| `getImportFindings` / `GET /api/cases/{case_id}/import-findings` | Retrieve duplicate/incomplete findings. |
| `confirmApplicantSet` / `POST /api/cases/{case_id}/applicant-set/confirm` | Lock/confirm assessment set. |

### Azure Table entities

- `Applicants`: candidate records, import status, synthetic flag, candidate reference.
- `CandidatePackages`: package completeness and required-doc status.
- `SourceDocuments`: document index for each candidate.
- `CaseTasks`: resolve import findings, confirm set.
- `CaseEvents`: import started, document registered, finding resolved, applicant set confirmed.

### Azure Blob artifacts

- `case-documents/cases/{case_id}/candidates/{candidate_id}/resume/{document_id}`
- `case-documents/cases/{case_id}/candidates/{candidate_id}/cover-letter/{document_id}`
- import batch manifests and findings reports

### Queue jobs

- `process-applicant-document`
- `detect-duplicates`
- `assemble-candidate-package`

### Foundry / AI usage

Foundry is optional here. Prefer deterministic document intake first. AI may later classify document type or extract candidate evidence, but imported documents remain untrusted evidence until processed and confirmed.

### Actors and permissions

- HR Specialist imports and resolves findings.
- Hiring Manager can view confirmed applicant set if authorized.
- Auditor can inspect import record.

### Gates and evidence

Assessment is blocked until applicant set is confirmed and blocking import findings are resolved or documented. Evidence includes hashes, document sources, candidate package completeness, and HR confirmation.

### Slice implications

For first demo, implement synthetic batch import for up to five candidates from fixtures and store documents in Blob. This is a must-have before live multi-candidate evaluation.

---

# 6. Stage 6 — Ready-to-Assess Checklist

## Existing business workflow summary

Run a checklist confirming posting/rubric/applicant prerequisites are complete and current before advisory assessment begins.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Run ready-to-assess checklist` | Show pass/fail checklist and unblock assessment when complete. |
| `What is blocking assessment?` | Explain missing prerequisites and next actions. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `runAssessmentReadinessCheck` / `POST /api/cases/{case_id}/assessment/readiness` | Evaluate gates. |
| `getAssessmentReadiness` / `GET /api/cases/{case_id}/assessment/readiness` | Retrieve latest checklist result. |
| `unlockAssessmentSet` / internal transition | Mark case state ready if gates pass. |

### Azure Table entities

- `CaseTasks`: checklist tasks.
- `CaseEvents`: readiness check run, blocked/unblocked.
- `ArtifactVersions`: required current versions.
- `Applicants`, `CandidatePackages`: package completion.
- `RecruitmentCases`: status transition to `assessment_ready`.

### Azure Blob artifacts

- `case-artifacts/cases/{case_id}/readiness/{run_id}/ready-to-assess.json`
- optional Markdown report

### Queue jobs

Usually none.

### Foundry / AI usage

None required. Readiness gates should be deterministic.

### Actors and permissions

- HR Specialist runs and resolves.
- Hiring Manager views readiness status.

### Gates and evidence

This is a gate stage. The service must return blocked reasons and next actions. It should not rely on Copilot conversation state.

### Slice implications

This is a strong near-term slice because it turns case/rubric/applicant state into a demonstrable workflow gate.

---

# 7. Stage 7 — Advisory Candidate Assessment

## Existing business workflow summary

Assess each confirmed applicant consistently against the approved rubric. AI-backed assessment runs behind controlled workflow services; the conversational agent presents and explains advisory output but does not decide or change candidate status.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Assess confirmed applicant set` | Start assessments for all confirmed candidates or selected candidate subset. |
| `Assess candidate` | Run/retrieve one candidate assessment. |
| `Show candidate assessment` | Present advisory result, evidence, gaps, uncertainty, and audit info. |
| `Regenerate stale assessments` | Re-run assessments after rubric changes where permitted. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `startCandidateAssessment` / `POST /api/cases/{case_id}/candidates/{candidate_id}/assessments` | Start one assessment. |
| `startAssessmentBatch` / `POST /api/cases/{case_id}/assessments/batch` | Queue assessment for confirmed candidates. |
| `getAssessment` / `POST /api/evaluations/retrieve` or case-specific wrapper | Retrieve assessment/audit record. |
| `listAssessments` / `GET /api/cases/{case_id}/assessments` | List assessment status by candidate. |
| `getAssessmentSummary` / `GET /api/cases/{case_id}/candidates/{candidate_id}/assessment-summary` | Business-friendly summary. |

### Azure Table entities

- `ModelAssessmentJobs`: batch/job status for async model candidate assessment.
- `ModelCandidateAssessments`: status, candidate, rubric version, evaluation ID, latest result summary, confidence, flags, Foundry run reference.
- `CandidatePackages`: evaluated package version and source hash.
- `Notifications`: assessment completed/failed/needs-attention notifications for HR and hiring managers.
- `CaseEvents`: model assessment queued/started/completed/failed/stale.
- `CaseTasks`: human candidate review pending after model assessment.

### Azure Blob artifacts

- Full candidate package used for evaluation.
- Full Foundry council outputs and final advisory assessment:
  `evaluations/cases/{case_id}/candidates/{candidate_id}/evaluations/{evaluation_id}/record.json`
- Role outputs, prompt/template versions, evidence citations, quality gates, redacted summaries.

### Queue jobs

- `run-model-candidate-assessment`
- `run-model-assessment-batch`
- `retry-model-assessment`
- `mark-stale-model-assessments`
- `write-assessment-complete-notification`

### Foundry / AI usage

This is the main Foundry council slice. Foundry / Agent Framework runs the **model candidate assessment** council asynchronously: evidence extraction, role perspectives, scoring, fairness/policy review, synthesis, quality gate checks, and final advisory output. The API facade and worker own orchestration contract, validation, persistence, advisory boundaries, and notification creation. The model assessment is a prerequisite for human candidate review; it is not the final candidate evaluation.

### Actors and permissions

- HR Specialist starts assessment.
- Hiring Manager views after assessment is available.
- Auditor reviews audit record.
- Interviewers generally do not see assessments unless assigned later.

### Gates and evidence

Assessment requires approved rubric and confirmed candidate package. Every assessment records rubric version/hash, candidate package version/hash, source refs, model/prompt versions, and human-review-required flags.

### Slice implications

For first demo, this is central: support up to five synthetic candidate packages, async queue-backed live Foundry council execution, persisted model assessment records, completion notifications, and Copilot summaries. This stage should not be conflated with human candidate review; human review starts after model assessment completion.

---

# 8. Stage 8 — Candidate Dashboard and Human Review

## Existing business workflow summary

Show completed model candidate assessments, track HR/hiring-manager review coverage, and record human criterion-level agreement, comments, corrections, overrides, and follow-up flags while preserving the original model assessment.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Show candidate dashboard` | Summarize candidate assessment status and review status. |
| `Review candidate assessment` | Present one completed model candidate assessment, one candidate at a time, and guide criterion-by-criterion human review. |
| `Record criterion agreement or override` | Store whether the reviewer agrees with the model rating or overrides it with rationale. |
| `Add review comment` | Store HR or hiring-manager review comment not tied to a single criterion. |
| `Mark candidate reviewed` | Mark actor-specific review complete only after all required criterion review items are complete. |
| `Show unresolved flags` | List unresolved high-severity or missing-evidence issues. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `getCandidateDashboard` / `GET /api/cases/{case_id}/candidate-dashboard` | Case-level assessment/review dashboard. |
| `startHumanCandidateReview` / `POST /api/cases/{case_id}/candidates/{candidate_id}/human-reviews` | Create a human review session after model assessment exists. |
| `recordCriterionReviewItem` / `POST /api/cases/{case_id}/candidates/{candidate_id}/human-reviews/{review_id}/criteria` | Store agree/override decision, override rating, and rationale for one criterion. |
| `createHumanReviewComment` / `POST /api/cases/{case_id}/candidates/{candidate_id}/reviews/comments` | Store general reviewer comments or follow-up flags. |
| `markReviewComplete` / `POST /api/cases/{case_id}/candidates/{candidate_id}/human-reviews/{review_id}/complete` | Mark reviewer-specific completion after all criteria have been reviewed. |
| `getReviewCoverage` / `GET /api/cases/{case_id}/review-coverage` | Determine coverage and blockers. |

### Azure Table entities

- `HumanCandidateReviews`: one review session per reviewer/candidate/model assessment.
- `HumanCriterionReviewItems`: one row per criterion decision: agree with model or override rating with rationale.
- `FinalCandidateEvaluations`: derived consolidated scores after required human review coverage.
- `FinalCriterionRatings`: deterministic aggregation result and explanation by criterion.
- `ModelCandidateAssessments`: review status summary and unresolved flags.
- `CaseTasks`: HR review pending, hiring-manager review pending, additional reviewer pending.
- `CaseEvents`: human review created, criterion agreement recorded, override recorded, review complete, final evaluation recalculated.

### Azure Blob artifacts

- Optional detailed review forms or export packages.
- Preserve original advisory assessment in Blob; store human review layer separately.

### Queue jobs

Usually none unless generating dashboard summaries asynchronously.

### Foundry / AI usage

Foundry can summarize review context and identify unresolved flags, but human comments, criterion agreement, overrides, and rationales are authored by humans. The model must not create interview feedback or human review on a person’s behalf. Final scoring is deterministic backend aggregation over model scores and human review decisions.

### Actors and permissions

- HR Specialists and Hiring Managers can review/comment according to case-scoped permissions; the model must support more than one reviewer in each role.
- Additional authorized reviewers may be attached for high-importance roles such as board positions.
- Auditor reads.
- Interviewers do not review candidate assessment unless assigned.

### Gates and evidence

Shortlist generation is blocked until required review coverage is complete. Human overrides do not erase the model assessment; they layer on top with actor, role, timestamp, criterion, override rating, and rationale. The final candidate evaluation uses the aggregation rule in Section 0.8 and preserves all model and human subjective language.

### Slice implications

For the first demo, implement criterion-level HR and hiring-manager human review for up to five candidates, including agree/override decisions and deterministic final score aggregation. This demonstrates human-in-the-loop governance and makes clear that the model assessment is only the starting point.

---

# 9. Stage 9 — Provisional and Official Advisory Shortlist

## Existing business workflow summary

Create a documented internal advisory shortlist package after human review coverage is complete; HR and hiring manager approve the current package version.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Show provisional shortlist` | Generate/read a provisional advisory shortlist from current completed reviews. |
| `Generate official advisory shortlist` | Create versioned official package after gates pass. |
| `Approve shortlist package` | Record HR/hiring-manager approval. |
| `Revise shortlist package` | Create new version after requested changes. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `generateProvisionalShortlist` / `POST /api/cases/{case_id}/shortlists/provisional` | Generate provisional view. |
| `generateOfficialShortlist` / `POST /api/cases/{case_id}/shortlists/official` | Create official package version. |
| `getShortlist` / `GET /api/cases/{case_id}/shortlists/{version}` | Retrieve shortlist package. |
| `approveArtifactVersion` | Approve shortlist version. |

### Azure Table entities

- `Shortlists`: package metadata, version, status, candidate IDs, caveats.
- `ArtifactVersions`: `shortlist` version record.
- `Approvals`: HR and hiring-manager approvals.
- `CaseEvents`: shortlist generated/revised/approved.
- `CaseTasks`: shortlist approval pending.

### Azure Blob artifacts

- Shortlist package JSON/Markdown/PDF under:
  `case-artifacts/cases/{case_id}/shortlists/{version}/`

### Queue jobs

- `generate-shortlist-package`

### Foundry / AI usage

Foundry can consolidate evidence and draft shortlist rationale. The API must enforce review-coverage gate and advisory language. The model must not autonomously select candidates as a decision; it drafts a package for human consideration.

### Actors and permissions

- HR Specialist generates.
- Hiring Manager reviews/approves.
- Auditor reads.

### Gates and evidence

Official shortlist blocked until review coverage complete. Approval version-specific. Not a candidate status change or final decision.

### Slice implications

Likely after first demo unless demo includes shortlist. The earliest demo can stop at reviewed candidate set.

---

# 10. Stage 10 — Interview Package and Interviewer Assignment

## Existing business workflow summary

Generate structured interview materials based on approved shortlist, rubric, follow-up areas, and competencies. Assign interviewer access without scheduling or contacting candidates.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Generate interview package` | Draft interview questions, scorecards, and follow-up areas. |
| `Review interview package` | Show current package and approval status. |
| `Assign interviewers` | Assign reviewers/interviewers to candidates/materials. |
| `Approve interview package` | Record version-specific approval. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `generateInterviewPackage` / `POST /api/cases/{case_id}/interview-package/draft` | Generate package. |
| `reviseInterviewPackage` / `POST /api/cases/{case_id}/interview-package/revise` | Version revisions. |
| `assignInterviewer` / `POST /api/cases/{case_id}/interview-assignments` | Assign interviewer/candidate access. |
| `getInterviewPackage` / `GET /api/cases/{case_id}/interview-package/current` | Retrieve package. |
| `approveArtifactVersion` | Approve package version. |

### Azure Table entities

- `ArtifactVersions`: interview package version.
- `InterviewAssignments`: assigned interviewer/candidate/materials.
- `Approvals`: interview package approval.
- `CaseTasks`: interviewer assignment pending, package approval pending.
- `CaseEvents`: package generated/approved, interviewer assigned.

### Azure Blob artifacts

- Interview package docs, scorecards, candidate-specific follow-up materials.

### Queue jobs

- `generate-interview-package`
- `generate-interview-export`

### Foundry / AI usage

Foundry drafts interview questions and follow-up areas grounded in approved rubric and shortlist. It does not schedule interviews or contact candidates.

### Actors and permissions

- HR Specialist generates/assigns.
- Hiring Manager approves.
- Interviewer views assigned materials only.
- Auditor reads.

### Gates and evidence

Interview package requires approval before use. Assignment controls visibility but is not scheduling.

### Slice implications

Beyond first demo unless your demo needs interview-stage coverage.

---

# 11. Stage 11 — Interview Feedback Capture

## Existing business workflow summary

Capture human-entered interview feedback and block final recommendation until required feedback coverage is complete.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Enter interview feedback` | Guided feedback capture for assigned interviewer/reviewer. |
| `Show feedback gaps` | HR/hiring manager view of missing feedback. |
| `Review interview feedback` | Summarize submitted feedback without inventing absent feedback. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `createInterviewFeedback` / `POST /api/cases/{case_id}/interview-feedback` | Store feedback. |
| `getFeedbackStatus` / `GET /api/cases/{case_id}/feedback-status` | Coverage and missing feedback. |
| `getCandidateFeedback` / `GET /api/cases/{case_id}/candidates/{candidate_id}/feedback` | Retrieve feedback. |

### Azure Table entities

- `InterviewFeedback`: feedback status, ratings, reviewer, candidate, package version.
- `CaseTasks`: feedback pending.
- `CaseEvents`: feedback submitted/updated.
- `InterviewAssignments`: expected feedback coverage.

### Azure Blob artifacts

- Long feedback forms or attachments, if needed.

### Queue jobs

Usually none.

### Foundry / AI usage

Foundry may summarize submitted feedback for HR/hiring manager, but must not generate interview feedback or fill missing interviews.

### Actors and permissions

- Interviewer submits their own feedback.
- HR monitors coverage.
- Hiring Manager reviews.
- Auditor reads.

### Gates and evidence

Final recommendation generation blocked until required feedback coverage complete. Missing feedback cannot be treated as completed.

### Slice implications

Beyond first demo unless the first demo includes interview flow.

---

# 12. Stage 12 — Final Advisory Recommendation and Export

## Existing business workflow summary

Generate a final advisory summary/package after required reviews and feedback are complete. It ends at recommendation for human offer consideration and does not trigger offers, rejections, contact, scheduling, or ADP updates.

## Azure Build implementation overlay

### Copilot Studio topics

| Topic | Purpose |
|---|---|
| `Generate final advisory package` | Create final package after gates pass. |
| `Show final recommendation` | Present final package summary and caveats. |
| `Export final package` | Generate export artifact. |
| `What blocks final package?` | Explain missing prerequisites. |

### Tools / API actions

| Tool / endpoint | Purpose |
|---|---|
| `generateFinalRecommendationPackage` / `POST /api/cases/{case_id}/final-recommendation` | Generate final version. |
| `getFinalRecommendationPackage` / `GET /api/cases/{case_id}/final-recommendation/current` | Retrieve current package. |
| `exportFinalPackage` / `POST /api/cases/{case_id}/exports/final-package` | Create export. |
| `runFinalPackageReadinessCheck` / `POST /api/cases/{case_id}/final-recommendation/readiness` | Validate prerequisites. |

### Azure Table entities

- `ArtifactVersions`: final recommendation package.
- `Exports`: export status and Blob path.
- `CaseEvents`: final package generated/exported/blocked.
- `CaseTasks`: final review/export tasks.
- `RecruitmentCases`: possible state transition to `final_package_ready` or `completed`.

### Azure Blob artifacts

- `case-artifacts/cases/{case_id}/final/{version}/final-recommendation.md`
- `final-recommendation.json`
- `final-export.pdf` or `final-export.docx`
- evidence pack references

### Queue jobs

- `generate-final-package`
- `generate-final-export`

### Foundry / AI usage

Foundry can consolidate evidence and draft the final advisory package. The API enforces gates and advisory language. The model cannot decide offers/rejections or update candidate status.

### Actors and permissions

- HR Specialist generates/export.
- Hiring Manager reviews.
- Auditor reads.

### Gates and evidence

Requires complete approvals/reviews/feedback coverage. Output is advisory and ends before offer/rejection/ADP actions.

### Slice implications

This is final MVP completion, not first demo unless the demo spans end-to-end.

---

# 13. First Demo Cut Line

The complete MVP includes all 12 stages, but the first credible stakeholder demo should not try to cover everything. A strong first demo can cover:

1. A pre-seeded or created case.
2. An approved rubric/job description assigned to the case.
3. Up to five synthetic candidate packages stored in Blob.
4. Ready-to-assess gate check.
5. Live or deterministic-backed advisory candidate assessment, depending on Foundry readiness.
6. Case dashboard with candidate assessment statuses.
7. HR and hiring-manager review comments/acknowledgements in Table state.
8. Evidence/audit retrieval for at least one candidate.

This demonstrates the real value: workflow state in Tables, documents in Blob, controlled Copilot topics, API facade gates, and human review. It can stop before shortlist, interview, and final recommendation.

---

# 14. Slice Roadmap Implications

This slice sequence is derived from the combined business workflow and Azure Build overlay. It prioritizes the first stakeholder demo while preserving the complete MVP data model.

| Order | Slice | Purpose |
|---:|---|---|
| 1 | Finish E6 and close it | Complete explicit Copilot topic orchestration, body-bindable retrieve operation, manual evidence, eval summary, closeout. |
| 2 | Adopt complete MVP data model | Add this data model to repo docs and create initial schema/contract tests for Table/Blob/Queue naming. |
| 3 | Case state foundation | Implement `RecruitmentCases`, `CaseParticipants`, `CaseTasks`, `CaseEvents`, `WorkflowGates`, `Notifications`; create/open/status topics. |
| 4 | Blob document registry | Implement `SourceDocuments` metadata, Blob upload/register/list/get APIs, hashes, synthetic flags, artifact references. |
| 5 | Case artifact/version foundation | Implement `ArtifactVersions`, `Approvals`, approved rubric/job-description assignment, and version-specific approval gates. |
| 6 | Candidate/applicant package import | Implement `Applicants`, `CandidatePackages`, candidate document completeness, and up to five synthetic candidate packages. |
| 7 | Async job and notification foundation | Implement `AsyncJobs`, Azure Queue messages, worker skeleton, status APIs, and `Notifications` APIs so users know when assessment completes. |
| 8 | Ready-to-assess checklist | Deterministic gate across case, approved rubric, confirmed applicant set, package completeness, and source/data rules. |
| 9 | Foundry model assessment for one candidate | Replace deterministic mock with live Azure AI Foundry / Agent Framework model candidate assessment behind worker/facade. |
| 10 | Model assessment persistence and audit retrieval | Persist model council outputs, role outputs, evidence citations, prompt/model metadata, quality gates, and full audit record in Blob/Table. |
| 11 | Batch model assessment for up to five candidates | Queue-backed batch execution, per-candidate status, notifications, retries, dashboard readiness. |
| 12 | Candidate dashboard | Copilot topic/tool to list candidates, model assessment statuses, flags, missing evidence, notifications, and review readiness. |
| 13 | Human candidate review — HR | HR reviewer sees one candidate at a time, reviews every model criterion rating, agrees or overrides with rationale. |
| 14 | Human candidate review — hiring manager / multiple reviewers | Hiring manager and additional authorized reviewers complete the same criterion-level review workflow. |
| 15 | Final candidate evaluation aggregation | Deterministically compute final criterion ratings from model score + human review decisions, preserving all rationales. |
| 16 | First demo polish/reset | Seed/reset script, demo topic path, synthetic case/candidate packages, evidence capture, known limitations. |
| Later | Shortlist/interview/final package | Stages 9-12 of full MVP, using the same data model and gate pattern. |
| Near-term technical enabler | Copilot Studio ALM/source-control capture | Export/unpack agent/topic/tool configuration where feasible to reduce manual UI work and drift. |

---

# 15. Remaining Open Design Decisions

The following are still open or need later ratification:

1. **Notification channel for MVP:** use Copilot pull-based notifications only, or also add Teams/Outlook/Power Automate proactive notifications for completed assessment jobs?
2. **Score scale:** store rubric-native scores and normalized 0-10 scores, or standardize the MVP scoring scale to 0-10 before live Foundry implementation?
3. **Reviewer weighting:** use equal weighting for all human override ratings in MVP, or allow role-specific weights later?
4. **Human review requirements:** what is the default required coverage for a normal case: one HR + one hiring manager, or configurable by role/position type from the start?
5. **Copilot ALM timing:** do we insert a short Copilot ALM/source-control capture slice immediately after E6 or after the first backend storage slices?
6. **Foundry execution boundary:** should Foundry be invoked by the Function App worker in the same codebase initially, or by a separate evaluator service once the pattern is proven?

---

# Appendix A — Complete MVP Data Model v0.2

This appendix defines the logical MVP data model for Azure Table Storage, Blob Storage, Queue messages, and selected derived records. It is intentionally implementation-ready but still subject to refinement through ADRs, schema tests, and slice implementation.

## A.1 Design principles

1. Azure Table Storage stores workflow state, indexes, statuses, gates, permissions, references, and queryable summaries.
2. Azure Blob Storage stores large documents, generated artifacts, full assessment records, evidence packs, exports, and long-form reports.
3. Azure Queue Storage carries asynchronous work requests and retries.
4. The API facade owns validation, gate checks, authorization, ID generation, version checks, and envelope responses.
5. Copilot topic variables are transient and never become the workflow system of record.
6. Foundry outputs are advisory model candidate assessments. Human reviews and final candidate evaluations are separate records.
7. All candidate/applicant content is synthetic in the lab until explicitly approved otherwise.
8. Every important action creates a `CaseEvents` record and, where appropriate, an `EvidenceRecords` row.

## A.2 Common fields

Most Table entities should include:

| Field | Purpose |
|---|---|
| `PartitionKey` | Usually `case_id`; for global lookup tables use a stable partition such as `global` or actor ID. |
| `RowKey` | Entity-specific ID or sortable composite key. |
| `entity_type` | Defensive type marker for mixed or future tables. |
| `case_id` | Recruitment case identifier where applicable. |
| `created_at`, `updated_at` | UTC ISO timestamps. |
| `created_by_actor_id`, `updated_by_actor_id` | Actor IDs from trusted identity mapping or lab header during early slices. |
| `created_by_role`, `updated_by_role` | Effective case role at time of action. |
| `correlation_id` | Request/job trace correlation. |
| `status` | Entity status using a constrained vocabulary. |
| `version` or `schema_version` | Record schema version and/or artifact version. |
| `etag` | Table optimistic concurrency marker where needed. |
| `synthetic` | Boolean flag for lab/test data. |
| `blob_uri` / `blob_path` | Pointer to Blob artifact when payload is too large for Table. |
| `sha256` | Hash for document/artifact integrity. |

## A.3 Table entities

### A.3.1 `RecruitmentCases`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `case` |
| `case_id` | string | Primary case ID. |
| `case_title` | string | Human-readable title. |
| `role_title` | string | Role being hired. |
| `department` | string | Department/business unit. |
| `recruitment_type` | string | e.g., permanent, contract, board, internal. |
| `case_status` | string | `intake_pending`, `posting_draft`, `rubric_pending`, `applicants_pending`, `assessment_ready`, `assessment_running`, `review_pending`, `shortlist_pending`, `interview_pending`, `final_pending`, `completed`, `cancelled`. |
| `current_stage` | string | Stage number/name. |
| `current_gate` | string | Active workflow gate. |
| `hr_owner_actor_id` | string | Primary HR owner. |
| `primary_hiring_manager_actor_id` | string | Primary hiring manager. |
| `target_start_date` | string/date | Optional. |
| `posting_period_start`, `posting_period_end` | string/date | Optional. |
| `active_intake_version` | string | Current intake artifact version. |
| `active_posting_version` | string | Current posting version. |
| `active_rubric_version` | string | Current approved rubric version. |
| `applicant_set_version` | string | Confirmed applicant set version. |
| `cancel_reason` | string | Required if cancelled. |
| `cancelled_at`, `cancelled_by_actor_id` | string | Terminal cancellation evidence. |

### A.3.2 `CaseParticipants`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `{role}#{actor_id}` |
| `actor_id` | string | Trusted actor/user reference. |
| `display_name` | string | Non-authoritative display. |
| `case_role` | string | `hr_specialist`, `hiring_manager`, `interviewer`, `reviewer`, `auditor`, `admin`. |
| `required_for_review` | bool | Whether this participant is required for candidate review coverage. |
| `required_for_approval` | bool | Whether this participant approves artifacts. |
| `scope` | string/json | Case-wide or candidate-specific scope. |
| `status` | string | `active`, `inactive`, `removed`. |

### A.3.3 `CaseTasks`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `task#{task_id}` |
| `task_type` | string | e.g., `complete_intake`, `approve_rubric`, `review_candidate`, `resolve_import_finding`. |
| `assigned_role` | string | Role required. |
| `assigned_actor_id` | string | Optional specific actor. |
| `candidate_id` | string | Optional. |
| `artifact_id`, `artifact_version` | string | Optional. |
| `status` | string | `open`, `blocked`, `completed`, `cancelled`. |
| `due_at` | string | Optional. |
| `blocking_gate` | string | Gate this task satisfies. |
| `completion_event_id` | string | Link to `CaseEvents`. |

### A.3.4 `CaseEvents`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `{timestamp}#{event_id}` |
| `event_id` | string | Unique event ID. |
| `event_type` | string | `case_created`, `artifact_version_created`, `approval_recorded`, `model_assessment_completed`, `human_override_recorded`, etc. |
| `actor_id`, `actor_role` | string | Actor and effective role. |
| `candidate_id` | string | Optional. |
| `artifact_id`, `artifact_version` | string | Optional. |
| `assessment_id`, `review_id`, `job_id` | string | Optional. |
| `summary` | string | Business-readable event summary. |
| `safe_details` | string/json | No secrets or raw sensitive data. |
| `evidence_id` | string | Link to evidence row/blob if applicable. |

### A.3.5 `WorkflowGates`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `gate#{gate_id}` |
| `gate_id` | string | e.g., `rubric_approved`, `assessment_unlocked`, `review_coverage_complete`. |
| `gate_status` | string | `locked`, `unlocked`, `blocked`, `satisfied`, `waived`. |
| `required_inputs` | string/json | Required artifacts/tasks. |
| `blocking_reasons` | string/json | Business-readable blockers. |
| `last_checked_at` | string | UTC. |
| `satisfied_by_event_id` | string | Optional. |
| `waiver_reason`, `waived_by_actor_id` | string | Only for governed waivers if allowed. |

### A.3.6 `Notifications`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `actor_id` for user inbox, or `case#{case_id}` for case notifications. |
| `RowKey` | string | `{created_at}#{notification_id}` |
| `notification_id` | string | Unique ID. |
| `case_id` | string | Related case. |
| `candidate_id` | string | Optional. |
| `job_id`, `assessment_id`, `artifact_id` | string | Optional links. |
| `notification_type` | string | `assessment_completed`, `assessment_failed`, `review_required`, `approval_required`, `gate_blocked`, `export_ready`. |
| `recipient_actor_id` | string | User recipient. |
| `recipient_role` | string | Role context. |
| `title` | string | Short message. |
| `message` | string | Business-readable notification. |
| `status` | string | `unread`, `read`, `dismissed`, `actioned`. |
| `action_tool` | string | Suggested Copilot tool/topic. |
| `action_payload` | string/json | Case/candidate refs for next action. |
| `channel` | string | `copilot_inbox`, future `teams`, `email`, `power_automate`. |

### A.3.7 `SourceDocuments`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `doc#{document_id}` |
| `document_id` | string | Unique document ID. |
| `candidate_id` | string | Optional for applicant docs. |
| `document_type` | string | `resume`, `cover_letter`, `job_description`, `rubric`, `adp_export`, `posting_source`, `interview_feedback`, etc. |
| `source_origin` | string | `manual_upload`, `fixture`, `adp_export`, `generated`, `external_reference`. |
| `blob_path` | string | Raw document path. |
| `normalized_text_blob_path` | string | Extracted text path if produced. |
| `mime_type`, `file_name`, `size_bytes` | string/int | Metadata. |
| `sha256` | string | Integrity hash. |
| `synthetic` | bool | Required in lab. |
| `processing_status` | string | `registered`, `queued`, `processed`, `failed`, `excluded`. |
| `version` | string | Source version. |

### A.3.8 `ArtifactVersions`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `artifact#{artifact_type}#{artifact_id}#{version}` |
| `artifact_id` | string | Logical artifact ID. |
| `artifact_type` | string | `role_intake`, `job_posting`, `screening_rubric`, `applicant_import_summary`, `shortlist_package`, `interview_package`, `final_recommendation`. |
| `version` | string | Version string. |
| `status` | string | `draft`, `under_review`, `approved`, `superseded`, `rejected`, `exported`. |
| `blob_path` | string | Artifact body/report. |
| `source_document_ids` | string/json | Provenance. |
| `sha256` | string | Artifact hash. |
| `created_by_actor_id` | string | Creator. |
| `approved_version_required` | bool | Whether downstream gates require approval. |

### A.3.9 `Approvals`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `approval#{artifact_id}#{version}#{role}#{actor_id}` |
| `approval_id` | string | Unique ID. |
| `artifact_id`, `artifact_type`, `artifact_version` | string | Version-specific target. |
| `actor_id`, `actor_role` | string | Approver. |
| `decision` | string | `approved`, `rejected`, `changes_requested`, `abstained`. |
| `comments` | string | Optional. |
| `decided_at` | string | UTC. |
| `superseded_by_version` | string | If artifact changes. |

### A.3.10 `Applicants`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `candidate#{candidate_id}` |
| `candidate_id` | string | Internal candidate ID. |
| `candidate_ref` | string | External/synthetic candidate reference. |
| `display_label` | string | Candidate display label, synthetic-safe. |
| `import_status` | string | `imported`, `incomplete`, `duplicate_pending`, `confirmed`, `excluded`. |
| `applicant_set_version` | string | Confirmed set version. |
| `duplicate_group_id` | string | Optional. |
| `blocking_findings` | string/json | Import issues. |
| `synthetic` | bool | Required for lab. |

### A.3.11 `CandidatePackages`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `package#{candidate_id}#{package_version}` |
| `candidate_id` | string | Candidate. |
| `package_version` | string | Version. |
| `rubric_version` | string | Rubric used for package readiness. |
| `document_ids` | string/json | Source docs included. |
| `required_document_status` | string/json | Resume, cover letter, required docs. |
| `package_status` | string | `draft`, `complete`, `blocked`, `stale`, `assessed`. |
| `blob_path` | string | Assembled evidence packet. |
| `sha256` | string | Package hash. |

### A.3.12 `ModelAssessmentJobs`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `job#{job_id}` |
| `job_id` | string | Unique job ID. |
| `job_type` | string | `single_candidate_model_assessment`, `batch_model_assessment`, `regenerate_stale_assessment`. |
| `candidate_ids` | string/json | Candidate(s) included. |
| `rubric_version` | string | Approved rubric version. |
| `requested_by_actor_id`, `requested_by_role` | string | Requester. |
| `status` | string | `queued`, `running`, `completed`, `partially_completed`, `failed`, `cancelled`. |
| `queued_at`, `started_at`, `completed_at` | string | UTC. |
| `total_count`, `completed_count`, `failed_count` | int | Batch progress. |
| `queue_message_id` | string | Queue trace. |
| `retry_count` | int | Retry state. |
| `error_summary` | string | Safe error. |

### A.3.13 `ModelCandidateAssessments`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `modelAssessment#{candidate_id}#{assessment_id}` |
| `assessment_id` | string | Model assessment ID. |
| `evaluation_id` | string | Existing evaluation/council ID if used. |
| `candidate_id`, `candidate_ref` | string | Candidate. |
| `package_version` | string | Candidate package assessed. |
| `rubric_version`, `rubric_sha256` | string | Approved rubric version/hash. |
| `assessment_status` | string | `queued`, `running`, `completed`, `failed`, `stale`, `superseded`. |
| `recommendation_label` | string | Advisory label only. |
| `confidence`, `confidence_score` | string/int | Model confidence. |
| `flags` | string/json | Missing evidence, fairness flags, quality gates. |
| `foundry_run_id` | string | Link to `FoundryRuns`. |
| `record_blob_path` | string | Full audit record. |
| `summary_blob_path` | string | Redacted summary/report. |
| `completed_at` | string | UTC. |
| `human_review_required` | bool | Always true for candidate-affecting outputs. |

### A.3.14 `ModelCriterionRatings`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `modelCriterion#{assessment_id}#{criterion_id}` |
| `assessment_id`, `candidate_id`, `criterion_id` | string | Links. |
| `criterion_name` | string | Snapshot name. |
| `model_score` | decimal | Native rubric score. |
| `model_score_normalized_10` | decimal | Optional normalized display score. |
| `model_rationale` | string | Summary rationale; full detail in Blob. |
| `supporting_evidence_ids` | string/json | Evidence references. |
| `contrary_evidence_ids` | string/json | Evidence references. |
| `missing_evidence_note` | string | Optional. |

### A.3.15 `HumanCandidateReviews`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `humanReview#{candidate_id}#{assessment_id}#{reviewer_role}#{reviewer_actor_id}` |
| `review_id` | string | Unique review session ID. |
| `assessment_id`, `candidate_id` | string | Links. |
| `reviewer_actor_id`, `reviewer_role` | string | Reviewer identity/role. |
| `review_status` | string | `not_started`, `in_progress`, `completed`, `returned_for_changes`, `withdrawn`. |
| `required_review` | bool | Whether counts toward gate. |
| `started_at`, `completed_at` | string | UTC. |
| `overall_comment` | string | Optional. |
| `follow_up_flags` | string/json | Optional flags. |
| `review_blob_path` | string | Optional detailed review form. |

### A.3.16 `HumanCriterionReviewItems`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `humanCriterion#{review_id}#{criterion_id}` |
| `review_id`, `assessment_id`, `candidate_id`, `criterion_id` | string | Links. |
| `model_score_snapshot` | decimal | Model score visible to reviewer. |
| `model_rationale_snapshot` | string | Model rationale visible to reviewer. |
| `agree_with_model` | bool | Reviewer decision. |
| `override_score` | decimal | Required when disagreeing. |
| `override_score_normalized_10` | decimal | Optional normalized display score. |
| `override_rationale` | string | Required when disagreeing. |
| `agreement_comment` | string | Optional when agreeing. |
| `reviewed_at` | string | UTC. |

### A.3.17 `ReviewRequirements`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `reviewReq#{candidate_id or all}#{role}` |
| `role` | string | Required role, e.g., `hr_specialist`, `hiring_manager`, `board_reviewer`. |
| `min_required_count` | int | Number required. |
| `candidate_scope` | string | `all_candidates`, specific candidate, shortlist only. |
| `status` | string | `active`, `satisfied`, `waived`. |
| `satisfied_count` | int | Current count. |

### A.3.18 `FinalCandidateEvaluations`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `finalEvaluation#{candidate_id}#{final_evaluation_id}` |
| `final_evaluation_id` | string | Unique ID. |
| `candidate_id`, `assessment_id` | string | Links. |
| `source_model_assessment_id` | string | Model assessment used. |
| `required_review_coverage_status` | string | `complete`, `incomplete`, `waived`. |
| `final_status` | string | `draft`, `ready_for_shortlist`, `superseded`. |
| `final_overall_score` | decimal | Optional aggregate across criteria. |
| `score_scale` | string | e.g., `rubric_native`, `normalized_10`. |
| `aggregation_policy_version` | string | Version of deterministic rule. |
| `report_blob_path` | string | Full final evaluation report. |
| `created_at` | string | UTC. |

### A.3.19 `FinalCriterionRatings`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `finalCriterion#{final_evaluation_id}#{criterion_id}` |
| `final_evaluation_id`, `candidate_id`, `criterion_id` | string | Links. |
| `model_score` | decimal | Snapshot. |
| `human_override_count` | int | Number of human overrides. |
| `human_agreement_count` | int | Number of human agreements. |
| `final_score` | decimal | Deterministic result. |
| `calculation_method` | string | `model_only_all_agree`, `model_plus_single_override_average`, `human_overrides_average`. |
| `calculation_explanation` | string | Business-readable formula. |
| `model_rationale` | string | Preserved. |
| `human_rationales` | string/json | All comments/rationales. |
| `evidence_refs` | string/json | Supporting evidence. |

### A.3.20 `Shortlists`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `shortlist#{shortlist_id}#{version}` |
| `shortlist_id`, `version` | string | IDs. |
| `status` | string | `provisional`, `official_draft`, `approved`, `changes_requested`, `superseded`. |
| `candidate_ids` | string/json | Included candidates. |
| `source_final_evaluation_ids` | string/json | Inputs. |
| `blob_path` | string | Package artifact. |
| `approval_status` | string | HR/hiring manager approval. |

### A.3.21 `InterviewPackages`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `interviewPackage#{package_id}#{version}` |
| `package_id`, `version` | string | IDs. |
| `shortlist_id` | string | Source shortlist. |
| `status` | string | `draft`, `approved`, `superseded`. |
| `questions_blob_path`, `scorecard_blob_path`, `guidance_blob_path` | string | Artifacts. |
| `approval_status` | string | Required before use. |

### A.3.22 `InterviewAssignments`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `interviewAssignment#{candidate_id}#{interviewer_actor_id}` |
| `candidate_id`, `interviewer_actor_id` | string | Assignment. |
| `package_id`, `package_version` | string | Materials version. |
| `visibility_scope` | string/json | What the interviewer can see. |
| `status` | string | `assigned`, `feedback_pending`, `feedback_complete`, `cancelled`. |

### A.3.23 `InterviewFeedback`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `feedback#{candidate_id}#{interviewer_actor_id}#{feedback_id}` |
| `feedback_id`, `candidate_id`, `interviewer_actor_id` | string | Links. |
| `package_id`, `package_version` | string | Interview package used. |
| `status` | string | `draft`, `submitted`, `returned`, `superseded`. |
| `ratings_json` | string/json | Structured ratings if small enough. |
| `feedback_blob_path` | string | Full feedback. |
| `submitted_at` | string | UTC. |

### A.3.24 `Exports`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `export#{export_id}` |
| `export_id` | string | Unique. |
| `export_type` | string | `posting`, `rubric`, `shortlist`, `interview_package`, `final_recommendation`, `case_audit`. |
| `source_artifact_ids` | string/json | Inputs. |
| `status` | string | `queued`, `generated`, `failed`, `downloaded`, `expired`. |
| `blob_path` | string | Export file. |
| `generated_by_actor_id` | string | Actor. |
| `generated_at` | string | UTC. |

### A.3.25 `FoundryRuns`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `foundryRun#{foundry_run_id}` |
| `foundry_run_id` | string | Foundry/Agent Framework run ID. |
| `assessment_id`, `job_id`, `candidate_id` | string | Links. |
| `model_deployment` | string | Deployment name/ref. |
| `agent_framework_version` | string | Version. |
| `prompt_template_ids` | string/json | Prompt/template refs. |
| `status` | string | `started`, `completed`, `failed`. |
| `token_usage_json` | string/json | If available. |
| `latency_ms` | int | If available. |
| `safe_error` | string | Redacted error if failed. |
| `trace_blob_path` | string | Redacted trace/evidence artifact. |

### A.3.26 `EvidenceRecords`

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` |
| `RowKey` | string | `evidence#{event_id}#{evidence_id}` |
| `evidence_id`, `event_id` | string | Links. |
| `evidence_type` | string | `manual_note`, `screenshot`, `connector_export`, `foundry_trace`, `test_output`, `approval_record`, `system_event`. |
| `blob_path` | string | Evidence artifact if externalized. |
| `summary` | string | Business-readable. |
| `redaction_status` | string | `not_needed`, `redacted`, `external_only`, `rejected`. |
| `contains_candidate_content` | bool | Flag. |
| `contains_secret` | bool | Must be false for repo artifacts. |

### A.3.27 `AsyncJobs`

This may be a generic companion to `ModelAssessmentJobs` for non-assessment jobs.

| Field | Type | Notes |
|---|---|---|
| `PartitionKey` | string | `case_id` or `global` |
| `RowKey` | string | `asyncJob#{job_id}` |
| `job_id`, `job_type` | string | Job identity. |
| `queue_name`, `queue_message_id` | string | Queue trace. |
| `payload_summary` | string | No secrets/raw content. |
| `status` | string | `queued`, `running`, `completed`, `failed`, `dead_lettered`, `cancelled`. |
| `retry_count`, `max_retries` | int | Retry policy. |
| `not_before`, `started_at`, `completed_at` | string | Timing. |
| `safe_error` | string | Redacted. |

## A.4 Blob containers and artifact types

| Container / path | Artifact types |
|---|---|
| `case-documents/cases/{case_id}/role-source/{document_id}/raw` | Role source docs, ADP exports, prior postings. |
| `case-documents/cases/{case_id}/candidates/{candidate_id}/{document_id}/raw` | Resume, cover letter, applicant materials. |
| `case-documents/cases/{case_id}/documents/{document_id}/normalized-text.json` | Extracted text, segments, metadata. |
| `case-artifacts/cases/{case_id}/intake/{version}/intake.json` | Structured intake. |
| `case-artifacts/cases/{case_id}/posting/{version}/posting.md|pdf|json` | Posting drafts/approved exports. |
| `case-artifacts/cases/{case_id}/rubric/{version}/rubric.json|md` | Approved rubric and scoring anchors. |
| `case-artifacts/cases/{case_id}/candidate-packages/{candidate_id}/{version}/package.json` | Assembled package used for model assessment. |
| `evaluations/cases/{case_id}/candidates/{candidate_id}/model-assessments/{assessment_id}/record.json` | Full model council audit record. |
| `evaluations/cases/{case_id}/candidates/{candidate_id}/model-assessments/{assessment_id}/summary.md` | Redacted model assessment summary. |
| `evaluations/cases/{case_id}/candidates/{candidate_id}/human-reviews/{review_id}/review.json` | Detailed human review form if too large for Table. |
| `evaluations/cases/{case_id}/candidates/{candidate_id}/final-evaluations/{final_evaluation_id}/report.md|pdf|json` | Final consolidated candidate evaluation. |
| `case-artifacts/cases/{case_id}/shortlists/{version}/shortlist.md|pdf|json` | Shortlist packages. |
| `case-artifacts/cases/{case_id}/interviews/{version}/...` | Interview questions, scorecards, guidance. |
| `case-artifacts/cases/{case_id}/feedback/{candidate_id}/{feedback_id}/...` | Interview feedback artifacts. |
| `case-artifacts/cases/{case_id}/final/{version}/final-package.md|pdf|zip` | Final advisory recommendation package. |
| `evidence/cases/{case_id}/events/{event_id}/{evidence_id}/...` | Redacted evidence, screenshots, exports, test outputs. |

## A.5 Queue message contracts

### `run-model-candidate-assessment`

```json
{
  "message_type": "run-model-candidate-assessment",
  "schema_version": "1.0",
  "case_id": "case-...",
  "candidate_id": "cand-...",
  "candidate_package_version": "v1",
  "rubric_version": "v1",
  "job_id": "job-...",
  "requested_by_actor_id": "actor-...",
  "requested_by_role": "hr_specialist",
  "correlation_id": "corr-...",
  "retry_count": 0
}
```

### `run-model-assessment-batch`

```json
{
  "message_type": "run-model-assessment-batch",
  "schema_version": "1.0",
  "case_id": "case-...",
  "candidate_ids": ["cand-001", "cand-002"],
  "rubric_version": "v1",
  "job_id": "job-...",
  "requested_by_actor_id": "actor-...",
  "correlation_id": "corr-..."
}
```

### `write-notification`

```json
{
  "message_type": "write-notification",
  "schema_version": "1.0",
  "case_id": "case-...",
  "recipient_actor_ids": ["actor-hr", "actor-hm"],
  "notification_type": "assessment_completed",
  "source_job_id": "job-...",
  "candidate_id": "cand-001",
  "assessment_id": "ma-...",
  "correlation_id": "corr-..."
}
```

## A.6 Core relationships and gates

| Relationship / Gate | Rule |
|---|---|
| Case to participants | A case has one HR owner, at least one hiring manager, and optional additional reviewers/interviewers/auditors. |
| Case to artifacts | Major artifacts are versioned. Approvals attach to a specific version. |
| Applicant set confirmation | Candidate assessment is blocked until the applicant set is confirmed and import findings are resolved or documented. |
| Rubric approval | Model candidate assessment is blocked until the current rubric version is approved. |
| Candidate package | Model assessment is blocked until the candidate package is complete and tied to the approved rubric/job artifacts. |
| Model assessment to human review | Human candidate review is blocked until a completed model candidate assessment exists. |
| Human review coverage | Shortlist and final candidate evaluation are blocked until required human review coverage is complete or governed waiver is recorded. |
| Final candidate evaluation | Derived from model ratings and human criterion review items using Section 0.8 aggregation. |
| Shortlist | Official shortlist generation is blocked until final candidate evaluations and required approvals are complete. |
| Interview package | Use is blocked until interview package version is approved and interviewer assignments are recorded. |
| Final recommendation | Generation/export is blocked until shortlist/interview/feedback gates are satisfied. |

## A.7 First-demo data model subset

The first stakeholder demo should use a subset of this full model:

- `RecruitmentCases`
- `CaseParticipants`
- `CaseTasks`
- `CaseEvents`
- `WorkflowGates`
- `Notifications`
- `SourceDocuments`
- `ArtifactVersions`
- `Approvals`
- `Applicants`
- `CandidatePackages`
- `ModelAssessmentJobs`
- `ModelCandidateAssessments`
- `ModelCriterionRatings`
- `HumanCandidateReviews`
- `HumanCriterionReviewItems`
- `FinalCandidateEvaluations`
- `FinalCriterionRatings`

Interview, shortlist, final export, and ADP-adjacent tables can remain present in the model but unimplemented until later MVP slices.

---

# Appendix B — One-Question Refinement Prompt

The highest-impact remaining question is:

**For MVP scoring, should the authoritative rubric scale be normalized to 0-10 now, or should the system preserve each rubric's native scale and compute/display normalized 0-10 values only for reporting?**

This affects the score fields in `ModelCriterionRatings`, `HumanCriterionReviewItems`, and `FinalCriterionRatings`, and it should be decided before implementing the human review/aggregation slices.
