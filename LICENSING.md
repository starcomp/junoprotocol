# Licensing Policy

Juno Protocol is multi-licensed **per component**. This is deliberate: each layer of the
stack plays a different role in the ecosystem, and the right license for an integrator-facing
SDK is not the right license for a network service. This document is the authoritative policy.

> [!NOTE]
> Per-component license terms also appear in each top-level directory's `README.md` and, once
> implementation begins, as [SPDX](https://spdx.dev/) headers (`SPDX-License-Identifier: ...`)
> in source files.

## Summary table

| Component(s) | License | SPDX identifier |
|---|---|---|
| `contracts/` — Solidity contracts, ABIs, schema definitions | **Apache-2.0** | `Apache-2.0` |
| `sdk/` — TypeScript + Python client SDKs | **Apache-2.0** | `Apache-2.0` |
| `extension/` — reference browser extension / widget | **Apache-2.0** | `Apache-2.0` |
| `oracle-node/` — detection oracle service | **AGPL-3.0-or-later** | `AGPL-3.0-or-later` |
| `fingerprinting/` — fingerprinting + ANN index service | **AGPL-3.0-or-later** | `AGPL-3.0-or-later` |
| `indexer/` — event indexer + read API service | **AGPL-3.0-or-later** | `AGPL-3.0-or-later` |
| `specs/` — protocol specs, JIP text | **CC-BY-4.0** | `CC-BY-4.0` |
| `docs/` — architecture, threat model, FAQ | **CC-BY-4.0** | `CC-BY-4.0` |
| Tiny inline examples / snippets | MIT acceptable | `MIT` |

The repository **root default** is [Apache-2.0](LICENSE). Where a directory's `README.md`
or a file's SPDX header names a different license, that more-specific declaration governs
that component.

## Rationale

### Apache-2.0 for contracts, SDK, and integrator-facing code

We chose **Apache-2.0 over MIT** specifically for its **explicit patent grant and patent-retaliation
clause**. Content watermarking and provenance is a **patent-dense space** — Google (SynthID), Adobe,
and the C2PA ecosystem all hold or may hold patents touching watermark and detection plumbing.
Integrators (browsers, platforms, marketplaces) embedding the Juno SDK and reading the contracts
need explicit legal cover to do so. MIT gives them no patent grant; Apache-2.0 does. This materially
reduces submarine-patent risk in a multi-rival environment.

### AGPL-3.0-or-later for the network services

The `oracle-node`, `fingerprinting`, and `indexer` services are the **moat-sensitive infrastructure**
of the network. AGPL-3.0 closes the "SaaS loophole" that plain GPL-3.0 leaves open: a well-capitalized
actor cannot run a **closed, hosted fork** of Juno's core services without contributing their
modifications back.

AGPL **does not** restrict simply *running a node* to serve the public network — that is the desired
behavior and is how operators earn participation rewards. It only constrains running a **closed hosted
fork**. If a genuine commercial-operator need for a non-AGPL build emerges, the stewarding Foundation
may offer a dual-licensing path at a later phase rather than weakening the license preemptively.

### CC-BY-4.0 for specs and docs

The protocol specifications — above all the **canonical attestation schema** ([JIP-1](specs/JIP-1-attestation-schema.md)) —
are meant to be a **neutral standard that anyone can implement**, including Google, OpenAI, Meta, and
independent detector vendors. **CC-BY-4.0** maximizes reuse of the standard and the documentation while
requiring only attribution. A standard that others must adopt should not be encumbered by a code license.

## Contribution mechanism — DCO, not (yet) a CLA

Contributions are accepted under the **Developer Certificate of Origin (DCO)**, **not** a heavyweight
Contributor License Agreement (CLA).

- Every commit must be **signed off** with a `Signed-off-by:` trailer (use `git commit -s`), certifying
  that you have the right to submit the work under the project's license. See [CONTRIBUTING.md](CONTRIBUTING.md)
  for the exact mechanics and the full DCO text.
- Contributors **retain their copyright**; they license their contribution under the license of the
  component they are modifying.
- A CLA is intentionally deferred. There is **no Foundation entity yet** to assign copyright/patent to.
  A CLA assigning rights to the Juno Foundation may be introduced once that entity legally exists
  (the design corpus places this at the token-launch phase); until then, DCO is the lightweight,
  community-friendly mechanism and avoids the "who do contributors even sign a CLA with?" problem.

## SPDX headers

Once implementation begins, every source file should carry an SPDX header matching its component's
license, for example:

```solidity
// SPDX-License-Identifier: Apache-2.0
```

```python
# SPDX-License-Identifier: AGPL-3.0-or-later
```

This makes the per-file license machine-readable and unambiguous even when files are vendored
or copied out of the monorepo.

## Trademarks

Open-source licenses grant rights to **code**, not to **trademarks**. The "Juno" / "Juno Protocol"
name and any associated marks are governed separately. Third-party names ("SynthID", "C2PA",
"Content Credentials") are used nominatively and remain the property of their respective owners;
see the disclaimer in [README.md](README.md).
