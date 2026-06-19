---
jip: 2
title: Dual-fingerprint (chash + phash) specification
author: Juno core
status: Draft
category: Core
created: 2026-06-18
---

## Abstract

Specifies the dual content fingerprint that keys every attestation: `chash` (exact identity) and `phash` (near-duplicate identity). Together they implement the **persistent-memory** property — surfacing a prior attestation for an incidentally-degraded near-duplicate even after a watermark or C2PA credential is stripped.

## Motivation

A watermark can be stripped; a C2PA manifest can be deleted. The registry's durable differentiator is that, keyed by perceptual hash, it *remembers* a prior verdict anyway. That memory is only safe if the matching is precise — a false near-dup match is a defamation-injection risk, not a quality bug.

## Specification

### `chash` (exact)

- `chash = SHA-256(canonicalize(media))`.
- Canonicalization **MUST** be frozen and golden-vector-tested per modality (e.g. for images: decode → normalize orientation/color profile → re-encode to a canonical form before hashing). The exact canonicalization is normative and versioned.
- `chash` is the on-chain **primary key** and the unit of exact dedup.

### `phash` (near-duplicate, advisory)

Per-modality perceptual/neural hashes:

| Modality | Algorithms (v1) |
|---|---|
| Image | DCT-pHash (coarse) **+** PDQ (256-bit robust) **+** CLIP/DINOv2 embedding |
| Text | MinHash / SimHash over normalized n-grams |
| Audio *(post-testnet)* | Chromaprint |
| Video *(post-testnet)* | keyframe-sampled PDQ + temporal segment map |

- Binary hashes are compared by **Hamming** distance; embeddings by **cosine** similarity.
- A match is **advisory**: it surfaces *"previously attested AI — not re-verified."* It **MUST NOT** auto-mint a verdict or trigger a slash (see [JIP-1](JIP-1-attestation-schema.md)).

### Geometric verification (the uncorrelated precision lever)

DCT-pHash, PDQ, and CLIP/DINOv2 are three *lossy views of the same global structure*; on the hardest clusters (same-product e-commerce shots, shared meme/UI templates, burst frames) they tend to fail **together**, so treating their joint false-positive rate as the product of independent rates is wrong — it collapses toward the worst single view. Image near-dup matching above the exact tier therefore **SHOULD** add **local-keypoint geometric verification** (ORB/SIFT descriptors + RANSAC inlier-ratio), whose failure mode is *not* global-structure-correlated and which is the standard precision lever in real copy-detection systems. The published precision result (below) **MUST** report the *measured* pairwise error-correlation across the hashes used, never an assumed ρ=0.

### Tiered persistence (normative)

Persistence is split by provable precision; only the lowest tiers may render anything stronger than an advisory prior:

| Tier | Match | Provable precision | Rendering |
|---|---|---|---|
| **A** | exact `chash` | ~1.0 | may state the prior attestation as fact-of-record |
| **A+** | recompression/format-invariant (same pixels, different encoder): tight global-hash distance **+** geometric-verification inlier ratio above threshold | credibly ~0.999 | as Tier A |
| **B** | edited / cropped / visually-similar near-dup | NOT yet provable | **advisory only**, person-presence-gated, human-reviewed before any "AI" rendering, TTL-bounded revocation |

Tier B **MUST NOT** drive a defamation-grade surface until it clears a published precision bar (below).

### Index

- ANN search runs **off-chain** (pgvector at MVP; Qdrant at scale). It is **rebuildable from chain events** and is a recall accelerator, not a source of truth.
- On-chain, only the `lsh_bucket` commitment + chosen `parent_ref` linkage are stored.

### Precision gate (normative, launch-blocking)

- A **precision number against a ≥ 1,000,000 hard-negative haystack** of visually-similar-but-distinct real media (stock, memes, product shots, UI screenshots) **MUST** be measured and published before any mainnet token/spend.
- Precision **MUST** be reported **per hard cluster** (and on a dual *clean* / *current* haystack), never as a single blended aggregate that hides where matching fails.
- The exact + Tier-A+ (recompression-invariant) tiers **MAY** ship as fact-of-record once their precision is published; the hard Tier-B near-dup claim **MUST** clear this bar before driving any non-advisory surface.
- A **published adversarial-evasion rate** (regeneration / img2img / style-transfer / reframe) **MUST** accompany it.
- Persistence is defined as *surfacing a prior attestation for incidentally-degraded near-duplicates* — explicitly **NOT** robust against motivated laundering. This boundary **MUST** be stated wherever a phash result is displayed.

## Rationale

Multiple complementary image hashes (cheap coarse + robust binary + semantic embedding) let the index trade recall vs precision per vertical, and let mainnet require multi-algorithm consensus to raise precision where false positives are most costly. But because those hashes are correlated views of global structure, consensus among them is weaker than it looks on the hard clusters; **geometric verification** is added precisely because its errors are uncorrelated with theirs, and **tiered persistence** ensures only provably-precise tiers ever assert anything stronger than a dated advisory prior.

## Security considerations

phash-collision → defamation injection (see [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md)); rate-limit phash-triggered queries; multi-algorithm consensus for mainnet.

## Copyright

CC-BY-4.0.
