# `contracts/` — On-chain economic-liability layer

> **License:** Apache-2.0 · **Status:** PLANNED (no contracts implemented yet) · **Stack:** Solidity, Foundry, OpenZeppelin, EAS

The chain **never runs detection.** These contracts store signed verdicts, make attesters financially liable, and meter paid fresh-detection. They are built **around** the [Ethereum Attestation Service (EAS)](https://attest.org), not as a from-scratch registry — EAS gives us the schema registry, attestation storage, revocation, and referenced attestations (`refUID`) for free.

## Testnet target

**Base Sepolia + EAS.** A single permissioned ECDSA attester behind an on-chain allowlist (no BLS, no rival-firm federation in the MVP — see [`ROADMAP.md`](../ROADMAP.md) §2).

## Minimal MVP contract set

| Contract | Role |
|---|---|
| **Canonical Attestation Schema** | The single chain-portable field layout, registered as an EAS schema string. See [`specs/JIP-1-attestation-schema.md`](../specs/JIP-1-attestation-schema.md). |
| **JunoAttestationModule** (EAS `SchemaResolver`) | Write path: enforces `chash` uniqueness (exact dedup), validates **k-of-n ECDSA** signatures from the staked detector allowlist, records the LSH bucket + parent `refUID` for near-dup linkage, reverts invalid writes. |
| **StakingManager** | Oracles/challengers lock `$JUNO` collateral; tracks active stake, unbonding delay, gates writes, pull-based reward accounting. |
| **Slashing** | Privileged; callable **only** by `OptimisticChallenge` on a resolved dispute. Burns/redistributes slashed stake (challenger bounty + treasury remainder). |
| **OptimisticChallenge** (+ DVM hook) | Per-attestation challenge window, bond escrow, dispute state machine (`Proposed → Challenged → Resolved`), escalation to a DVM (testnet = Safe multisig). |
| **QueryPayment** | Meters **fresh-detection** payments (**reads are free**); routes fees to the reward pool + burn slice. The 60/30/10 split. |
| **Treasury** | Collects slash remainders + fee retention; funds emissions. Testnet = Safe vault. |
| **JunoToken (tJUNO)** | Testnet faucet ERC-20, zero monetary value. |

## Deferred (mainnet-conditional, NOT in MVP)

`ThresholdSigVerifier` (BLS via BN254 precompile), Solana compressed registry, Bitcoin anchoring, OpenZeppelin `Governor` + `Timelock` with binding votes, hardened upgrade proxy.

## Testing & security gates

- Foundry unit + **invariant** tests (stake conservation; no-slash-without-resolved-challenge; honest oracle never slashed by a frivolous challenge; `challenger reward ≤ slashed amount`).
- Echidna property fuzzing of bond/slash arithmetic; a Certora spec for slashing conservation.
- Slither + semgrep + gas-diff gating on every PR.
- A **scoped external audit** of these contracts is a hard launch gate (see [`SECURITY.md`](../SECURITY.md)).
