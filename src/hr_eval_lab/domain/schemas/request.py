"""EvaluationRequest — the POST /api/evaluations body (single schema source)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hr_eval_lab.config import RigorMode


class EvaluationRequest(BaseModel):
    """One evaluation request: fixture candidate by reference OR inline text.

    ``requested_rigor`` is ADVISORY ONLY and can never lower the
    server-resolved rigor (BR-002); any downgrade attempt is recorded.
    """

    model_config = ConfigDict(extra="forbid")

    position_id: str = Field(min_length=1)
    candidate_ref: Optional[str] = None
    resume_text: Optional[str] = None
    cover_letter_text: Optional[str] = None
    idempotency_key: str = Field(min_length=1)
    evaluation_question: Optional[str] = None
    requested_rigor: Optional[RigorMode] = None

    @model_validator(mode="after")
    def _candidate_source_shape(self) -> "EvaluationRequest":
        inline = self.resume_text is not None or self.cover_letter_text is not None
        if self.candidate_ref is not None and inline:
            raise ValueError("provide candidate_ref OR inline resume/cover-letter text, not both")
        if self.candidate_ref is None:
            if self.resume_text is None or self.cover_letter_text is None:
                raise ValueError(
                    "provide candidate_ref, or both resume_text and cover_letter_text"
                )
        return self
