# Juno Protocol Specifications

> **License:** CC-BY-4.0 · **Status:** Draft

This directory holds the normative protocol specifications and the **Juno Improvement Proposal (JIP)** process. Specs are licensed CC-BY-4.0 so the standard is freely implementable by anyone — including Google, OpenAI, Meta, and other vendors.

> **Migration note:** specs currently live in-repo for convenience during bootstrap. They will move to a dedicated **`juno-protocol/jips`** repository so the standard versions independently of the implementation (mirroring how EIPs live apart from go-ethereum). JIP numbers are stable across that move.

## Index

| Spec | Title | Status |
|---|---|---|
| [`jip-process.md`](jip-process.md) | The JIP process and lifecycle | Living |
| [`jip-template.md`](jip-template.md) | Authoring template | Living |
| [`JIP-1-attestation-schema.md`](JIP-1-attestation-schema.md) | Canonical chain-portable attestation object | Draft |
| [`JIP-2-fingerprint.md`](JIP-2-fingerprint.md) | Dual-fingerprint (`chash` + `phash`) specification | Draft |
| [`JIP-3-audio-video-fingerprint.md`](JIP-3-audio-video-fingerprint.md) | Audio & video fingerprinting + temporal segment maps | Draft |

> **Reference implementation:** [`JIP-1`](JIP-1-attestation-schema.md) is realized as an executable, test-verified artifact in [`schema/`](../schema/) — the canonical EAS schema string and a Borsh⇄EAS round-trip equivalence test.

## Conventions

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174).
- A change to any **Core** spec (the schema, the trust model, on-chain semantics) requires a JIP at `Review` and, where it touches economics, an on-chain vote to activate (see [`GOVERNANCE.md`](../GOVERNANCE.md)).
