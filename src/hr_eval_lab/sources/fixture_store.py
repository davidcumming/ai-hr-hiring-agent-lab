"""Fixture resolution, version pinning, and sha256 verification (BR-009).

The manifest (``fixtures/manifest.json``) is the hash authority. Every
resolved file is re-verified on each evaluation; any mismatch raises
:class:`SourceIntegrityError`, which the facade maps to envelope status
``blocked`` with ZERO council execution (DT-007). Mismatch details carry
artifact id + expected/actual hash only — never content.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

POSITION_ID = "pos-sample-001"
CANDIDATE_REF = "cand-sample-001"
RUBRIC_ID = "rub-sample-001"

DEFAULT_FIXTURES_ROOT = Path("fixtures")


class UnknownArtifactError(KeyError):
    """Unknown position/candidate reference -> envelope ``validation_failed``."""


@dataclass
class SourceIntegrityError(Exception):
    """Hash mismatch -> envelope ``blocked``; zero council execution."""

    artifact_id: str
    expected_sha256: str
    actual_sha256: str

    def safe_detail(self) -> str:
        return (
            f"source integrity failure for artifact '{self.artifact_id}': "
            f"expected sha256 {self.expected_sha256[:12]}…, "
            f"got {self.actual_sha256[:12]}…"
        )


@dataclass
class ResolvedSource:
    artifact_id: str
    version: str
    sha256: str
    text: str
    origin: str  # "fixture" | "inline"
    synthetic: bool = True


class FixtureStore:
    """Resolves fixture artifacts by id with per-run hash verification."""

    def __init__(self, root: str | Path = DEFAULT_FIXTURES_ROOT) -> None:
        self.root = Path(root)
        manifest = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        self._by_id = {a["artifact_id"]: a for a in manifest["artifacts"]}

    def known_position(self, position_id: str) -> bool:
        return position_id == POSITION_ID and position_id in self._by_id

    def known_candidate(self, candidate_ref: str) -> bool:
        return candidate_ref == CANDIDATE_REF and f"{candidate_ref}:resume" in self._by_id

    def resolve(self, artifact_id: str) -> ResolvedSource:
        """Resolve + hash-verify one artifact. Raises on unknown id or mismatch."""
        entry = self._by_id.get(artifact_id)
        if entry is None:
            raise UnknownArtifactError(artifact_id)
        # Manifest paths are repo-relative ("fixtures/..."); resolve against
        # the store root's parent so a relocated root still works.
        path = self.root.parent / entry["path"]
        data = path.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != entry["sha256"]:
            raise SourceIntegrityError(
                artifact_id=artifact_id,
                expected_sha256=entry["sha256"],
                actual_sha256=actual,
            )
        return ResolvedSource(
            artifact_id=artifact_id,
            version=entry["version"],
            sha256=actual,
            text=data.decode("utf-8"),
            origin="fixture",
            synthetic=bool(entry.get("synthetic", True)),
        )

    def resolve_rubric_json(self) -> tuple[dict, ResolvedSource]:
        source = self.resolve(RUBRIC_ID)
        return json.loads(source.text), source


def inline_source(artifact_id: str, text: str) -> ResolvedSource:
    """Wrap inline request text as a versioned, hashed source (origin=inline)."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return ResolvedSource(
        artifact_id=artifact_id,
        version="inline-v1",
        sha256=digest,
        text=text,
        origin="inline",
        synthetic=True,  # BR-011: synthetic-only lab; callers must supply synthetic text
    )
