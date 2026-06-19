# Juno Protocol Governance

> **Status:** pre-alpha. The structures below describe the *intended* model and its staged rollout. Today the project is at **Stage 0** (founder / core-team stewardship). Nothing here is legally operative yet.

Juno deliberately separates **two kinds of authority** that most crypto projects conflate. This mirrors the protocol's own core insight: just as detection cannot be trustlessly verified on-chain, code-review judgment cannot be exercised by a token vote. The two tracks never exercise each other's powers.

| Track | Owns | Held by |
|---|---|---|
| **Code / technical track** | Git merge rights, release signing, interface & schema JIPs, reference implementations | Maintainers → Technical Steering Committee (TSC) |
| **Economic / protocol track** | On-chain parameters (fees, emissions, slashing %, challenge window), treasury, grants, federation membership | Multisig council → DAO (Snapshot signaling → on-chain Governor) |

**Changes that touch both — e.g. tokenomics or slashing — require BOTH a merged JIP AND an on-chain vote.** Neither track can route around the other.

## Maintainer model (staged)

- **Stage 0 — BDFL / founder.** Founder holds merge rights and all keys. (Current stage.)
- **Stage 1 — Core team.** 3–5 maintainers with merge rights across defined `CODEOWNERS` areas. Two-approval rule for `contracts/` and `specs/`.
- **Stage 2+ — Technical Steering Committee (TSC).** An elected committee owns the technical roadmap, release process, and interface/schema JIP ratification by rough consensus. TSC seats and term limits are defined by a Meta JIP.

The maintainer model decentralizes on the same criteria-gated cadence as the protocol (see [`ROADMAP.md`](ROADMAP.md) §6, §8). The TSC is **not** the DAO and cannot move treasury, change economic parameters, or admit/remove detectors.

## Relationship to the Foundation and the DAO

Three bodies, formed only when triggered (see [`ROADMAP.md`](ROADMAP.md) §9):

- **Juno Labs Inc.** (DevCo) — employs core contributors; the only entity that exists at MVP.
- **Juno Foundation** (Cayman foundation company) — stewards treasury, trademark, and grants; formed at token launch.
- **Juno DAO** (Wyoming DUNA wrapper) — gives on-chain governance legal personality; formed at 100+ members.

The **TSC governs the codebase**; the **DAO governs the deployed protocol**; the **Foundation stewards neutral assets** (trademark, treasury, the federation allowlist). Federation membership is held by the neutral Foundation/independent body precisely so that no competitor controls who may attest — this is the antitrust posture, not a nicety.

## The JIP (Juno Improvement Proposal) process

Protocol-level changes are proposed and ratified as JIPs. The process, categories, and lifecycle live in [`specs/jip-process.md`](specs/jip-process.md); the template is [`specs/jip-template.md`](specs/jip-template.md).

Lifecycle: `Draft → Review → Last Call → Final` (or `Stagnant` / `Withdrawn`).

Categories:
- **Core** — schema, trust model, on-chain semantics.
- **Interface** — SDK, REST/GraphQL, extension contracts.
- **Economic** — token, emissions, fees, slashing. *Activation requires an on-chain vote.*
- **Meta** — process and governance itself.

Specs currently live in this repo under [`specs/`](specs/) and will migrate to a dedicated `juno-protocol/jips` repository (mirroring how EIPs live apart from go-ethereum) so the standard versions independently of the implementation.

## Decision-making

- Routine code changes: maintainer review + CI green + DCO sign-off.
- Interface/schema changes: an Interface/Core JIP at `Review` + TSC rough consensus.
- Economic changes: an Economic JIP **and** an on-chain vote (once governance is live; council-executed before then).
- Emergency safety actions (pause, detector de-listing): the Security Council, within published, time-bound, sunset-reviewed powers.

## Anti-plutocracy

On-chain governance uses checkpointed `ERC20Votes` snapshots, per-tx treasury caps, capped per-holder voting weight, mandatory timelocks, and a non-transferable, slashable **oracle-reputation** signal that gates oracle-policy votes independently of token wealth. Quadratic/conviction voting is used **only** for off-chain Snapshot signaling and grants, never for binding on-chain power. See [`ROADMAP.md`](ROADMAP.md) §8.3.
