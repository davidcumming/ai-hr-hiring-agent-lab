---
name: documentation-consistency-validator
description: "Independently checks updated current-state docs and actual architecture against implementation evidence. Use at Stage 13 to confirm docs accurately describe what was built."
context: fork
---

# Skill: Documentation Consistency Validator

**Used at:** Stage 13 — Documentation validation (Orchestration Map §3 stage table)
**Execution model:** `isolated-verification`
**Supports:** Process Doc §26 Documentation Validation, §30 Definition of Done

---

## 1. Purpose

Independently check the updated current-state documentation and actual architecture (produced by `current-state-reconciler`) against implementation evidence, answering one question: do the updated docs accurately describe what was built? If not, identify the specific mismatches, classify them as blocking or non-blocking, and recommend treatment. This skill verifies independently and does not rewrite the artifact it checks — blocking mismatches go back to Stage 12. It reads the docs cold and must not share session context with the reconciler.

---

## 3. Do Not Use This Skill For

- Rewriting documentation — return blocking mismatches to Stage 12 (`current-state-reconciler`).
- Approving merge readiness — this skill produces a pass/fail recommendation; human release authority approves merge at Stage 16.
- Validating code correctness or eval pass/fail — this checks documentation against evidence; evals were Stage 11 and are treated here as evidence inputs.

---

## 4. Required Inputs

| # | Input | Required? | Notes |
|---|---|---|---|
| 1 | Updated current-state documentation files | Yes | Produced/updated by `current-state-reconciler` at Stage 12 |
| 2 | Branch diff analysis | Yes | Reconciler's Section A |
| 3 | Actual-architecture update summary | Yes | Reconciler's Section C |
| 4 | Test/eval summaries | Yes | What passed (deterministic + live-model) |
| 5 | Manual evidence summary | If exists | Normalized by `manual-evidence-normalizer` |
| 6 | Approved ADRs | If exists | To check architecture claims against approved decisions |
| 7 | Architecture guidelines | Yes | Read-only — check docs are consistent with active guidelines |
| 8 | Known limitations register | Yes | Verify unimplemented behaviour is classified as a limitation |
| 9 | GitHub Issues | Yes | Verify unresolved work is tracked, not documented as complete |

Do not load: the reconciler's working sessions or agent transcripts (read docs cold); the slice spec as a documentation-authority source.

---

## 6. Source Authority Rules

This skill **overrides the standard hierarchy**: the slice spec is intent, not a documentation authority. Use the diff and evidence — not the spec — to assess documentation accuracy. A feature not in the diff is a limitation, not a capability. The items being graded (updated current-state docs and actual-architecture update) are checked against: branch diff + implementation summary + approved manual evidence (what was built); approved ADR (architecture correctness); GitHub Issues (unresolved tracking); test + eval summaries (behaviour verified); known limitations register (limitation classification). Do not invent corrections or write replacement text.

---

## 7. Process Steps

1. **Read all inputs cold** — without prior knowledge of how the documentation was drafted.

2. **Validate current-state documentation against evidence**, per updated section:
   - **Accuracy** — is every claimed capability present in the diff, implementation summary, or approved evidence? Any unsupported claim is blocking.
   - **Slice-language absence** — any "Slice N added…", "This branch implemented…", "The next slice will…" is a blocking mismatch.
   - **Completeness** — are major user-visible/agent-behaviour changes in the diff all documented?
   - **Aspirational-text absence** — are any not-built or future features described as current?
   - **Known-limitation correctness** — is unimplemented/partial behaviour classified as a limitation, not a capability?
   - **Security/privacy/compliance/audit** — documented for new capabilities that require it (including Canadian data residency where relevant)?
   - **Unresolved-items tracking** — is anything tracked as open in GitHub Issues presented as complete? Are branch-diff gap items surfaced as issue candidates?

3. **Validate actual architecture against evidence**, per updated section:
   - **Only-built-components** — all listed components present in the diff or approved manual evidence; none listed that were not built.
   - **Guideline consistency** — claims consistent with active guidelines; any guideline gap authorized by an approved ADR.
   - **Manual-configuration components** — noted with source-control debt status and follow-up issue references/candidates.
   - **ADR cross-reference accuracy.**

4. **Classify each finding:**

   | Classification | Criteria |
   |---|---|
   | **Blocking mismatch** | False claim about current behaviour; missing major user-visible functionality; contradiction with approved ADR or security/privacy decision; claim unsupported by any evidence; slice-specific language in current-state docs |
   | **Non-blocking gap** | Minor omission not affecting correctness; gap that should be a follow-up issue; improvable but not false |
   | **Observation** | Informational; noted for future improvement |

   Blocking mismatches prevent advancement; the orchestrator returns to Stage 12.

5. **Produce the validation report** with: scope (files/evidence reviewed); blocking mismatches (file + section + description + required correction); non-blocking gaps (location + recommended treatment); observations; pass/fail recommendation; follow-up issue candidates.

---

## 9. Output Format

Use `templates/documentation-validation-report-template.md`. Write to `docs/delivery/slices/<slice-id>/documentation-validation-report.md`. The final response includes scope summary, blocking mismatches, non-blocking gaps, observations, recommendation, follow-up issue candidates, the report file path, and handoff notes. Recommendation must be one of:

| Value | Meaning |
|---|---|
| `PASS` | No blocking mismatches, no significant gaps; advance to Stage 14 |
| `CONDITIONAL-PASS` | No blocking mismatches; non-blocking gaps noted; advance to Stage 14; gaps become issue candidates |
| `FAIL — return to Stage 12` | One or more blocking mismatches; return to `current-state-reconciler` |

---

## 10. Quality Bar

Before handoff, confirm:

- This ran as an isolated-verification subagent with no shared context from the reconciler.
- No documentation was rewritten — only findings were produced.
- The slice spec was not used as a documentation authority; the diff and evidence were.
- Every claimed capability was checked against evidence; any claim without evidence is a blocking mismatch.
- Every updated section was checked for slice-specific language (always blocking if found).
- Actual architecture was checked against the diff and approved ADRs; only-built-components verified.
- Manual-configuration components were verified for source-control debt status and follow-up references.
- Every finding is classified; blocking classifications cite file, section, claim, and evidence gap.
- The blocking/non-blocking criteria were applied rigorously — minor gaps not inflated, false claims not excused.
- The recommendation follows the defined rules with specific rationale; handoff (Stage 14 or Stage 12) is clear.

---

## 11. Failure Modes to Avoid

- **Treating minor gaps as blocking** (overcorrects, blocks valid docs) or **treating all gaps as non-blocking** (lets false claims through) — apply the classification criteria strictly; slice-specific language is always blocking.
- **Using the slice spec as documentation authority** — the diff and evidence are truth.
- **Rewriting documentation as part of validation** — flag mismatches; do not fix them here, and do not share working context with the reconciler.

---

## 13. Handoff to Next Skill

**If PASS or CONDITIONAL-PASS:** advance to Stage 14 — Traceability & closeout. Pass forward the validation report file path, non-blocking gaps and follow-up issue candidates, and confirmation that documentation is cleared for closeout (to `traceability-matrix-builder` and `closeout-package-builder`).

**If FAIL:** return to Stage 12 — Current-state reconciliation. Pass forward the validation report file path and the list of blocking mismatches with specific correction requirements. `current-state-reconciler` must address these before re-running Stage 13.
