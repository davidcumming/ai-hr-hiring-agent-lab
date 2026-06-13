---
name: high-risk-human-review-packager
description: Packages high-risk eval results, failure-mode findings, and classifications into a structured review package. Use when high-risk eval scenarios need an informed human release decision (Stage 11).
---
# Skill: High-Risk Human Review Packager

**Used at:** Stage 11 — Eval results & failure classification (Orchestration Map §3 stage table), conditional — fires when high-risk eval scenarios exist.
**Execution model:** `inline`
**Supports:** Process Doc §18 Testing and Eval Requirements, §29 Slice Closeout Package

---

## 1. Purpose

Package high-risk eval results, unsafe failure-mode findings, and classification outputs into a structured review package that lets the release authority make an informed, efficient risk decision. This skill assembles evidence and frames the decision questions; the human release authority reads the package and decides. It does not approve risk, downplay failures, or recommend acceptance — and it never softens the classifications it receives from `eval-failure-classifier`.

Conditional on high-risk eval scenarios (Process Doc §18.2); not produced for standard-tier slices unless an unusual circumstance warrants it, or when non-blocking candidates on any tier need a structured human-approval package.

---

## 3. Do Not Use This Skill For

- Classifying failures (`eval-failure-classifier`) or summarizing eval results for the repo (`eval-result-summarizer`).
- Approving risk or accepting non-blocking failures (human release authority).
- Producing the full closeout package (`closeout-package-builder`) or handling GitHub Issue create/draft actions (`github-issue-drafter`).

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Eval summary | Yes | Complete: version block, scenario results, failure summary. |
| 2 | Failure classification report | Yes | Identifies which failures require human review. |
| 3 | Unsafe failure-mode register | Yes | Which behaviours were pre-designated as requiring human review. |
| 4 | Eval contract | Yes | Scenario intent, expected behaviour, human-review designations. |
| 5 | Slice spec | Yes | Business/process context the reviewer needs. |
| 6 | Reviewer notes | Optional | Notes recorded during the eval run. |

---

## 7. Process Steps

### Step 1 — Identify scenarios requiring human review

From the classification report and eval contract, list: scenarios designated for human review in the contract; scenarios that failed and were classified `BLOCK`, `NBC`, or `MLM`; scenarios in the unsafe failure-mode register; and any scenario where a human approval question must be answered before the slice proceeds.

### Step 2 — Collect evidence excerpts

For each scenario requiring review, extract: the scenario description and why it is high-risk (from the contract/register); a brief observed-behaviour description (no full outputs); the failure classification and rationale; the external artifact reference for the full output; and the unsafe-mode designation if applicable.

### Step 3 — Frame the decision questions

For each item, formulate a specific, answerable question for the release authority — binary or clearly bounded, and genuinely open (not framed so the obvious answer is "approve"). Each question should identify the consequence of both approval and rejection. Examples: "Is the residual risk from SCN-007 (1/8 failure rate, minor quality degradation) acceptable? [Accept with tracking issue / Reject — fix required]". Avoid vague questions like "Is this okay?".

### Step 4 — Assemble the package

Populate the template: package metadata and slice context; scenarios requiring review; per-scenario evidence (description, observed, classification, artifact ref, decision question); blocking-failures summary (for awareness); non-blocking candidates requiring approval; model limitations requiring decision; risk summary (approve vs. reject outcomes); approval checklist and reviewer decision/signature space.

### Step 5 — Verify safe to share

No full outputs reproduced; no PHI/PII in the body; references only for sensitive content; classifications not softened or misrepresented.

---

## 9. Output Format

Use `templates/high-risk-review-package-template.md`. Place at `docs/delivery/slices/<slice-id>/human-review.md`; it enters the closeout package. Reference raw artifacts by external location; never paste full transcripts; no PHI/PII in the body.

---

## 10. Quality Bar

Before handoff, confirm:

- All scenarios designated for review in the contract, all unsafe-mode register scenarios, and all `BLOCK`/`NBC`/`MLM` classifications are present; no high-risk scenario omitted.
- Each per-scenario section includes why it is high-risk, what was tested, brief observed behaviour, classification, rationale, artifact reference, and a decision question.
- Each decision question is specific, answerable, genuinely open (not leading to "approve"), and states the consequence of both approval and rejection.
- Classifications match the `eval-failure-classifier` output exactly — none softened; blocking failures listed with criterion and fix direction; non-blocking candidates with residual risk and proposed issue; model limitations with decision options.
- No full outputs, no PHI/PII in the body; artifact references correct.
- The package does not approve risk on the reviewer's behalf or downplay failures, and is concise enough for efficient review.
- Reviewer-decisions section, overall approval status, and signature/identity/date space are present.
- Handoff notes state what happens after decisions are recorded; the package clearly states it is for review, not an approval.

See AGENTS.md cross-cutting rules (Authority and human gates; Evidence, privacy, context).

---

## 11. Failure Modes to Avoid

- Softening or omitting failures to make the package look better; including raw outputs or PHI/PII in the body.
- Framing decision questions so the obvious answer is "approve"; omitting any unsafe-mode register scenario.
- Using the package to pre-approve risk for the human; producing it before `eval-failure-classifier` has completed.
- Making the package too long to review efficiently.

---

## 13. Handoff to Next Skill

After the human reviewer completes the package:

- All items approved: orchestrator proceeds to Stage 12 (`current-state-reconciler`), with approval records attached to the closeout package.
- Blocking items rejected: fix loop applies (as with any `BLOCK` outcome).
- Non-blocking acceptances requiring issues: `github-issue-drafter` creates safe tracking issues or drafts decision-needed/sensitive items.
- Regression promotion recommended: `regression-promotion-recommender` evaluates candidates.

Return with: package status (`complete`/`partial`/`blocked`); count of scenarios requiring review; count of decision questions needing answers; key risks the reviewer must consider. Do not approve risk or recommend merge; state that the human's decisions are required before the slice can proceed.
