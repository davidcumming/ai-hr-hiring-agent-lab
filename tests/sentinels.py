"""Never-log sentinel strings (DT-011, BR-010).

Each sentinel is a distinctive substring drawn verbatim from the synthetic
fixture resume / cover-letter bodies (and therefore from prompt/mock I/O,
which quotes packet segments). None of these strings may ever appear in any
log line or in any table-equivalent (metadata-first) persistence row.

Phrases are chosen to survive the packet builder's whitespace normalization
(single-line spans only) and to be unique to fixture document bodies — they do
not occur in artifact ids, role names, statuses, or other safe metadata.
"""

from __future__ import annotations

#: Substrings unique to fixtures/candidates/cand-sample-001/resume.md
RESUME_SENTINELS = [
    "jordan.rivera@example.test",
    "Provincial Health Data Agency",
    "fare-system upgrade",
    "City Transit Modernization Office",
    "Synthetic University",
]

#: Substrings unique to fixtures/candidates/cand-sample-001/cover-letter.md
COVER_LETTER_SENTINELS = [
    "reading knowledge of French",
    "available with four weeks' notice",
    "enrolled in a workplace French",
]

ALL_SENTINELS = RESUME_SENTINELS + COVER_LETTER_SENTINELS
