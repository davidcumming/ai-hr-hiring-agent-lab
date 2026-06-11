# Privacy, Data Residency, and Auditability Rubric

Use this rubric in Section C of the eval risk profile to assess eval-data governance requirements for a slice.

The goal is to determine: what data types do eval scenarios need to represent, can synthetic data substitute, what residency and retention rules apply, and are there any blockers that prevent eval design from proceeding.

---

## 1. Data Type Inventory

Before assessing governance requirements, inventory every type of data that live eval scenarios would need to represent.

Work through the slice spec's inputs, outputs, tool calls, retrieved documents, and workflow state fields. For each data element, determine:

| Data element | Type | PHI? | PII? | Sensitive business data? | Residency rule? | Retention rule? |
|---|---|---|---|---|---|---|
| (list each element from the slice) | User input / System state / External artifact / Retrieved document / Log entry | Yes/No/Unknown | Yes/No/Unknown | Yes/No/Unknown | Yes/No/Unknown | Yes/No/Unknown |

---

## 2. PHI Assessment

**Definition:** Protected Health Information — any health data that can be linked to an identifiable individual. In the Canadian federal healthcare context, this includes data governed under applicable provincial health information acts (e.g., PHIPA in Ontario, HIA in Alberta, PIPA/FIPPA in BC).

**Questions to answer:**

- Does any eval scenario need to represent a patient record, clinical note, diagnostic result, prescription, care plan, or related document?
- Does any eval scenario need to represent data that would be PHI if combined with an identifier?
- Is the slice part of a workflow that processes PHI even if the slice itself only sees a subset?

**Governance requirements when PHI is involved:**

- Real PHI may not be used in eval scenarios without explicit governance approval and a documented legal basis.
- Synthetic PHI must be realistic enough to test the failure modes but must be demonstrably synthetic (e.g., generated names, fake MRN, synthetic dates).
- Synthetic PHI must still satisfy Canadian residency requirements for storage and processing.
- Eval artifacts containing PHI or PHI-like data must be stored in approved, access-controlled locations.
- Eval artifacts may not be committed to the code repository.

---

## 3. PII Assessment

**Definition:** Personally Identifiable Information — any data that can be used to identify a specific individual. In Canada, governed under PIPEDA (federal) or equivalent provincial legislation.

**Questions to answer:**

- Do eval scenarios need to represent names, email addresses, phone numbers, addresses, employee IDs, or other individual identifiers?
- Is the PII required to test a realistic scenario, or can a token substitute (e.g., `[USER_NAME]`)?
- Does the slice handle PII in ways that must be validated (e.g., redaction, masking, access control)?

**Governance requirements when PII is involved:**

- Prefer synthetic PII or tokens unless realistic PII patterns are required to test a specific failure mode.
- If realistic PII is required (e.g., testing a redaction feature), document the governance basis.
- Do not use real employee or patient data without explicit approval.
- Eval artifacts containing realistic PII must be access-controlled and not committed to the repo.

---

## 4. Canadian Data Residency Assessment

**Canadian residency rule:** For projects operating under Canadian federal or provincial data governance requirements, data must remain within Canada unless explicit authorization exists to send it abroad. This applies to both production data and eval data.

**Questions to answer:**

- Is this project subject to Canadian data residency requirements? (Default answer for healthcare/government: Yes.)
- Will eval scenarios be run against Azure AI services? If so, are those services provisioned in Canadian Azure regions (Canada Central, Canada East)?
- Will eval data be stored in an Azure storage account? If so, is it in a Canadian region?
- Will eval data be sent to any third-party AI service (e.g., OpenAI API direct, non-Azure model endpoint)? If so, does that service have a Canadian residency option?
- Does the eval tooling (e.g., Azure AI Foundry, Prompt Flow) support data-residency configuration?

**Blockers:**

- If any eval infrastructure processes or stores data outside Canada without authorization, flag as a hard blocker.
- If the model endpoint is non-Canadian and no authorization exists, flag as a hard blocker.
- Do not assume data-residency compliance — verify the infrastructure configuration or flag for verification.

---

## 5. Sensitive Business Data Assessment

Sensitive business data includes proprietary process information, commercially sensitive data, competitive intelligence, and data that is not individually identifying but carries confidentiality obligations.

**Questions to answer:**

- Do eval scenarios need to represent data with confidentiality agreements or internal classification markings?
- Does the slice process data about third-party organizations that have contractual privacy expectations?

**Governance requirements:**

- Synthetic or anonymized business data is preferred.
- If real business data is required, document the classification level and approval.
- Eval artifacts containing sensitive business data must be access-controlled.

---

## 6. Audit Retention and Auditability

**Questions to answer:**

- Does the slice create audit events that must be retained for a defined period?
- Does the slice participate in a compliance-governed workflow where all inputs and outputs must be traceable?
- Do eval runs need to produce evidence that is itself auditable (e.g., for a regulatory review)?

**Governance requirements when auditability applies:**

- Eval run artifacts must be stored in a location accessible for audit review.
- Eval artifacts must not be deleted or overwritten within the retention period.
- Artifact references must be preserved in the eval summary, not only the raw outputs.
- If the eval infrastructure does not support required retention, flag as a blocker.

---

## 7. External Artifact Handling

External artifacts are inputs to the agent that originate outside the organization's direct control: uploaded documents, third-party API responses, shared references, attachments.

**Questions to answer:**

- Do eval scenarios need to simulate external artifacts?
- Do those simulated artifacts contain PHI, PII, or sensitive data?
- Are there restrictions on storing copies of third-party documents for eval purposes?

**Governance requirements:**

- Use synthetic or representative-only external artifacts wherever possible.
- If a realistic external artifact is required, document the source and the governance basis for using it.
- Store external eval artifacts in approved locations subject to applicable residency rules.

---

## 8. Synthetic Data Requirements Summary

Based on the assessment above, summarize:

| Data category | Can synthetic data fully substitute? | Partial substitute? | Real data required? | Governance approval needed? |
|---|---|---|---|---|
| PHI | | | | |
| PII | | | | |
| Sensitive business data | | | | |
| External artifacts | | | | |
| Audit evidence | | | | |

Where real data is required, flag it as a blocker pending governance approval before `eval-contract-designer` proceeds.

---

## 9. Governance Blockers

A governance blocker means `eval-contract-designer` cannot finalize scenarios that require the blocked data type until the blocker is resolved.

| Blocker ID | Description | Data type | Applies to which eval scenarios | Required action | Who resolves |
|---|---|---|---|---|---|
| GB-001 | | | | | |

---

## 10. Residency Compliance Checklist

- [ ] Eval infrastructure (model endpoints) confirmed to be in approved Canadian regions, or explicit authorization documented.
- [ ] Eval data storage confirmed to be in approved Canadian regions, or explicit authorization documented.
- [ ] No third-party model API used for sensitive data eval without residency confirmation.
- [ ] Eval artifact retention and access control requirements identified.
- [ ] PHI/PII in eval scenarios is synthetic or explicitly approved real data.
- [ ] Eval artifacts are not committed to the code repository.
- [ ] External artifact usage documented with governance basis.
