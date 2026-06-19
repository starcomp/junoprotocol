"""
Tiered matcher (pure stdlib) — implements the JIP-2 persistence tiers.

  Tier A   : exact chash equality                       (precision ~1.0 by construction)
  Tier A+  : recompression / format-invariant —         (target ~0.999)
             chash differs, pHash within a STRICT band,
             AND geometric verification (ORB/RANSAC) confirms the same scene
  Tier B   : edited / cropped / visually-similar near-dup (ADVISORY ONLY; not provable)
  None     : no match

Geometric verification is the precision lever whose errors are NOT correlated with
the pHash family (JIP-2). Tier A+ therefore REQUIRES a geom confirmation; without a
geom result a strict-pHash candidate degrades to advisory Tier B (never A+), so the
"provable" tiers never depend on the correlated hashes alone.
"""
from dataclasses import dataclass
from typing import Optional

from .hashing import hamming64

# Thresholds (tunable; the harness sweeps these and publishes the operating point).
PHASH_STRICT = 6     # max pHash Hamming to be eligible for Tier A+
PHASH_LOOSE = 12     # max pHash Hamming to be eligible for Tier B
GEOM_MIN_INLIERS = 15
GEOM_MIN_INLIER_RATIO = 0.25

TIER_A = "A"
TIER_A_PLUS = "A+"
TIER_B = "B"


@dataclass(frozen=True)
class Feature:
    chash: str
    phash: int
    ref: str = ""  # path or id, for reporting


@dataclass(frozen=True)
class GeomResult:
    inliers: int
    inlier_ratio: float

    def confirms(self) -> bool:
        return self.inliers >= GEOM_MIN_INLIERS and self.inlier_ratio >= GEOM_MIN_INLIER_RATIO


def classify(query: Feature, candidate: Feature, geom: Optional[GeomResult] = None) -> Optional[str]:
    """Return the highest tier at which `candidate` matches `query`, or None."""
    if query.chash == candidate.chash:
        return TIER_A
    d = hamming64(query.phash, candidate.phash)
    if d <= PHASH_STRICT and geom is not None and geom.confirms():
        return TIER_A_PLUS
    if d <= PHASH_LOOSE:
        return TIER_B
    return None


# Tier ordering for "at tier-or-better" recall accounting.
_RANK = {TIER_A: 3, TIER_A_PLUS: 2, TIER_B: 1, None: 0}


def tier_rank(tier: Optional[str]) -> int:
    return _RANK[tier]


def best_candidate(query: Feature, candidates, geom_fn=None):
    """
    Return (best_candidate, tier, geom) over a candidate pool.

    geom_fn(query, candidate) -> GeomResult | None is called ONLY for candidates
    that already pass the strict pHash band (so geometric verification — the
    expensive step — runs on a tiny prefiltered set), matching the real harness.
    """
    best = (None, None, None)
    for c in candidates:
        if query.chash == c.chash:
            return (c, TIER_A, None)
        d = hamming64(query.phash, c.phash)
        geom = None
        if d <= PHASH_STRICT and geom_fn is not None:
            geom = geom_fn(query, c)
        tier = classify(query, c, geom)
        if tier_rank(tier) > tier_rank(best[1]):
            best = (c, tier, geom)
    return best
