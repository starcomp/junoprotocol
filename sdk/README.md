# `sdk/` — Client SDKs (TypeScript + Python)

> **License:** Apache-2.0 (patent grant for integrators) · **Status:** PLANNED · **Packages:** `@juno-protocol/sdk` (npm), `juno-protocol` (PyPI)

The integration surface for submitters and integrators. Apache-2.0 specifically so browsers and platforms have the patent cover they need to embed it.

## Core API (planned)

```ts
import { Juno } from "@juno-protocol/sdk";

const juno = new Juno({ network: "base-sepolia" });

// Integrator: free lookup. Hashes media CLIENT-SIDE (WASM) — raw media never leaves the device.
const result = await juno.lookup(fileOrBuffer);
//   → { verdict, confidence, modelLineage, attestationUid, challengeStatus, provenance }

// Submitter: register provenance for content you generated.
await juno.submitProvenance({ media, c2paManifest });

// Watch challenge outcomes for an attestation.
juno.subscribeChallenges(attestationUid, (event) => { /* ... */ });
```

## Design commitments

- **Client-side hashing.** The SDK bundles a WASM perceptual-hasher so integrators send only fingerprints, never raw media — a privacy and GDPR control (see [`ROADMAP.md`](../ROADMAP.md) §9.4).
- **No bare "AI" assertion.** `verdict` is probabilistic (`not` / `watermarked` / `uncertain`) with a `confidence`; the SDK surfaces methodology and never returns a bare factual "this is AI" string. A `phash`-derived result is flagged as a **prior claim**, not a fresh detection.
- **Stable, chain-portable types** generated from the canonical schema ([`specs/JIP-1-attestation-schema.md`](../specs/JIP-1-attestation-schema.md)), so integrators don't re-integrate if the protocol migrates chains.
