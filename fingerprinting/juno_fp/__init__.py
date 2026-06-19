"""
juno_fp — Juno fingerprinting & the S1 precision harness.

S1 is the cheapest credible kill-gate-#3 artifact: a PUBLISHABLE precision number
for the provably-precise persistence tiers — exact (Tier A) and recompression /
format-invariant (Tier A+) — measured against a hard-negative haystack, per JIP-2.

Design split (so this runs anywhere):
  - hashing.py / match.py / eval.py  -> PURE STDLIB. The DCT-pHash, the tiered
    matcher, and the precision/recall math have no third-party dependencies and
    are unit-tested by tests/test_smoke.py with no install required.
  - geom.py / transforms.py          -> OPTIONAL deps (OpenCV / Pillow), imported
    lazily. Needed only to run the harness over REAL images (scripts/).
"""
from . import hashing, match, eval  # noqa: F401

__all__ = ["hashing", "match", "eval"]
__version__ = "0.0.0"
