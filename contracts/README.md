# `contracts/` — On-chain economic-liability layer

> **License:** Apache-2.0 · **Status:** SKELETON (W0) — `JunoAttestationModule` + `StakingManager` implemented; the rest PLANNED. **Authored without a local Foundry toolchain; not yet compiled here — CI compiles via `forge build`/`forge test`.** · **Stack:** Solidity ^0.8.19, Foundry, EAS

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

## Current skeletons (W0)

What actually exists in this repo today:

```
contracts/
├── foundry.toml, remappings.txt
├── src/
│   ├── interfaces/IEAS.sol            # vendored minimal EAS: Attestation struct + ISchemaResolver
│   ├── interfaces/IStakingManager.sol
│   ├── interfaces/IERC20.sol
│   ├── vendor/SchemaResolver.sol      # vendored minimal EAS resolver base (onlyEAS → onAttest/onRevoke)
│   ├── JunoAttestationModule.sol      # ✅ chash dedup + staked-writer gating IMPLEMENTED; k-of-n = STUB
│   └── StakingManager.sol             # ✅ stake/unbond/withdraw/slash IMPLEMENTED; rewards = TODO
└── test/
    ├── mocks/MockERC20.sol
    ├── JunoAttestationModule.t.sol    # unit: dedup, staked-writer gating, schema/provenance guards
    └── StakingManager.invariant.t.sol # invariants: totalStaked == Σ stake; manager solvency
```

**Implemented now:** the two MVP write-path invariants — `chash` exact dedup and staked-writer gating — plus full stake/unbond/withdraw/slash accounting.
**Explicit stubs (marked in-code):** `JunoAttestationModule._verifyKOfN` (shape-check only; real k-of-n ECDSA over the signed content hash is a TODO), the slash "burn" sink (routes to treasury, not a real burn), and `SafeERC20`/reward accounting.
**Vendored:** `IEAS.sol` + `SchemaResolver.sol` are minimal stand-ins so the skeleton compiles self-contained — production MUST swap in the audited `@ethereum-attestation-service/eas-contracts`.

The canonical attestation layout the resolver decodes is defined and **test-verified** in [`schema/`](../schema/) (the EAS schema string ⇄ Borsh round-trip). The `abi.decode` type list in `JunoAttestationModule` MUST match `schema/`'s `EAS_SCHEMA_STRING`.

## Build & test

```sh
cd contracts
forge install foundry-rs/forge-std   # one-time: populates lib/
forge build
forge test                            # unit + invariant
forge test --profile ci               # more fuzz/invariant runs
```

## Deferred (mainnet-conditional, NOT in MVP)

`ThresholdSigVerifier` (BLS via BN254 precompile), Solana compressed registry, Bitcoin anchoring, OpenZeppelin `Governor` + `Timelock` with binding votes, hardened upgrade proxy.

## Testing & security gates

- Foundry unit + **invariant** tests (stake conservation; no-slash-without-resolved-challenge; honest oracle never slashed by a frivolous challenge; `challenger reward ≤ slashed amount`).
- Echidna property fuzzing of bond/slash arithmetic; a Certora spec for slashing conservation.
- Slither + semgrep + gas-diff gating on every PR.
- A **scoped external audit** of these contracts is a hard launch gate (see [`SECURITY.md`](../SECURITY.md)).
