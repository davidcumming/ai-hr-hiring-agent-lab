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

No Azure resources, Power Platform settings, Copilot Studio topics, secrets,
real applicant data, live Foundry wiring, production identity, or current-state
docs were changed in this implementation pass.

## 3. Copilot Studio Follow-Up

After this API/Swagger change is deployed or otherwise made available to the
custom connector, Copilot Studio needs a connector/API-definition update or
re-import. Expected manual steps:

1. Refresh or recreate the connector/connection if metadata is stale.
2. Add or select `retrieveEvaluationForCopilot`.
3. Bind the action body field `evaluation_id` to the stored topic variable,
   for example `Topic.submitted_evaluation_id`.
4. Do not use `Dynamically fill with AI` for this identifier.
5. Run the submit -> store `evaluation_id` -> retrieve smoke.
6. Capture redacted manual evidence without Function keys, connection secrets,
   tenant IDs, subscription IDs, real applicant data, or secret-bearing
   screenshots.

## 4. Validation Targets

Implementation validation should include:

- `python3 scripts/export_openapi.py --check`
- `python3 scripts/export_copilot_openapi.py --check`
- `python3 -m pytest`
- `git diff --check`
- a lightweight secret scan on changed files, with policy-wording false
  positives documented if present

## 5. E6 Recommendation

E6 should continue with `retrieveEvaluationForCopilot`. The slice should be
declared blocked only if Copilot Studio also cannot bind the stored topic
variable into this body field after the custom connector/API definition is
updated.
