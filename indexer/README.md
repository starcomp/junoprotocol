# `indexer/` — Event indexer & read API

> **License:** AGPL-3.0-or-later · **Status:** PLANNED · **Stack:** TypeScript/Node, Postgres 16 + pgvector

Ingests EAS attestation events into Postgres + pgvector and serves the **free read path**. This is the surface integrators query to show a "real vs AI" label.

## Why AGPL

The indexer is moat-sensitive infrastructure. AGPL prevents a well-capitalized actor from running a **closed hosted clone** without upstreaming, while still permitting anyone to run a node for the public network.

## APIs

- **REST hot path:** `POST /lookup { chash, phash } → { verdict, confidence, model_lineage, attestation_uid, challenge_status, provenance }`. chash served from edge cache.
- **GraphQL:** rich queries over attestations, challenges, attesters, and near-dup links.

**Reads are free.** Only *fresh detection* (handled by the oracle + `QueryPayment`) is paid, and in stablecoin.

## Rebuildability is the point

The index is derived state — fully reconstructable from on-chain EAS events. This is a direct answer to "why a blockchain?": the neutral, multi-writer, economically-liable record lives on-chain; the indexer is just a queryable cache anyone can rebuild and verify. See [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

## Performance targets (MVP)

- `/lookup` p95 < 100 ms on cached `chash`.
- ANN `phash` lookup p95 < 300 ms at ≥ 1M indexed fingerprints.
