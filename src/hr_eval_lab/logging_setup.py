"""Central logging configuration + never-log redaction (BR-010, DT-011).

Log records may carry only: ids, hashes, statuses, role names, durations, and
counters. The primary control is that no call site passes content; this module
adds a defense-in-depth redaction filter that rejects any record containing a
registered sentinel substring (sentinels are derived from fixture bodies by the
test suite). No resume text, prompt text, or model I/O ever reaches a log line.
"""

from __future__ import annotations

import logging
from typing import Iterable

LOGGER_NAME = "hr_eval_lab"

_SENTINELS: set[str] = set()


def register_sentinels(sentinels: Iterable[str]) -> None:
    """Register never-log sentinel substrings (defense-in-depth)."""
    for s in sentinels:
        if s:
            _SENTINELS.add(s)


def clear_sentinels() -> None:
    _SENTINELS.clear()


class RedactionFilter(logging.Filter):
    """Drop (and replace with a safe marker) any record carrying sentinel text."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # pragma: no cover - malformed record
            record.msg = "[REDACTED: unrenderable log record]"
            record.args = ()
            return True
        for sentinel in _SENTINELS:
            if sentinel in message:
                record.msg = "[REDACTED: never-log sentinel match]"
                record.args = ()
                break
        return True


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the central lab logger (configured once, idempotent)."""
    logger = logging.getLogger(LOGGER_NAME if name is None else f"{LOGGER_NAME}.{name}")
    root = logging.getLogger(LOGGER_NAME)
    if not any(isinstance(f, RedactionFilter) for f in root.filters):
        root.addFilter(RedactionFilter())
        root.setLevel(logging.INFO)
    return logger
