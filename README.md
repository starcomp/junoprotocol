# Juno Protocol

**A neutral, cross-vendor, economically-liable registry of record for AI-content provenance — so people can tell real media from AI-generated media.**

> [!WARNING]
> **STATUS: pre-alpha / pre-testnet.** Nothing here is audited. There is **no token**. There is no live network. **Do not use any of this in production.** Schemas, interfaces, economics, and chain decisions are all subject to change. This repository is a design-stage skeleton published for transparency and to invite review.

---

## What Juno is (and is not)

Juno is **not an "AI detector."** Platforms that own the watermarking keys — Google (SynthID), and increasingly Meta, OpenAI, and others — are shipping native "is this AI?" detection into Search, browsers, and their own products for free. Trying to out-detect them is a losing position.

Juno owns the one durable niche those vendors will *structurally never* build: a **neutral, cross-vendor, economically-liable registry of record with persistent memory.** It records signed provenance attestations keyed by content fingerprint, makes the parties who produce those attestations *financially liable* for being wrong, and *remembers* that a piece of media was attested as AI-generated **even after the watermark or C2PA credential is stripped**.

- **Reads are free.** Looking up "has this fingerprint been attested?" costs nothing.
- **Only fresh detection is paid** (in stablecoin), by liability-bearing buyers who need a neutral record they can cite — marketplaces, ad-verification firms, insurers, election-integrity programs.

Juno consumes **Google SynthID** and **C2PA Content Credentials** as detector inputs at the oracle edge. It does **not** run detection on-chain and does **not** reimplement anyone's watermark.

## The four-property thesis

A blockchain is only justified here by four properties. Juno is honest that two are strong and two are conditional:

1. **Neutral registry** *(strong)* — a multi-writer record of provenance attestations that no single AI firm owns or can censor. No competitor will host a registry for its rivals; a neutral protocol can.
2. **Persistent perceptual memory** *(conditional)* — once any fingerprint is attested as AI-generated, the registry surfaces that **prior attestation** for incidentally-degraded near-duplicates (recompression, crop, resize), so the record survives credential stripping. This is surfaced as a **labeled prior claim — "previously attested AI, not re-verified"** — never as a fresh re-detection, and never auto-applied to a verdict. It is *not* robust against motivated laundering (regeneration / img2img / restyle); see [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).
3. **Economic liability** *(strong, but scoped)* — attesters and challengers post stake; provably-wrong attestations are slashable via an optimistic challenge market. Liability covers **detectable-disagreement faults** (C2PA manifest mismatch, reproducible detector output), **not** the underlying "is this AI?" truth, which is not on-chain-verifiable.
4. **Bootstrap incentives** *(conditional)* — emissions can subsidize coverage of the long tail before fee revenue exists. A native token is justified *only* by this and a burn-backed staking asset; if that fails to validate, the design is willing to fall back to a stablecoin-fee + bonded-collateral model with no native token.

## Repository map

| Directory | Purpose | License |
|---|---|---|
| [`schema/`](schema/) | **Canonical attestation schema (JIP-1)** — single source of truth, with EAS + Borsh codecs and a test-verified round-trip equivalence. The foundation everything keys off. | Apache-2.0 |
| [`contracts/`](contracts/) | Solidity + Foundry. EAS-based attestation registry wrappers + the economic-liability stack (staking, slashing, optimistic challenge, query payment, treasury, governance). | Apache-2.0 |
| [`oracle-node/`](oracle-node/) | Detection oracle. Wraps the Google AI Content Detection API (SynthID) + C2PA verification, normalizes results, and signs attestations. | AGPL-3.0-or-later |
| [`fingerprinting/`](fingerprinting/) | Content fingerprinting: `chash` (SHA-256) + per-modality perceptual/neural hashing + an approximate-nearest-neighbor (ANN) index service. | AGPL-3.0-or-later |
| [`indexer/`](indexer/) | Event indexer + read API (GraphQL/REST). **Reads are free.** | AGPL-3.0-or-later |
| [`sdk/`](sdk/) | TypeScript + Python client SDKs for submitters and integrators. | Apache-2.0 |
| [`extension/`](extension/) | Reference "Is this AI?" browser extension / widget. | Apache-2.0 |
| [`specs/`](specs/) | Protocol specifications and the Juno Improvement Proposal (JIP) process, including the canonical attestation schema. | CC-BY-4.0 |
| [`docs/`](docs/) | Architecture, threat model, and FAQ. | CC-BY-4.0 |
| [`site/`](site/) | Self-contained static landing page for GitHub Pages (no build step, no dependencies). | CC-BY-4.0 / Apache-2.0 |

