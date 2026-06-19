# `oracle-node/` — Detection oracle

> **License:** AGPL-3.0-or-later · **Status:** PLANNED · **Stack:** Python

A stake-aware node that produces signed provenance attestations. It pulls a job, runs a **pluggable `DetectorProvider` chain**, runs C2PA verification, normalizes the result into the [canonical attestation object](../specs/JIP-1-attestation-schema.md), signs it (single ECDSA key at MVP), and hands it to the submission path.

**The oracle runs detection off-chain. The chain never does.** Detection correctness is enforced *after the fact* by the on-chain economic-liability layer, not verified on-chain.

## `DetectorProvider` chain (REAL vs STUBBED at MVP)

| Provider | Status | Notes |
|---|---|---|
| `SynthIDTextProvider` | **REAL** | Wraps the open-source [`synthid-text`](https://github.com/google-deepmind/synthid-text) detector — the one license-free SynthID detector that exists. Text only. |
| `C2PAVerifyProvider` | **REAL** | Verifies Content Credentials manifests against the C2PA Trust List (`c2pa-python` / `c2pa-rs`). |
| `LabeledCorpusProvider` | **STUB (honest)** | Deterministic detector over a **real labeled corpus** we control (known-AI from Imagen/Gemini + known-real public sets). Default for image. Emits real verdicts on known data — never fabricated confidence. |
| `GoogleContentDetectionProvider` | **CODE-COMPLETE, FLAG-GATED** | Adapter for Google's AI Content Detection API. Drops in zero-refactor **if and only if** partner access **and** ToS clearance land (see kill-gate #1 in [`ROADMAP.md`](../ROADMAP.md) §13). Off by default. |

## Multi-signal & graceful degradation (normative — [JIP-4](../specs/JIP-4-trust-model.md))

The provider chain is deliberately **detector-agnostic**. Launch-blocking, *slashable* signals **MUST** be ToS-clean and freely re-runnable (so a "reproducible detector-output mismatch" is a fault a challenger can actually prove): C2PA verification, open SynthID-Text, the owned classifier. `GoogleContentDetectionProvider` and any other vendor API are **pluggable, off by default, and never on the launch critical path** — their outputs are explicitly **non-slashable, attributed advisory** records (a third party re-running a vendor API to police a claim could itself breach that vendor's terms).

**Graceful-degradation invariant:** the full happy-path (fingerprint → attest → record → read → challenge) **MUST** run with the vendor-API class disabled. CI **MUST** include a "vendor-disabled" end-to-end run; a build that breaks when the vendor class is off **MUST** fail. A hostile ToS change or outage then degrades one class's coverage — it never halts the protocol.

## Honesty guarantees

Every stub/mock attestation carries an unforgeable `provenance=mock` field, is signed with a **non-staked test key**, and is **excluded from every reward/slash path**. The product surface renders `provenance=mock` distinctly so a stub can never be mistaken for a real verdict.

## Liability scope (important)

Economic liability covers **detectable-disagreement faults only** — a C2PA manifest mismatch or a reproducible detector-output mismatch. It does **not** cover the underlying "is this AI?" truth, which depends on Google's secret keys and is not on-chain-verifiable. A unanimous-wrong federation is unslashable; see [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md) (correlated detector failure).

## Key custody

Software keys are acceptable on testnet. **HSM/KMS custody is mandatory before mainnet** with mandated rotation.
