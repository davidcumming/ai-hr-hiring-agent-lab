# ADR-0003: Database footprint consolidation

> **Status:** Proposed / pending (decision deferred; evaluate before the pattern hardens across capabilities)
> **Date:** 2026-06-09
> **Relates to:** R14 in `framework-assessment-and-recommendations.md`; `Initial_Documentation/40.2-technical-architecture-guidelines.md` §1.3, §8, §10, §10.1, §18

## Context

Each agentic capability currently provisions **four data services**:

- **Azure Table + Blob** — system of record and evidence ledger (state, idempotency, case ACLs in Table; documents, drafts, exports, evidence payloads in Blob).
- **Cosmos DB** — contextual memory persistence (behind the facade-owned Memory Service / SDK Adapter).
- **PostgreSQL + pgvector** — RAG / retrieval store (reference material and embeddings).

For a small team, that is four services to provision, secure, back up, residency-pin, and restore-test per capability. 40.2 §8 itself flags a sharp edge: **Azure Table Storage has no point-in-time restore**, forcing each capability to declare a bespoke backup/export mechanism, an RPO/RTO, and a periodic restore test. The cost of carrying four engines compounds as capabilities multiply.

The **binding principle to preserve** is the **role separation** that 40.2 §1.3 and §18 enforce: system of record ≠ memory ≠ RAG ≠ telemetry. That separation is a *responsibility* boundary, not a requirement that each role run on a distinct physical engine. Consolidating engines is acceptable only if the role boundaries (and their "must not" rules) remain intact in code and access control.

This decision should be made **before the four-service shape hardens** across HR Hiring, Communications Review, Meeting Notes, and future capabilities — retrofitting a consolidation across several live capabilities is far more costly.

## Options

**Option (a) — Cosmos DB serverless for state + memory + vectors (drop Postgres).**
Cosmos DB serverless holds workflow state, governed memory, and RAG vectors; **Azure Storage / Blob is retained for evidence payloads with immutability** regardless.

- *Pros:* PITR built in (addresses the Table-Storage gap §8 calls out); change feed is useful for the evidence-reconciliation sweeps (§5) and memory save-triggers (§10); DiskANN vector search eliminates Postgres + pgvector; one fewer engine to secure and residency-pin.
- *Cons:* concentrates state, memory, and RAG in one engine — the role-separation boundaries must be enforced rigorously in code and access control to avoid blurring system-of-record vs. memory vs. RAG; moving authoritative *state* off Azure Table changes the §8 system-of-record commitment and the same-partition entity-group-transaction pattern (§5) — this needs careful validation; Cosmos as system of record is currently a 40.2 anti-pattern (§20) and would require explicit reversal.

**Option (b) — Postgres for memory + RAG (drop Cosmos).**
PostgreSQL (with pgvector) holds both memory persistence and RAG; Cosmos is removed.

- *Pros:* one relational engine for both context stores; pgvector already in the stack for RAG; familiar backup/restore story; removes Cosmos as a separate service.
- *Cons:* the memory service contract (§10) would re-target Postgres — a memory-provider change that 40.2 §10 requires an approved ADR for; loses Cosmos change feed for save-triggers/reconciliation; relational schema for the proposed/confirmed/superseded/restricted/expired memory lifecycle must be designed.

**Option (c) — Status quo (four services).**
Keep Table+Blob, Cosmos, and Postgres+pgvector per capability.

- *Pros:* matches 40.2 as written; clean physical separation of roles; no migration.
- *Cons:* four services to operate per capability; the Table-Storage no-PITR backup burden persists; cost and operational surface grow with each capability.

## Recommendation

**Evaluate consolidation now and record the decision before the pattern hardens.** Of the consolidation paths, **Option (a) (Cosmos serverless for state + memory + vectors)** is the more attractive on operational grounds — PITR, change feed, and DiskANN directly address gaps the framework already names — **but only if** moving authoritative state off Azure Table can be reconciled with the §8 system-of-record commitment, the §5 transactional state-plus-evidence pattern, and the §20 anti-pattern that currently forbids Cosmos as system of record. If that reconciliation is not clean, prefer **Option (b)** (consolidate memory + RAG on Postgres, keep Azure Storage as system of record + evidence) as the lower-risk consolidation. **Keep Azure Storage / Blob immutability for the evidence ledger under every option.** Do not adopt Option (c) by default merely because it matches the current text — the assessment's point is to decide deliberately before lock-in.

## Consequences

- Whichever option is accepted, 40.2 (§1.3, §8, §10, §10.1, §18, §20) must be updated to match — including, for Option (a), an explicit reversal of the "Cosmos as system of record" anti-pattern and a revised system-of-record commitment. (40.2 edits are owned by another agent; this ADR is cross-referenced from 40.2.)
- A memory-provider change (Options a or b) triggers the §10 requirement for an approved ADR — this record can serve as that ADR once accepted.
- Residency pinning (§15) and restore testing simplify with fewer engines but must still cover every retained store.
- The role-separation invariant (§1.3, §18) is restated as a code/access-control boundary, not a physical-engine boundary.

## Open questions / what must be verified before acceptance

1. For Option (a): can Cosmos DB serverless satisfy the **system-of-record transactional guarantee** (atomic state + evidence-metadata commit, §5) and the optimistic-concurrency / ETag pattern (§8) the facade relies on? If not, state stays on Azure Table.
2. Confirm **Cosmos DB serverless PITR, change feed, and DiskANN vector search** are available in the Canadian Foundry/Azure regions in scope (ties to ADR-0004).
3. For Option (b): design the relational schema for the full memory status lifecycle (`proposed`/`advisory`/`confirmed`/`rejected`/`superseded`/`restricted`/`audit-only`/`expired`) and confirm pgvector performance for the RAG corpus sizes expected.
4. Confirm Blob versioning + time-based immutability remain the evidence-payload store under the chosen option (held firm regardless).
5. Cost-model the consolidated footprint vs. status quo per capability at expected scale.
