# Copilot Studio Registration Guide - Candidate Evaluation Tools

Status: current lab registration guide. This guide prepares a human to
register or refresh the three evaluation API actions in Copilot Studio or
Power Platform. It does not create Azure resources, register Copilot Studio
automatically, enable Entra auth, enable Foundry, export Copilot ALM, or
change the runtime API.

## Contract artifacts

Use these two artifacts for different purposes:

| Artifact | Purpose |
|---|---|
| `openapi/evaluations-api.json` | Source API contract for the FastAPI app. Generated from the app factory as OpenAPI 3.1 and drift-checked by `scripts/export_openapi.py --check`. Do not replace it with the curated connector file. |
| `openapi/copilot-studio/evaluations-tool.swagger.json` | Curated Swagger 2.0 registration artifact for Copilot Studio and Power Platform custom connector import. It contains `submitEvaluation`, `getEvaluation`, and `retrieveEvaluationForCopilot`, and intentionally supports fixture-reference evaluation only for Copilot-facing submit. |

The curated Swagger file is environment-neutral. Its `host` is the synthetic
placeholder `function-app-host.example`; set the real host in the connector or
REST/API tool UI after deriving it from Azure. The artifact uses `basePath: /`,
`schemes: [https]`, and paths `/api/evaluations`,
`/api/evaluations/{evaluation_id}`, and `/api/evaluations/retrieve` because
`host.json` leaves the Azure Functions route prefix empty.

The Copilot-facing submit action exposes only safe synthetic-fixture lab
request fields: `position_id`, `candidate_ref`, optional `idempotency_key`,
optional `evaluation_question`, and optional `requested_rigor`. It
intentionally does not expose inline applicant text fields. Do not submit
inline resumes, cover letters, or real applicant data through this
Copilot-facing tool. Inline applicant text remains outside Copilot Studio
registration scope, even though the underlying FastAPI source API still
supports it in the OpenAPI 3.1 contract.

The Copilot-friendly retrieve action is
`retrieveEvaluationForCopilot` (`POST /api/evaluations/retrieve`). It accepts
only body field `evaluation_id` and is the preferred action when a Copilot
Studio topic stores an evaluation id in a workflow variable. The canonical
explicit-ID read remains `getEvaluation` (`GET /api/evaluations/{evaluation_id}`)
for clients that can reliably supply the path parameter.

## Manual registration checklist

1. In Copilot Studio or Power Platform, start the REST/API tool or custom
   connector import flow.
2. Import `openapi/copilot-studio/evaluations-tool.swagger.json`.
3. Review the general connector settings and replace the placeholder host with
   the current generated Function App host for the lab environment.
4. Configure API key authentication in a header named `x-functions-key`.
5. Supply the Function key only in the secure connection or authentication
   configuration. Never paste the key into Swagger, Markdown, shell examples,
   screenshots, source control, or issue text.
6. Select exactly three actions:
   - `submitEvaluation`
   - `getEvaluation`
   - `retrieveEvaluationForCopilot`
7. Confirm the descriptions remain advisory-only and make clear that the tool
   returns decision support for human review, not a hiring decision.
8. Test submit only with the synthetic fixture-reference payload:

```json
{
  "position_id": "pos-sample-001",
  "candidate_ref": "cand-sample-001"
}
```

## Temporary lab identity headers

The hosted Function App currently has two auth layers:

| Layer | Current lab behavior |
|---|---|
| Azure Functions host auth | Function-level auth. The connector supplies the Function key through secure header auth named `x-functions-key`. |
| App-level lab auth | Temporary simulated headers: `X-Lab-Actor-Id`, `X-Lab-Roles`, optional `X-Lab-Actor-Display`. These are not production identity and are not an Entra substitute. |

Preferred lab path:

- If the Copilot Studio, REST/API tool, or custom connector UI supports static,
  default, hidden, or internal header parameters, configure:
  - `X-Lab-Actor-Id`: `copilot-lab-user`
  - `X-Lab-Roles`: `hr`
  - `X-Lab-Actor-Display`: `Copilot Lab User`
- Then test `submitEvaluation`, copy or store the returned `evaluation_id`,
  and test both `getEvaluation` and `retrieveEvaluationForCopilot`.

Fallback path:

- If static/default/internal headers are not supported, create the REST/custom
  connector actions and verify that the three actions import correctly, but do
  not claim end-to-end Copilot invocation is complete.
- End-to-end invocation must wait until connector policy/header support is
  configured or a later Entra-auth slice replaces the simulated `X-Lab-*`
  headers.

## Topic workflow checklist

The current manual lab topic workflow is intentionally narrow:

1. Use a single synthetic sample-candidate topic such as
   `E6 Evaluate Sample Candidate`.
2. On the submit path, call `submitEvaluation` with `pos-sample-001` and
   `cand-sample-001`.
3. Store the returned response-envelope `evaluation_id` in an explicit
   topic/workflow variable, currently `submitted_evaluation_id`.
4. On the retrieve path, call `retrieveEvaluationForCopilot` and bind
   `submitted_evaluation_id` to body field `evaluation_id`.
5. Do not use `Dynamically fill with AI` for `evaluation_id`.
6. Set `submitEvaluation` and `retrieveEvaluationForCopilot` availability to
   `Only when referenced by topics or agents` so broad standalone tool routing
   does not pre-empt the topic workflow.
