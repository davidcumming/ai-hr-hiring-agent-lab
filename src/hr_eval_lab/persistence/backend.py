"""Storage backend boundary (readiness pack, coding target 2).

``StorageBackend`` is the formal seam between the facade's persistence layer
and a physical store. Two backends exist:

- :class:`LocalFilesystemBackend` — the default; fully functional; writes the
  artifact-per-evaluation layout under the local persistence root.
- ``AzureBlobBackend`` (``azure_blob_backend.py``) — Blob-backed record and
  artifact persistence for explicitly enabled Azure Functions paths; fails
  closed unless configured and ``HRHA_ENABLE_AZURE_STORAGE=true``. It imports
  no Azure SDK at import time or in default tests.

Local artifact layout (mirrors the future blob layout so wiring is
configuration, not restructuring)::

    evaluations/{evaluation_id}/record.json
    evaluations/{evaluation_id}/request.json
    evaluations/{evaluation_id}/source-documents.json
    evaluations/{evaluation_id}/evidence-packet.json
    evaluations/{evaluation_id}/council/{role}.json
    evaluations/{evaluation_id}/synthesis.json
    evaluations/{evaluation_id}/quality-gates.json
    evaluations/{evaluation_id}/provider-metadata.json
    evaluations/{evaluation_id}/human-review.json
    metadata/evaluations.jsonl          (summary rows; NO text fields)
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from hr_eval_lab.domain.schemas.storage import ArtifactType, StorageArtifactRef

if TYPE_CHECKING:  # import-time dependency avoided (config imports nothing heavy anyway)
    from hr_eval_lab.config import LabConfig


class StorageNotConfiguredError(RuntimeError):
    """A non-default storage backend was selected without valid configuration
    (or without live Azure being explicitly enabled). Safe, fail-closed."""


def canonical_json(payload: Any) -> str:
    """Canonical JSON: sorted keys, fixed separators, UTF-8 (byte-identity)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class StorageBackend(ABC):
    """Seam contract for evaluation persistence."""

    @abstractmethod
    def write_evaluation_record(self, evaluation_id: str, record_payload: dict) -> None:
        """Persist the full audit record (canonical JSON)."""

    @abstractmethod
    def read_evaluation_record(self, evaluation_id: str) -> Optional[dict]:
        """Load one full audit record, or None if absent."""

    @abstractmethod
    def write_artifact(
        self,
        evaluation_id: str,
        artifact_type: ArtifactType,
        role_or_name: str,
        payload: Any,
    ) -> StorageArtifactRef:
        """Persist one artifact for the evaluation; returns its reference."""

    @abstractmethod
    def list_artifacts(self, evaluation_id: str) -> list[StorageArtifactRef]:
        """List artifact references for one evaluation (metadata only)."""

    @abstractmethod
    def write_metadata_row(self, record_summary: dict) -> None:
        """Append one summary row to the evaluations metadata table."""

    @abstractmethod
    def read_metadata_row(self, evaluation_id: str) -> Optional[dict]:
        """Read one summary row by evaluation_id, or None."""


class LocalFilesystemBackend(StorageBackend):
    """Default backend: local filesystem, append-only-by-code."""

    METADATA_TABLE = "evaluations.jsonl"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        (self.root / "evaluations").mkdir(parents=True, exist_ok=True)
        (self.root / "metadata").mkdir(parents=True, exist_ok=True)

    # -- paths -----------------------------------------------------------------

    def _eval_dir(self, evaluation_id: str) -> Path:
        return self.root / "evaluations" / evaluation_id

    def _artifact_name(self, artifact_type: ArtifactType, role_or_name: str) -> str:
        if artifact_type == "council-role":
            return f"council/{role_or_name}.json"
        return f"{role_or_name}.json"

    # -- records -----------------------------------------------------------------

    def write_evaluation_record(self, evaluation_id: str, record_payload: dict) -> None:
        path = self._eval_dir(evaluation_id) / "record.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(canonical_json(record_payload), encoding="utf-8")

    def read_evaluation_record(self, evaluation_id: str) -> Optional[dict]:
        path = self._eval_dir(evaluation_id) / "record.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # -- artifacts ---------------------------------------------------------------

    def write_artifact(
        self,
        evaluation_id: str,
        artifact_type: ArtifactType,
        role_or_name: str,
        payload: Any,
    ) -> StorageArtifactRef:
        name = self._artifact_name(artifact_type, role_or_name)
        path = self._eval_dir(evaluation_id) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        body = canonical_json(payload)
        path.write_text(body, encoding="utf-8")
        raw = body.encode("utf-8")
        return StorageArtifactRef(
            evaluation_id=evaluation_id,
            artifact_type=artifact_type,
            name=name,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
        )

    def list_artifacts(self, evaluation_id: str) -> list[StorageArtifactRef]:
        eval_dir = self._eval_dir(evaluation_id)
        if not eval_dir.exists():
            return []
        refs: list[StorageArtifactRef] = []
        for path in sorted(eval_dir.rglob("*.json")):
            rel = path.relative_to(eval_dir).as_posix()
            if rel.startswith("council/"):
                artifact_type: ArtifactType = "council-role"
            elif rel == "record.json":
                artifact_type = "record"
            else:
                stem = rel[: -len(".json")]
                artifact_type = stem if stem in (
                    "request",
                    "source-documents",
                    "evidence-packet",
                    "synthesis",
                    "quality-gates",
                    "provider-metadata",
                    "human-review",
                ) else "record"  # unknown files default conservatively
            raw = path.read_bytes()
            refs.append(
                StorageArtifactRef(
                    evaluation_id=evaluation_id,
                    artifact_type=artifact_type,
                    name=rel,
                    sha256=hashlib.sha256(raw).hexdigest(),
                    size_bytes=len(raw),
                )
            )
        return refs

    # -- metadata summary table ----------------------------------------------------

    def write_metadata_row(self, record_summary: dict) -> None:
        path = self.root / "metadata" / self.METADATA_TABLE
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(canonical_json(record_summary) + "\n")

    def read_metadata_row(self, evaluation_id: str) -> Optional[dict]:
        path = self.root / "metadata" / self.METADATA_TABLE
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("PartitionKey") == evaluation_id:
                return row
        return None


def select_backend(config: "LabConfig") -> StorageBackend:  # noqa: F821 (lazy hint)
    """Resolve the configured storage backend.

    Lazy: the Azure module is imported only when explicitly selected. The
    module itself still imports no Azure SDKs until it has passed its storage
    enablement/configuration checks.
    """
    backend_id = config.storage.backend
    if backend_id == "local_filesystem":
        return LocalFilesystemBackend(config.persistence.root)
    if backend_id == "azure_blob":
        from hr_eval_lab.persistence.azure_blob_backend import AzureBlobBackend

        return AzureBlobBackend(config.storage.azure)
    raise StorageNotConfiguredError(f"unknown storage backend: {backend_id!r}")
