# Architecture Decision Records (ADR) Index

> **Status:** Draft register. The records below are **proposed, not accepted.** Each captures the options and a recommendation for a decision the team has deferred; none is binding until the team marks it Accepted after the verification noted in its "Open questions" section.
> **Source:** These ADRs were drafted from the recommendations in `framework-assessment-and-recommendations.md` (R7, R8, R12, R14, R18) per the `remediation-plan.md` rule: "draft ADRs and add pending-decision checklist items rather than make the call."
> **Template:** Each ADR follows a lightweight format — Title, Status, Date, Context, Options, Recommendation, Consequences, Open questions / what must be verified before acceptance.

## How to use this register

A proposed ADR records a decision the team has not yet made. Read it to understand the options on the table and the recommended direction, but do not treat its recommendation as a committed architecture choice. To accept an ADR, complete the verification listed in its "Open questions" section, change its Status to `Accepted` (with the date and approver), and propagate any consequent edits into the affected documents named in the record.

This index is the canonical list of ADRs. The mature ADR template and a full index are part of the §41 mature-documentation backlog; this is a lightweight interim register seeded with the assessment's deferred decisions.

## Records

| ADR | Title | Status | Recommendation | Relates to |
|---|---|---|---|---|
| [ADR-0001](ADR-0001-orchestrator-topology.md) | Orchestrator topology (subagent vs. main-session dispatch) | Proposed / pending | Run the orchestrator in the main session if nested subagent dispatch is unsupported | R8 |
| [ADR-0002](ADR-0002-foundry-agent-framework-generation-pin.md) | Microsoft Foundry / Agent Framework generation pin | Proposed / pending | Pin new capabilities to Agent Framework 1.0 GA + next-gen Foundry Agent Service (Responses API) | R12 |
| [ADR-0003](ADR-0003-database-footprint-consolidation.md) | Database footprint consolidation | Proposed / pending | Evaluate consolidation before the four-service pattern hardens; preserve role separation | R14 |
| [ADR-0004](ADR-0004-canadian-residency-verification.md) | Canadian data-residency verification checklist | Proposed / pending | Verify and record two residency checks per capability (pending verification) | R18 |
| [ADR-0005](ADR-0005-skill-agent-source-location.md) | Skill/agent source location (un-hiding the package) | Proposed / pending | Un-hide the canonical source + add a sync/install script, as a dedicated follow-up | R7 |

## Status legend

- **Proposed / pending** — drafted; options and a recommendation are stated, but the team has not decided. The "Open questions" section lists what must be verified before acceptance.
- **Accepted** — the team has decided; the record is binding and its consequences have been propagated into the affected documents.
- **Superseded** — replaced by a later ADR (link the successor).
