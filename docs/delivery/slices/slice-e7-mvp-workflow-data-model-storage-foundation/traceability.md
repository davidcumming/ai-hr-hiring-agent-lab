# Traceability: E7 Workflow Storage Foundation

| Requirement / criterion | Implementation evidence | Test evidence |
|---|---|---|
| 18 workflow Table entities exist as strict schemas | `src/hr_eval_lab/domain/schemas/workflow.py` | `tests/test_e7_workflow_schemas.py` |
| Table rows expose `PartitionKey`, `RowKey`, `entity_type`, `schema_version`, and synthetic-safe defaults | `WorkflowTableEntity.to_table_entity()` | `test_e7_workflow_entities_have_table_keys_type_marker_and_schema_version` |
| Case-partitioned workflow entities use the case id as the Table partition, with Notification supporting actor-inbox and case-inbox partitions | `CasePartitionedWorkflowEntity`, `Notification._validate_notification_partition()` | `test_e7_case_partitioned_entities_require_partition_key_to_equal_case_id`, `test_e7_notification_supports_actor_inbox_and_case_inbox_partitions` |
| Critical workflow RowKeys use pinned prefixes | `WorkflowTableEntity.row_key_prefix` on critical entities | `test_e7_critical_table_entities_require_row_key_prefix` |
| List/dict Table properties serialize to canonical JSON strings | `WorkflowTableEntity.to_table_entity()` and `from_table_entity()` | `test_e7_table_json_properties_serialize_as_canonical_strings` |
| Exact Blob paths match the overlay | `src/hr_eval_lab/domain/schemas/workflow_artifacts.py` | `tests/test_e7_blob_paths.py` |
| Unsafe Blob path input is rejected | `validate_blob_path()` and path builders | `test_e7_blob_path_builders_reject_unsafe_segments`, `test_e7_validate_blob_path_rejects_traversal_and_unknown_containers` |
| Queue messages validate required IDs, correlation IDs, retry metadata, and schema version | `src/hr_eval_lab/domain/schemas/workflow_queue.py` | `tests/test_e7_queue_messages.py` |
| Queue messages do not carry raw applicant text or secret-bearing fields | strict queue schemas with `extra="forbid"` and forbidden-marker validation | `test_e7_queue_messages_forbid_extra_raw_content_and_bad_retry_count`, `test_e7_queue_messages_reject_forbidden_markers_in_allowed_string_fields`, `test_e7_queue_messages_reject_forbidden_markers_in_allowed_list_fields`, `test_e7_queue_payloads_are_identifier_only_and_secret_free` |
| Local deterministic adapter writes Table, Blob, and Queue-shaped data | `src/hr_eval_lab/persistence/workflow_store.py` | `tests/test_e7_local_workflow_store.py` |
| No public API or OpenAPI/Copilot contract expansion | E7 code is not wired into `create_app()` routes | `tests/test_e7_non_goals.py`; export drift checks |
| No Azure SDK import or live cloud path for E7 | `LocalWorkflowStore` imports only stdlib/Pydantic/local schemas | `test_e7_workflow_store_import_does_not_import_azure_sdks` |
