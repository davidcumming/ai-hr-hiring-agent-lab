# Implementation Notes: E6 Copilot-Friendly Retrieve Wrapper

## 1. Summary

E6 manual Copilot Studio implementation found that Copilot Studio could not
reliably bind a stored topic variable into the existing path-parameter action
`getEvaluation.evaluation_id`. The topic editor stripped the explicit YAML
binding after save and reported that the input binding was not eligible or no
longer found.

To keep the E6 state-handoff goal moving without changing retrieval semantics,
the API now exposes an additive wrapper:

| Method | Path | operationId | Purpose |
|---|---|---|---|
| `POST` | `/api/evaluations/retrieve` | `retrieveEvaluationForCopilot` | Copilot-friendly retrieve action with `evaluation_id` supplied as a JSON body field. |

The existing route remains unchanged:

| Method | Path | operationId |
|---|---|---|
| `GET` | `/api/evaluations/{evaluation_id}` | `getEvaluation` |

## 2. What Changed

- Added `EvaluationRetrieveRequest` with only `evaluation_id`.
- Added `POST /api/evaluations/retrieve`, which authenticates first, validates
  the body second, and reuses the same retrieve envelope logic as the GET
  route.
- Preserved the standard response envelope:
  - unknown IDs return HTTP 200 with `status="validation_failed"`;
  - successful reads return HTTP 200 with `status="completed"` and the full
    persisted audit record;
  - missing identity remains HTTP 401 and non-`hr` callers remain HTTP 403.
- Regenerated the source OpenAPI contract and the curated Copilot Studio
  Swagger artifact.
- Kept `getEvaluation` in the Copilot Swagger so existing explicit-ID/manual
  retrieve usage remains available.
- Updated the Power Apps custom connector from
  `openapi/copilot-studio/evaluations-tool.swagger.json` so it exposes
  `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`.

No secrets, real applicant data, live Foundry wiring, production identity, or
current-state docs were changed in this documentation/evidence pass.

## 3. Manual Copilot Studio Result

The manual Copilot Studio implementation completed after the connector update
and a tool-routing correction:

- The new backend endpoint `POST /api/evaluations/retrieve` was deployed and
  directly tested.
- The custom connector test for `retrieveEvaluationForCopilot` succeeded with
  HTTP 200, `status="completed"`, and an `evaluation_id` match.
- The topic `E6 Evaluate Sample Candidate` calls `submitEvaluation`, stores the
  returned `evaluation_id` in `submitted_evaluation_id`, and reuses that stored
  value for `retrieveEvaluationForCopilot`.
- The final Copilot Studio test prompt `Evaluate the sample candidate.`
  completed the topic and displayed `eval-a427db3ad61c4e8eac20`.
- The final response preserved advisory-only and human-review-required language
  and used only synthetic sample-candidate data.

The remaining issue was Copilot Studio tool routing precedence, not the
body-based retrieve wrapper. The standalone `submitEvaluation` tool initially
pre-empted the topic until `submitEvaluation` and
`retrieveEvaluationForCopilot` were set to `Only when referenced by topics or
agents`.

Manual evidence is captured in
`docs/delivery/slices/slice-e6-copilot-evaluation-id-state/manual-config-evidence.md`.
No Function key, connection secret, tenant ID, subscription ID, real applicant
data, or secret-bearing screenshot is recorded there.

## 4. Validation Targets

Implementation validation should include:

- `python3 scripts/export_openapi.py --check`
- `python3 scripts/export_copilot_openapi.py --check`
- `python3 -m pytest`
- `git diff --check`
- a lightweight secret scan on changed files, with policy-wording false
  positives documented if present

## 5. E6 Recommendation

E6 should continue to use `retrieveEvaluationForCopilot` for topic-driven
retrieve workflows. Future Copilot Studio topic-driven connector actions should
use topic/agent referenced availability instead of broad direct agent use when
standalone tools would otherwise pre-empt the intended topic.
