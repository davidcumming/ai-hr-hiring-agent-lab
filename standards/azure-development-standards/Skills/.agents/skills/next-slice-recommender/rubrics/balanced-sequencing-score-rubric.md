# Balanced Sequencing Rubric

Assess each unblocked next-slice candidate against all ten dimensions below. Record a short rationale per dimension and a qualitative standing (e.g. strong / moderate / weak / blocked). There is no numeric total — rank candidates by overall sequencing strength, then apply the two hard rules.

## Dimensions

- [ ] **Business value** — Does it directly enable a primary user/process outcome with clear stakeholder value, or only enable distant/foundational value?
- [ ] **Dependency order** — Is it independent and does it enable future high-value slices, or does it depend on unresolved prior work?
- [ ] **Testability** — Are acceptance criteria and deterministic test scope well-defined, or vague/unknown?
- [ ] **Eval readiness** — Can live-model eval scenarios be drafted now, or is the behaviour too ambiguous to evaluate?
- [ ] **Technical risk** — Does it fit proven patterns, or introduce significant new architecture / external dependencies?
- [ ] **Demo/stakeholder value** — Is it visible and demonstrable to stakeholders now? (Weight lower if demos are not a priority at this stage.)
- [ ] **Unresolved issue impact** — Are related open GitHub Issues absent, constraining, or directly blocking?
- [ ] **Architecture readiness** — Are required guidelines and ADRs in place, or is an ADR needed before spec generation?
- [ ] **Manual-config / source-control risk** — Are changes source-controllable, or would they push manual-config debt toward/over the ceiling?
- [ ] **Implementation complexity** — Is it low-complexity with proven patterns, or high-complexity with unknown patterns and large scope?

## Hard Rules

1. A candidate that is **blocked on dependency order** (an unresolved dependency must complete first) must not be selected until the dependency is resolved.
2. A candidate that is **not testable / not eval-ready** (behaviour cannot be defined well enough to test or evaluate) is blocked for selection — it cannot enter spec generation until the behaviour is defined.

A candidate that trips either hard rule is a blocked candidate: list it separately with its blocking reason and required resolution; do not rank it first.
