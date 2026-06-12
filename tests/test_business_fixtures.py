"""Business fixture package integrity tests (fixpkg-e1-business).

Validates the curated business fixture package under
``fixtures/business/e1-candidate-evaluation/`` (see
``docs/delivery/slices/slice-e1-candidate-evaluation-council/fixture-selection-report.md``):

- manifest parses and matches the files on disk (existence + sha256, BR-009 discipline);
- every selected candidate has resume + cover letter unless explicitly marked as a
  negative-test fixture (``cover_letter_missing: true``);
- the primary scenario is complete (job posting, role profile, rubric, scoring guidance,
  policies, primary resume + cover letter);
- no junk files (``.DS_Store``, ``__MACOSX``, AppleDouble ``._*``) were curated;
- no obvious secret-looking values are present (fixtures are synthetic-only, BR-011);
- candidate documents are never marked as Copilot knowledge sources (routing rule);
- policy documents are categorized as ``hr_policy`` and routed as knowledge candidates;
- expected-behaviour notes carry the mandatory advisory-flag expectations (BR-007);
- the provisional rubric is explicitly unapproved (human gate, gap G-2).

These tests are pure fixture checks: no app logic, no live calls. The runtime
``FixtureStore`` intentionally remains bound to ``cand-sample-001``/``pos-sample-001``;
business candidates are exercised via inline text submission (FR-001) until they are
registered in the runtime store (documented gap, fixture-curation-notes.md).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "fixtures" / "business" / "e1-candidate-evaluation"
MANIFEST_PATH = PKG_ROOT / "manifest.json"


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def artifacts(manifest: dict) -> list[dict]:
    return manifest["artifacts"]


# ---------------------------------------------------------------------------
# Manifest integrity
# ---------------------------------------------------------------------------


def test_manifest_parses_with_required_package_fields(manifest: dict) -> None:
    for field in (
        "fixture_package_id",
        "fixture_package_version",
        "selected_scenario",
        "source_zip",
        "synthetic_notice",
        "artifacts",
    ):
        assert field in manifest, f"manifest missing required field: {field}"
    assert manifest["fixture_package_id"] == "fixpkg-e1-business"
    assert "SYNTHETIC" in manifest["synthetic_notice"]


def test_manifest_artifacts_carry_required_fields(artifacts: list[dict]) -> None:
    required = (
        "artifact_id",
        "normalized_path",
        "source_path",
        "document_type",
        "evaluation_role",
        "synthetic",
        "version",
        "sha256",
        "copilot_usage",
        "blob_usage",
        "foundry_usage",
    )
    for art in artifacts:
        for field in required:
            assert field in art, f"{art.get('artifact_id')} missing field: {field}"
        assert art["synthetic"] is True, f"{art['artifact_id']} must be synthetic (BR-011)"


def test_all_manifest_files_exist_with_matching_hashes(artifacts: list[dict]) -> None:
    for art in artifacts:
        path = REPO_ROOT / art["normalized_path"]
        assert path.is_file(), f"missing fixture file: {art['normalized_path']}"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == art["sha256"], (
            f"hash mismatch for {art['artifact_id']}: manifest {art['sha256'][:12]}…, "
            f"actual {actual[:12]}…"
        )


def test_no_package_files_missing_from_manifest(artifacts: list[dict]) -> None:
    manifested = {REPO_ROOT / a["normalized_path"] for a in artifacts}
    documented = {
        PKG_ROOT / "README.md",
        PKG_ROOT / "manifest.json",
        PKG_ROOT / "rejected" / "README.md",
    }
    on_disk = {p for p in PKG_ROOT.rglob("*") if p.is_file()}
    unaccounted = on_disk - manifested - documented
    assert not unaccounted, f"files on disk but not in manifest: {sorted(unaccounted)}"


# ---------------------------------------------------------------------------
# Candidate completeness
# ---------------------------------------------------------------------------


def _candidate_dirs() -> list[Path]:
    dirs = [PKG_ROOT / "candidates" / "primary"]
    dirs += sorted((PKG_ROOT / "candidates" / "secondary").iterdir())
    return [d for d in dirs if d.is_dir()]


def test_every_candidate_has_metadata_and_resume() -> None:
    for d in _candidate_dirs():
        assert (d / "candidate-metadata.json").is_file(), f"{d.name}: missing metadata"
        assert (d / "resume.md").is_file(), f"{d.name}: missing resume"


def test_cover_letter_present_unless_explicit_negative_test() -> None:
    for d in _candidate_dirs():
        meta = json.loads((d / "candidate-metadata.json").read_text(encoding="utf-8"))
        if meta.get("cover_letter_missing"):
            assert not (d / "cover-letter.md").exists(), (
                f"{d.name}: marked cover_letter_missing but a cover letter file exists"
            )
            assert (d / "notes.md").is_file(), (
                f"{d.name}: negative-test fixture must carry explanatory notes.md"
            )
        else:
            assert (d / "cover-letter.md").is_file(), f"{d.name}: missing cover letter"


def test_primary_scenario_is_complete() -> None:
    pos = PKG_ROOT / "positions" / "senior-manager-digital-health"
    for fname in ("job-posting.md", "role-profile.md", "rubric.v1.json", "scoring-guidance.md"):
        assert (pos / fname).is_file(), f"primary position package missing {fname}"
    primary = PKG_ROOT / "candidates" / "primary"
    assert (primary / "resume.md").is_file()
    assert (primary / "cover-letter.md").is_file()
    policies = sorted((PKG_ROOT / "policies").glob("*.md"))
    assert len(policies) == 5, f"expected 5 policy docs, found {len(policies)}"


def test_candidate_documents_are_loadable_nonempty_text() -> None:
    """Loadability floor for the council's evidence path: every curated candidate
    document reads as non-trivial UTF-8 text (inline submission inputs, FR-001)."""
    for d in _candidate_dirs():
        for fname in ("resume.md", "cover-letter.md"):
            path = d / fname
            if path.exists():
                text = path.read_text(encoding="utf-8")
                assert len(text.strip()) > 200, f"{path} suspiciously short"
                assert "UNREADABLE FILE SIMULATION" not in text, (
                    f"{path}: unreadable-simulation fixtures must not be curated"
                )


# ---------------------------------------------------------------------------
# Rubric (provisional, human gate)
# ---------------------------------------------------------------------------


def test_rubric_is_anchored_and_approval_is_lab_scoped_only() -> None:
    """PO decision 2026-06-12: rub-smdh-001 v1 is approved for synthetic/test-only
    Slice E1 lab evaluation. The approval scope must stay explicit and must never
    imply production hiring approval (BR-007/BR-011 posture)."""
    rubric = json.loads(
        (PKG_ROOT / "positions" / "senior-manager-digital-health" / "rubric.v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert rubric["rubric_id"] == "rub-smdh-001"
    approval = rubric["approval"]
    assert approval["approved"] is True, "PO approval (2026-06-12) must be recorded"
    assert approval["approved_by"] == "Product Owner"
    assert "synthetic/test-only" in approval["approval_scope"], (
        "approval scope must remain explicitly synthetic/test-only"
    )
    assert approval["production_hiring_approval"] is False, (
        "lab approval must never imply production hiring approval"
    )
    assert rubric["scale"]["min"] == 1 and rubric["scale"]["max"] == 5
    assert set(rubric["scale"]["anchors"]) == {"1", "2", "3", "4", "5"}
    assert len(rubric["criteria"]) == 6
    for crit in rubric["criteria"]:
        for field in ("criterion_id", "name", "kind", "definition", "evidence_expectations"):
            assert crit.get(field), f"criterion {crit.get('criterion_id')} missing {field}"
        assert crit["kind"] in ("required", "preferred")


# ---------------------------------------------------------------------------
# Junk and secrets
# ---------------------------------------------------------------------------


def test_no_junk_files_in_curated_package() -> None:
    junk = [
        p
        for p in PKG_ROOT.rglob("*")
        if p.name == ".DS_Store" or p.name.startswith("._") or "__MACOSX" in p.parts
    ]
    assert not junk, f"junk files curated: {junk}"


SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|client[_-]?secret|connection[_-]?string)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bbearer\s+[a-z0-9_\-\.]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
    re.compile(r"(?i)sharedaccesssignature|accountkey="),  # Azure SAS / storage keys
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),  # bare API-key shape
]


def test_no_secret_looking_values_in_fixtures() -> None:
    for path in PKG_ROOT.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        for pattern in SECRET_PATTERNS:
            assert not pattern.search(text), f"secret-looking value in {path}: {pattern.pattern}"


# ---------------------------------------------------------------------------
# Routing classification rules
# ---------------------------------------------------------------------------


def test_candidate_documents_never_marked_as_copilot_knowledge(artifacts: list[dict]) -> None:
    for art in artifacts:
        if art["document_type"] in ("resume", "cover_letter", "candidate_metadata", "fixture_notes"):
            assert art["copilot_usage"].upper().startswith("NO"), (
                f"{art['artifact_id']}: candidate-related documents must never be Copilot "
                f"knowledge sources (got: {art['copilot_usage']!r})"
            )


def test_policy_documents_categorized_and_routed_as_knowledge_candidates(
    artifacts: list[dict],
) -> None:
    policy_arts = [
        a for a in artifacts if a["normalized_path"].startswith(
            "fixtures/business/e1-candidate-evaluation/policies/"
        )
    ]
    assert len(policy_arts) == 5
    for art in policy_arts:
        assert art["document_type"] == "hr_policy", (
            f"{art['artifact_id']}: policy docs must be categorized hr_policy"
        )
        assert art["copilot_usage"].upper().startswith("YES"), (
            f"{art['artifact_id']}: policy docs are the intended Copilot knowledge candidates"
        )
        assert art["blob_usage"].upper().startswith("YES"), (
            f"{art['artifact_id']}: exact policy versions must be blob-copied per run (BR-009)"
        )


def test_no_artifact_claims_live_configuration(manifest: dict) -> None:
    assert "NO Azure" in manifest["live_configuration_status"], (
        "manifest must state that no live Azure/Copilot/Foundry configuration was performed"
    )


# ---------------------------------------------------------------------------
# Expected-behaviour notes (BR-007 expectations present)
# ---------------------------------------------------------------------------


def test_expected_behavior_notes_carry_mandatory_flag_expectations() -> None:
    for fname in ("expected-behavior-primary.md", "expected-behavior-secondary.md"):
        text = (PKG_ROOT / "expected" / fname).read_text(encoding="utf-8")
        assert "human_review_required" in text, f"{fname}: missing human_review_required"
        assert "decision_support_only" in text, f"{fname}: missing decision_support_only"
        assert "provisional" in text.lower(), f"{fname}: provisional status must be stated"
