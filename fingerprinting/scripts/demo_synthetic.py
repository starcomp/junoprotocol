#!/usr/bin/env python3
"""
ILLUSTRATIVE end-to-end S1 run on a SYNTHETIC corpus — zero dependencies.

Builds synthetic originals + their transform-matrix variants + hard/confusable
negatives entirely in memory, runs the real match→eval pipeline (with a
pure-python stand-in for geometric verification), and writes report.json + .md.

⚠️ NOT publishable. Synthetic images + a correlation stand-in for ORB/RANSAC.
Purpose: prove the pipeline runs and show the report shape before a real ≥1M
haystack exists. Real numbers come from scripts/run_s1.py over real images.

Run: python3 fingerprinting/scripts/demo_synthetic.py --out fingerprinting/examples/s1_demo_report
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from juno_fp import eval as ev          # noqa: E402
from juno_fp import synthetic as syn     # noqa: E402
from juno_fp.match import best_candidate  # noqa: E402

DISCLAIMER = (
    "> ⚠️ **ILLUSTRATIVE — NOT PUBLISHABLE.** Synthetic images and a pure-python "
    "correlation *stand-in* for ORB/RANSAC geometric verification. This only "
    "demonstrates the harness pipeline and report shape. Real, publishable numbers "
    "come from `scripts/run_s1.py` over a real ≥1M hard-negative haystack.\n"
)


def build_corpus():
    mats = {}          # ref -> matrix
    origins = []       # (ref, cluster)
    variants = []      # (ref, origin_ref, cluster, split)
    negatives = []     # (ref, cluster, split)

    origin_specs = [
        ("grad_h", {}), ("grad_v", {}), ("grad_diag", {}), ("radial", {}),
        ("sine", {"fx": 2, "fy": 1}), ("sine", {"fx": 1, "fy": 3, "phase": 1.0}),
        ("blobs", {"k": 4}), ("blobs", {"k": 6}),
    ]
    for idx, (kind, kw) in enumerate(origin_specs):
        ref = f"orig:{kind}:{idx}"
        m = syn.make_image(kind, seed=idx, **kw)
        mats[ref] = m
        origins.append((ref, kind))
        split = "clean" if idx % 2 == 0 else "current"
        # invariance variants: exact byte-copy (Tier A) + recompression-like (Tier A+)
        for tname, tm in [("exact", [row[:] for row in m]),
                          ("quant16", syn.quantize(m, 16)),
                          ("quant32", syn.quantize(m, 32)),
                          ("jitter4", syn.jitter(m, 4, seed=idx))]:
            vref = f"var:{kind}:{idx}:{tname}"
            mats[vref] = tm
            variants.append((vref, ref, kind, split))
        # degrading variants (Tier B-ish)
        for tname, tm in [("crop10", syn.crop(m, 0.1)), ("resize50", syn.resize_half(m))]:
            vref = f"var:{kind}:{idx}:{tname}"
            mats[vref] = tm
            variants.append((vref, ref, kind, split))

    # distinct hard negatives (different content)
    for s in range(6):
        ref = f"neg:distinct:{s}"
        mats[ref] = syn.make_image("blobs", seed=100 + s, k=5)
        negatives.append((ref, "distinct", "current"))
    for s in range(4):
        ref = f"neg:sine:{s}"
        mats[ref] = syn.make_image("sine", seed=200 + s, fx=3 + s, fy=2)
        negatives.append((ref, "distinct", "clean"))

    # CONFUSABLE negatives: an origin with a large occlusion — globally similar-ish,
    # different content. The teaching case: pHash may flag it, geometric
    # verification should keep it OUT of the provable A+ tier.
    for idx in range(3):
        oref, kind = origins[idx]
        ref = f"neg:confusable:{idx}"
        mats[ref] = syn.occlude(mats[oref], frac=0.5, seed=idx + 1)
        negatives.append((ref, "confusable", "current"))

    return mats, origins, variants, negatives


def main():
    ap = argparse.ArgumentParser(description="Illustrative synthetic S1 run.")
    ap.add_argument("--out", default="s1_demo_report")
    args = ap.parse_args()

    mats, origins, variants, negatives = build_corpus()

    pool_refs = [r for (r, _) in origins] + [r for (r, _, _) in negatives]
    pool = [syn.feature_of(mats[r], r) for r in pool_refs]

    def geom_fn(q, c):
        return syn.synthetic_geom(mats[q.ref], mats[c.ref])

    trials = []
    for (vref, oref, cluster, split) in variants:
        qf = syn.feature_of(mats[vref], vref)
        best, tier, _ = best_candidate(qf, pool, geom_fn=geom_fn)
        trials.append(ev.Trial(vref, tier, bool(best) and best.ref == oref, True, cluster, split))
    for (nref, cluster, split) in negatives:
        qf = syn.feature_of(mats[nref], nref)
        cands = [c for c in pool if c.ref != nref]
        best, tier, _ = best_candidate(qf, cands, geom_fn=geom_fn)
        trials.append(ev.Trial(nref, tier, False, False, cluster, split))

    from juno_fp.match import PHASH_STRICT, PHASH_LOOSE, GEOM_MIN_INLIERS, GEOM_MIN_INLIER_RATIO
    rep = ev.evaluate(trials, thresholds={
        "phash_strict": PHASH_STRICT, "phash_loose": PHASH_LOOSE,
        "geom_min_inliers": GEOM_MIN_INLIERS, "geom_min_inlier_ratio": GEOM_MIN_INLIER_RATIO,
        "synthetic": True,
    })

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(f"{args.out}.json", "w") as f:
        json.dump(ev.to_dict(rep), f, indent=2)
    md = DISCLAIMER + "\n" + ev.to_markdown(rep, title="S1 — ILLUSTRATIVE synthetic run")
    with open(f"{args.out}.md", "w") as f:
        f.write(md)

    pt = rep.per_tier
    print(f"trials={rep.trials} positives={rep.positives}")
    print(f"Tier A   precision={pt['A']['precision']}  (tp={pt['A']['tp']} fp={pt['A']['fp']})")
    print(f"Tier A+  precision={pt['A+']['precision']}  (tp={pt['A+']['tp']} fp={pt['A+']['fp']})")
    print(f"Tier B   precision={pt['B']['precision']}  (tp={pt['B']['tp']} fp={pt['B']['fp']})")
    print(f"wrote {args.out}.json and {args.out}.md")


if __name__ == "__main__":
    main()
