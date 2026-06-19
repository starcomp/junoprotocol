# Juno Protocol — Threat Model

> **Status:** Draft. Summarized from [`ROADMAP.md`](../ROADMAP.md) §11. A full `SECURITY-THREATMODEL.md` coverage matrix (every attack → mitigation → test/runbook) is a prerequisite before any economic contract deploys; CI fails on an uncovered row.

## Posture in one sentence

SynthID detection cannot be verified on-chain, so integrity reduces to keeping a small set of licensed detectors honest and punishing *detectable, provable* wrong attestations faster and cheaper than an attacker can profit. The threat model centers on the **federation and the challenge market**, not cryptographic novelty.

## Threats & mitigations

| Threat | Severity | Mitigation |
|---|---|---|
| **Correlated detector failure** — every honest oracle calls Google's one API; a Google-side bug/model-update/key-compromise makes the whole federation simultaneously and identically wrong, and an optimistic market **cannot slash a unanimous, genuinely-mistaken majority**. | **Critical (the #1 systemic risk)** | Never auto-finalize high-stakes changes before the challenge window elapses; emergency pause that quarantines/marks-stale attestations from a declared correlated-failure incident; mandatory `detector_version` so a bad version is bulk-flaggable; **gate real federation on ≥2 genuinely independent detectors existing**; scope liability to detectable-disagreement faults only. The chain cannot manufacture detection truth it doesn't have. |
| **phash collision (defamation injection)** — a false near-dup match brands innocent real media as "AI", and persistent memory *amplifies* it. | High | phash is **advisory-only**: a match never mints/mutates a verdict or triggers a slash; it surfaces a labeled prior. `chash` governs exact identity. Published precision gate against a ≥1M hard-negative haystack (launch-blocking). Rate-limit phash-triggered queries; multi-algorithm consensus at mainnet. No bare "AI" label on identifiable persons without human review. |
| **Oracle collusion** | High | Optimistic challenge lets any bonded watchdog submit a fraud proof for a slice of slashed stake; permissioned licensing means colluders risk a real-world license + reputation; keep m large relative to n; guardian can de-list. (Residual risk overlaps correlated-failure when collusion is unprovable.) |
| **Detector key compromise** | High | m-of-n threshold sigs (mainnet) so one share can't forge; **HSM/KMS custody mandatory before mainnet**; mandated rotation; de-list compromised oracle. |
| **Governance takeover** (flash-loan / low quorum) | High | Doxxed guardian multisig + timelock on dangerous levers during bootstrap; checkpointed snapshot voting; per-holder weight cap; slash %, window, and allowlist behind a longer timelock + guardian veto even post-handoff. |
| **Frivolous-challenge / griefing DoS** | Medium | Asymmetric bonds (challenger bond ≥ oracle stake-at-risk slice, with a floor); losing-challenger bond burned; an escalation game that resolves rather than stalls; rate-limit per key. |
| **MEV / front-running of challenges** | Medium | **Commit-reveal** challenge bonds + **order-independent attestation acceptance** (first valid sig wins, deterministic tie-break); private-mempool reveal as mainnet hardening. |
| **Replay / duplication** | Medium | Bind every attestation to `{chash, detector_version, timestamp, nonce}`; on-chain uniqueness on `(fingerprint, attester, epoch)`; emissions credited once per unique fingerprint-attestation. |
| **Watermark stripping** | Inherent | Not solvable on-chain — but it is *why* persistent memory exists: once attested, the chain remembers the verdict keyed by fingerprint even after stripping. We mitigate the consequence; we cannot prevent the stripping. Not robust to motivated regeneration-laundering (declared boundary). |

## The single biggest systemic risk

**Correlated detector failure.** Because detection is 100% Google-keyed, "m-of-n" is *n copies of one correlated dependency* until a genuinely independent second licensed detector exists, and a unanimous-wrong federation is unslashable by an optimistic market with no on-chain truth oracle to point to. This drives two binding design decisions: real federation is gated on independent detectors existing, and economic liability is scoped to detectable-disagreement faults — never the "is-this-AI" verdict that needs Google's secret keys.

## Verification program

Foundry invariant tests + Echidna fuzzing + a Certora slashing-conservation spec in CI; a coverage matrix as a deploy gate; a scoped external audit (hard launch gate); an incentivized ≥4-week attack-net before mainnet; an Immunefi bounty at mainnet. See [`SECURITY.md`](../SECURITY.md).
