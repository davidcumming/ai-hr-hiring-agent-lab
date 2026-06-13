---
name: github-issue-drafter
description: Creates safe GitHub Issues for backlog tracking, or drafts them when requested, tooling is unavailable, or publication is sensitive/risky. Use when tracking unresolved, deferred, or risk-bearing work.
---
# Skill: GitHub Issue Drafter

**Used at:** Stage 14 — Traceability & closeout (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §27 GitHub Issues

---

## 1. Purpose

Create well-structured GitHub Issues for unresolved, deferred, or risk-bearing backlog work surfaced during planning, implementation, evals, documentation reconciliation, or closeout. Use **create mode** by default when GitHub tooling is available, duplicates have been checked, and the issue is safe to publish. Use **draft mode** when the user asks for a draft, GitHub tooling is unavailable, duplicate status cannot be checked, or publication could create security, privacy, compliance, disclosure, or external-facing risk.

Creating an issue records backlog work; it does not approve an ADR, accept residual risk, authorize release, approve merge, or convert backlog into committed delivery scope.

---

## 3. Do Not Use This Skill For

- Using Azure DevOps or any other tracker — the canonical tracker is GitHub Issues (Process Doc §27).
- Drafting duplicates — if an existing open issue already covers the item, note that issue and do not draft.
- Replacing the traceability matrix — the matrix finds gaps; this skill drafts the response to them.
- Inventing issue types — the authoritative list is Process Doc §27; reference it by number, do not restate it in output.
- Closing, deleting, reprioritizing, assigning, milestoning, or converting issues into committed scope.
- Publishing sensitive or disclosure-risky content that belongs in a secure artifact reference.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Issue candidate list | Yes | From `traceability-matrix-builder` or explicit request; each should carry item ID, type, severity, summary |
| 2 | Closeout findings | Conditional | From `closeout-package-builder`: residual risks / follow-ups not yet in the candidate list |
| 3 | Eval failure classification | Conditional | From `eval-failure-classifier` (Stage 11); non-blocking failures only |
| 4 | Documentation validation gaps | Conditional | From `documentation-consistency-validator` (Stage 13); non-blocking gaps |
| 5 | Manual-config / source-control debt | Conditional | Debt items needing tracking |
| 6 | Architecture gaps | Conditional | From `adr-gap-detector` (Stage 6); gaps deferred without an approved ADR |
| 7 | Open GitHub Issues (current) | Yes | Required to avoid duplicates |
| 8 | Repository labels | Recommended | Apply standard labels when available; recommend unavailable labels |
| 9 | GitHub tooling availability | Yes | Create mode requires working issue-create tooling |
| 10 | Requested mode | Optional | `create` / `draft`; default is `create` when safe |
| 11 | Publication-safety context | Yes | Whether content is safe to publish in an issue |
| 12 | Slice ID and name | Yes | For the "Related slice" field |

---

## 7. Process Steps

### Step 1 — Consolidate and deduplicate
Gather all candidates and deduplicate against the open-issue list. Where an existing issue tracks the same gap, note its number and skip drafting.

### Step 2 — Determine issue type
Confirm each type against Process Doc §27. If a candidate fits no type, use the closest match and note the uncertainty; do not invent types. Fallback is `technical-debt` with a note.

### Step 3 — Run the publication-safety check
Before creating anything, confirm the body contains no secrets, credentials, tenant IDs, subscription IDs, personal data, real candidate data, sensitive screenshots, raw eval transcripts, or sensitive payloads. If sensitive detail is needed, reference the secure artifact instead. If the issue would be security-sensitive, compliance-sensitive, external-facing, or disclosure-sensitive, use draft mode and state the reason.

### Step 4 — Prepare each issue record
Complete `templates/github-issue-draft-template.md`. Every field is populated or explicitly "TBD — requires human input". Never leave blank: Type, Summary (title), Context, Reason created, Severity, Acceptance criteria (≥1), Verification / re-test criteria, Related slice, Source trace, Labels.

### Step 5 — Assess severity

| Severity | Characteristics |
|---|---|
| Critical | Blocks merge, breaks production, or is an unaccepted safety/privacy/compliance risk |
| High | Significant gap; non-blocking now but must be addressed in next 1–2 slices |
| Medium | Meaningful gap for the near-term roadmap |
| Low | Minor debt, cosmetic gap, or enhancement; deferrable |

Do not assign Critical to issues the Release Authority has already accepted as non-blocking.

### Step 6 — Apply or suggest labels
Use standard labels where available, especially `agent-created`, `follow-up`, `manual-config-debt`, `documentation`, `eval`, `architecture`, `copilot-studio`, `azure`, and type-specific repo labels. If a desired label does not exist, create the issue without that label and report it as "recommended label unavailable" rather than inventing a label.

### Step 7 — Create or draft
Use create mode when tooling is available and the issue is safe to publish. After creation, capture the issue number, URL, labels applied, and source trace.

Use draft mode when requested, tooling is unavailable, duplicate status cannot be checked, or the publication-safety check fails. State the draft reason and what must happen before creation.

---

## 9. Output Format

Use `templates/github-issue-draft-template.md` per issue. Reference sensitive eval content by artifact ID; no PHI, PII, secrets, tenant/subscription IDs, real candidate data, sensitive screenshots, raw eval transcripts, or Canadian-residency-restricted data in any issue body. The full output is: (1) duplicate-check summary noting any candidate skipped for an existing open issue; (2) safety-check summary; (3) created issue records with numbers/URLs and labels, plus draft records with draft reasons; (4) caveats on missing tooling, missing labels, or sensitive publication risk.

---

## 10. Quality Bar

Before handoff, confirm:

- [ ] The open-issue list was checked; no issue record duplicates an existing open issue of the same scope.
- [ ] No issue was created or drafted for a fully completed item (Covered in the traceability matrix).
- [ ] Each title is concise and action-oriented (describes the gap/action, not a symptom).
- [ ] Each issue type is one of the canonical Process Doc §27 types; none invented; non-GitHub trackers not referenced.
- [ ] Each issue record has all required fields populated or explicitly TBD, including ≥1 testable acceptance criterion and stated verification / re-test criteria.
- [ ] Severity is assessed; Critical is not applied to items the Release Authority already accepted as non-blocking.
- [ ] For security-risk and manual-config-debt items, the risk is explicit.
- [ ] Related slice is populated; owner/priority default to "TBD — requires human input" when unknown (no personal names unless provided).
- [ ] Source trace is populated with the source slice, artifact, finding, eval result, or implementation evidence that caused the issue.
- [ ] No PHI, PII, secrets, tenant/subscription IDs, real candidate data, sensitive screenshots, raw eval transcripts, or Canadian-residency-restricted data appears in any field.
- [ ] Labels are applied when available or reported as unavailable recommendations.
- [ ] Created issues include number and URL; drafts include a clear draft reason.
- [ ] No language implies that issue creation is risk acceptance, ADR approval, release approval, merge approval, or a final product/architecture decision.
- [ ] Issue records are grouped by type; any candidate not created/drafted (duplicate or insufficient info) is listed with a reason.

---

## 13. Handoff to Next Skill

Pass created issue refs and draft records to `closeout-package-builder`; `archive-package-preparer` (Stage 17) references the issue list in the manifest; `manual-config-debt-monitor` (Stage 19) consumes `manual-config-debt` and `source-control-debt` issues for ceiling tracking. The skill response must include the duplicate-check summary (or "No duplicates found"), safety-check summary, created issue refs, draft records with reasons, candidates skipped, and any caveats on missing input or unavailable labels. Obeys the recommend-never-approve and source-of-truth rules in AGENTS.md; creating or drafting an issue for a residual risk is tracking, not approval.
