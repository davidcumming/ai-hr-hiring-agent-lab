"""Standard response envelope (adopted API-contracts style, slice field subset).

Status vocabulary emitted this slice: ``completed``, ``blocked``,
``validation_failed``, ``unauthorized``. The remainder of the adopted
vocabulary (``needs_input``, ``error``) is declared RESERVED in the OpenAPI
document and never emitted here. ``case_id`` is always null this slice
(case-less rule, PO §2.2.1). ``user_message``/``safe_details`` obey never-log
discipline: no document text ever appears in them.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EnvelopeStatus = Literal[
    "completed",
    "blocked",
    "validation_failed",
    "unauthorized",
    "needs_input",  # reserved — never emitted this slice
    "error",  # reserved — never emitted this slice
]


class Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EnvelopeStatus
    evaluation_id: Optional[str] = None
    case_id: None = None  # always null this slice (case-less evaluations)
    correlation_id: Optional[str] = None
    user_message: str = ""
    safe_details: Optional[str] = None
    result: Optional[Any] = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
