#!/usr/bin/env python3
"""
Run the S1 precision evaluation and emit the publishable report.

Reads a corpus manifest (from build_corpus.py), fingerprints everything, and for
each query (each transform variant = a true near-dup; each hard negative = a
distractor) finds its best match across the registry pool (originals + negatives),
geometric-verifying strict-pHash candidates. Then computes precision/recall per
tier, per cluster, per split, and writes report.json + report.md.

The headline numbers are Tier A (exact) and Tier A+ (recompression-invariant)
precision against the hard-negative haystack — the kill-gate-#3 artifact.

Requires Pillow + OpenCV (see requirements.txt).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from juno_fp import eval as ev          # noqa: E402
from juno_fp.hashing import chash_file, phash_from_image  # noqa: E402
from juno_fp.match import Feature, best_candidate          # noqa: E402


def _feature(path):
    return Feature(chash=chash_file(path), phash=phash_from_image(path), ref=path)


def main():
    ap = argparse.ArgumentParser(description="Run the S1 precision eval.")
    ap.add_argument("--corpus", required=True, help="dir containing manifest.json")
    ap.add_argument("--out", default="s1_report", help="output prefix")
    ap.add_argument("--no-geom", action="store_true",
                    help="skip geometric verification (A+ then degrades to advisory B)")
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(args.corpus, "manifest.json")))

    # Build the registry pool: originals + negatives (the "previously attested" set).
    pool_items = manifest["originals"] + manifest["negatives"]
    pool = {it["path"]: _feature(it["path"]) for it in pool_items}
    feats = dict(pool)  # reuse for queries that are already in the pool

    geom_fn = None
    if not args.no_geom:
        from juno_fp.geom import orb_ransac
        geom_fn = lambda q, c: orb_ransac(q.ref, c.ref)  # noqa: E731

    trials = []

    # Positive queries: each variant should match its origin.
    for v in manifest["variants"]:
        qf = _feature(v["path"])
        cands = [pool[p] for p in pool]  # registry pool
        best, tier, _ = best_candidate(qf, cands, geom_fn=geom_fn)
        is_true = bool(best) and best.ref == v["origin"]
        trials.append(ev.Trial(query_id=v["path"], tier=tier, is_true_match=is_true,
                               is_positive=True, cluster=v["cluster"], split=v["split"]))

    # Negative queries: a hard negative has no near-dup origin; any match is a FP.
    for n in manifest["negatives"]:
        qf = feats[n["path"]]
        cands = [pool[p] for p in pool if p != n["path"]]  # exclude self
        best, tier, _ = best_candidate(qf, cands, geom_fn=geom_fn)
        trials.append(ev.Trial(query_id=n["path"], tier=tier, is_true_match=False,
                               is_positive=False, cluster=n["cluster"], split=n["split"]))

    from juno_fp.match import PHASH_STRICT, PHASH_LOOSE, GEOM_MIN_INLIERS, GEOM_MIN_INLIER_RATIO
    rep = ev.evaluate(trials, thresholds={
        "phash_strict": PHASH_STRICT, "phash_loose": PHASH_LOOSE,
        "geom_min_inliers": GEOM_MIN_INLIERS, "geom_min_inlier_ratio": GEOM_MIN_INLIER_RATIO,
        "geom": not args.no_geom,
    })

    with open(f"{args.out}.json", "w") as f:
        json.dump(ev.to_dict(rep), f, indent=2)
    with open(f"{args.out}.md", "w") as f:
        f.write(ev.to_markdown(rep))

    a = rep.per_tier["A"]["precision"]
    ap_ = rep.per_tier["A+"]["precision"]
    print(f"Tier A precision: {a}  |  Tier A+ precision: {ap_}")
    print(f"wrote {args.out}.json and {args.out}.md")


if __name__ == "__main__":
    main()
