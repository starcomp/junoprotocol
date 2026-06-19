> ⚠️ **ILLUSTRATIVE — NOT PUBLISHABLE.** Synthetic images and a pure-python correlation *stand-in* for ORB/RANSAC geometric verification. This only demonstrates the harness pipeline and report shape. Real, publishable numbers come from `scripts/run_s1.py` over a real ≥1M hard-negative haystack.

# S1 — ILLUSTRATIVE synthetic run

- Trials: **61**  ·  Positives (true near-dups): **48**
- Thresholds: `{'phash_strict': 6, 'phash_loose': 12, 'geom_min_inliers': 15, 'geom_min_inlier_ratio': 0.25, 'synthetic': True}`

## Precision & recall by tier

| Tier | TP | FP | Precision | Recall @≥tier |
|---|---:|---:|---:|---:|
| A (exact) | 8 | 0 | 1.0000 | 0.167 |
| A+ (recompress-invariant) | 17 | 0 | 1.0000 | 0.521 |
| B (advisory near-dup) | 4 | 0 | 1.0000 | 0.604 |

## Precision by hard-negative cluster

| Cluster | A | A+ | B |
|---|---:|---:|---:|
| blobs | 1.0000 | 1.0000 | 1.0000 |
| confusable | — | — | — |
| distinct | — | — | — |
| grad_diag | 1.0000 | 1.0000 | — |
| grad_h | 1.0000 | 1.0000 | — |
| grad_v | 1.0000 | 1.0000 | — |
| radial | 1.0000 | 1.0000 | 1.0000 |
| sine | 1.0000 | 1.0000 | 1.0000 |

## Precision by haystack split

| Split | A | A+ | B |
|---|---:|---:|---:|
| clean | 1.0000 | 1.0000 | 1.0000 |
| current | 1.0000 | 1.0000 | 1.0000 |

> Tiers A and A+ are the **provable** persistence tiers and may render as fact of record. Tier B is **advisory only** (human-reviewed, person-presence-gated) and is not gated by this number. Persistence surfaces a *labeled prior* for incidentally-degraded near-duplicates — it is **not** robust to motivated regeneration-laundering (report the adversarial-evasion rate separately). See JIP-2 / JIP-4.