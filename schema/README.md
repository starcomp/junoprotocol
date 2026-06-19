# `@juno-protocol/schema` — canonical attestation schema (JIP-1)

> **License:** Apache-2.0 · **Status:** working artifact (W0). This is **the foundation everything keys off** — the single source of truth for how a Juno attestation is encoded on every chain.

[`src/canonical.js`](src/canonical.js) defines the canonical field layout **once** (the `FIELDS` array). The EAS schema string, the Solidity decode tuple, the Rust/Borsh struct, and both codecs are all *derived from it in the same order*, so the two on-chain representations can never silently drift. This is the executable form of [`specs/JIP-1-attestation-schema.md`](../specs/JIP-1-attestation-schema.md).

## The EAS schema string

This is what you register with the EAS `SchemaRegistry` on Base Sepolia:

```
uint8 schemaVersion,bytes32 chash,bytes32 phashCommit,bytes lshBucket,uint8 verdict,uint16 confidence,uint16 modelLineage,uint16 detectorVersion,bytes32 c2paManifestHash,bytes32 segmentMapHash,uint32 attesterSetId,bytes sigRef,uint64 timestamp,uint8 provenance
```

Run `npm run print-schema` to emit this plus the Solidity decode tuple, the Solidity `CanonicalAttestation` memory struct, and the Rust/Borsh struct — copy those **verbatim** into the resolver and the (mainnet-conditional) Solana program so they stay in lockstep.

## Two JIP-1 fields are intentionally NOT in the encoded data

| JIP-1 field | Why it's not in the schema data | Where it lives instead |
|---|---|---|
| `parent_ref` | It's attestation *metadata*, not payload. | EAS's **native `refUID`** field on the `Attestation` struct (a Solana **leaf pointer** at mainnet). |
| (`time`) | EAS already stamps attestation time. | Our `timestamp` field is the **detection** time (may differ), so it *is* kept in the data. |

## The `sigRef` signing rule (important)

You cannot sign bytes that contain the signature. So detectors sign
`keccak256(contentEncode(attestation))` — the ABI encoding of **every canonical field except `sigRef`** — and the on-chain resolver recomputes that exact hash and verifies the k-of-n ECDSA signatures packed into `sigRef`. See `contentEncode()` in [`src/eas.js`](src/eas.js) and `JunoAttestationModule._contentHash` in [`contracts/`](../contracts/).

## Run the test

```sh
cd schema
node test/roundtrip.test.js        # dependency-free; runs on Node >= 12
# or, with the optional faithfulness cross-check:
npm install                        # installs ethers@5 (optional devDependency)
npm test
```

The [round-trip equivalence test](test/roundtrip.test.js) proves:

1. EAS (ABI) encode → decode is lossless.
2. Borsh encode → decode is lossless.
3. EAS and Borsh enumerate identical fields in identical order (no cross-chain drift).
4. Cross-representation: the object recovered from EAS equals the one recovered from Borsh equals the original.
5. Edge cases: empty dynamic bytes, max-width uints.
6. `contentEncode` excludes `sigRef` and depends on the real fields.
7. **Faithfulness (optional):** the hand-written ABI coder matches `ethers`' `defaultAbiCoder` **byte-for-byte** — i.e. our encoding is exactly what EAS stores and the Solidity resolver `abi.decode`s.

The coder is dependency-free so it runs in any environment (including very old Node); `ethers` is an *optional* devDependency used solely for check #7. CI runs the full suite (including #7) on a modern Node.

## CI guard

`specs/JIP-1` declares that CI **must** fail on drift between the deployed EAS schema and the canonical layout. The intended check: register/read the on-chain schema string and assert it equals `EAS_SCHEMA_STRING` from [`src/canonical.js`](src/canonical.js), and run this round-trip suite on every PR touching `schema/`, `contracts/`, or `specs/JIP-1`.
