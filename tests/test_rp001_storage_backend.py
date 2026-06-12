"""RP-001..RP-004, RP-014: storage backend boundary, artifact layout, summary
rows, transcripts (readiness pack).

All local/deterministic. No network, no Azure SDK, synthetic data only.
"""

from __future__ import annotations

import json

from tests.conftest import HR_HEADERS, post_evaluation

from hr_eval_lab.domain.schemas.storage import RecordSummaryRow, StorageArtifactRef
from hr_eval_lab.domain.schemas.transcript import CouncilRoleInvocation
from hr_eval_lab.persistence.backend import LocalFilesystemBackend

EXPECTED_ARTIFACTS = {
    "record.json",
    "request.json",
    "source-documents.json",
    "evidence-packet.json",
    "synthesis.json",
    "quality-gates.json",
    "provider-metadata.json",
    "human-review.json",
}


def _submitted(client, key="rp001"):
    response = post_evaluation(client, idempotency_key=key)
    assert response.status_code == 200
    return response.json()["evaluation_id"]


def test_rp001_backend_roundtrip_and_artifact_layout(make_client):
    """Local backend writes record + the full artifact tree; list/read work."""
    client = make_client()
    evaluation_id = _submitted(client)
    backend = client.app.state.store.backend

    record = backend.read_evaluation_record(evaluation_id)
    assert record is not None and record["evaluation_id"] == evaluation_id

    artifacts = backend.list_artifacts(evaluation_id)
    names = {a.name for a in artifacts}
    assert EXPECTED_ARTIFACTS.issubset(names)
    council = {n for n in names if n.startswith("council/")}
    assert {f"council/{e['role_id']}.json" for e in record["role_executions"]} == council
    for ref in artifacts:
        assert isinstance(ref, StorageArtifactRef)
        assert len(ref.sha256) == 64 and ref.size_bytes > 0


def test_rp001_domain_roundtrip_is_deterministic(tmp_path):
    """Schema JSON roundtrip through the backend is byte-stable."""
    backend = LocalFilesystemBackend(tmp_path)
    payload = {"b": 2, "a": [1, 2, {"z": None, "y": "café"}]}
    backend.write_evaluation_record("eval-x", payload)
    again = backend.read_evaluation_record("eval-x")
    assert again == payload
    raw1 = (tmp_path / "evaluations" / "eval-x" / "record.json").read_bytes()
    backend.write_evaluation_record("eval-x", again)
    raw2 = (tmp_path / "evaluations" / "eval-x" / "record.json").read_bytes()
    assert raw1 == raw2


def test_rp002_source_hash_provenance_in_record_and_summary(make_client):
    """Source ids/hashes/versions survive the new layout end to end."""
    client = make_client()
    evaluation_id = _submitted(client)
    backend = client.app.state.store.backend
    record = backend.read_evaluation_record(evaluation_id)
    sources = record["sources"]
    assert sources and all(s.get("sha256") for s in sources)

    row = backend.read_metadata_row(evaluation_id)
    assert row is not None
    assert sorted(row["source_hashes"]) == sorted(s["sha256"] for s in sources)

    docs = json.loads(
        (backend._eval_dir(evaluation_id) / "source-documents.json").read_text()
    )
    assert docs == sources


def test_rp004_metadata_summary_is_text_free(make_client):
    """metadata/evaluations.jsonl: schema-valid summary; no resume/cover text."""
    client = make_client()
    evaluation_id = _submitted(client)
    store = client.app.state.store
    row = store.backend.read_metadata_row(evaluation_id)
    summary = RecordSummaryRow.model_validate(row)
    assert summary.human_review_required is True
    assert summary.decision_support_only is True

    # Sentinel strings from the synthetic fixture must not appear in the file.
    raw = (store.root / "metadata" / "evaluations.jsonl").read_text(encoding="utf-8")
    resume_text = (client.app.state.fixtures.resolve("cand-sample-001:resume")).text
    for sentinel in [line for line in resume_text.splitlines() if len(line) > 25][:5]:
        assert sentinel not in raw
    # And the schema simply has no free-text field:
    field_names = set(RecordSummaryRow.model_fields)
    assert not field_names & {"resume_text", "cover_letter_text", "text", "body", "content"}


def test_rp014_council_transcripts_validate(make_client):
    """Every per-role transcript validates as CouncilRoleInvocation; model-backed
    roles carry prompt template provenance; code roles carry none."""
    client = make_client()
    evaluation_id = _submitted(client)
    backend = client.app.state.store.backend
    record = backend.read_evaluation_record(evaluation_id)
    eval_dir = backend._eval_dir(evaluation_id)

    for execution in record["role_executions"]:
        path = eval_dir / "council" / f"{execution['role_id']}.json"
        invocation = CouncilRoleInvocation.model_validate(
            json.loads(path.read_text(encoding="utf-8"))
        )
        assert invocation.evaluation_id == evaluation_id
        assert invocation.output_json == execution["output"]
        assert invocation.validation_status in ("valid", "valid_after_retry")
        if execution["role_kind"] == "model":
            assert invocation.prompt_template_id == f"prompt-{execution['role_id']}"
            assert invocation.prompt_template_version == "v1"
            assert invocation.model_or_agent_ref is None  # mock backend
            assert invocation.safe_error is None
        else:
            assert invocation.prompt_template_id is None


def test_rp015_mandatory_flags_in_new_surfaces(make_client):
    """human-review artifact + summary row keep the advisory invariants."""
    client = make_client()
    evaluation_id = _submitted(client)
    backend = client.app.state.store.backend
    human_review = json.loads(
        (backend._eval_dir(evaluation_id) / "human-review.json").read_text()
    )
    assert human_review["decision_support_only"] is True
    assert human_review["human_review"]["human_review_required"] is True
