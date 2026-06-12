"""hr_eval_lab — slice-e1 Single-Candidate Calibrated Evaluation Council.

Advisory, evidence-grounded candidate evaluation behind a local FastAPI facade.
Deterministic mock provider by default (ai_backend_type = "none"); the Foundry
Agents backend is a non-functional seam stub (live wiring deferred by PO
decision 2026-06-11). No live cloud activity of any kind occurs in this slice.
"""

__version__ = "0.1.0"
