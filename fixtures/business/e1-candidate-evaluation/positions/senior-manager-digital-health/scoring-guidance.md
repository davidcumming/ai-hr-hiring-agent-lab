# Scoring Guidance: Senior Manager, Digital Health Strategy (Fixture)

> **Provenance (2026-06-11).** Sections "Recommended Scoring Approach" and "Rules for Use"
> below are reproduced **verbatim** from `HR-Screening-Rubric-Standard.md` (Canada Health
> Infoway prototype sample, Version 0.1 Draft Sample). The "Rubric derivation notes" section
> at the end is curation commentary, clearly separated. SYNTHETIC sample content.

## 5. Recommended Scoring Approach

A simple structured approach may be used:

### Required Qualification Assessment
- Meets clearly
- Partially meets / unclear
- Does not meet

### Preferred Qualification Assessment
- Strong evidence
- Some evidence
- No evidence identified

### Overall Advisory Category
- Strong Match
- Possible Match
- Weak Match
- Insufficient Information

The organization may choose not to use numeric scoring at the initial screening stage if a descriptive approach is more appropriate.

## 6. Rules for Use

### 6.1 Apply the Same Rubric to All Candidates
Once screening begins, the same agreed rubric should be used across the candidate pool unless a documented adjustment is approved.

### 6.2 Record Rationale
Reviewers should capture brief rationale, especially for screening-out decisions or ambiguous cases.

### 6.3 Avoid Overreliance on Single Signals
A single keyword or single missing phrase should not determine suitability unless it maps to a clearly mandatory requirement.

### 6.4 Distinguish Absence of Evidence from Evidence of Absence
Where information is unclear, the reviewer should note uncertainty rather than assume the candidate lacks the qualification.

### 6.5 Use Human Judgment
The rubric supports consistent assessment but does not replace human review.

---

## Rubric derivation notes (curation commentary, not source content)

`rubric.v1.json` in this folder is a **derived** rubric, approved by the Product Owner on
2026-06-12 for **synthetic/test-only Slice E1 lab evaluation** (gap G-2 resolved). The
approval does **not** imply production hiring approval:

- Criteria names and definitions come only from `role-profile.md` section 7 (screening rubric
  considerations) and `job-posting.md` sections "Approved Required Qualifications" and
  "Approved Preferred Qualifications". No new criteria were invented.
- The anchored 1-5 scoring scale follows this repo's council evaluation contract and the
  precedent of `fixtures/positions/pos-sample-001/rubric.v1.json`. The source standard
  (section 5 above) permits a descriptive scoring approach instead; the PO approved the
  anchored 1-5 form for lab testing.
- Bilingualism (English/French) is listed in the source preferred qualifications but is not a
  scored criterion in v1; it is recorded in the rubric's `unscored_assets` field.
- `approved: true` with `approval_scope: synthetic/test-only Slice E1 lab evaluation` and
  `production_hiring_approval: false` — PO decision recorded 2026-06-12 in
  `docs/delivery/slices/slice-e1-candidate-evaluation-council/fixture-curation-notes.md`.
