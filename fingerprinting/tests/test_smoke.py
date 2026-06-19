#!/usr/bin/env python3
"""
Dependency-free smoke test for the S1 harness core (no Pillow/OpenCV/numpy needed).

Exercises the pieces that produce the publishable number — the DCT pHash, the
tiered matcher, best-candidate retrieval, and the precision/recall eval — on
synthetic data, so the logic is verified anywhere `python3` runs.
Run: python3 fingerprinting/tests/test_smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from juno_fp.hashing import sha256_hex, dct_phash, hamming64  # noqa: E402
from juno_fp.match import (Feature, GeomResult, classify, best_candidate,  # noqa: E402
                           PHASH_STRICT, PHASH_LOOSE, TIER_A, TIER_A_PLUS, TIER_B)
from juno_fp import eval as ev  # noqa: E402

_checks = 0


def ok(cond, msg):
    global _checks
    assert cond, "FAIL: " + msg
    _checks += 1
    print("  ok:", msg)


# --------------------------------------------------------------------------- #
def test_chash():
    a = b"the same bytes"
    ok(sha256_hex(a) == sha256_hex(b"the same bytes"), "chash equal for identical bytes")
    ok(sha256_hex(a) != sha256_hex(b"different bytes"), "chash differs for different bytes")


def test_match_logic():
    origin = Feature(chash="X", phash=0b0)
    exact = Feature(chash="X", phash=0b0)
    near = Feature(chash="Y", phash=0b111)          # hamming 3 -> within STRICT
    loose = Feature(chash="Z", phash=(1 << 10) - 1)  # hamming 10 -> within LOOSE
    far = Feature(chash="W", phash=(1 << 20) - 1)    # hamming 20 -> none

    ok(classify(origin, exact) == TIER_A, "exact chash -> Tier A")
    ok(hamming64(origin.phash, near.phash) <= PHASH_STRICT, "near is within strict band")
    ok(classify(origin, near, GeomResult(20, 0.4)) == TIER_A_PLUS, "strict band + geom -> A+")
    ok(classify(origin, near, None) == TIER_B, "strict band WITHOUT geom -> advisory B (never A+)")
    ok(classify(origin, near, GeomResult(3, 0.05)) == TIER_B, "weak geom -> B, not A+")
    ok(hamming64(origin.phash, loose.phash) <= PHASH_LOOSE, "loose within loose band")
    ok(classify(origin, loose) == TIER_B, "loose -> Tier B")
    ok(classify(origin, far) is None, "far -> no match")


def test_best_candidate():
    origin = Feature(chash="orig", phash=0b0, ref="orig")
    query = Feature(chash="var", phash=0b11, ref="var")               # hamming 2 to origin
    negs = [Feature(chash=f"n{i}", phash=(1 << (13 + i)) - 1, ref=f"n{i}") for i in range(3)]
    pool = [origin] + negs

    def geom_fn(q, c):  # confirms only the genuine near-dup pair
        return GeomResult(40, 0.6) if c.ref == "orig" else GeomResult(0, 0.0)

    best, tier, _ = best_candidate(query, pool, geom_fn=geom_fn)
    ok(best.ref == "orig" and tier == TIER_A_PLUS, "best candidate = true origin at A+")


def test_eval_precision():
    T = ev.Trial
    trials = [
        T("v1", TIER_A_PLUS, True, True, "stock", "current"),
        T("v2", TIER_A_PLUS, True, True, "stock", "current"),
        T("v3", TIER_A_PLUS, True, True, "memes", "clean"),
        T("v4", TIER_B, False, True, "memes", "clean"),   # positive that mis-matched a negative at B
        T("n1", None, False, False, "stock", "current"),  # correct reject
        T("n2", TIER_B, False, False, "products", "current"),  # false positive at B
    ]
    rep = ev.evaluate(trials)
    ok(rep.positives == 4, "4 positive queries counted")
    ok(rep.per_tier[TIER_A_PLUS]["tp"] == 3 and rep.per_tier[TIER_A_PLUS]["fp"] == 0,
       "A+ has 3 TP / 0 FP")
    ok(rep.per_tier[TIER_A_PLUS]["precision"] == 1.0, "A+ precision = 1.0 (no false A+)")
    ok(rep.per_tier[TIER_B]["fp"] == 2 and rep.per_tier[TIER_B]["precision"] == 0.0,
       "B precision = 0.0 with 2 FP (the harness surfaces where it fails)")
    ok(abs(rep.per_tier[TIER_A_PLUS]["recall_at_or_better"] - 0.75) < 1e-9,
       "recall @>=A+ = 3/4")
    md = ev.to_markdown(rep)
    ok("Precision & recall by tier" in md and "Precision by hard-negative cluster" in md,
       "markdown report renders")


def test_dct_phash_sanity():
    N = 16

    def grad_h():  # horizontal gradient (low-freq energy along columns)
        return [[(j * 255) // (N - 1) for j in range(N)] for _ in range(N)]

    def grad_v():  # vertical gradient
        return [[(i * 255) // (N - 1) for _ in range(N)] for i in range(N)]

    def radial():
        c = (N - 1) / 2.0
        return [[min(255, int((((i - c) ** 2 + (j - c) ** 2) ** 0.5) * 24)) for j in range(N)]
                for i in range(N)]

    def recompress(mat, step=24):  # simulate quantization: keep structure, change bytes
        return [[(v // step) * step for v in row] for row in mat]

    ph_h, ph_v, ph_r = dct_phash(grad_h()), dct_phash(grad_v()), dct_phash(radial())
    within = hamming64(ph_h, dct_phash(recompress(grad_h())))
    cross_hv = hamming64(ph_h, ph_v)
    cross_hr = hamming64(ph_h, ph_r)

    print(f"     [phash] within(recompress)={within}  cross(h,v)={cross_hv}  cross(h,r)={cross_hr}")
    ok(within <= PHASH_LOOSE, f"recompressed near-dup stays within loose band ({within})")
    ok(cross_hv > within and cross_hr > within, "distinct patterns are farther than a recompress")
    ok(cross_hv >= 12, f"clearly-different patterns are clearly far ({cross_hv})")


if __name__ == "__main__":
    for fn in [test_chash, test_match_logic, test_best_candidate,
               test_eval_precision, test_dct_phash_sanity]:
        print(fn.__name__)
        fn()
    print(f"\nOK — {_checks} checks passed.")
