"""Versioned prompt registry (readiness pack, coding target 4).

Source-controlled prompt templates for the council roles. Under the
deterministic mock the templates are **recorded, never executed** — the mock
derives outputs from the evidence packet directly and stamps the template id
and version into ``ProviderMetadata`` so the audit trail already carries the
prompt provenance the live backend will need.

Rules enforced here and by tests:

- every required role has a template;
- every template contains every mandatory safety constraint
  (:data:`MANDATORY_CONSTRAINTS`);
- no template contains secrets, endpoints, deployment names, tenant or
  subscription identifiers, or real applicant data.

Template files live at ``templates/<role_id>.v<N>.md``; version = highest N.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

TEMPLATES_DIR = Path(__file__).parent / "templates"

#: Roles that MUST have a registered prompt template.
REQUIRED_PROMPT_ROLES: tuple[str, ...] = (
    "request_normalizer",
    "evidence_extraction",
    "merit_advocate",
    "risk_gaps_advocate",
    "neutral_scoring_judge",
    "policy_fairness_auditor",
    "synthesis_judge",
    "quality_gate_evaluator",
    "second_synthesis_judge",
    "rubric_calibration_judge",
)

#: Every template must contain each of these constraint sentences verbatim.
MANDATORY_CONSTRAINTS: tuple[str, ...] = (
    "Use only the controlled evidence packet and source references.",
    "Do not infer facts that are not supported by the evidence.",
    "Distinguish direct, indirect, contrary, and missing evidence explicitly.",
    "Do not use protected characteristics or proxies for protected characteristics in any scoring or reasoning.",
    "Apply the rubric exactly as written.",
    "Output structured JSON only, conforming to the declared schema.",
    "Your output is advisory decision support only; it is never a hiring decision.",
    "High-impact hiring evaluations require human review.",
)

_FILENAME_RE = re.compile(r"^(?P<role>[a-z0-9_]+)\.v(?P<version>\d+)\.md$")


@dataclass(frozen=True)
class PromptTemplate:
    role_id: str
    template_id: str  # stable id, e.g. "prompt-merit_advocate"
    version: str  # e.g. "v1"
    body: str


def _scan() -> dict[str, dict[int, Path]]:
    found: dict[str, dict[int, Path]] = {}
    for path in sorted(TEMPLATES_DIR.glob("*.md")):
        match = _FILENAME_RE.match(path.name)
        if not match:
            continue
        found.setdefault(match.group("role"), {})[int(match.group("version"))] = path
    return found


def list_roles() -> list[str]:
    """Roles with at least one registered template version."""
    return sorted(_scan().keys())


def get_template(role_id: str, version: int | None = None) -> PromptTemplate:
    """Load a role's template (latest version by default)."""
    versions = _scan().get(role_id)
    if not versions:
        raise KeyError(f"no prompt template registered for role '{role_id}'")
    chosen = version if version is not None else max(versions)
    if chosen not in versions:
        raise KeyError(f"role '{role_id}' has no template version v{chosen}")
    return PromptTemplate(
        role_id=role_id,
        template_id=f"prompt-{role_id}",
        version=f"v{chosen}",
        body=versions[chosen].read_text(encoding="utf-8"),
    )
