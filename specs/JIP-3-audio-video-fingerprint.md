---
jip: 3
title: Audio & video fingerprinting
author: Juno core
status: Draft
category: Core
created: 2026-06-18
requires: 1, 2
---

## Abstract

Extends the dual-fingerprint model of [JIP-2](JIP-2-fingerprint.md) from image+text to **audio** and **video**, and specifies the **temporal segment map** — the structure that records *which spans* of a time-based medium are AI-generated/watermarked and whose hash is committed on-chain as the canonical attestation's `segment_map_hash` ([JIP-1](JIP-1-attestation-schema.md)). Audio and video are **post-testnet** modalities (the testnet MVP is image+text only), so this spec is Draft and forward-looking.

## Motivation

A watermark or C2PA manifest on an audio clip or video can be stripped by a transcode; the registry's durable value is that, keyed by perceptual hash, it still surfaces the prior attestation for an incidentally-degraded near-duplicate. Time-based media adds a dimension images lack: a file is rarely uniformly AI or uniformly real (a podcast with one cloned segment; a video with three AI-generated shots). A single file-level verdict is therefore lossy and, for identifiable people, defamation-prone. We need (a) robust per-modality perceptual hashes and (b) a precise, on-chain-committed map of *which segments* a verdict applies to.

## Specification

The key words MUST, SHOULD, and MAY are as defined in RFC 2119/8174.

### 1. Audio

**`chash` (exact).** Canonicalize before hashing, and the canonicalization MUST be frozen and golden-vector-tested:

1. decode to PCM;
2. downmix to **mono**;
3. resample to **16 kHz**;
4. quantize to **signed 16-bit little-endian** samples;
5. write a canonical headerless raw-PCM byte stream.

`chash = SHA-256(canonical_pcm)`. This is the exact-identity primary key; bit-identical re-encodes collapse to one `chash`.

**`phash` (near-duplicate, advisory).** Two complementary fingerprints:

- **Chroma fingerprint** — a Chromaprint/AcoustID-style chroma fingerprint over the canonical PCM (the v1 robust hash). Compared by **Hamming** distance over aligned sub-fingerprints. Robust to bitrate/codec changes and mild EQ.
- **Neural audio embedding** *(optional, v1.1)* — a learned fixed-length embedding for semantic near-dup (e.g. the same generated voice across containers). Compared by **cosine** similarity.

Declared **failure boundaries** (a match is NOT expected to survive these): pitch-shift, time-stretch, heavy re-mixing, very short (<3 s) clips, and — explicitly — **voice-cloning regeneration** (a freshly regenerated clip is new content, not a near-duplicate).

### 2. Video

**`chash` (exact).** Canonicalize the elementary stream (not the container): decode, normalize frame rate to a canonical sampling for hashing of the decoded frames + audio track (the audio track reuses §1), then `SHA-256` of the canonical byte stream. Container/metadata differences MUST NOT change `chash`.

**`phash` (near-duplicate, advisory).**

- **Keyframe-sampled PDQ** — sample keyframes at a defined cadence (v1: **2 fps or every shot-boundary keyframe, whichever is denser, capped at 4 fps**), PDQ-hash each sampled frame (256-bit), and store the ordered sequence of frame hashes. Near-dup is a **sequence-alignment** over frame-PDQ Hamming distances (tolerant of trimming/inserted frames).
- **Per-shot embedding** *(optional, v1.1)* — a shot-level neural embedding for semantic matching across re-encodes/letterboxing.

Robust to re-encoding, bitrate change, moderate crop/letterbox, and trimming. Declared **failure boundary:** regeneration / heavy editing / style-transfer of the visual content.

### 3. Temporal segment map (normative)

The segment map is the canonical record of *which spans* a verdict covers. It is an **off-chain, content-addressed blob**; only its hash goes on-chain.

**Serialization.** Canonical form is **CBOR** (deterministic encoding, RFC 8949 §4.2); a canonical-JSON form (sorted keys, no insignificant whitespace) is permitted for tooling. The serialization MUST be byte-deterministic so the hash is reproducible.

**Schema (v1).**

