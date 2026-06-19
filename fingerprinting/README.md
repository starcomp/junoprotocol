# `fingerprinting/` — Content fingerprinting & near-duplicate index

> **License:** AGPL-3.0-or-later · **Status:** PLANNED (image + text targeted for MVP, REAL) · **Stack:** Python, pgvector

Computes the dual fingerprint that keys every attestation and powers the **persistent-memory** property: a recompressed / cropped / re-encoded near-duplicate still surfaces the prior attestation.

## Dual fingerprint

- **`chash`** — SHA-256 of the canonicalized bytes. **Exact identity / primary key.** Governs on-chain dedup.
- **`phash`** — per-modality perceptual / neural hash. **Near-duplicate identity.** Advisory only — a phash hit surfaces a *labeled prior claim* ("previously attested AI — not re-verified"), never a fresh verdict, never an auto-slash.

| Modality | Hashes (MVP) | Status |
|---|---|---|
| Image | DCT-pHash (cheap coarse) + **PDQ** (256-bit robust) + CLIP/DINOv2 embedding | **REAL** |
| Text | MinHash / SimHash | **REAL** |
| Audio | Chromaprint | post-testnet |
| Video | keyframe-sampled PDQ + temporal segment maps | post-testnet |

## ANN index

Approximate-nearest-neighbor lookup runs **off-chain** (it cannot run in a contract). At MVP: **pgvector** (Hamming distance for binary hashes, cosine for embeddings) behind a thin interface so `pgvector → Qdrant` is a config swap. The chain stores only the LSH bucket commitment + chosen parent linkage; the index is fully **rebuildable from chain events** — it is a recall accelerator, not a source of truth.

## Hard gate: precision

Persistence is only safe if near-dup matching is precise. **Kill-gate #3** ([`ROADMAP.md`](../ROADMAP.md) §13) requires a **published precision number against a ≥1M hard-negative haystack** of visually-similar-but-distinct real media, plus a published adversarial-evasion rate (regeneration / img2img / restyle / reframe). A false near-dup match is a **defamation-injection** risk, not a mere quality bug — see [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md).

## S1 precision harness (`juno_fp/` + `scripts/`)

The cheapest credible kill-gate-#3 artifact: a **publishable precision number** for the *provable* persistence tiers — **Tier A** (exact `chash`) and **Tier A+** (recompression / format-invariant, confirmed by ORB/RANSAC geometric verification) — measured against a hard-negative haystack, per [JIP-2](../specs/JIP-2-fingerprint.md). Tier B (edited / cropped near-dup) is advisory-only and not gated by this number.

```
fingerprinting/
├── juno_fp/
│   ├── hashing.py   # chash (SHA-256) + 64-bit DCT pHash + Hamming   — PURE STDLIB
│   ├── match.py     # tiered matcher (A / A+ / B), thresholds          — PURE STDLIB
│   ├── eval.py      # precision/recall per tier · per cluster · split  — PURE STDLIB
│   ├── geom.py      # ORB + RANSAC geometric verification              — needs OpenCV
│   └── transforms.py# recompress/format/resize/crop transform matrix   — needs Pillow
├── scripts/
│   ├── build_corpus.py  # originals (+subfolder=cluster) → transform variants + manifest.json
│   └── run_s1.py        # fingerprint, match, eval → report.json + report.md
└── tests/test_smoke.py  # dependency-free: verifies the core logic anywhere python3 runs
```

**Design split:** the parts that produce the number — DCT pHash, the tiered matcher, the eval math — are **pure stdlib** and verified by `tests/test_smoke.py` (no install). Only the real-image edges (`geom.py`, `transforms.py`, and `scripts/run_s1.py`) need Pillow/OpenCV (`requirements.txt`).

Run:

```sh
# core logic — no dependencies
python3 fingerprinting/tests/test_smoke.py

# real eval (needs requirements.txt + your own corpus)
pip install -r fingerprinting/requirements.txt
python3 fingerprinting/scripts/build_corpus.py --originals <dir> --negatives <dir> --out corpus/
python3 fingerprinting/scripts/run_s1.py --corpus corpus/ --out s1_report
#   → s1_report.json + s1_report.md (precision per tier / cluster / clean-vs-current split)
```

**Corpus you supply:** a few thousand `--originals` (organized in `clean/` or `current/` then by content-type subfolder) and the **≥1M `--negatives`** hard-negative haystack (visually-similar-but-distinct *real* media: stock near-dups, meme/UI templates, same-product shots). The harness generates the near-dup variants; you bring the originals and the haystack. Report the adversarial-evasion rate (regeneration/img2img/restyle) separately — it is the declared laundering boundary, not a persistence positive.

## CI

Frozen canonicalization + golden-vector tests; an **adversarial transform suite** (crop / recompress / rotate / noise / watermark-strip) runs on every PR and reports recall against documented benign-transform sets.
