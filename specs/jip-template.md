---
jip: <assigned by editors>
title: <concise title>
author: <name / handle / email>
status: Draft
category: <Core | Interface | Economic | Meta>
created: <YYYY-MM-DD>
requires: <comma-separated JIP numbers, optional>
---

## Abstract

A short (≤ 200 word) description of the change.

## Motivation

Why is this needed? What problem does it solve? Which of Juno's four properties (neutral registry / persistent memory / economic liability / bootstrap) does it serve, and how?

## Specification

The normative spec. Use RFC 2119 keywords (**MUST**, **SHOULD**, **MAY**). Be precise and complete enough to implement from this section alone. For schema changes, give the exact field layout and the EAS-string ⇄ Borsh-struct mapping.

## Rationale

Why this design over the alternatives considered? What tradeoffs were made?

## Backwards compatibility

Does this break existing attestations, integrators, or the deployed schema? How is `schema_version` handled? Migration path, if any.

## Security considerations

Map each risk this introduces or affects to an entry in [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md), and to a test or operational control. **Required** for Core/Economic JIPs. Call out any new defamation, liability, or correlated-failure surface.

## Test cases / reference implementation

Links to tests, golden vectors, or a reference implementation (if available).

## Copyright

Released under CC-BY-4.0.
