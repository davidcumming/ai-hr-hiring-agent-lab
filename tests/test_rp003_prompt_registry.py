"""RP-009: versioned prompt registry — coverage, mandatory safety constraints,
no secrets / no real-looking tenant/subscription/endpoint values (readiness pack).
"""

from __future__ import annotations

import re

import pytest

from hr_eval_lab.prompts.registry import (
    MANDATORY_CONSTRAINTS,
    REQUIRED_PROMPT_ROLES,
    get_template,
    list_roles,
)

#: Anything matching these would indicate leaked live config or real data.
FORBIDDEN_PATTERNS = [
    re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I),  # GUIDs
    re.compile(r"https?://(?!example\.)[a-z0-9.-]+\.(azure|microsoft|windows)\.[a-z.]+", re.I),
    re.compile(r"(api[_-]?key|client[_-]?secret|connection[_-]?string|sas[_-]?token)\s*[:=]", re.I),
    re.compile(r"(subscription[_-]?id|tenant[_-]?id)\s*[:=]", re.I),
    re.compile(r"AccountKey=", re.I),
]


def test_rp009_all_required_roles_registered():
    assert set(REQUIRED_PROMPT_ROLES) <= set(list_roles())
    assert len(REQUIRED_PROMPT_ROLES) == 10


@pytest.mark.parametrize("role_id", REQUIRED_PROMPT_ROLES)
def test_rp009_every_template_contains_every_mandatory_constraint(role_id):
    template = get_template(role_id)
    assert template.template_id == f"prompt-{role_id}"
    assert template.version == "v1"
    for constraint in MANDATORY_CONSTRAINTS:
        assert constraint in template.body, (role_id, constraint)


@pytest.mark.parametrize("role_id", REQUIRED_PROMPT_ROLES)
def test_rp009_no_secrets_or_live_identifiers_in_templates(role_id):
    body = get_template(role_id).body
    for pattern in FORBIDDEN_PATTERNS:
        assert not pattern.search(body), (role_id, pattern.pattern)


def test_rp009_unknown_role_and_version_fail_safely():
    with pytest.raises(KeyError):
        get_template("not_a_role")
    with pytest.raises(KeyError):
        get_template("merit_advocate", version=99)
