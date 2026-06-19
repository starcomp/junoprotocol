# Security Policy

> [!WARNING]
> Juno Protocol is **pre-alpha and unaudited.** There is no mainnet deployment and no token of value. **Do not rely on any code here in production.**

## Reporting a vulnerability

Please report suspected vulnerabilities **privately**. Do **not** open a public issue for security problems.

- **Email:** `security@junoprotocol.org` (PGP key: *PLACEHOLDER — to be published before testnet*).
- Alternatively, use **GitHub Private Vulnerability Reporting** on this repository (Security → Report a vulnerability).

Please include: affected component and commit, a description, reproduction steps or a PoC, and impact assessment. We aim to acknowledge within **72 hours** and to agree on a disclosure timeline with you.

We support **coordinated disclosure**. Please give us a reasonable window to remediate before public disclosure. We will credit reporters who wish to be credited.

## Scope

In scope:
- `contracts/` — the economic-liability contracts (staking, slashing, optimistic challenge, query payment, treasury) and the EAS schema resolver.
- `oracle-node/`, `fingerprinting/`, `indexer/` — attestation production, fingerprinting, and the read path.
- `sdk/`, `extension/` — anything that could mislead an integrator or end user about a verdict.

Out of scope (for now): third-party dependencies' own vulnerabilities (report upstream), the Google AI Content Detection API itself, and theoretical attacks already documented as accepted/known boundaries in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) (e.g. watermark stripping at generation time, motivated regeneration-laundering of perceptual hashes).

## Security posture

The threat model centers on the **federation and the challenge market**, not cryptographic novelty: SynthID detection cannot be verified on-chain, so integrity reduces to keeping a small set of licensed detectors honest and punishing *detectable, provable* wrong attestations faster and cheaper than an attacker can profit.

The single biggest systemic risk is **correlated detector failure** — until a genuinely independent second licensed detector exists, "m-of-n" is *n copies of one Google API*, and a unanimous-wrong federation is unslashable. This is why real federation is gated on independent detectors existing and why economic liability is scoped to detectable-disagreement faults only. Full analysis: [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) and [`ROADMAP.md`](ROADMAP.md) §11.

## Audits & bounty

- **Pre-launch:** a scoped external audit of the economic contracts + EAS integration is a **hard launch gate** (Trail of Bits / OpenZeppelin / Spearbit / Zellic), with zero open high/critical at launch.
- **Invariant/formal testing:** Foundry invariant tests + Echidna fuzzing + a targeted Certora spec for the slashing-conservation invariant run in CI.
- **Incentivized attack-net:** a public points/testnet-token chaos program runs **≥4 weeks before mainnet**.
- **Bug bounty:** a funded **Immunefi** program with tiered payouts goes live at mainnet. (Testnet runs the attack-net instead.)

## Key custody

Oracle signing keys are held in HSM/KMS (AWS CloudHSM / GCP Cloud KMS / YubiHSM) before mainnet, with mandated rotation and a published per-oracle custody attestation. Dangerous protocol levers sit behind a guardian multisig pause + timelock.
