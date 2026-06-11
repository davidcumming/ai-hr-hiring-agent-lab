# ADR-0004: Canadian data-residency verification checklist

> **Status:** Proposed / pending (verification checklist; status of each check is "pending verification")
> **Date:** 2026-06-09
> **Relates to:** R18 in `framework-assessment-and-recommendations.md`; `Initial_Documentation/40.2-technical-architecture-guidelines.md` §15, §19; `40.8 Privacy, Data Residency, and Auditability Policy` (§40.8 of the Process Doc)

## Context

40.2 §15 handles residency for the Azure data-bearing services well: a single declared region of record, co-located stores, residency-honouring Foundry endpoints, and no silent cross-border movement. Two boundary points sit at the edge of that coverage and deserve **explicit, recorded verification** before the first PHI-adjacent capability:

1. **Model availability in Canadian Foundry regions.** Not every model or model version is deployable in **Canada Central / Canada East**. A capability designed around a model that is unavailable in-region forces a cross-region inference exception — exactly the kind of unrecorded cross-boundary movement §15 prohibits.
2. **Copilot Studio cross-geo data movement for generative features.** Generative features in Power Platform environments can involve data movement outside the environment's geography unless the relevant admin settings restrict it. The front door (Copilot Studio) is the one layer not fully inside the Azure residency boundary 40.2 §15 pins.

**This ADR does not assert current Azure or Power Platform behaviour.** Both change frequently. It frames the two checks as a verification checklist to be performed and recorded per capability, with each item carrying status **"pending verification."** The findings belong in each capability's specialization overlay (40.2 §19) and, where the project handles sensitive data, in the §40.8 Privacy / Residency / Auditability policy.

## Options

**Option (a) — Add the two checks as a mandatory verification checklist in the new-capability process, recorded per capability.**
Each capability must perform and record both checks before its first PHI-adjacent slice; findings go in the overlay.

- *Pros:* makes the two known boundary risks explicit and auditable; aligns with §15's "no silent cross-border movement" and §19's overlay model; cheap to run; catches an unavailable-model design before it forces a cross-region exception.
- *Cons:* adds two items to the new-capability checklist; requires re-verification when models or platform settings change.

**Option (b) — Rely on the existing §15 residency guardrails without explicit per-capability checks.**

- *Pros:* no checklist additions.
- *Cons:* §15 does not currently call out model-in-region availability or Copilot Studio generative cross-geo movement specifically; the gaps stay implicit and can surface only after a capability is designed around an unavailable model.

## Recommendation

**Adopt Option (a) — add both checks to the 40.2 §19 new-capability checklist and record the findings in each capability overlay**, with each item tracked as "pending verification" until confirmed for that capability and region. (The 40.2 §19 edit is owned by another agent; this ADR records the decision and the checklist.) Treat this as a standing verification step, not a one-time assertion.

## Verification checklist (record per capability; status "pending verification" until confirmed)

| # | Check | What to confirm | Where recorded | Status |
|---|---|---|---|---|
| 1 | **Model availability in Canadian Foundry regions** | The specific model and version the capability uses is deployable in **Canada Central** and/or **Canada East**; if not, an approved cross-region inference exception is recorded with its residency impact. | Capability overlay (40.2 §19, item 11 residency) | Pending verification |
| 2 | **Copilot Studio cross-geo data movement for generative features** | Generative features of the capability's Copilot Studio agent do not move data outside the approved Canadian geography, or the relevant Power Platform admin settings are confirmed to restrict such movement; any residual movement is approved and recorded. | Capability overlay + §40.8 policy where sensitive data is in scope | Pending verification |

## Consequences

- 40.2 §19 gains the two checklist items; each capability overlay records the findings and their verification date.
- Where a model is unavailable in-region, the capability either re-selects a model or records an approved cross-region inference exception (§15) — it does not silently proceed.
- The §40.8 Privacy / Residency / Auditability policy references this checklist for projects handling sensitive / PHI data.
- Both checks are re-run when the model/version changes or when Power Platform residency settings change.

## Open questions / what must be verified before acceptance

1. Confirm, **at decision time**, the current set of models/versions available in Canada Central / Canada East for the capabilities planned (Microsoft availability changes frequently — verify, do not assume).
2. Confirm the **current** Power Platform / Copilot Studio admin controls governing generative-feature cross-geo data movement and whether they are tenant- or environment-scoped.
3. Decide where the canonical record lives when a project has no §40.8 policy yet (exploratory non-sensitive projects) — default to the capability overlay until §40.8 is authored.
4. Define the re-verification trigger (model/version change, platform setting change) so the checks do not silently go stale.
