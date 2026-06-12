"""DeterministicMockProvider — the default backend (``ai_backend_type = none``).

Fully deterministic and content-derived: outputs are computed from the
evidence packet via stable rules (criterion-keyword matching against rubric
anchors) plus a sha256-derived seed of the canonical packet serialization for
identifiers — identical inputs => identical outputs (DT-002). Integer/string
arithmetic only (no floats in output values).

Outputs are schema-valid for all 8 model-backed role types and cite REAL
packet segment / evidence-item ids, so citation resolution genuinely exercises
gates 3 and 6.

Scenario scripting (test-only): the constructor accepts an optional script
table mapping ``role_id`` to either a dict (shallow-merged over the generated
payload) or a callable ``(role_id, packet, role_context, payload) -> payload``.
Scripts are injectable only through test composition — there is no API or
config path to them; the default app path constructs the provider unscripted.
"""

from __future__ import annotations

import hashlib
from typing import Any, Callable, Union

from hr_eval_lab.domain.schemas import council as c
from hr_eval_lab.domain.schemas.audit import EvidencePacket, PacketSegment
from hr_eval_lab.domain.schemas.provider import (
    ProviderMetadata,
    ProviderResult,
    TokenUsage,
)
from hr_eval_lab.evidence.packet_builder import canonical_packet_json
from hr_eval_lab.providers.base import CouncilProvider

ScriptEntry = Union[dict, Callable[..., dict]]

#: Candidate-document artifact suffixes admissible as scoring evidence.
_CANDIDATE_DOC_SUFFIXES = ("resume", "cover_letter")

#: Deterministic contrary-evidence markers (e.g. "not yet fully bilingual").
_CONTRARY_MARKERS = ("not yet", "not fully", "no experience", "am not")

#: Prohibited-factor scan terms for the mock auditor (distinctive phrases only).
_PROHIBITED_TERMS = (
    "years old",
    "date of birth",
    "married",
    "my children",
    "religion",
    "disabled",
    "disability status",
    "nationality",
    "photograph",
)

_QUOTE_LIMIT = 200


def _is_candidate_doc(segment: PacketSegment) -> bool:
    return any(segment.artifact_id.endswith(s) for s in _CANDIDATE_DOC_SUFFIXES)


