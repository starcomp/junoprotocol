---
jip: 1
title: Canonical chain-portable attestation object
author: Juno core
status: Draft
category: Core
created: 2026-06-18
requires: 2
---

## Abstract

Defines the **canonical attestation object** — the single, versioned, chain-portable field layout that every Juno provenance attestation conforms to. It is defined **once** and mapped deterministically onto both an EAS ABI encoding (testnet/L2) and a Borsh/Anchor struct (mainnet-conditional Solana), so submitters and integrators integrate against one schema regardless of the underlying chain.

## Motivation

The registry's value (neutral, multi-writer, persistent, portable) collapses if integrators must re-integrate on every chain migration or if two vendors encode verdicts differently. A frozen canonical schema with a proven round-trip mapping is the foundation of the **neutral registry** property.

## Specification

### Fields

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `u8` | Versioned for forward-compat. Readers **MUST** reject unknown major versions. |
| `chash` | `bytes32` | SHA-256 of the canonicalized media bytes. **PRIMARY KEY.** Exact dedup; **MUST** be unique on-chain. |
| `phash_commit` | `bytes32` | Commitment over the full neural perceptual hash. The full `phash` is emitted in the event/calldata, not stored as state. |
| `lsh_bucket` | `bytesN` | A locality-**preserving** bucket key (NOT a cryptographic hash) enabling cheap on-chain coarse near-dup linkage. Hamming-locality **MUST** be preserved. |
| `verdict` | `u8` | `0 = not`, `1 = watermarked`, `2 = uncertain`. **MUST NEVER** encode a bare factual "is AI" assertion; it is a probabilistic detector opinion. |
| `confidence` | `u16` | Basis points (0–10000). |
| `model_lineage` | `u16` | Enum: Gemini / Imagen / Veo / Lyria / partner / unknown. |
| `detector_version` | `u16` | Identifies the exact detector build, so a bad version can be bulk-flagged. |
| `c2pa_manifest_hash` | `bytes32` | Hash of the verified C2PA manifest, if any (else zero). |
| `segment_map_hash` | `bytes32` | Hash of the off-chain segment map (which regions/timestamps are watermarked). |
| `attester_set_id` | `u32` | Which signer set produced this attestation. |
| `sig_ref` | `bytes` | k-of-n ECDSA signature references (testnet). BLS aggregate reference (mainnet-conditional). |
| `timestamp` | `u64` | Unix seconds. |
| `parent_ref` | `refUID` | Near-dup parent linkage (EAS `refUID` / parent-leaf pointer). Zero if none. |
| `provenance` | `u8` | `0 = staked-real`, `1 = mock`. Mock attestations **MUST** be excluded from every reward/slash path and rendered distinctly. |

### Chain mappings

- **EAS (testnet/L2):** the fields above register as an EAS schema string; `parent_ref` uses native `refUID`; revocation uses native EAS revocation.
- **Borsh/Anchor (mainnet-conditional):** the same field order serializes as a `#[repr]` leaf struct in a concurrent Merkle tree.
- A **round-trip equivalence test MUST** prove that encode→decode across both representations is lossless and field-order-stable. CI **MUST** fail on drift between the deployed EAS schema and this document.

### Design constraints (normative)

- `phash` is **advisory**. A `phash_commit`/`lsh_bucket` match **MUST NOT** auto-mint a verdict, auto-mutate an existing attestation, or trigger a slash. It surfaces a *labeled prior claim* only.
- Person-linkable perceptual data **MUST NOT** be written to any immutable anchor (e.g. Bitcoin). Only `chash`/Merkle roots with no person-linkable perceptual data may be anchored (see [`ROADMAP.md`](../ROADMAP.md) §9.4, GDPR).

## Rationale

We commit the locality-preserving `lsh_bucket` (not a cryptographic hash-of-phash) because a crypto hash destroys the Hamming locality the bucketing needs; fine-grained near-dup search is therefore an off-chain, challengeable operation, and the chain stores only the commitment + chosen linkage.

## Backwards compatibility

`schema_version` gates all future changes. Adding fields requires a major-version bump and a new EAS schema registration; old attestations remain valid under their version.

## Security considerations

See [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md): phash-collision (defamation injection), replay/duplication (bound via `{chash, detector_version, timestamp, nonce}`), and correlated detector failure (mitigated partly by mandatory `detector_version`).

## Copyright

CC-BY-4.0.