```
SegmentMap {
  version: u8,                 // = 1
  media_chash: bytes32,        // binds the map to its media (must equal the attestation chash)
  duration_ms: u64,
  segments: [ Segment ]        // ordered by start_ms, non-overlapping per modality
}

Segment {                      // audio form
  start_ms: u64,
  end_ms: u64,
  modality: "audio",
  verdict: u8,                 // 0 not, 1 watermarked, 2 uncertain  (mirrors JIP-1)
  confidence: u16              // basis points
}

Segment {                      // video form
  start_ms: u64,
  end_ms: u64,
  modality: "video",
  bbox: [x, y, w, h] | null,   // optional normalized region within frame(s)
  verdict: u8,
  confidence: u16
}
```

**On-chain commitment.** `segment_map_hash = SHA-256(canonical_serialization)` and MUST be written into the canonical attestation's `segment_map_hash` field ([JIP-1](JIP-1-attestation-schema.md)). An attestation over time-based media SHOULD include a segment map; if the whole file is uniformly classified, a single full-duration segment is used. The blob is stored on the DA layer (IPFS at testnet, Arweave for permanence at mainnet) addressed by this hash.

**Verdict reconciliation.** The attestation's top-level `verdict`/`confidence` (JIP-1) for time-based media is a SUMMARY (e.g. "contains AI segments"); the segment map is authoritative for *where*. Consumers MUST NOT render a file-level "AI" claim over identifiable persons without consulting the segment map (defamation control — see Security considerations and [JIP-2](JIP-2-fingerprint.md)).

### 4. Indexing

Audio chroma fingerprints and video keyframe-PDQ sequences are indexed for near-dup off-chain, per-modality and sharded (audio sub-fingerprint inverted index; video frame-PDQ ANN with sequence re-ranking), consistent with JIP-2's "off-chain ANN + on-chain commitment" model. The index is rebuildable from chain events; the chain stores only the `lsh_bucket` commitment + chosen `parent_ref` linkage.

### 5. Precision gate (normative, launch-blocking for these modalities)

Before audio/video attestations are offered in any paid/production capacity:

- A **precision** number MUST be published against a **hard-negative haystack** of similar-but-distinct *real* audio/video (e.g. covers, live versions, re-uploads, common stock footage, screen recordings), sized to the relevant deployment, alongside an **adversarial-evasion rate** (regeneration / pitch-shift / time-stretch for audio; re-render / restyle for video).
- Persistence MUST be stated wherever surfaced as *surfacing a labeled prior for incidentally-degraded near-duplicates* — never a fresh re-detection, and **not** robust to motivated laundering.

## Rationale

Chromaprint and PDQ are mature, open, and robust to the dominant benign transforms (transcode/bitrate, re-encode/crop) while cheap to index at scale; neural embeddings are layered as optional semantic backstops rather than the primary key so the core remains explainable and auditable. The segment map is content-addressed and off-chain because per-span data is large and privacy-sensitive (it may localize a real person in a frame) — only its hash is anchored, mirroring JIP-2's treatment of person-linkable perceptual data.

## Backwards compatibility

Additive. No change to the JIP-1 on-chain schema — audio/video reuse the existing `chash`, `phash_commit`, `lsh_bucket`, and `segment_map_hash` fields. `model_lineage` gains audio/video values (Lyria, Veo). The segment map carries its own `version` for independent evolution.

## Security considerations

- **Defamation / false near-dup:** identical to [JIP-2](JIP-2-fingerprint.md) but aggravated by localization — a wrong segment can place "AI" on a specific person at a specific timestamp. phash stays **advisory**; segment-level claims over identifiable persons require human review; the precision gate is launch-blocking. See [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md).
- **Segment-map tampering:** the on-chain `segment_map_hash` makes the blob tamper-evident; a mismatch between blob and committed hash MUST be treated as invalid.
- **Partial-coverage laundering:** an attacker may regenerate only the watermarked segments. This is the declared regeneration boundary; the registry surfaces the prior attestation for unmodified spans and cannot vouch for regenerated ones.
- **Cost/DoS:** keyframe sampling and chroma extraction are bounded by the defined cadences to cap per-item compute; oracles MUST rate-limit fingerprint jobs.

## Copyright

CC-BY-4.0.
