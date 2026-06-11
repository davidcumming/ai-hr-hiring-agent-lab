# Reconciled Planning Context: <Topic or Capability Area>

## 1. Context Metadata

| Field | Value |
|---|---|
| Context ID | `<context-id>` |
| Topic / Capability Area | `<topic>` |
| Date Created | `<yyyy-mm-dd>` |
| Created By | `<agent/user>` |
| Documentation Repo Reference | `<path/link/description>` |
| Code Repo Baseline | `<branch/commit/current-state-doc-reference>` |
| Status | `Draft / Ready for Slice Planning / Blocked` |

## 2. Planning Question or Target Area

The planning question or capability area being reconciled.

## 3. Inputs Reviewed

| Input Type | Reference | Notes |
|---|---|---|
| Documentation repo source | `<reference>` | `<notes>` |
| Current-state doc | `<reference>` | `<notes>` |
| Architecture guideline | `<reference>` | `<notes>` |
| Actual architecture | `<reference>` | `<notes>` |
| ADR | `<reference>` | `<notes>` |
| Implementation lesson | `<reference>` | `<notes>` |
| Process lesson | `<reference>` | `<notes>` |
| Known limitation | `<reference>` | `<notes>` |
| GitHub Issue | `<reference>` | `<notes>` |
| Test/eval summary | `<reference>` | `<notes>` |

## 4. Source Authority Summary

| Claim Type | Authority Used |
|---|---|
| Current product behaviour | `<source>` |
| Strategic intent | `<source>` |
| Architecture rules | `<source>` |
| Unresolved work | `<source>` |
| Verified behaviour | `<source>` |
| Known limitations | `<source>` |

## 5. Current-State Baseline

What the current product already supports here. No aspirational claims unless confirmed by current-state docs or evidence.

## 6. Strategic Intent Summary

What the documentation repo says should eventually exist. Label as intent, not current reality.

## 7. Reconciliation Findings

| ID | Finding | Category | Source(s) | Planning Impact |
|---|---|---|---|---|
| RF-001 | `<finding>` | `aligned / already-implemented / partially-implemented / planned-or-aspirational / stale-or-contradicted / blocked / requires-adr / requires-eval-design / requires-privacy-review / manual-config-risk / candidate-for-next-slice / strategic-doc-update-recommended` | `<sources>` | `<impact>` |

## 8. Already Implemented Capabilities

| Capability | Evidence | Planning Impact |
|---|---|---|
| `<capability>` | `<evidence>` | `Do not re-plan / May extend / Needs doc update` |

## 9. Partially Implemented Capabilities

| Capability | Implemented Portion | Remaining Gap | Candidate for Slice? |
|---|---|---|---|
| `<capability>` | `<implemented>` | `<gap>` | `Yes / No / Maybe` |

## 10. Planned or Aspirational Capabilities

| Capability | Strategic Source | Current-State Status | Notes |
|---|---|---|---|
| `<capability>` | `<source>` | `Not implemented / Unknown` | `<notes>` |

## 11. Stale or Contradicted Assumptions

| Assumption | Contradicting Source | Recommended Treatment |
|---|---|---|
| `<assumption>` | `<source>` | `Ignore for planning / Update strategic docs / Requires decision` |

## 12. Architecture and ADR Implications

| Item | Impact | Action |
|---|---|---|
| `<guideline/ADR implication>` | `<impact>` | `No action / Draft ADR / Update guideline / Block planning` |

## 13. Known Limitations and GitHub Issue Impacts

| Issue / Limitation | Impact on Planning | Required Action |
|---|---|---|
| `<issue/limitation>` | `<impact>` | `<action>` |

## 14. Testing and Eval Implications

| Behaviour / Capability | Test/Eval Implication | Readiness |
|---|---|---|
| `<behaviour>` | `<test/eval need>` | `Ready / Needs eval design / Blocked` |

## 15. Privacy, Data Residency, and Auditability Implications

| Concern | Applies? | Planning Impact |
|---|---|---|
| PHI | `Yes / No / Unknown` | `<impact>` |
| PII | `Yes / No / Unknown` | `<impact>` |
| Canadian data residency | `Yes / No / Unknown` | `<impact>` |
| Audit trail | `Yes / No / Unknown` | `<impact>` |
| Sensitive eval data | `Yes / No / Unknown` | `<impact>` |
| External sharing | `Yes / No / Unknown` | `<impact>` |

## 16. Manual Configuration and Source-Control Risks

| Surface / Component | Risk | Planning Impact | Follow-Up Needed |
|---|---|---|---|
| `<Azure/Power Platform/Copilot Studio/Foundry/Entra/etc.>` | `<risk>` | `<impact>` | `Yes / No / Unknown` |

## 17. Candidate Next-Slice Areas

Planning candidates only — does not create the slice spec.

| Candidate | Business/Process Outcome | Readiness | Main Risk | Recommended Next Action |
|---|---|---|---|---|
| `<candidate>` | `<outcome>` | `Ready / Not Ready / Blocked` | `<risk>` | `Use slice-sizer / Use slice-spec-generator / Resolve blocker / Draft ADR / Clarify requirement` |

## 18. Blockers and Open Questions

| ID | Blocker / Question | Blocking? | Owner / Next Action |
|---|---|---|---|
| BQ-001 | `<question>` | `Yes / No` | `<action>` |

## 19. Recommended Handoff

**Recommendation:** `<slice-sizer / slice-spec-generator / adr-gap-detector / strategic-doc-update-recommender / manual-config-debt-monitor / human clarification required>`

**Rationale:** `<brief reason>`

## 20. Strategic Documentation Update Recommendations

| Recommendation | Reason | Priority |
|---|---|---|
| `<recommended update>` | `<reason>` | `High / Medium / Low` |