See [`LICENSING.md`](LICENSING.md) for the full per-component licensing policy and rationale.

## How it works (short)

1. A **submitter** (or the reference extension) computes a content fingerprint: `chash` (SHA-256, exact identity) + a per-modality perceptual hash (`phash`, near-duplicate identity).
2. A staked **detection oracle** runs Google's SynthID detection and/or C2PA verification *off-chain*, normalizes the result into the [canonical attestation object](specs/JIP-1-attestation-schema.md), and signs it.
3. The attestation is written to the **registry** (Ethereum Attestation Service on an L2 for testnet). The chain enforces `chash` uniqueness, staked-writer gating, and links near-duplicates.
4. An **integrator** queries the **indexer** (free) by fingerprint and gets back the verdict, confidence, model lineage, and challenge status.
5. A **challenger** can dispute a wrong attestation within a challenge window; resolution slashes the loser's stake.

The chain stores verdicts and stake/slashing state. **The chain does not run SynthID.** Detection correctness is enforced *after the fact* by the economic-liability layer, not verified on-chain — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Quickstart

> [!NOTE]
> **PLANNED / STUB.** No runnable artifacts exist yet. When the testnet MVP lands, a one-command `docker-compose` devnet and a <15-minute integrator quickstart will live here. Until then, this section is a placeholder.

```sh
# PLANNED — not yet functional
git clone https://github.com/starcomp/junoprotocol
cd junoprotocol
# ... setup steps to come
```

## Committed chain decisions

- **Testnet:** Base Sepolia + the Ethereum Attestation Service (EAS) as the registry primitive. A single permissioned ECDSA attester (no BLS, no rival-firm federation in the MVP).
- **Mainnet:** default to staying on a default L2. A Solana + state-compression hot path is **conditional** — gated on a capacity/cost model that actually justifies it, not assumed.

See [`ROADMAP.md`](ROADMAP.md) for the full plan, timeline, kill-gates, and milestones.

## Governance & contributing

- [`ROADMAP.md`](ROADMAP.md) — the master roadmap (maintained separately).
- [`GOVERNANCE.md`](GOVERNANCE.md) — maintainer model, the Technical Steering Committee, its separation from on-chain DAO governance, and the JIP lifecycle.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to contribute, DCO sign-off, the JIP process, coding standards.
- [`SECURITY.md`](SECURITY.md) — responsible disclosure and security posture.
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) — Contributor Covenant v2.1.

## License summary

Juno is multi-licensed per component to fit each layer's role:

- **Apache-2.0** — contracts, SDK, and reference example code (explicit patent grant for integrators).
- **AGPL-3.0-or-later** — the network services (oracle-node, fingerprinting, indexer), so closed hosted forks must upstream.
- **CC-BY-4.0** — specifications and documentation, so the standard is freely implementable.

The repository root defaults to [Apache-2.0](LICENSE). Full policy: [`LICENSING.md`](LICENSING.md).

## Disclaimer — no affiliation with Google/Alphabet

Juno Protocol is **not affiliated with, sponsored by, or endorsed by Google LLC, Alphabet Inc., Adobe, the C2PA / Content Authenticity Initiative, or any other vendor.** "SynthID" is a Google product and "C2PA" / "Content Credentials" are projects of the Coalition for Content Provenance and Authenticity; these names are used here **nominatively**, solely to describe the third-party tools that Juno oracles run, and are the property of their respective owners. Juno uses these technologies **strictly per their own terms of service**, as a data source at the oracle edge. Juno uses no Google/SynthID or C2PA logos in its branding and makes no claim of partnership or endorsement.

Whether the Google AI Content Detection API's terms even *permit* on-chain re-attestation, paid relay, and federation is an **open, load-bearing diligence question** — see [`ROADMAP.md`](ROADMAP.md) and [`docs/FAQ.md`](docs/FAQ.md).
