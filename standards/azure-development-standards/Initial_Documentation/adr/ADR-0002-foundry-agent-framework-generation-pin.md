# ADR-0002: Microsoft Foundry / Agent Framework generation pin

> **Status:** Proposed / pending (decision deferred)
> **Date:** 2026-06-09
> **Relates to:** R12 in `framework-assessment-and-recommendations.md`; `Initial_Documentation/40.2-technical-architecture-guidelines.md` §1.1, §1.3, §6

## Context

The platform moved under the framework's feet. At Build 2026, **Azure AI Foundry was renamed Microsoft Foundry**; **Microsoft Agent Framework 1.0 reached GA** (the production successor to the Semantic Kernel / AutoGen patterns, with skills, memory, and middleware as first-class concepts); and a **next-generation Foundry Agent Service** is GA, built on the OpenAI **Responses API**.

40.2 already references "Foundry Agent Service / Agent Framework 1.0 workflow" as the multi-step backend in its stack diagram (§1.1), division-of-responsibility table (§1.3), and Foundry usage boundaries (§6 decision table). What it does not do is *pin a generation* — it does not say which release of the Agent Framework and Foundry Agent Service new capabilities should target, nor record the Responses-API basis of the next-gen Agent Service. Without a pinned generation, capabilities risk being built against mixed or assumed versions, and the §6 "smallest backend that meets the need" table's right-hand column has no stable anchor.

The §6 decision logic itself — default to a model endpoint for single bounded structured generation; use a workflow for tool use, multi-step reasoning, multi-agent propose/validate, or reusable traceable capabilities — remains valid regardless of generation. This ADR pins the *target generation*, not the decision logic.

## Options

**Option (a) — Pin to the GA stack: Microsoft Agent Framework 1.0 GA + next-gen Foundry Agent Service on the Responses API.**
New capabilities target Agent Framework 1.0 workflows for multi-step/multi-agent backends and the next-gen Foundry Agent Service (Responses API) as the agent runtime.

- *Pros:* targets production-grade, supported releases; first-class skills/memory/middleware in Agent Framework 1.0; aligns the §6 right-hand column on a single named generation; matches the direction Microsoft is steering new work.
- *Cons:* requires confirming feature parity for the specific capabilities planned (e.g. memory providers, tracing/eval) on these exact releases; Responses-API behaviours must be validated against the facade's output-validation and retry contract.

**Option (b) — Pin to the prior generation (classic Foundry Agent Service / pre-1.0 framework patterns).**
Continue on the generation 40.2 was originally written against.

- *Pros:* no migration; existing assumptions hold.
- *Cons:* targets a superseded generation; misses Agent Framework 1.0's first-class skills/memory/middleware; diverges from current Microsoft naming and guidance; accrues migration debt.

**Option (c) — No pin (status quo).**
Leave the generation unspecified.

- *Pros:* none beyond deferral.
- *Cons:* capabilities built against mixed/assumed versions; re-eval triggers (process §21) cannot reference a stable backend generation; the naming-sweep recommendation (R12) stays unresolved.

## Recommendation

**Adopt Option (a) — pin new capabilities to Microsoft Agent Framework 1.0 GA and the next-generation Foundry Agent Service on the Responses API.** Re-anchor the 40.2 §6 decision table's right-hand column on Agent Framework 1.0 workflows (a 40.2 edit owned by another agent — this ADR records the decision, not the edit). Pair acceptance with the terminology sweep R12 calls for (Azure AI Foundry → Microsoft Foundry across 40.2 and the skills).

## Consequences

- 40.2 §1.1 / §1.3 / §6 are updated to name Agent Framework 1.0 and the next-gen Foundry Agent Service (Responses API) as the pinned target; terminology sweep renames Azure AI Foundry → Microsoft Foundry.
- The per-generation metadata recorded per generation (§6: model/agent/workflow ID and version, trace/eval IDs) gains a generation marker, so re-eval triggers (§21.1) can fire on a generation change.
- Memory and tracing/eval choices (§10, and R13's Foundry-evaluations harness) are evaluated against Agent Framework 1.0 capabilities specifically.

## Open questions / what must be verified before acceptance

1. **Confirm GA status and Canadian-region availability** of Agent Framework 1.0 and the next-gen Foundry Agent Service for the regions in scope (ties to ADR-0004 residency verification).
2. Verify that the **Responses-API** behaviour of the next-gen Agent Service is compatible with the facade's output-schema validation, bounded corrective-retry, and 429/backoff contract (40.2 §6).
3. Confirm **feature parity** for the capabilities planned — in particular any Agent Framework memory providers vs. the current Cosmos-backed memory service (40.2 §10 requires an approved ADR for any memory-provider change; coordinate with that requirement).
4. Confirm the **exact current product names** at decision time (platform naming has changed recently; verify before propagating the terminology sweep).