class DeterministicMockProvider(CouncilProvider):
    ai_backend_type = "none"

    def __init__(self, script: dict[str, ScriptEntry] | None = None) -> None:
        self._script = script or {}

    # -- seam implementation -------------------------------------------------

    def invoke_role(
        self,
        role_id: str,
        packet: EvidencePacket,
        role_context: dict[str, Any],
    ) -> ProviderResult:
        builders = {
            c.ROLE_EVIDENCE_EXTRACTION: self._evidence_extraction,
            c.ROLE_MERIT_ADVOCATE: self._merit_advocate,
            c.ROLE_RISK_GAPS_ADVOCATE: self._risk_gaps_advocate,
            c.ROLE_NEUTRAL_SCORING_JUDGE: self._neutral_scoring,
            c.ROLE_POLICY_FAIRNESS_AUDITOR: self._policy_fairness,
            c.ROLE_SYNTHESIS_JUDGE: self._synthesis,
            c.ROLE_SECOND_SYNTHESIS_JUDGE: self._second_synthesis,
            c.ROLE_RUBRIC_CALIBRATION_JUDGE: self._rubric_calibration,
        }
        if role_id not in builders:
            raise ValueError(f"unknown model-backed role: {role_id}")
        payload = builders[role_id](packet, role_context)

        entry = self._script.get(role_id)
        if callable(entry):
            payload = entry(role_id, packet, role_context, payload)
        elif isinstance(entry, dict):
            payload = {**payload, **entry}

        seed = hashlib.sha256(
            (canonical_packet_json(packet) + "|" + role_id).encode("utf-8")
        ).hexdigest()
        # Prompt provenance: templates are RECORDED, never executed, under the
        # mock (the registry is source-controlled config; readiness target 4).
        try:
            from hr_eval_lab.prompts.registry import get_template

            template = get_template(role_id)
            prompt_template_id: str | None = template.template_id
            prompt_template_version: str | None = template.version
        except KeyError:
            prompt_template_id = None
            prompt_template_version = None
        metadata = ProviderMetadata(
            ai_backend_type="none",
            trace_id=f"local-{seed[:16]}",
            eval_run_id=None,  # nullable placeholder (C-COND-2); live value via deferred ADR
            agent_run_id=f"mock-{seed[16:28]}",
            model_deployment=None,
            prompt_version=prompt_template_version,
            prompt_template_id=prompt_template_id,
            prompt_template_version=prompt_template_version,
            model_or_agent_ref=None,  # null under the deterministic mock
            warnings=[],
            safe_error=None,
            token_usage=TokenUsage(prompt=0, completion=0),
            latency_ms=0,
        )
        return ProviderResult(role_id=role_id, payload=payload, metadata=metadata)

    # -- shared deterministic analysis ----------------------------------------

    def _keyword_hits(
        self, packet: EvidencePacket
    ) -> dict[str, list[tuple[PacketSegment, str]]]:
        """criterion_id -> ordered (segment, keyword) hits in candidate docs."""
        hits: dict[str, list[tuple[PacketSegment, str]]] = {}
        for criterion in packet.rubric.criteria:
            found: list[tuple[PacketSegment, str]] = []
            for segment in packet.segments:
                if not _is_candidate_doc(segment):
                    continue
                lowered = segment.text.lower()
                for keyword in criterion.keywords:
                    if keyword.lower() in lowered:
                        found.append((segment, keyword))
            hits[criterion.criterion_id] = found
        return hits

    def _base_scores(self, packet: EvidencePacket) -> dict[str, int]:
        """Distinct-keyword-count -> anchored 1–5 score (integer arithmetic)."""
        scores: dict[str, int] = {}
        for criterion_id, found in self._keyword_hits(packet).items():
            distinct = len({kw.lower() for _, kw in found})
            if distinct == 0:
                scores[criterion_id] = 1
            elif distinct == 1:
                scores[criterion_id] = 3
            elif distinct == 2:
                scores[criterion_id] = 4
            else:
                scores[criterion_id] = 5
        return scores

    def _evidence_index(self, role_context: dict[str, Any]) -> dict[str, list[dict]]:
        """criterion_id -> extraction evidence items (from prior outputs)."""
        prior = role_context.get("prior_outputs", {})
        extraction = prior.get(c.ROLE_EVIDENCE_EXTRACTION, {})
        index: dict[str, list[dict]] = {}
        for item in extraction.get("evidence_items", []):
            index.setdefault(item["criterion_id"], []).append(item)
        return index

    # -- role builders ---------------------------------------------------------

    def _evidence_extraction(
        self, packet: EvidencePacket, role_context: dict[str, Any]
    ) -> dict:
        items = []
        counter = 0
        for criterion in packet.rubric.criteria:
            seen_segments: set[str] = set()
            for segment, _keyword in self._keyword_hits(packet)[criterion.criterion_id]:
                if segment.segment_id in seen_segments:
                    continue
                seen_segments.add(segment.segment_id)
                counter += 1
                lowered = segment.text.lower()
                relation = (
                    "contrary"
                    if any(m in lowered for m in _CONTRARY_MARKERS)
                    else "supporting"
                )
                items.append(
                    {
                        "evidence_id": f"ev-{counter:03d}",
                        "criterion_id": criterion.criterion_id,
                        "artifact_id": segment.artifact_id,
                        "segment_id": segment.segment_id,
                        "quote": segment.text[:_QUOTE_LIMIT],
                        "relation": relation,
                    }
                )
        notes = []
        for criterion in packet.rubric.criteria:
            if not any(i["criterion_id"] == criterion.criterion_id for i in items):
                notes.append(
                    f"No direct evidence located for criterion "
                    f"{criterion.criterion_id} ({criterion.name})."
                )
        return {
            "role": "evidence_extraction",
            "evidence_items": items,
            "coverage_notes": notes,
        }

    def _proposed(
        self,
        packet: EvidencePacket,
        role_context: dict[str, Any],
        adjust: int,
        stance: str,
    ) -> list[dict]:
        base = self._base_scores(packet)
        evidence = self._evidence_index(role_context)
        proposals = []
        for criterion in packet.rubric.criteria:
            cid = criterion.criterion_id
            items = evidence.get(cid, [])
            supporting = [i for i in items if i["relation"] == "supporting"]
            score = base[cid]
            missing = len(supporting) == 0
            if not missing:
                score = max(1, min(5, score + adjust))
            proposals.append(
                {
                    "criterion_id": cid,
                    "score": score,
                    "rationale": (
                        f"{stance} reading of cited evidence against anchor "
                        f"scale for {criterion.name}."
                        if not missing
                        else f"No direct evidence for {criterion.name}; "
                        "conservative floor score."
                    ),
                    "citations": [i["evidence_id"] for i in supporting],
                    "missing_evidence": missing,
                }
            )
        return proposals

    def _merit_advocate(self, packet: EvidencePacket, role_context: dict[str, Any]) -> dict:
        evidence = self._evidence_index(role_context)
        proposals = self._proposed(packet, role_context, +1, "Strength-oriented")
        arguments = [
            {
                "criterion_id": cid,
                "claim": f"Cited evidence supports capability on {cid}.",
                "citations": [i["evidence_id"] for i in items if i["relation"] == "supporting"],
            }
            for cid, items in sorted(evidence.items())
            if any(i["relation"] == "supporting" for i in items)
        ]
        return {
            "role": "merit_advocate",
            "stance": "merit",
            "arguments": arguments,
            "proposed_scores": proposals,
        }

    def _risk_gaps_advocate(
        self, packet: EvidencePacket, role_context: dict[str, Any]
    ) -> dict:
        evidence = self._evidence_index(role_context)
        proposals = self._proposed(packet, role_context, -1, "Risk/gap-oriented")
        arguments = []
        for criterion in packet.rubric.criteria:
            cid = criterion.criterion_id
            items = evidence.get(cid, [])
            contrary = [i for i in items if i["relation"] == "contrary"]
            if contrary:
                arguments.append(
                    {
                        "criterion_id": cid,
                        "claim": f"Contrary evidence limits the claim on {cid}.",
                        "citations": [i["evidence_id"] for i in contrary],
                    }
                )
            elif not items:
                arguments.append(
                    {
                        "criterion_id": cid,
                        "claim": f"No direct evidence in the packet for {cid}; "
                        "this is a gap, not a disqualification.",
                        "citations": [],
                    }
                )
        return {
            "role": "risk_gaps_advocate",
            "stance": "risk_gaps",
            "arguments": arguments,
            "proposed_scores": proposals,
        }

    def _neutral_scoring(
        self, packet: EvidencePacket, role_context: dict[str, Any]
    ) -> dict:
        return {
            "role": "neutral_scoring_judge",
            "scores": self._proposed(packet, role_context, 0, "Neutral anchored"),
        }

    def _policy_fairness(
        self, packet: EvidencePacket, role_context: dict[str, Any]
    ) -> dict:
        findings = []
        violations: list[str] = []
        counter = 0
        for segment in packet.segments:
            if not _is_candidate_doc(segment):
                continue
            lowered = segment.text.lower()
            for term in _PROHIBITED_TERMS:
                if term in lowered:
                    counter += 1
                    violations.append(term)
                    findings.append(
                        {
                            "finding_id": f"ff-{counter:03d}",
                            "severity": "high",
                            "category": "prohibited_factor",
                            "description": (
                                "Prohibited-factor-adjacent content detected in a "
                                "candidate document segment; it must not influence "
                                "any score."
                            ),
                            "segment_refs": [segment.segment_id],
                        }
                    )
        anomalous = list(role_context.get("anomalous_segments", []))
        for segment_id in anomalous:
            counter += 1
            findings.append(
                {
                    "finding_id": f"ff-{counter:03d}",
                    "severity": "medium",
                    "category": "anomalous_content",
                    "description": (
                        "Instruction-like content detected in candidate material; "
                        "treated strictly as data, never followed (BR-012)."
                    ),
                    "segment_refs": [segment_id],
                }
            )
        overall = "high" if violations else ("medium" if anomalous else "info")
        return {
            "role": "policy_fairness_auditor",
            "findings": findings,
            "overall_severity": overall,
            "prohibited_factor_violations": sorted(set(violations)),
            "anomalous_content_flagged": bool(anomalous),
        }

    def _synthesis(self, packet: EvidencePacket, role_context: dict[str, Any]) -> dict:
        prior = role_context.get("prior_outputs", {})
        evidence = self._evidence_index(role_context)
        neutral = {
            s["criterion_id"]: s
            for s in prior.get(c.ROLE_NEUTRAL_SCORING_JUDGE, {}).get("scores", [])
        }
        merit = {
            s["criterion_id"]: s
            for s in prior.get(c.ROLE_MERIT_ADVOCATE, {}).get("proposed_scores", [])
        }
        risk = {
            s["criterion_id"]: s
            for s in prior.get(c.ROLE_RISK_GAPS_ADVOCATE, {}).get("proposed_scores", [])
        }
        base = self._base_scores(packet)

        evaluations = []
        disagreements = []
        missing_required: list[str] = []
        evidenced = 0
        for criterion in packet.rubric.criteria:
            cid = criterion.criterion_id
            items = evidence.get(cid, [])
            supporting = [i["evidence_id"] for i in items if i["relation"] == "supporting"]
            contrary = [i["evidence_id"] for i in items if i["relation"] == "contrary"]
            # Evidence wins, not votes: anchor to the neutral/base score.
            score = neutral.get(cid, {}).get("score", base[cid])
            missing = len(supporting) == 0
            if missing:
                score = 1
                if criterion.kind == "required":
                    missing_required.append(cid)
            else:
                evidenced += 1
            evaluations.append(
                {
                    "criterion_id": cid,
                    "criterion_name": criterion.name,
                    "score": score,
                    "rationale": (
                        f"Anchored to scale point {score} from cited evidence."
                        if not missing
                        else "No direct evidence in the packet; conservative floor "
                        "score with explicit missing-evidence note (BR-013)."
                    ),
                    "supporting_evidence": supporting,
                    "contrary_evidence": contrary,
                    "missing_evidence_note": (
                        None
                        if not missing
                        else f"No direct evidence found for {criterion.name}; "
                        "absence is missing evidence, never a disqualification."
                    ),
                }
            )
            m, r = merit.get(cid), risk.get(cid)
            if m and r and abs(m["score"] - r["score"]) >= 2:
                disagreements.append(
                    {
                        "topic": f"Score spread on {cid} ({criterion.name})",
                        "positions": [
                            f"merit_advocate: {m['score']}",
                            f"risk_gaps_advocate: {r['score']}",
                        ],
                        "resolution_rationale": (
                            "Resolved to the evidence-anchored neutral score; "
                            "evidence wins, not votes (AB-004)."
                        ),
                    }
                )

        required = [cr for cr in packet.rubric.criteria if cr.kind == "required"]
        req_scores = [e["score"] for e in evaluations if e["criterion_id"] in {cr.criterion_id for cr in required}]
        if missing_required:
            label = "insufficient_evidence"
        elif all(s >= 3 for s in req_scores):
            label = "advance_to_interview"
        elif all(s <= 2 for s in req_scores):
            label = "do_not_advance"
        else:
            label = "hold_for_review"

        total = len(packet.rubric.criteria)
        if evidenced == total:
            confidence, confidence_score = "high", 80
        elif evidenced * 2 >= total:
            confidence, confidence_score = "medium", 60
        else:
            confidence, confidence_score = "low", 30

        limitations = [
            "Advisory output produced by the deterministic mock backend "
            "(ai_backend_type=none); not a live model evaluation.",
        ]
        for e in evaluations:
            if e["missing_evidence_note"]:
                limitations.append(e["missing_evidence_note"])

        return {
            "role": "synthesis_judge",
            "criterion_evaluations": evaluations,
            "disagreements": disagreements,
            "recommendation_label": label,
            "confidence": confidence,
            "confidence_score": confidence_score,
            "limitations": limitations,
        }

    def _second_synthesis(
        self, packet: EvidencePacket, role_context: dict[str, Any]
    ) -> dict:
        prior = role_context.get("prior_outputs", {})
        synthesis = prior.get(c.ROLE_SYNTHESIS_JUDGE, {})
        confidence = synthesis.get("confidence", "low")
        concurrence = "concur" if confidence == "high" else "partial"
        return {
            "role": "second_synthesis_judge",
            "concurrence": concurrence,
            "rationale": (
                "Independent re-synthesis over the same evidence packet reached "
                f"a {concurrence} position relative to the first synthesis."
            ),
            "criterion_score_deltas": [],
            "confidence": confidence,
        }

    def _rubric_calibration(
        self, packet: EvidencePacket, role_context: dict[str, Any]
    ) -> dict:
        prior = role_context.get("prior_outputs", {})
        synthesis = prior.get(c.ROLE_SYNTHESIS_JUDGE, {})
        notes = []
        consistent_all = True
        for e in synthesis.get("criterion_evaluations", []):
            has_evidence = bool(e.get("supporting_evidence"))
            consistent = (e["score"] >= 3) == has_evidence or e["score"] in (1, 2)
            consistent_all = consistent_all and consistent
            notes.append(
                {
                    "criterion_id": e["criterion_id"],
                    "anchor_consistent": consistent,
                    "note": (
                        "Score is consistent with the anchored scale given the "
                        "cited evidence density."
                        if consistent
                        else "Score/anchor tension detected; flagged for human review."
                    ),
                }
            )
        return {
            "role": "rubric_calibration_judge",
            "calibration_notes": notes,
            "overall_consistent": consistent_all,
        }
