# JIP-0: The Juno Improvement Proposal Process

> **Status:** Living · **License:** CC-BY-4.0

A JIP (Juno Improvement Proposal) is the unit of protocol change. The process is modeled on EIPs and Rust RFCs. It exists so that protocol changes are proposed in the open, reviewed on their technical merits, and — for changes that bind the deployed protocol — ratified through the right authority.

## Categories

| Category | Scope | Ratified by |
|---|---|---|
| **Core** | Attestation schema, trust model, on-chain semantics | TSC rough consensus (+ on-chain vote if it changes economics) |
| **Interface** | SDK, REST/GraphQL, extension contracts | TSC rough consensus |
| **Economic** | Token, emissions, fees, slashing %, challenge window | **Merged JIP AND an on-chain vote** |
| **Meta** | Process, governance, the JIP process itself | TSC + community |

This mirrors the project's two-track authority split (see [`GOVERNANCE.md`](../GOVERNANCE.md)): the **TSC owns interfaces and schemas**; the **DAO owns economic parameters**. Neither can route around the other; an Economic JIP needs both.

## Lifecycle

```
  Idea ──▶ Draft ──▶ Review ──▶ Last Call ──▶ Final
                       │            │
                       ├──▶ Stagnant (inactive ≥ 6 months)
                       └──▶ Withdrawn (by author)
```

- **Draft** — opened as a PR adding `JIP-N-*.md` using the [template](jip-template.md). A JIP editor assigns the number.
- **Review** — actively discussed; the spec is sufficiently complete to evaluate. Requires a *Security Considerations* section.
- **Last Call** — final review window (≥ 2 weeks) before acceptance; surfaced widely.
- **Final** — accepted and normative. Economic JIPs are only `Final` after the on-chain vote activates them.
- **Stagnant / Withdrawn** — inactive or pulled by the author. Can be revived.

## Requirements for a Core/Economic JIP

- A complete, unambiguous specification (RFC 2119 keywords).
- **Security Considerations** mapped to [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md).
- **Backwards-compatibility** analysis (the canonical schema is `schema_version`-tagged for forward-compat).
- For schema changes: an updated Borsh⇄EAS round-trip equivalence test. **CI fails on drift** between the deployed EAS schema and the canonical JIP.

## Roles

- **Author** — writes and champions the JIP.
- **JIP editors** — assign numbers, enforce formatting and process (not merit).
- **TSC** — ratifies Core/Interface JIPs by rough consensus.
- **DAO** — activates Economic JIPs by on-chain vote.
