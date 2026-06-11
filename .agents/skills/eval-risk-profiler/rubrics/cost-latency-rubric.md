# Cost and Latency Rubric

Use this rubric in Section D of the eval risk profile to define cost and latency criteria that the eval contract must enforce.

Cost and latency are first-class eval dimensions, not implementation footnotes. For agentic systems built on Microsoft Azure AI, Copilot Studio, Azure AI Foundry, or Power Platform, cost and latency failures can materially affect user experience, operations, and budget — and they can be detected during eval if criteria are defined here.

---

## 1. Why Cost and Latency Belong in Eval Design

Agentic systems can enter unexpected loops, make redundant tool calls, or invoke expensive model operations in edge-case inputs. If no criteria are defined before implementation, there is no way to detect these behaviours during eval and they may surface only in production.

Defining cost and latency criteria at the risk-profile stage ensures:

- The eval contract can include cost/latency scenarios.
- The implementation plan can optimize for the right targets.
- Threshold violations are detectable during the eval run.
- Budgets are ratified by the human before they become binding commitments.

---

## 2. Latency Criteria

### 2.1 Response-Time Envelope

Define the expected end-to-end latency for the primary user-facing interaction:

| Scenario type | Target response time | Maximum acceptable | Notes |
|---|---|---|---|
| Standard interactive response | `<target, e.g., 5 s>` | `<max, e.g., 10 s>` | |
| Background processing / async | `<target>` | `<max>` | |
| High-complexity multi-step orchestration | `<target>` | `<max>` | |
| Regression eval run (batch) | `<target>` | `<max>` | |

If no budget has been provided by the user, propose reasonable defaults for the slice's complexity tier and flag them for human ratification.

**Microsoft-stack reference points:**

- Azure AI Foundry / Prompt Flow: measure latency at the flow level, not only at the model call level.
- Copilot Studio: end-to-end response includes connector latency, not only LLM latency.
- Power Platform: connector round-trip adds to total latency; measure the full orchestration.

### 2.2 Latency Outlier Rule

Define when a latency outlier should count as a failure in eval:

- A response that takes more than 2× the maximum acceptable latency is a failure unless the eval scenario explicitly permits extended processing.
- A response that exceeds the maximum acceptable latency on more than 20% of repeated runs is a systemic failure.

Adjust these thresholds for the slice's SLA context.

---

## 3. Token and Cost Criteria

### 3.1 Token Budget per Interaction

Estimate the expected token budget (input + output) for each interaction type. Use the slice spec to identify the typical input size (context, retrieved documents, conversation history) and expected output size.

| Interaction type | Expected input tokens | Expected output tokens | Total budget | Notes |
|---|---|---|---|---|
| Standard interaction | | | | |
| Complex multi-document retrieval | | | | |
| Adversarial / edge-case eval | | | | |

Token budgets should reflect the slice's typical operating range. A budget that allows 10× normal usage for a simple response is not a budget.

### 3.2 Cost per Interaction

Translate token budgets into approximate per-interaction cost estimates using current model pricing for the target model.

| Model | Input cost (per 1K tokens) | Output cost (per 1K tokens) | Estimated cost per standard interaction | Notes |
|---|---|---|---|---|
| `<target model>` | | | | |

If the cost per interaction is material relative to the project's operational budget, flag it for human ratification.

### 3.3 Cost Outlier Rule

Define when a cost outlier should count as a failure in eval:

- An interaction that consumes more than 3× the standard token budget is a failure unless the eval scenario explicitly involves a high-complexity input.
- An eval run in which more than 10% of interactions exceed the budget is a systemic failure.

---

## 4. Model and Tool-Call Count Criteria

Agentic systems may make multiple model calls, tool calls, or orchestration steps per user interaction. Unbounded call counts are a common source of runaway cost and latency.

### 4.1 Model Call Count

| Scenario type | Expected model calls | Maximum acceptable | Notes |
|---|---|---|---|
| Standard single-turn interaction | | | |
| Multi-step orchestration (normal path) | | | |
| Degraded / error-recovery path | | | |

### 4.2 Tool Call Count

| Tool name / category | Expected calls per interaction | Maximum acceptable | Notes |
|---|---|---|---|
| `<primary retrieval tool>` | | | |
| `<state-mutation tool>` | | | |
| `<external API tool>` | | | |

### 4.3 Loop Detection Rule

An agent that makes the same tool call more than twice in a row without making progress (defined as a change in workflow state or retrieved content) is in a loop. Loop detection is a required eval scenario for any Standard or High-Assurance slice that uses tool calls.

---

## 5. Measurement Plan

Specify how cost and latency will be measured during eval runs.

| Measurement concern | Recommended approach | Tool / service | Notes |
|---|---|---|---|
| End-to-end latency | Instrument at the flow / orchestration level | Azure AI Foundry metrics, Application Insights, Prompt Flow traces | |
| Per-call latency | Capture at model-call and tool-call level | Azure Monitor, Foundry tracing | |
| Token usage | Capture at completion call | Model response metadata, Foundry token tracking | |
| Tool-call count | Count tool invocations per orchestration run | Foundry traces, custom logging | |
| Cost estimate | Derive from token count × published price | Post-eval calculation or Foundry cost dashboard | |

---

## 6. Threshold Recommendation Format

For each threshold, specify:

- **Metric** — what is being measured.
- **Target** — expected normal value.
- **Threshold** — value above which the eval scenario counts as a failure.
- **Applies to** — which scenarios or eval types this threshold governs.
- **Ratification status** — `Human ratified` / `Proposed — requires human ratification` / `Blocked — no budget provided`.

If cost/latency budgets have not been provided, all thresholds should be marked `Proposed — requires human ratification`. Do not default to "no limit."

---

## 7. Special Cases

### 7.1 Streaming responses

If the slice uses streaming output (token-by-token delivery), latency criteria should address both time-to-first-token (TTFT) and total response time. TTFT is the user-perceived latency; total time is the cost exposure.

### 7.2 Batch or background operations

If the slice includes batch or background processing (e.g., nightly summaries, async document processing), latency criteria should address throughput per hour rather than per-interaction latency.

### 7.3 Cost accumulation across a session

For multi-turn agents, token cost accumulates across turns. Specify a session-level budget in addition to a per-turn budget if session cost is material.

### 7.4 Regression eval cost

Regression eval runs cost money. For large regression suites, specify a maximum per-run cost and consider whether regression evals should use a cheaper model tier for initial screening with the production model used for confirmation runs only.

---

## 8. Red Flags for Eval Contract Design

Flag the following for the `eval-contract-designer`:

- Any interaction type with no defined latency or cost target — do not proceed without one.
- Any tool that has no maximum call count — loop risk must be evaluated.
- Any retrieval pattern that may return unbounded document volume — context-window cost risk.
- Any eval scenario that requires a large number of model calls or tool invocations — may need special eval harness.
- Any model endpoint without a Canadian data-residency guarantee — intersects with Section C governance.
