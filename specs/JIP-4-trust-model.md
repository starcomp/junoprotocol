---
jip: 4
title: Trust model — claim-of-record, multi-signal ensemble, graceful degradation
author: Juno core
status: Draft
category: Core
created: 2026-06-19
requires: 1
---

## Abstract

Defines what a Juno attestation actually *asserts*, which signals it draws on, and how the protocol stays alive when any one signal is unavailable. Three decisions: (1) attestations are **claims of record** — "attester A ran detector build V over content C and observed output O," a locally-reproducible fact — **not** truth-claims that "this is AI"; (2) Juno is a **detector-agnostic, multi-signal** registry whose primary signals are ToS-clean and independent (C2PA verification, open SynthID-Text, an owned classifier, platform disclosure), with any single vendor's API a **pluggable, flag-gated** provider that is never on the launch critical path; (3) a **graceful-degradation invariant** guarantees the protocol runs with any one detector class disabled. Together these make the slashing market sound, defuse the single-vendor dependency, and bound defamation exposure.

## Motivation

Two hard problems sit under the whole protocol:

- **The slashing market has no truth oracle.** "Is this AI?" cannot be verified on-chain (the detector needs secret keys), so an optimistic challenge market has nothing to slash against — a unanimous-but-wrong federation is unslashable. The fix is to make the *asserted thing* reproducible.
- **A single-vendor dependency is both a legal and a systemic risk.** If every attestation depends on one external detection API, that vendor's terms, outages, and model bugs become the protocol's terms, outages, and correlated failure mode.

This JIP resolves both by narrowing what is asserted and widening what is consulted.

## Specification

The key words MUST, MUST NOT, SHOULD, and MAY are as defined in RFC 2119/8174.

### 1. Claim-of-record (normative)

An attestation is a signed, reproducible record of an observation, not a verdict of truth:

> *Attester `A`, holding active stake, ran detector build `detector_version=V` (or verified C2PA manifest `M`) over content with fingerprint `C`, and observed normalized output `O` (the `verdict` + `confidence` fields of [JIP-1](JIP-1-attestation-schema.md)).*

- The **slashable fault is a *reproducible detector-output mismatch*** — `A` reported `O`, but re-running build `V` over `C` (or re-verifying `M`) deterministically yields `O' ≠ O`. The fault is **detectable disagreement**, never "the verdict was wrong about reality."
- Renderers **MUST** present an attestation as a **sourced claim**, attributed and dated ("attested AI by `A` using `V` on `<date>`"), **MUST NOT** present it as a present-tense factual assertion that media *is* AI, and **MUST NOT** apply a bare "AI" label to identifiable persons or named authors without human review. (Defamation control; see [JIP-1](JIP-1-attestation-schema.md) and [`docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md).)
- This gives the challenge market **deterministic ground truth** (re-run and compare) without ever needing an on-chain "is-this-AI" oracle.

### 2. Detector-agnostic, multi-signal ensemble (normative)

The oracle's `DetectorProvider` chain ([`oracle-node/`](../oracle-node/README.md)) ingests multiple, deliberately heterogeneous signal classes. Each attestation records *which* class and `detector_version` produced its output.

| Signal class | Independence / ToS posture | Launch role |
|---|---|---|
| **C2PA / Content Credentials verification** | Open spec, vendor-independent, deterministically re-runnable | Primary |
| **Open SynthID-Text** (Apache-2.0) | No external API, no ToS, deterministically re-runnable | Primary |
| **Owned / academic classifier** | Self-hosted, re-runnable; see independence caveat §4 | Primary (advisory for unlabeled media) |
| **Platform disclosure labels** | Source-attributed third-party claim | Primary |
| **Vendor detection APIs** (e.g. Google SynthID image/audio/video) | External, ToS-uncertain, may be non-re-runnable by third parties | **Pluggable, flag-gated, OFF by default — never launch-blocking** |

- **Launch-blocking providers MUST be ToS-clean and reproducible.** A provider whose terms forbid third-party re-running (so its output cannot be a slashable claim-of-record) **MUST NOT** be a launch-blocking or slashable signal; it MAY contribute an explicitly non-slashable, attributed advisory record.
- No single vendor's model or terms is load-bearing: the registry's value (neutral, persistent, multi-writer) holds across the primary signal classes regardless of any one vendor.

### 3. Graceful-degradation invariant (normative)

- No read-path verdict, slashing predicate, or federation threshold **MUST** require any single detector class.
- The full happy-path (submit → fingerprint → attest → record → read → challenge) **MUST** run with the vendor-API class disabled.
- CI **MUST** include a "vendor-API-disabled" run of the end-to-end path; a build in which disabling the vendor class breaks the happy-path **MUST** fail.

Consequence: a hostile vendor ToS change or outage degrades coverage of one class — it never halts the protocol.

## Rationale

Narrowing the assertion to a reproducible claim is what makes a permissionless slashing market possible at all; everything else (federation, bonding, challenges) is built on having something deterministic to dispute. Going multi-signal is not hedging — it is the only way the "neutral, cross-vendor registry" property is *true* rather than aspirational. The graceful-degradation invariant turns "we don't depend on Google" from a slogan into a CI-enforced property.

## Backwards compatibility

Additive and clarifying. No change to the JIP-1 on-chain layout — `detector_version`, `verdict`, `confidence`, and `provenance` already carry everything claim-of-record needs. This JIP fixes the *interpretation* (a reproducible claim, not a truth-verdict) and the *provider policy* (ToS-clean primary, vendor-API pluggable).

## Security considerations

- **Correlated detector failure** is decomposed into three sub-problems with different status:
  - **(A) Slashability of correlated honest error — solved here.** Claim-of-record gives the market a reproducible target, so a faithfully-reported-but-wrong output is *not* a fault (and not slashed), while a *misreported* output always is.
  - **(B) Containment — solved by operations.** Mandatory `detector_version`, bulk per-version quarantine, finalization windows that don't auto-finalize high-stakes claims, AND a **continuous secret canary**: a held-out, periodically-refreshed labeled set re-scored on every `detector_version` to catch *quiet* drift, not only loud verdict-flip spikes.
  - **(C) Genuine witness independence for unlabeled media — NOT solved.** For an unlabeled, laundered image/audio/video clip with no manifest, C2PA/text/platform signals are silent and the only speaker is a classifier that may be **correlated-by-construction** (trained on the same generators). Independence **MUST** be *measured* (a published cross-detector error-correlation matrix on the §JIP-2 haystack), not assumed.
- **Forbidden until independence is measured:** an "independence-weighted cross-class consensus score," and any high-confidence *persistent* image verdict, **MUST NOT** ship before the correlation matrix supplies real weights — otherwise the score returns false confidence on exactly the unlabeled content the registry exists to flag.
- **Re-run legality:** because the slashing predicate requires re-running a detector, challengers re-running a **vendor API** could itself breach that vendor's terms — another reason vendor-API outputs are non-slashable advisory records, and slashable faults are scoped to the ToS-clean, freely-re-runnable signals + C2PA mismatch.

## Copyright

CC-BY-4.0.