7. Render the result as an advisory/audit summary requiring human review.

Manual evidence for this workflow is note-based and partial. No
source-controlled Copilot topic export, connector export, durable screenshot,
transcript, production identity, or live Foundry evidence is stored in the
repo.

## Hosted smoke commands

These commands validate the hosted API contract outside Copilot Studio. They
derive the generated Function App hostname dynamically and pass the Function
key through a shell variable. They do not print the key.

```bash
cd "/Users/davidcumming/coding_projects/ai-hr-hiring-agent-lab"

HOST="$(az resource show \
  --resource-group rg-hrha-lab-cac \
  --resource-type Microsoft.Web/sites \
  --name func-hrha-lab-cac001 \
  --query 'properties.defaultHostName' \
  -o tsv)"

APP_URL="https://$HOST"
read -rsp "Function key: " HRHA_FUNCTION_KEY
printf '\n'

IDEMPOTENCY_KEY="copilot-lab-$(date +%s)"

POST_RESPONSE="$(curl -sS -X POST "$APP_URL/api/evaluations" \
  -H "content-type: application/json" \
  -H "x-functions-key: ${HRHA_FUNCTION_KEY:?set HRHA_FUNCTION_KEY}" \
  -H "X-Lab-Actor-Id: copilot-lab-smoke" \
  -H "X-Lab-Roles: hr" \
  -H "X-Lab-Actor-Display: Copilot Lab Smoke" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  --data-binary '{"position_id":"pos-sample-001","candidate_ref":"cand-sample-001"}')"

EVALUATION_ID="$(printf '%s' "$POST_RESPONSE" | python3 -c \
  'import json,sys; d=json.load(sys.stdin); print(d.get("evaluation_id") or (d.get("result") or {}).get("evaluation_id") or "")')"

if [ -z "$EVALUATION_ID" ]; then
  printf '%s\n' "POST did not return evaluation_id. Response keys:"
  printf '%s' "$POST_RESPONSE" | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin).keys()))'
  exit 1
fi

GET_RESPONSE="$(curl -sS -X GET "$APP_URL/api/evaluations/$EVALUATION_ID" \
  -H "x-functions-key: ${HRHA_FUNCTION_KEY:?set HRHA_FUNCTION_KEY}" \
  -H "X-Lab-Actor-Id: copilot-lab-smoke" \
  -H "X-Lab-Roles: hr" \
  -H "X-Lab-Actor-Display: Copilot Lab Smoke")"

BODY_RETRIEVE_RESPONSE="$(curl -sS -X POST "$APP_URL/api/evaluations/retrieve" \
  -H "content-type: application/json" \
  -H "x-functions-key: ${HRHA_FUNCTION_KEY:?set HRHA_FUNCTION_KEY}" \
  -H "X-Lab-Actor-Id: copilot-lab-smoke" \
  -H "X-Lab-Roles: hr" \
  -H "X-Lab-Actor-Display: Copilot Lab Smoke" \
  --data-binary "{\"evaluation_id\":\"$EVALUATION_ID\"}")"

POST_JSON="$POST_RESPONSE" GET_JSON="$GET_RESPONSE" BODY_JSON="$BODY_RETRIEVE_RESPONSE" python3 - <<'PY'
import json
import os

post = json.loads(os.environ["POST_JSON"])
get = json.loads(os.environ["GET_JSON"])
body = json.loads(os.environ["BODY_JSON"])
record = get.get("result") or {}
advisory = post.get("result") or {}
evaluation_id = post.get("evaluation_id") or advisory.get("evaluation_id")

print("submit_status:", post.get("status"))
print("get_status:", get.get("status"))
print("body_retrieve_status:", body.get("status"))
print("evaluation_id:", evaluation_id)
print("get_evaluation_id:", get.get("evaluation_id"))
print("body_retrieve_evaluation_id:", body.get("evaluation_id"))
print("record_ai_backend_type:", record.get("ai_backend_type") or advisory.get("ai_backend_type"))
print("record_provider:", record.get("provider_id") or advisory.get("provider_id") or "deterministic_mock")

if post.get("status") != "completed":
    raise SystemExit("submitEvaluation did not complete")
if get.get("status") != "completed":
    raise SystemExit("getEvaluation did not complete")
if body.get("status") != "completed":
    raise SystemExit("retrieveEvaluationForCopilot did not complete")
if get.get("evaluation_id") != evaluation_id:
    raise SystemExit("GET did not retrieve the submitted evaluation")
if body.get("evaluation_id") != evaluation_id:
    raise SystemExit("body-based retrieve did not retrieve the submitted evaluation")
if (record.get("ai_backend_type") or advisory.get("ai_backend_type")) != "none":
    raise SystemExit("ai_backend_type changed unexpectedly")
PY
```

Use the header-based Function key path. Do not use query-string function-key
authentication in smoke commands or documentation.

## Out of scope

The current lab registration path does not enable Foundry, live model calls,
Entra auth, real candidate data, source-controlled Copilot ALM/export,
multi-candidate workflows, response-envelope changes, Azure resource
creation, automated Copilot registration, production readiness, or committed
secrets.
