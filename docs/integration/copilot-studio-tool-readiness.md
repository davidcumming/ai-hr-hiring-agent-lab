# Copilot Studio Tool Readiness — Candidate Evaluation Council API

Status: **readiness documentation only.** No Copilot Studio environment, custom
connector, or Entra app registration exists for this lab; no portal
configuration should be performed now. This document records what the
implemented API already provides for future tool registration, and what remains
outstanding.

## What the implemented contract already provides

The committed contract is `openapi/evaluations-api.json`, generated from the
live app factory by `scripts/export_openapi.py` (drift-checked by test).

| Readiness item | Status in the implemented API |
|---|---|
| Stable operation IDs | `submitEvaluation` (`POST /api/evaluations`), `getEvaluation` (`GET /api/evaluations/{evaluation_id}`) |
| Tool-suitable descriptions | Operation `summary`/`description` state purpose, advisory-only boundary, status vocabulary, and HTTP mapping in business language |
| Standard response envelope | Adopted envelope subset: `status`, `evaluation_id`, `case_id` (always null — case-less), `correlation_id`, `user_message`, `safe_details`, `result`, `errors`, `warnings` |
| Fixed status vocabulary | Emitted: `completed | blocked | validation_failed | unauthorized`; declared-reserved: `needs_input`, `error`. Business outcomes return HTTP 200; malformed body 400; missing identity 401; wrong role 403 |
| Correlation ID header | `X-Correlation-Id` accepted on requests (POST and GET) and returned on responses that have a correlation id to carry: the server-assigned id (also in the envelope) takes precedence; a caller-supplied value is echoed back when no envelope correlation id exists. Early-failure responses (400/401/403, envelope-less `validation_failed`) carry the header only if the caller sent one |
| Idempotency key header | `Idempotency-Key` accepted on `POST` as an equivalent of the body field `idempotency_key` (one required; mismatch → HTTP 400); replays return the original result without re-running the council |
| No backend selection in requests | The request schema contains **no** provider/model/deployment/endpoint/agent field; provider selection is server-side configuration only |
| Advisory-only output | Every result carries `decision_support_only: true` and `human_review_required: true`; recommendation labels are the fixed advisory enum; `effective_rigor` and the escalation-policy outcome are in the result |
| Synthetic examples only | All fixtures and documented examples are synthetic (`cand-sample-001`, `pos-sample-001`) |

## Not yet in place (future wiring work; all human-gated)

- Entra app registration and delegated OAuth: today authentication is
  **simulated lab identity headers** (`X-Lab-Actor-Id`, `X-Lab-Roles`) — a lab
  stand-in, never an Entra substitute. Tool registration requires the real
  identity design (Entra groups for `hr` etc.) before exposure.
- A reachable hosted endpoint (the facade currently runs locally only).
- Swagger 2.0 conversion if the Power Platform registration path requires it
  (source docs note Power Platform tool registration historically expects
  Swagger 2.0, <1 MB); the committed document is OpenAPI 3.1.0 from FastAPI.
- Connector/DLP decisions per the source architecture: REST/API tool
  registration, no premium/custom connector commitments — to be re-validated
  when live wiring is undertaken.
- Live provider/storage wiring (deferred ADR; kill-switch and live-enable
  guards stay in place until then).

## Tool description drafts (for the future registration)

- **submitEvaluation** — "Submit one synthetic candidate evaluation to the
  advisory Calibrated Evaluation Council for a sample position and approved
  rubric. Returns an advisory, evidence-grounded result that always requires
  human review. Never makes or implies a hiring decision."
- **getEvaluation** — "Retrieve the full persisted audit record of a prior
  evaluation by evaluation_id, including every council role output, rigor
  resolution, escalation triggers, and quality-gate results. Advisory decision
  support only."
