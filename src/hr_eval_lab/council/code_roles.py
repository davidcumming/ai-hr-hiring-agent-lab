"""Deterministic code roles: Request Normalizer, Source Ingestion/Versioning
output shaping, and the Deterministic Rules Validator (council roles 1, 2, 4).

These are facade-owned, make no provider calls, and their outputs are recorded
in the audit record like every other intermediate output. The Rules Validator
runs BEFORE the judgment roles (DT-016) and performs: required-document
presence, disqualifier D1 evidence presence/absence (absence = missing
evidence, NEVER disqualification), and the instruction-like-content scan that
sets the anomalous-content flag (BR-012: candidate text is data, never
instructions — flagged, never followed).
"""

from __future__ import annotations

from hr_eval_lab.domain.schemas.audit import EvidencePacket
from hr_eval_lab.domain.schemas.request import EvaluationRequest
from hr_eval_lab.rigor.resolver import HIRING_CLASSIFICATION

#: Deterministic instruction-like content markers (lowercase substring scan).
INSTRUCTION_LIKE_MARKERS = (
    "ignore your",
    "ignore the rubric",
    "ignore previous",
    "ignore all previous",
    "disregard",
    "you must score",
    "score 5",
    "score this candidate",
    "give me the highest",
    "system prompt",
    "override your instructions",
    "as an ai",
    "act as",
)


def request_normalizer(request: EvaluationRequest) -> dict:
    """Role 1 — normalize the request and classify risk (hiring => high-impact
    default, BR-001). Output is metadata-only (no document text)."""
    return {
        "role": "request_normalizer",
        "normalized_request": {
            "position_id": request.position_id,
            "candidate_ref": request.candidate_ref,
            "inline_documents": request.candidate_ref is None,
            "has_evaluation_question": request.evaluation_question is not None,
            "requested_rigor": request.requested_rigor,
        },
        "risk_classification": HIRING_CLASSIFICATION,
    }


def source_ingestion_output(packet: EvidencePacket) -> dict:
    """Role 2 — record packet construction (versioned, hash-verified sources;
    packet completion precedes any provider call, FR-005)."""
    counts: dict[str, int] = {}
    for segment in packet.segments:
        counts[segment.artifact_id] = counts.get(segment.artifact_id, 0) + 1
    return {
        "role": "source_ingestion_versioning",
        "sources": [s.model_dump(mode="json") for s in packet.sources],
        "segment_counts": counts,
        "packet_complete": True,
    }


def deterministic_rules_validator(
    packet: EvidencePacket, request: EvaluationRequest
) -> dict:
    """Role 4 — deterministic pre-judgment checks (no provider call)."""
    artifact_ids = {s.artifact_id for s in packet.sources}
    required_docs = {
        "resume": any(a.endswith("resume") for a in artifact_ids),
        "cover_letter": any(a.endswith("cover_letter") for a in artifact_ids),
        "job_description": any(
            a == packet.rubric.rubric_id.replace("rub", "pos") or "pos" in a
            for a in artifact_ids
        ),
        "rubric": packet.rubric.rubric_id in artifact_ids,
    }

    # Disqualifier D1 (work eligibility): note evidence presence/absence.
    # Absence is MISSING EVIDENCE, never a disqualification (BR-013).
    d1_markers = ("eligible to work", "work permit", "citizen", "permanent resident")
    d1_segments = [
        seg.segment_id
        for seg in packet.segments
        if any(m in seg.text.lower() for m in d1_markers)
    ]
    d1 = {
        "evidence_present": bool(d1_segments),
        "segment_refs": d1_segments,
        "note": (
            "Work-eligibility statement located in candidate material."
            if d1_segments
            else "No work-eligibility statement found: recorded as missing "
            "evidence, never a disqualification (D1 rule)."
        ),
    }

    # Instruction-like-content scan over candidate document segments AND the
    # free-text evaluation_question (untrusted content is data, not commands).
    anomalous_segments: list[str] = []
    patterns_found: list[str] = []
    candidate_artifacts = {
        a for a in artifact_ids if a.endswith("resume") or a.endswith("cover_letter")
    }
    for seg in packet.segments:
        if seg.artifact_id not in candidate_artifacts:
            continue
        lowered = seg.text.lower()
        for marker in INSTRUCTION_LIKE_MARKERS:
            if marker in lowered:
                if seg.segment_id not in anomalous_segments:
                    anomalous_segments.append(seg.segment_id)
                if marker not in patterns_found:
                    patterns_found.append(marker)
    if request.evaluation_question:
        lowered = request.evaluation_question.lower()
        for marker in INSTRUCTION_LIKE_MARKERS:
            if marker in lowered:
                if "evaluation_question" not in anomalous_segments:
                    anomalous_segments.append("evaluation_question")
                if marker not in patterns_found:
                    patterns_found.append(marker)

    return {
        "role": "deterministic_rules_validator",
        "required_documents_present": required_docs,
        "disqualifier_d1": d1,
        "anomalous_content_detected": bool(anomalous_segments),
        "anomalous_segments": anomalous_segments,
        "instruction_like_patterns_found": patterns_found,
    }
