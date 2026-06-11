# Risk Tier Rubric

Use this rubric in Section A of the eval risk profile. Work through every indicator before assigning a tier. Never average indicators — use the highest applicable tier.

---

## Tier Definitions

### Low

Assign `Low` only when the slice has limited behavioural and governance risk and **all** of the following are true:

- No PHI or sensitive PII is processed, stored, or transmitted.
- No approval, rejection, escalation, or authoritative decision with consequence.
- No external sharing, export, or notification.
- No memory write/read that affects future user or business decisions.
- No permission or authorization change.
- No irreversible or hard-to-reverse state change.
- No audit-sensitive workflow step.
- No material cost or latency risk.
- No meaningful harm if agent output is slightly wrong.
- Behaviour can be validated with a small set of deterministic tests and low-risk live evals.

**Typical examples:** read-only information display; internal formatting or sorting; draft generation with no persistent state; lookup-only tool calls.

---

### Standard

Assign `Standard` when the slice supports normal product workflow behaviour where mistakes matter but are correctable.

**Typical Standard traits:**

- Internal workflow state changes (e.g., status transitions, assignment).
- User-facing explanations or summaries — not authoritative.
- Normal clarifying-question behaviour.
- Bounded tool use with reversible side effects.
- Non-sensitive data capture or validation.
- Limited persistence with audit trail.
- Moderate documentation impact.
- Live-model evals required but not intensive human review.
- Failures can usually be remediated through implementation, prompt, or workflow changes without major governance review.

**Typical examples:** intake request routing; draft status update; reviewer assignment; non-sensitive form fill; workflow state clarification.

---

### High-Assurance

Assign `High-Assurance` when the slice touches any material risk area.

**Any one of these triggers High-Assurance:**

| Trigger | Why it elevates tier |
|---|---|
| Approvals, rejections, recommendations, or workflow decisions with consequence | Incorrect output can affect rights, entitlements, or safety |
| Evidence claims or source-grounded assertions | False grounding can mislead; downstream actions may rely on it |
| PHI (Protected Health Information) | Regulated; breach has legal, clinical, and reputational consequences |
| Sensitive PII | Privacy obligations; potential harm to individuals |
| Canadian data residency obligation | Regulated; data may not leave approved regions |
| Auditability obligation | Regulatory or governance requirement to retain evidence |
| External sharing, export, or notification | Data leaves the controlled environment |
| Memory behaviour that affects future decisions | Persistent state can propagate errors across sessions |
| Permissions, identity, roles, or authorization changes | Misconfiguration can create unauthorized access |
| Irreversible or hard-to-reverse state changes | Mistakes cannot be easily undone |
| User-facing authoritative outputs (e.g., recommendations with clinical/legal weight) | Users may rely on output without independent verification |
| Healthcare workflow implications | Patient safety, clinical workflow integrity |
| Safety, compliance, legal, reputational, or trust risk | Broad risk category |
| Cost or latency risk that could materially affect operations | Budget exposure or SLA violation |
| Manual configuration/source-control debt that could hide implementation truth | Evidence integrity risk |

If any trigger applies materially, classify as `High-Assurance` unless the user explicitly approves a lower tier with documented rationale.

---

## Uncertainty Tiers

Use when the risk cannot be determined with available information:

| Uncertainty tier | When to use |
|---|---|
| `Standard with unresolved risk` | Likely Standard but one or more indicators are unknown |
| `High-Assurance pending clarification` | At least one High-Assurance trigger may apply; needs clarification |
| `Blocked pending clarification` | Cannot assign a defensible tier without missing information |

---

## Risk Indicator Scorecard

Complete this for every profile. Columns: Indicator | Applies (Yes/No/Unknown) | Severity (Low/Medium/High/Unknown) | Notes.

| Indicator | Applies? | Severity | Notes |
|---|---|---|---|
| PHI | | | |
| PII | | | |
| Sensitive business data | | | |
| Canadian data residency | | | |
| Auditability obligation | | | |
| Approval/rejection/decision behaviour | | | |
| Evidence claims or grounded assertions | | | |
| External sharing, export, or notification | | | |
| Memory behaviour (write/read affecting future behaviour) | | | |
| Permissions, identity, authorization | | | |
| Irreversible or hard-to-reverse state changes | | | |
| Authoritative user-facing output | | | |
| Healthcare workflow implications | | | |
| Safety, compliance, legal, or trust risk | | | |
| Cost/latency operational risk | | | |
| Manual-config/source-control debt | | | |

---

## Split Recommendation

If the high-assurance element is separable from a lower-risk remainder, recommend splitting the slice. This allows the lower-risk portion to proceed with lighter eval treatment while the high-risk portion gets appropriate rigor.

Criteria for recommending a split:

- The high-risk behaviour is in a discrete functional area with clear boundaries.
- The two portions can each be independently implemented, tested, and closed out.
- The split does not create circular dependencies that would block either sub-slice.
- Splitting does not fragment a single coherent user outcome.

---

## Classification Principles

1. **Use the highest applicable tier.** Do not average indicators.
2. **When uncertain, escalate.** Missing privacy, architecture, or data-governance information is itself a risk signal.
3. **Distinguish risk from complexity.** A technically simple slice can be High-Assurance. A technically complex slice can be Standard.
4. **Eval burden matters.** If live evals require human review, repeated high-confidence thresholds, privacy-safe fixtures, or adversarial scenarios, the slice is likely High-Assurance.
5. **Manual-config debt matters.** If portal or low-code configuration is not source-controlled and affects behaviour, permissions, data, or auditability, elevate tier or require a follow-up issue.
