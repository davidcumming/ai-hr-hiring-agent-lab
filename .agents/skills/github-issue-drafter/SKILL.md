---
name: github-issue-drafter
description: Drafts well-structured GitHub Issues for unresolved, deferred, or risk-bearing work surfaced during planning, implementation, evals, or closeout. Use when tracking gaps; never creates issues.
---
# Skill: GitHub Issue Drafter

**Used at:** Stage 14 — Traceability & closeout (Orchestration Map §3 stage table)
**Execution model:** `inline`
**Supports:** Process Doc §27 GitHub Issues

---

## 1. Purpose

Draft well-structured GitHub Issues for unresolved, deferred, or risk-bearing work surfaced during planning, implementation, evals, documentation reconciliation, or closeout. Each draft is ready for human review and, once the Release Authority approves, for direct creation in GitHub. This skill drafts issues only; it never creates them — creation needs human approval (Process Doc §27).

---

## 3. Do Not Use This Skill For

- Using Azure DevOps or any other tracker — the canonical tracker is GitHub Issues (Process Doc §27).
- Drafting duplicates — if an existing open issue already covers the item, note that issue and do not draft.
- Replacing the traceability matrix — the matrix finds gaps; this skill drafts the response to them.
- Inventing issue types — the authoritative list is Process Doc §27; reference it by number, do not restate it in output.

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
| 8 | Slice ID and name | Yes | For the "Related slice" field |

---

## 7. Process Steps

### Step 1 — Consolidate and deduplicate
Gather all candidates and deduplicate against the open-issue list. Where an existing issue tracks the same gap, note its number and skip drafting.

### Step 2 — Determine issue type
Confirm each type against Process Doc §27. If a candidate fits no type, use the closest match and note the uncertainty; do not invent types. Fallback is `technical-debt` with a note.

### Step 3 — Draft each issue
Complete `templates/github-issue-draft-template.md`. Every field is populated or explicitly "TBD — requires human input". Never leave blank: Type, Summary (title), Context, Reason created, Severity, Acceptance criteria (≥1), Verification / re-test criteria, Related slice.

### Step 4 — Assess severity

| Severity | Characteristics |
|---|---|
| Critical | Blocks merge, breaks production, or is an unaccepted safety/privacy/compliance risk |
| High | Significant gap; non-blocking now but must be addressed in next 1–2 slices |
| Medium | Meaningful gap for the near-term roadmap |
| Low | Minor debt, cosmetic gap, or enhancement; deferrable |

Do not assign Critical to issues the Release Authority has already accepted as non-blocking.

### Step 5 — Suggest labels
Propose ≥1 label per issue (starting suggestions only; teams override): `bug` → `bug` (+`regression` if a previously passing scenario); `documentation-gap` → `documentation`; `source-control-debt` → `tech-debt`,`source-control`; `eval-failure` → `eval`,`blocking`/`non-blocking`; `architecture-decision-needed` → `architecture`,`adr-needed`; `security-risk` → `security` (+`privacy` if residency-related); `manual-config-debt` → `tech-debt`,`config`; `test-gap` → `testing`; `technical-debt` → `tech-debt`; `enhancement` → `enhancement`.

### Step 6 — Produce the draft package
Output all drafts in one structured response, grouped by type. State clearly that no issue has been created and that human approval is required before creation.

---

## 9. Output Format

Use `templates/github-issue-draft-template.md` per issue. Reference sensitive eval content by artifact ID; no PHI, PII, or Canadian-residency-restricted data in any issue body — flag anything that belongs in secure storage for the human to redact before creation. The full output is: (1) a duplicate-check summary noting any candidate skipped for an existing open issue; (2) the draft issues; (3) an approval prompt for the Release Authority.

---

## 10. Quality Bar

Before handoff, confirm:

- [ ] The open-issue list was checked; no draft duplicates an existing open issue of the same scope.
- [ ] No draft was created for a fully completed item (Covered in the traceability matrix).
- [ ] Each title is concise and action-oriented (describes the gap/action, not a symptom).
- [ ] Each issue type is one of the canonical Process Doc §27 types; none invented; non-GitHub trackers not referenced.
- [ ] Each draft has all required fields populated or explicitly TBD, including ≥1 testable acceptance criterion and stated verification / re-test criteria.
- [ ] Severity is assessed; Critical is not applied to items the Release Authority already accepted as non-blocking.
- [ ] For security-risk and manual-config-debt drafts, the risk is explicit.
- [ ] Related slice is populated; owner/priority default to "TBD — requires human input" when unknown (no personal names unless provided).
- [ ] No PHI, PII, or Canadian-residency-restricted data appears in any field.
- [ ] No language implies an issue has been created or that issue creation is risk acceptance.
- [ ] The "Awaiting human approval — no issues created" statement is present.
- [ ] Drafts are grouped by type; any candidate not drafted (duplicate or insufficient info) is listed with a reason.

---

## 13. Handoff to Next Skill

After Release Authority approval (Stage 16): approved drafts are created in GitHub by a human-directed action; `closeout-package-builder` records the issue numbers; `archive-package-preparer` (Stage 17) references the issue list in the manifest; `manual-config-debt-monitor` (Stage 19) consumes `manual-config-debt` and `source-control-debt` issues for ceiling tracking. The skill response must include the duplicate-check summary (or "No duplicates found"), all drafts, the "Awaiting human approval — no issues created" statement, an explicit list of candidates not drafted, and any caveats on missing input. Obeys the recommend-never-approve and source-of-truth rules in AGENTS.md; drafting an issue for a residual risk is tracking, not approval.
