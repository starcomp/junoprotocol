# Juno Protocol — Architecture

> **Status:** Draft. The authoritative source for what we build and in what order is [`ROADMAP.md`](../ROADMAP.md).

## The one principle everything follows from

**SynthID detection cannot be verified on-chain.** The Bayesian detector needs Google's secret keys. So the chain **never runs detection.** It does the four things a single company's database structurally cannot:

1. **Neutral registry** — a multi-writer record no single AI firm owns or can censor.
2. **Persistent memory** — keyed by perceptual hash, it remembers a verdict even after a watermark/credential is stripped.
3. **Economic liability** — attesters stake and are slashable for *provable, detectable* wrong attestations.
4. **Bootstrap** — emissions can subsidize coverage of the long tail before fees exist.

Detection correctness is enforced **after the fact** by the economic-liability layer — not verified on-chain.

## System diagram (logical)

```
  ┌─────────────┐     media      ┌────────────────────┐
  │  Submitter / │ ─────────────▶ │  Fingerprinting     │  chash (SHA-256, exact)
  │  Extension   │   (client-side │  service            │  phash (perceptual, near-dup)
  └─────────────┘    WASM hash)   └─────────┬──────────┘
                                            │ fingerprint
                                            ▼
                                  ┌────────────────────┐  runs SynthID (off-chain) +
                                  │  Detection Oracle   │  C2PA verify; signs the
                                  │  (staked)           │  canonical attestation
                                  └─────────┬──────────┘
                                            │ signed attestation (k-of-n ECDSA)
                                            ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  ON-CHAIN  (Base Sepolia + EAS at testnet)                            │
  │  ┌──────────────────┐  ┌──────────┐  ┌──────────────────┐  ┌────────┐ │
  │  │ JunoAttestation  │  │ Staking  │  │ OptimisticChallenge│ │Treasury│ │
  │  │ Module (resolver)│  │ /Slashing│  │  (+ DVM hook)     │  │/Query  │ │
  │  └──────────────────┘  └──────────┘  └──────────────────┘  └────────┘ │
  │   chash uniqueness · staked-writer gating · refUID near-dup linkage    │
  └─────────────────────────────────┬────────────────────────────────────┘
                                     │ events
                                     ▼
                          ┌────────────────────┐   FREE /lookup  ┌─────────────┐
                          │  Indexer (Postgres │ ───────────────▶│ Integrator  │
                          │  + pgvector ANN)   │  verdict/conf/   │ (badge UI)  │
                          └────────────────────┘  lineage/status  └─────────────┘
```

## On-chain layer

Built **around EAS**, not replacing it. EAS provides the schema registry, attestation storage, revocation, and `refUID` linkage; Juno adds the economic contracts (`StakingManager`, `Slashing`, `OptimisticChallenge`, `QueryPayment`, `Treasury`) and a `SchemaResolver` (`JunoAttestationModule`) that enforces dedup, staked-writer gating, and k-of-n ECDSA signatures. See [`contracts/README.md`](../contracts/README.md) and [`specs/JIP-1-attestation-schema.md`](../specs/JIP-1-attestation-schema.md).

## Off-chain layer

All the real work is off-chain: detection (oracle), fingerprinting + ANN, and the indexer/read API. **What is REAL vs STUBBED at MVP is marked in the product** (`provenance=mock`) so a stub is never mistaken for a real verdict. See [`oracle-node/`](../oracle-node/README.md), [`fingerprinting/`](../fingerprinting/README.md), [`indexer/`](../indexer/README.md).

## Trust model

- **Testnet:** a single permissioned ECDSA attester behind an on-chain allowlist (architected for a set, shipped as n=1). No BLS, no rival-firm federation.
- **Mainnet-conditional:** BLS threshold signatures and a real m-of-n federation — gated on **≥ 2 genuinely independent licensed detectors existing**, plus their legal sign-off. Until then, "m-of-n" would be *n copies of one Google API* (the correlated-failure risk).
- **Liability is scoped** to detectable-disagreement faults (C2PA mismatch, reproducible detector-output mismatch), **not** the underlying "is this AI?" truth, which is not on-chain-verifiable.

## Why a blockchain at all

The indexer is fully **rebuildable from chain events** — it's a cache. The thing that *isn't* reconstructable from any one company's database is the neutral, multi-writer, economically-liable, persistent record itself. That is the justification. Two of the four properties (neutral registry, economic liability) are genuinely chain-justified; two (persistence via off-chain ANN with on-chain commitments; token bootstrap) are conditional and the project is willing to ship a stablecoin-collateral / consortium version if they don't hold. See [`ROADMAP.md`](../ROADMAP.md) §1.1.
