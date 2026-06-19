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

## CI

Frozen canonicalization + golden-vector tests; an **adversarial transform suite** (crop / recompress / rotate / noise / watermark-strip) runs on every PR and reports recall against documented benign-transform sets.
