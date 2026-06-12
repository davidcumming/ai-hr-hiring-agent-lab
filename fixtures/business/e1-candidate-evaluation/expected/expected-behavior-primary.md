# Expected Behaviour — Primary Scenario (PROVISIONAL)

> **Status: provisional.** The source zip contains no council-output-level expected results for
> these candidates (gap G-4). Sections marked *[source]* restate the phase-6.1 package's own
> expected-behaviour notes verbatim or near-verbatim; sections marked *[provisional]* are derived
> from this slice's eval contract and spec (FR-007/FR-008, BR-007/BR-008/BR-013) and must be
> validated by the Product Owner against real council output (AC-019 analogue). Synthetic data only.

## Scenario

- Position: `pos-smdh-001` — Senior Manager, Digital Health Strategy
- Rubric: `rub-smdh-001` v1 (PO-approved 2026-06-12 for **synthetic/test-only Slice E1 lab
  evaluation**; not a production hiring approval)
- Candidate: `cand-a001-nadia-belcourt` (A001 Nadia Belcourt), resume + cover letter + metadata

## Expected import/assessment posture *[source]*

Strong default-assessment candidate: clear evidence of digital health strategy, product/program
leadership, stakeholder engagement, interoperability awareness, privacy/security awareness, and
measurable outcomes. Import status `ready`; no risk flags; not excluded from assessment.

## Expected council behaviour *[provisional]*

- All six rubric criteria scored on the anchored 1–5 scale, each with cited supporting evidence
  resolvable to the evidence packet; expected posture is high scores on C1–C5 (strategy
  leadership, multi-stakeholder delivery, communication, governed-environment context,
  digital-health/interoperability familiarity) given the resume's direct evidence.
- C6 (executive briefing): direct evidence exists ("executive briefings", "executive reporting");
  expect direct-evidence scoring, not a missing-evidence note.
- No prohibited factors or proxy signals should be flagged; the fairness block should be present
  and empty of findings.
- No escalation triggers are specifically expected; any that fire must be recorded with rationale.
- Advisory recommendation label from the fixed enum only (plausibly `advance_to_interview`);
  never an advance/reject decision.
- `decision_support_only: true` and `human_review_required: true` on the record — universal,
  no exceptions (BR-007).
- All quality gates pass: schema validity, all-criteria-scored, evidence-per-score,
  no-prohibited-factors, human-review flag present, groundedness.
- Provider metadata truthful (`ai_backend_type: none` until live Foundry wiring).
