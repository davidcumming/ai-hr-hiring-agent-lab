# Implementation Lessons

Durable technical and Microsoft-stack lessons promoted from completed slices. Process and workflow lessons live in `docs/delivery/process-lessons.md`.

## slice-e5-copilot-studio-registration-smoke

### IL-slice-e5-copilot-studio-registration-smoke-001

- **Title:** Dataverse is a prerequisite for reliable Copilot Studio agent and tool work.
- **Category:** Microsoft-stack constraint
- **Lesson:** Dataverse must exist in the Power Platform environment before Copilot Studio agent, connector, and tool/action work is reliable. When Dataverse is initially absent, agent authoring and tool registration can look like a Copilot Studio problem even though the underlying blocker is environment provisioning.
- **Future planning impact:** Future Copilot Studio slices should confirm Dataverse availability before planning agent/tool registration or smoke validation steps.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 3.1 and 3.2; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/traceability.md` FR-E5-02.
- **Strategic-doc update recommended:** Yes, but not in this cleanup. Current-state drift remains tracked by issue #4.

### IL-slice-e5-copilot-studio-registration-smoke-002

- **Title:** Expected Copilot and Dataverse role names may not appear.
- **Category:** Microsoft-stack constraint
- **Lesson:** Expected role names such as an Agent Author role may not be visible in the tenant or environment. Available Environment Maker, Bot Author, and system-admin-style access can unblock lab smoke work, but the exact roles used must be recorded carefully because they affect repeatability, auditability, and future least-privilege design.
- **Future planning impact:** Future portal or low-code setup slices should record the available role names actually used and avoid assuming role labels from documentation will appear exactly in the lab environment.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` section 3.2; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` sections 1.1 and 7.
- **Strategic-doc update recommended:** Yes, but defer to a current-state or environment-runbook slice.

### IL-slice-e5-copilot-studio-registration-smoke-003

- **Title:** Separate connector, connection, action, and topic responsibilities.
- **Category:** integration
- **Lesson:** A Power Apps custom connector is the API definition. A Power Platform/Copilot connection is the stored credential binding. A Copilot Studio tool/action is the agent-level operation and input mapping. A Copilot topic/workflow is the orchestration and state-management layer. Treating these as one "connector" hides the actual place a failure needs to be fixed.
- **Future planning impact:** Future Copilot Studio integration plans should name each layer separately and assign evidence, tests, and follow-up issues to the layer that actually owns the behavior.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 3.4, 3.5, 3.7, and 3.9.
- **Strategic-doc update recommended:** Yes, but issue #4 tracks current-state doc reconciliation separately.

### IL-slice-e5-copilot-studio-registration-smoke-004

- **Title:** Refresh Power Platform connections after connector host or security changes.
- **Category:** configuration management
- **Lesson:** Power Platform connections can become stale after Power Apps custom connector host or security changes and may need refresh or recreation before Copilot Studio calls use the new metadata. A successful connector import does not prove the stored connection is using the corrected host and auth settings.
- **Future planning impact:** Connector-change runbooks should include connection refresh/recreate steps plus verification that avoids exposing Function keys, connection secrets, tenant IDs, subscription IDs, or secret-bearing screenshots.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` section 3.6; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/closeout.md` RR-E5-03; issue #2.
- **Strategic-doc update recommended:** Yes, as part of issue #2 or a later runbook slice.

### IL-slice-e5-copilot-studio-registration-smoke-005

- **Title:** Map idempotency body fields and headers explicitly.
- **Category:** integration
- **Lesson:** `Idempotency-Key` may need explicit Copilot Studio tool/action mapping even when an `idempotency_key` body field is present. The body field and header field are distinct, and omitting the header can produce malformed request behavior even when the business payload looks complete.
- **Future planning impact:** Future tool/action mapping checks should verify required headers and body fields independently, especially where the facade uses idempotency or correlation controls.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 3.7 and 3.9; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/traceability.md` AC-E5-01.
- **Strategic-doc update recommended:** No separate strategic update; carry forward into E6 acceptance checks.

### IL-slice-e5-copilot-studio-registration-smoke-006

- **Title:** Store workflow identifiers explicitly.
- **Category:** integration
- **Lesson:** Do not rely on "Dynamically fill with AI" for workflow identifiers such as `evaluation_id`. Copilot Studio should store identifiers explicitly in topic/workflow variables and pass those variables into later tool/action calls.
- **Future planning impact:** E6 should make explicit `evaluation_id` storage and handoff the primary behavior under test, instead of treating natural-language or AI-filled chaining as reliable workflow state.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 3.8 and 3.9; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/traceability.md` AB-E5-03; issue #1.
- **Strategic-doc update recommended:** Yes, after E6 proves the pattern.

### IL-slice-e5-copilot-studio-registration-smoke-007

- **Title:** Function hosts are evidence; Function keys are secrets.
- **Category:** privacy/residency
- **Lesson:** Function App host names are configuration evidence, but Function keys are secrets. Evidence may record the host name and the fact that direct Function auth was used, but must not record key values, connection secrets, tenant identifiers, subscription identifiers, or secret-bearing screenshots. Function keys are secrets and must stay out of repository artifacts.
- **Future planning impact:** Future manual evidence and runbook artifacts should distinguish non-secret endpoint configuration from secret credential material, and should route production-like auth replacement through a scoped identity slice.
- **Source reference:** `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/manual-config-evidence.md` sections 3.5 and 8; `docs/delivery/slices/slice-e5-copilot-studio-registration-smoke/traceability.md` BR-E5-05; issue #3.
- **Strategic-doc update recommended:** No architecture rule change here; issue #3 tracks identity replacement.
