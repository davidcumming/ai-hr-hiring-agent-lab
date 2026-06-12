"""Controlled evidence packet builder — code-built BEFORE any provider call.

Invoked by the Source Ingestion/Versioning code role (FR-005, DT-016). Source
content is segmented into stably addressed segments (``resume:s01`` …) so that
every later citation is mechanically resolvable to a packet segment or
evidence-item id (gates 3/6). Segment ids are a contract consumed by the mock
provider and the quality gates.
"""

from __future__ import annotations

import json

from hr_eval_lab.domain.schemas.audit import (
    EvidencePacket,
    PacketSegment,
    RubricCriterionView,
    RubricView,
    SourceRef,
)
from hr_eval_lab.sources.fixture_store import ResolvedSource

#: artifact_id suffix -> short segment prefix
_PREFIXES = {
    "resume": "resume",
    "cover_letter": "cover_letter",
    "job_description": "job_description",
}


def segment_text(text: str) -> list[str]:
    """Split source text into stable paragraph-level segments.

    Deterministic: blank-line separated blocks, whitespace-normalized inside a
    block, empty blocks dropped. Identical input bytes => identical segments.
    """
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip() == "":
            if current:
                blocks.append(" ".join(current))
                current = []
        else:
            current.append(line.strip())
    if current:
        blocks.append(" ".join(current))
    return blocks


def _prefix_for(artifact_id: str) -> str:
    for suffix, prefix in _PREFIXES.items():
        if artifact_id.endswith(suffix) or artifact_id == suffix:
            return prefix
    return artifact_id.replace(":", "_")


def build_packet(
    resume: ResolvedSource,
    cover_letter: ResolvedSource,
    job_description: ResolvedSource,
    rubric_json: dict,
    rubric_source: ResolvedSource,
    evaluation_question: str | None = None,
) -> EvidencePacket:
    """Assemble the controlled evidence packet from hash-verified sources."""
    sources: list[SourceRef] = []
    segments: list[PacketSegment] = []

    doc_map = [
        (resume, "resume"),
        (cover_letter, "cover_letter"),
        (job_description, "job_description"),
    ]
    for source, prefix in doc_map:
        sources.append(
            SourceRef(
                artifact_id=source.artifact_id,
                version=source.version,
                sha256=source.sha256,
                origin=source.origin,  # type: ignore[arg-type]
                synthetic=source.synthetic,
            )
        )
        for index, block in enumerate(segment_text(source.text), start=1):
            segments.append(
                PacketSegment(
                    segment_id=f"{prefix}:s{index:02d}",
                    artifact_id=source.artifact_id,
                    text=block,
                )
            )

    sources.append(
        SourceRef(
            artifact_id=rubric_source.artifact_id,
            version=rubric_source.version,
            sha256=rubric_source.sha256,
            origin=rubric_source.origin,  # type: ignore[arg-type]
            synthetic=rubric_source.synthetic,
        )
    )

    rubric = RubricView(
        rubric_id=rubric_json["rubric_id"],
        version=rubric_json["version"],
        sha256=rubric_source.sha256,
        scale_min=int(rubric_json["scale"]["min"]),
        scale_max=int(rubric_json["scale"]["max"]),
        anchors={k: str(v) for k, v in rubric_json["scale"]["anchors"].items()},
        criteria=[
            RubricCriterionView(
                criterion_id=c["criterion_id"],
                name=c["name"],
                kind=c["kind"],
                definition=c["definition"],
                keywords=list(c.get("keywords", [])),
            )
            for c in rubric_json["criteria"]
        ],
        disqualifier_note=(
            rubric_json["disqualifying_criteria"][0]["definition"]
            if rubric_json.get("disqualifying_criteria")
            else ""
        ),
        prohibited_factors_note=rubric_json.get("prohibited_factors_note", ""),
    )

    return EvidencePacket(
        sources=sources,
        rubric=rubric,
        segments=segments,
        evaluation_question=evaluation_question,
    )


def canonical_packet_json(packet: EvidencePacket) -> str:
    """Canonical serialization of the packet (mock determinism seed input)."""
    return json.dumps(
        packet.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
