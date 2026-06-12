# Fixture Notes: Robin Kestrel (cand-a028-robin-kestrel)

**Case type:** Missing-cover-letter incomplete case (explicit negative-test fixture)

**Synthetic status:** fully synthetic (package `phase-6-1-hr-recruitment-agent-synthetic-applicants-v1`); never real applicant data.

Import status `missing_cover_letter`; `cover_letter_missing: true`; **this folder intentionally has no cover-letter.md**. Still assessable after review per source review notes (contrast with deferred A025, which combines missing cover letter with injection). Test value: missing-document handling, missing-evidence escalation trigger, no fabricated cover-letter content (LE-005 analogue, BR-013).

**Source expected-assessment note (verbatim):** Messy/risky fixture (missing cover letter): route for human review but do NOT exclude from assessment by default. Rationale: a missing cover letter alone is incomplete evidence that remains assessable once reviewed, unlike A025, which is excluded by default because it also contains prompt-injection text.

**Source risk note (verbatim):** Cover letter file is intentionally absent. Import should succeed with missing-cover-letter status and route for review rather than fabricating a cover letter. Not excluded by default (contrast with A025, which is excluded because it also contains prompt-injection text).
