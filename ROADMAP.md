# Juno Protocol — Master Roadmap

> **Status:** Pre-implementation lead-engineering plan. This document is the single source of truth for what we build, in what order, and what we will *not* build until specific gates are cleared. It supersedes the eight dimension designs and folds in the three adversarial critiques.
>
> **One-line thesis:** Juno is a neutral, cross-vendor, economically-liable **registry of record** for content-provenance attestations with persistent perceptual-hash memory — *not* an AI detector. Reads are free; only fresh detection is paid.
>
> **Reading order:** §1 (why this might fail and how we counter it) and §13 (kill-gates) are the load-bearing sections. Everything else is downstream of them.

---

## Table of Contents

1. [Vision & the four-property thesis](#1-vision--the-four-property-thesis)
2. [Protocol architecture overview](#2-protocol-architecture-overview)
3. [Off-chain stack](#3-off-chain-stack)
4. [The testnet MVP (Minimal Viable Protocol)](#4-the-testnet-mvp-minimal-viable-protocol)
5. [Build plan for the MVP](#5-build-plan-for-the-mvp)
6. [Future development roadmap](#6-future-development-roadmap)
7. [Tokenomics](#7-tokenomics)
8. [DAO & progressive decentralization](#8-dao--progressive-decentralization)
9. [Nonprofit / foundation / legal structure](#9-nonprofit--foundation--legal-structure)
10. [Open-source project](#10-open-source-project)
11. [Security & audit program](#11-security--audit-program)
12. [Immediate next steps](#12-immediate-next-steps)
13. [Key decisions for the founder to ratify](#13-key-decisions-for-the-founder-to-ratify)

---

## 1. Vision & the four-property thesis

Juno is a **neutral registry of record** for "is this media AI-generated?" attestations. It rests on four properties, each of which is the *only* reason a blockchain (versus a single company's database) is justified:

1. **Neutral registry** — a multi-writer, vendor-agnostic record that no single AI firm owns or can unilaterally rewrite. Google will not host OpenAI's provenance claims, and vice versa; a neutral substrate is the structural gap.
2. **Persistent phash-keyed memory** — once any media is attested, the registry *remembers* the verdict keyed by a perceptual hash, so a recompressed / cropped / re-encoded near-duplicate still surfaces the **prior attestation** even after a watermark is stripped. This is the registry's single genuine technical differentiator over free, trivially-strippable C2PA credentials.
3. **Economic-liability layer** — attesters stake collateral and are slashable through an optimistic challenge market, so the registry can punish a *detectable, provable* wrong attestation faster and cheaper than an attester can profit from it.
4. **Token bootstrap** — a decaying-emission subsidy pays oracles to cover the long tail of media before organic query-fee demand exists. This is the *weakest* of the four and is explicitly contingent (see §1.1 and §7).

### 1.1 Why this might fail, and how we counter it

The three adversarial critics are right about the most dangerous things, and we adopt their fixes as binding design constraints rather than rebutting them. **We do not paper over these.**

| Existential challenge | Honest reading | Our counter (binding) |
|---|---|---|
| **(a) "Why pay when Search/Chrome make detection free?"** | C2PA verification is already free/client-side and Google is shipping SynthID detection natively into Search and Chrome — the exact consumer surface our reference extension targets. A registry nobody pays to *read* has no revenue. | **Abandon the "AI detector" framing entirely — Google wins that.** Reposition as the one thing Google structurally will not build: a neutral, cross-vendor, economically-liable **registry of record with persistent memory**. **Reads are FREE; only fresh detection is paid, in stablecoin.** Sell to **liability-bearing buyers** (stock-media marketplaces, ad-verification firms, insurers, election-integrity programs) who have an audit/liability need a free native label does not satisfy — never to browsers Google already serves. **Gate on ≥3 signed paid-pilot LOIs** before any token or mainnet spend (§13). |
| **(b) Existential Google-API dependency / obviation** | Detection is 100% Google-keyed, distribution (Chrome) is Google, and the consumer label is going native in Google's own products. Worse than "no access" is "access *and* native detection," which leaves us a thin wrapper Google can obviate at will. The API ToS may *also* flatly prohibit on-chain re-attestation, paid relay, or federation. | **Treat the ToS question as diligence item #1** — a binary legal answer (does the ToS even permit on-chain re-attestation / paid relay / federation?) gates all further build (§13). Keep the Foundation **arm's-length** (no partnership, no endorsement, nominative-fair-use only) and hold detector **licenses at the oracle edge**, not in the core entity. Make the schema **detector-agnostic** with graceful degradation to C2PA-only operation. Position in the gap Google will not fill: neutral persistence + liability across vendors. |
| **Rival-firm BLS federation is impossible** | A live m-of-n BLS threshold federation of Google/OpenAI/Meta co-running a joint DKG is organizationally, legally (antitrust), and operationally infeasible on any startup timeline; on testnet there is one real detector backend (Google text, private preview), so "m-of-n independent detectors" is *n copies of one correlated dependency*. | **No BLS, no federation in the MVP.** Single permissioned ECDSA attester behind an on-chain allowlist; architect for an attester *set* but ship n=1. **Real federation is gated on ≥2 genuinely independent licensed detectors *existing*** — a partnerships outcome, not an engineering sprint. |
| **phash precision / defamation** | A false near-dup match brands innocent real media as "AI" — the defamation hot-spot — and persistent memory *amplifies* it by design. The only published metric is a 200-image recall toy with no precision at web scale. | Reframe phash as an **advisory, labeled prior claim**: *"previously attested AI — not re-verified."* A phash hit never auto-mints a verdict, never auto-slashes, and is rendered as a prior, not a fresh truth. **Publish a precision number against a ≥1M hard-negative haystack as a hard launch gate** (§4, §13). Make defamation constraints product-defining: **no bare "AI" label on identifiable persons or named authors** without human review. |
| **Token superfluity / scale-vs-cost / slashing can't adjudicate** | Properties 1 & 2 need no token; a stablecoin-fee + bonded-stablecoin-slashing design could deliver liability (#3) without $JUNO. "Billions of attestations" (the Solana justification) contradicts the real per-detection cost. The challenge market cannot adjudicate the verdict that needs Google's secret keys — a unanimous-wrong federation is unslashable. | Justify $JUNO **only** by bootstrap-via-emissions + a burn-backed staking asset, *contingent on anti-spam demand-gating validating in simulation*; pre-commit a **token-drop exit** to a stablecoin-collateral model if it fails (§7). **Defer Solana state-compression until a published capacity model justifies it** — default mainnet is staying on the L2. Scope liability to **detectable-disagreement faults only** (C2PA manifest mismatch, reproducible detector-output mismatch), *not* the "is-this-AI" verdict that needs Google's keys — and say so plainly to integrators. |

The blunt summary: **two of the four properties are genuinely chain-justified (neutral registry, economic liability), and two are contingent (persistence is an off-chain ANN index with on-chain commitments; token-bootstrap may be superfluous).** We lead with the two strong properties, treat the two weak ones as supporting-and-contingent, and we are willing to ship a multi-org consortium + stablecoin-collateral version if the chain/token justification fails to hold. That honesty is the product.

---

## 2. Protocol architecture overview

### 2.1 Committed chain decision

| Phase | Decision | Rationale | Alternative considered |
|---|---|---|---|
| **Testnet** | **Base Sepolia + EAS** (Ethereum Attestation Service) | EAS gives schema registry, on-chain/off-chain attestations, revocation, referenced attestations (`refUID` for near-dup linkage), and a mature TS SDK + GraphQL indexer for free. We write only the ~3 economic contracts around it. Sub-cent gas, free faucet, strongest EAS ecosystem. Collapses weeks of registry work. | Custom Solidity registry (more audit surface, slower); Solana devnet (heavy Anchor/compression work, schedule risk); OP/Arbitrum Sepolia (equivalent; Base chosen for gas + distribution). |
| **Mainnet** | **Default: stay on the L2.** Solana state-compression is **conditional** and deferred until a published capacity model proves the long-tail volume justifies it. | The "billions of cheap attestations" thesis is unproven and likely contradicted by real per-detection cost; realistic steady-state is probably *millions of high-value attestations*, which the L2/EAS stack serves fine. Building Solana + BLS + Bitcoin anchoring before product-market fit is over-engineering and ~8–12 wks of avoidable spend + a second audit. | Solana + SPL state compression (only if capacity model justifies); Celestia/Avail DA + custom rollup (maximal scale, far higher burden). |

**This reverses the original "Solana is the mainnet hot path" assumption.** Solana is a *capacity-gated option*, not a roadmap commitment. The trigger to build it is a written capacity model (attestations/day, ANN index RAM + rebuild time, Solana tree count/depth, monthly indexer cost) showing the L2 cannot serve real demand economically — not a desire for scale we cannot yet size.

### 2.2 Minimal contract / module set (testnet)

The chain never runs detection. It stores signed verdicts, makes attesters financially liable, and meters paid detection. Built around EAS, not replacing it.

| Module | Role | Notes |
|---|---|---|
| **Canonical Attestation Schema** | Single source-of-truth, chain-portable field layout. | Foundational. Encoded as an EAS schema string (testnet) and a Borsh/Anchor struct (mainnet-conditional), with a round-trip equivalence test proving portability. |
| **JunoAttestationModule** (EAS `SchemaResolver`) | Registry write path. Enforces `chash` uniqueness (exact dedup), validates **k-of-n ECDSA** signatures from the staked detector allowlist, records LSH bucket index + parent `refUID` for near-dup linkage. Reverts invalid writes. | No BLS in MVP. |
| **Staking** | Oracles/challengers lock $JUNO collateral; tracks active stake, unbonding delay, gates writes, pull-based reward accounting. | OpenZeppelin ERC-20 + ReentrancyGuard. |
| **Slashing** | Privileged module, callable *only* by OptimisticChallenge on a resolved dispute. Burns/redistributes slashed stake (challenger bounty + Treasury remainder). | Implements property 3. |
| **OptimisticChallenge (+ DVM hook)** | Per-attestation challenge window, bond escrow, dispute state machine (`Proposed → Challenged → Resolved`), escalation to a DVM. Testnet DVM = Safe multisig; mainnet = token-weighted vote. | UMA optimistic-oracle pattern. |
| **QueryPayment / Metering** | Demand side. Meters **fresh-detection** payments (reads are free); routes fees to reward pool (pull-based claims) + burn slice. | The revenue loop that funds security. |
| **Treasury** | Collects slash remainders + fee burn/retention; funds emissions. Testnet: Safe-controlled vault. | Mainnet: Governor/Timelock-controlled. |
| **$JUNO (testnet faucet ERC-20)** | Staking collateral + (testnet) fee unit. Zero monetary value. | Mainnet token gated behind §13. |

**Deferred (mainnet-conditional, not MVP):** `ThresholdSigVerifier` (BLS via BN254 precompile / Solana alt_bn128), Solana compressed registry, Bitcoin anchoring, OZ Governor + Timelock with real voting, hardened upgrade proxy.

### 2.3 Canonical chain-portable attestation object

Defined **once**, mapped deterministically onto both an EAS ABI encoding and a Borsh/Anchor struct so integrators never re-integrate when we migrate. Schema is frozen before onboarding many integrators.

```
schema_version    u8        // versioned for forward-compat
chash             bytes32   // SHA-256 of canonical bytes; PRIMARY KEY, exact dedup, unique on-chain
phash_commit      bytes32   // commitment over the full neural phash (full phash in event/calldata)
lsh_bucket        bytesN    // locality-PRESERVING bucket key (NOT a crypto hash) for cheap on-chain coarse linkage
verdict           u8        // 0=not, 1=watermarked, 2=uncertain   (NEVER a bare "AI" assertion)
confidence        u16       // basis points
model_lineage     u16       // enum: Gemini/Imagen/Veo/Lyria/partner/unknown
detector_version  u16       // identifies the exact detector build (bulk-flag a bad version)
c2pa_manifest_hash bytes32  // hash of the verified C2PA manifest, if any
segment_map_hash  bytes32   // hash of off-chain segment map (which regions/timestamps watermarked)
attester_set_id   u32       // which signer set produced this
sig_ref           bytes     // k-of-n ECDSA refs (testnet); BLS aggregate ref (mainnet-conditional)
timestamp         u64
parent_ref        refUID    // near-dup parent linkage (EAS refUID / parent-leaf pointer)
```

**Resolved design tensions (from the critics):**

- **phash storage:** commit *only the locality-preserving LSH bucket key* on-chain (cheap, challengeable, coarse linkage); keep the full phash off-chain. A cryptographic hash-of-phash on-chain is useless for LSH because it destroys the Hamming locality the bucketing needs — so we store the bucket key, not a hash, and concede fine-grained linkage is an off-chain operation gated by challenges. (This also keeps person-linkable perceptual data off any immutable anchor — see §9 GDPR.)
- **Near-dup search:** ANN/vector similarity cannot run in a contract. The chain stores the *commitment + chosen linkage*; the search runs off-chain in a (rebuildable, challengeable) indexer.
- **Trust model:** k-of-n ECDSA allowlist on testnet (trivial verification, full economic semantics). BLS is a mainnet-conditional upgrade, gated on real independent detectors existing.

---

## 3. Off-chain stack

The chain stores attestations and stake/slash state; **all the real work is off-chain.** What is REAL vs STUBBED at MVP is marked explicitly and surfaced in the product so no stub can be mistaken for a real verdict.

| Service | Role | REAL vs STUBBED at MVP |
|---|---|---|
| **Detection Oracle node** (Python) | Pulls a job, runs a pluggable `DetectorProvider` chain, runs C2PA verify (`c2pa-python` / `c2pa-rs` against the Trust List), normalizes into the canonical attestation, signs (single ECDSA key at MVP), hands to submission. | **REAL:** open-source `synthid-text` detector (text only — the one license-free SynthID detector that exists). **REAL:** C2PA manifest verification. **STUBBED:** an honest deterministic detector over a **real labeled corpus** we control (known-AI from Imagen/Gemini + known-real public sets), default for image. **CODE-COMPLETE, FLAG-GATED:** `GoogleContentDetectionProvider` adapter — drops in zero-refactor when/if partner access + ToS clearance land. All stubbed/mock attestations carry an unforgeable `provenance=mock` field, a non-staked test key, and are excluded from any reward/slash path. |
| **Fingerprinting service** | `chash` = SHA-256 (exact) + per-modality perceptual/neural hash + ANN index. Image: DCT-pHash (cheap coarse) + PDQ (256-bit robust) + CLIP/DINOv2 embedding **+ ORB/RANSAC geometric verification** (the precision lever whose errors are *uncorrelated* with the hash family). Text: MinHash/SimHash. **Tiered persistence** (exact / recompression-invariant / advisory near-dup — see [JIP-2](specs/JIP-2-fingerprint.md)). (Audio Chromaprint + video keyframe-PDQ: **post-testnet**.) | **REAL** for image + text. ANN in pgvector at MVP (Hamming for binary hashes, cosine for embeddings); thin interface so pgvector→Qdrant is a config swap. Adversarial transform suite (crop/recompress/rotate/noise) in CI. |
| **Indexer + Read API** | Ingests EAS attestation events → Postgres 16 + pgvector. Serves GraphQL (rich queries) + a thin REST `POST /lookup {chash, phash} → {verdict, confidence, lineage, attestation_uid, challenge_status}` hot path with chash edge caching. | **REAL.** Rebuildable from chain events (this is the answer to "why blockchain" — the index is just a recall accelerator anyone can reconstruct). |
| **SDK** (TypeScript + Python) | `lookup()`, `submitProvenance()`, `subscribeChallenges()`. Bundles client-side WASM pHash so integrators never upload raw media. Published quickstart. | **REAL.** `@juno-protocol/sdk` (npm) + PyPI. |
| **Reference "Is this AI?" extension / widget** | MV3 extension: hashes media **client-side** (WASM, never uploads raw media), calls `/lookup`, renders a verdict badge with lineage + challenge status. Doubles as the flag/curator entry point. | **REAL.** This is a *reference integrator and demo*, NOT the revenue surface (Google serves browsers for free). Crypto/wallet/"on-chain" language hidden from the end-user surface. |
| **Relayer** (gasless) | EIP-712 / ERC-2771 meta-tx so submitters never hold gas. | **CONSTRAINED at MVP:** anonymous gasless flagging is **OFF by default**; any on-chain write requires a bonded/stake-gated path; hard spend cap with auto-shutoff. Gasless UX and Sybil-resistance are in direct tension — we resolve it toward Sybil-resistance. |
| **Blob / DA layer** | Segment maps + challenge evidence as content-addressed blobs; only the CID/hash goes on-chain. | IPFS (pinned) at testnet; Arweave for permanence is mainnet. |

**Honesty markers baked into the product:** a published "what is REAL vs STUBBED" table on the dashboard; `provenance=mock` rendered distinctly; detector precision/recall on the held-out corpus published so the demo never overstates detection ability. The chain is never claimed to "detect."

---

## 4. The testnet MVP (Minimal Viable Protocol)

### 4.1 The ONE golden end-to-end journey

> A **Submitter** posts an AI image to the demo gateway → the **Fingerprinting service** computes `chash` + `phash` + embedding → the single **Detection Oracle** runs detection (honest stub by default, real text-SynthID for text, Google adapter flag-gated) and writes an **EAS attestation** keyed by fingerprint while holding staked $JUNO → the **Integrator** (browser extension) queries by fingerprint and renders a badge → the operator **strips the watermark, recompresses to JPEG q60, and crops 10%** and re-queries — the registry **still returns the prior "AI" attestation** via near-dup match, surfaced as a *labeled prior claim* → a **Challenger** posts a bond to dispute a deliberately-wrong attestation, the **Safe multisig DVM** resolves it, the oracle's stake is **slashed**, the challenger is **paid**, and the attestation is **revoked** — all visible on the dashboard.

This single journey demonstrates all four properties: neutrality (a second attester key writes to the same registry), persistent memory (the strip-and-recompress moment), economic liability (the live slash), and bootstrap (the dashboard shows emissions → staking → fees → burn).

### 4.2 In-scope / out-of-scope cut list

| Area | IN (testnet MVP) | OUT (post-testnet / mainnet) |
|---|---|---|
| Chain | Base Sepolia + EAS, custom Juno schema, revocation | Solana + state compression; Bitcoin anchoring |
| Attesters | **Single** permissioned ECDSA oracle; 2nd dummy key registered to *prove* multi-writer neutrality | m-of-n BLS threshold federation + DKG |
| Detection | Honest **stub over a real labeled corpus** (default); **real** text-SynthID; **real** C2PA verify; Google adapter flag-gated | Real SynthID image/audio/video (blocked on Google access + ToS) |
| Modalities | **Image + short text only** | Audio (Lyria), video (Veo), temporal segment maps |
| Fingerprint | `chash` SHA-256 + DCT-pHash + PDQ + CLIP/DINOv2 embedding ANN (pgvector) | Sharded Qdrant; web-scale ANN |
| Economics | Faucet ERC-20 $JUNO, StakingManager (stake/lock/slash/withdraw), QueryPayment (paid fresh-detection; **free reads**), Treasury, 60/30/10 fee split, constant testnet emission | Real-value token, TGE, buy/burn AMM, decay curve, fee-flip, stablecoin auto-swap |
| Challenge | Optimistic single-round, bonded, **configurable window** (compress to ~10 min for live demos), 3-of-5 Safe arbiter, slashing + EAS revocation | Multi-round fraud-proof escalation, token DVM |
| Governance | Snapshot signaling + Safe council; federation = council-managed allowlist | OZ Governor + Timelock binding votes; token DVM |
| Read surface | REST `/lookup` + GraphQL; MV3 extension; public dashboard | Production paid metering at scale |
| Relayer | Bonded/stake-gated writes only; anonymous gasless flagging **off**; spend cap | ERC-4337 account abstraction; permissionless gasless |

### 4.3 What is stubbed (and why it is honest)

- **Detection** is stubbed for image (real labeled corpus, real verdicts, never fabricated confidence) because trustless on-chain detection is impossible by design — the chain's claim is registry/memory/liability/bootstrap, none of which depend on real detection. Text detection *is* real.
- **Federation** is n=1 because BLS+DKG of rival firms is infeasible and "n copies of one Google API" is not real independence. Neutrality is proven by the registry being multi-writer, not by a fake federation.
- **Token value** is zero (faucet) because the MVP's job is to make staking/slashing/payment *real on-chain and observable*, not to have market value.

### 4.4 Quantitative success criteria (hard gates)

| Criterion | Target |
|---|---|
| **phash precision (HARD GATE)** | **Published precision number against a ≥1M hard-negative haystack** of visually-similar-but-distinct real media (stock, memes, product shots, UI screenshots). Plus a **published adversarial-evasion rate** (regeneration/img2img/style-transfer/reframe). Persistence is re-stated as *surfacing a prior attestation for incidentally-degraded near-duplicates* — NOT laundering-robust, NOT a re-verified detection. **No mainnet token/spend until this number is published and acceptable for the chosen vertical's false-positive tolerance.** |
| **Persistence recall** | ≥90% recall on a documented ≥200-image benign-transform set (recompress + moderate crop + resize + watermark-strip), measured and published. Adversarial regeneration explicitly declared a known failure boundary. |
| **Neutrality** | Two distinct attester keys write to the same registry, both readable by the integrator; schema is open. |
| **Liability** | A live end-to-end challenge in <10 min overturns a deliberately-wrong attestation, slashes staked $JUNO, pays the challenger, and revokes the attestation. |
| **Read latency** | `/lookup` p95 <100ms on cached chash; ANN phash lookup p95 <300ms at ≥1M indexed fingerprints. |
| **Economic invariants** (simulated) | `E[honest-challenge profit] > 0` and `E[bad-attestation profit] < 0` across an oracle-error-rate sweep; oracle epoch reward ≥ modeled operating cost at target volume; 60/30/10 split reconciles within rounding. Spam/collusion/Sybil attack scripts extract **no** net positive tokens. |
| **Integrity of fakes** | Published "real vs stubbed" table; stub detector precision/recall reported; `provenance=mock` unmistakable. |
| **Reproducibility** | A third party runs the one-command demo against public Base Sepolia and reproduces the persistence result. |

### 4.5 Demo script

1. Open dashboard (live attestations, stakes, fee pool, challenges, slash log).
2. Submit a known-AI image → oracle attests "AI" with confidence → extension badge shows it.
3. **Strip + recompress (q60) + crop 10%** → re-query → badge still shows "previously attested AI — not re-verified." *(The wow moment.)*
4. Register a second attester key, write an attestation → show the registry is multi-writer.
5. Plant a deliberately-wrong attestation → Challenger bonds → Safe DVM rules → oracle slashed, challenger paid, attestation revoked → all on the dashboard in <10 min.
6. Show the precision-eval report and the "real vs stubbed" integrity table.

---

## 5. Build plan for the MVP

**Honest sizing:** ~**4–6 months, 2–3 engineers** (1–2 Solidity/crypto, 1–2 ML/fingerprinting, 1 full-stack/SDK; fractional legal + a lead). The "~8 weeks" figures in the source designs each scoped a *different non-overlapping subset* and assumed each other's outputs; the union — including the audit and the ≥4-week attack-net the security program *mandates as launch gates* — is multi-quarter. We reconcile into **one critical path**.

| Workstream | Sequence | Depends on | Rough effort |
|---|---|---|---|
| **W0 — Schema & scaffold** — canonical attestation spec; EAS schema string + Borsh struct + round-trip equivalence test; monorepo + CI + Base Sepolia deploy config; faucet $JUNO. | First | — | ~1 eng-wk |
| **W1 — Fingerprinting (image + text, REAL)** — `chash` + DCT-pHash + PDQ + CLIP/DINOv2 + MinHash/SimHash; pgvector ANN; frozen canonicalization + golden-vector tests; adversarial transform suite in CI. | ∥ W2 | W0 | ~3 eng-wks |
| **W2 — Read-only registry on EAS** — register Juno schema; `JunoAttestationModule` resolver (chash dedup, staked-writer gating, k-of-n ECDSA, LSH bucket, refUID); TS reference read/write. | ∥ W1 | W0 | ~2 eng-wks |
| **W3 — Single-oracle write + indexer + extension** — oracle node (stub detector default, real text-SynthID, C2PA verify, Google adapter flag-gated); indexer → Postgres+pgvector; `/lookup` + GraphQL; MV3 extension; gateway. | after W1, W2 | W1, W2 | ~4 eng-wks |
| **W4 — Token, staking, query payment** — StakingManager (stake/lock/unbond/withdraw); QueryPayment (**free reads, paid fresh detection**, 60/30/10 split); Treasury (Safe vault); constant emission. | after W2 | W2 | ~2 eng-wks |
| **W5 — Slashing + optimistic challenge** — OptimisticChallenge (window, bonds, state machine, Safe DVM hook); Slashing; commit-reveal challenge + order-independent acceptance (MEV defense); full Foundry coverage (dedup, k-of-n sig, challenge happy-path, frivolous-challenge slashing, reentrancy, **phash-is-advisory**). | after W4 | W4 | ~3 eng-wks |
| **W6 — Precision eval + persistence hardening** — build the **≥1M hard-negative haystack** + adversarial-evasion set; tune thresholds; **publish precision + evasion numbers** (the §13 gate); persistence recall to target. | after W3 | W3 | ~2–3 eng-wks |
| **W7 — Cryptoeconomic sim + invariant dashboard** — agent-based sim + on-chain indexer; sweep error rates/volumes; prove the economic invariants; spam/collusion/Sybil attack scripts fail. | after W5 | W5 | ~2 eng-wks |
| **W8 — Scoped external audit (LAUNCH GATE)** — tight audit of the 3 economic contracts + EAS integration (Trail of Bits / OpenZeppelin / Spearbit / Zellic). All high/critical closed; mediums triaged publicly. | after W5, frozen scope | W5 | ~3–4 wk engagement |
| **W9 — Incentivized attack-net + IR fire drill (LAUNCH GATE)** — public points/testnet-token chaos program running every documented attack; <30-min pause fire drill; correlated-failure quarantine demonstrated; findings folded back into tests. | after W8 | W8 | ≥4–6 wks |
| **W10 — Public testnet launch + demo + report** — one-command deploy; golden-journey script; success-criteria report published. | last | all | ~1 eng-wk |

**Critical path:** W0 → (W1 ∥ W2) → W3 → W4 → W5 → W6/W7 → **W8 (audit) → W9 (attack-net) →** W10. The two security gates (W8, W9) alone exceed two months and run after the contracts freeze, which is why the realistic figure is 4–6 months, not 8 weeks.

---

## 6. Future development roadmap

Every phase has explicit **graduation criteria**. Advancement is criteria-gated, not calendar- or discretion-driven.

### Phase A — Testnet MVP (single oracle, EAS, image+text)
Deliver §4. **Graduate when:** all §4.4 hard gates pass (esp. the published phash precision number), the scoped audit has zero open high/critical, and the ≥4-week attack-net completes with no participant able to slash an honest oracle, mint a verdict from a phash collision alone, profitably front-run a winning challenge, or drain bonds via griefing.

### Phase B — Guarded mainnet (still single/few permissioned attesters)
Mainnet deployment on the **L2** (Solana NOT yet — see §2.1). Real-value token *only if §13 kill-gates cleared*. Guardian multisig + timelock on all dangerous levers; phash precision proven at production index size; defamation gating enforced contractually. **Graduate when:** ≥3 signed paid-pilot LOIs converted to live paying integrators in the beachhead vertical; HSM/KMS custody live; funded Immunefi bounty live; second full audit of any mainnet-only code.

### Phase C — Real federation (≥2 independent licensed detectors)
**Hard precondition: ≥2 *genuinely independent* licensed detector implementations exist** (not n copies of one Google API) and their operators' legal teams have signed off on a body that can slash them. Only then build BLS threshold signing, federation registry with asymmetric add/remove, and the token-weighted DVM. **Graduate when:** ≥2 independent detectors attesting in production; FRAND membership operated by a neutral body (not competitor-controlled); antitrust counsel sign-off on file.

### Phase D — Full decentralization
OZ Governor + Timelock binding on the economic track; token DVM; oracle-reputation vote-gating; Security Council reduced to a narrow, sunset-bound emergency role. Solana state-compression **only if** the capacity model (§2.1) justifies it. **Graduate when:** value-secured threshold met, N consecutive cycles of >X% delegate participation, broad delegate ecosystem, legal sign-off on "sufficient decentralization."

---

## 7. Tokenomics

**Defensible jobs of $JUNO: only (3) economic-liability collateral and (4) bootstrap emissions.** Properties 1 & 2 do not need a token; we concede this openly. Fees are payable in **stablecoin** (auto-swapped) so $JUNO is never a read tax — and **reads are free**; only fresh detection is paid.

### 7.1 Testnet (now)
A single **faucet token (tJUNO), zero monetary value**, rate-limited faucet (e.g. 10k/address/24h, captcha or GitHub-OAuth gated). Exercises the full loop: stake → attest → challenge → slash → fee distribution. No bridge, no market, no real value. The economic objective is not price but to validate three invariants empirically (see §4.4).

### 7.2 Mainnet TGE design + securities-risk mitigations
- **No public sale.** Distribution is **retroactive / work-based** (earned for completed verification work) and **work-locked** (vests on attestations served, not time).
- Suggested allocation: community/ecosystem ~40%, Foundation treasury ~25% (long vest, governance-locked), core contributors ~20% (4-yr vest, 1-yr cliff), strategic partners/early oracles ~10% (work-locked), public goods / liquidity ~5%.
- **Utility-first framing baked into contracts and comms:** token is required collateral to attest and the unit of fee-for-service; **never** marketed as an investment. Buy-and-burn is described as a fee sink funding security, **never** as a mechanism to increase holder value. No dividends, no revenue-share to passive holders, no profit/price talk. Emissions are documented as work-based subsidies. Documented Howey review; geofence restricted jurisdictions at the faucet/app layer.
- **Live securities tell we are removing:** if legal counsel flags buy-and-burn as supply-reduction-for-appreciation, we drop it and run a **pure stablecoin-fee + bonded-stablecoin-collateral** model. The Tokenomics design already concedes this is viable.

### 7.3 The pre-committed token-drop exit
**We commit, in writing, before any TGE, to a fallback:** if (a) anti-spam demand-gating fails to validate in simulation, or (b) the securities posture cannot be made defensible, or (c) the bootstrap thesis does not hold, then Juno ships **without a native token** as a stablecoin-fee + bonded-stablecoin-slashing public-good registry. This is not a failure mode bolted on late — it is the default the burden of proof must overcome.

### 7.4 Sources & sinks

| | Mechanism |
|---|---|
| **Sources** | Decaying emissions (mainnet: ~30% of supply on exponential/halving decay, ~4-yr, `Eₜ = E₀·2^(−t/H)`, H≈12mo), routed **only to demand-gated, query-touched fingerprints**; fresh-detection query fees (stablecoin). |
| **Sinks** | Buy-and-burn slice of fees (30%, contingent on securities clearance); slashing burns; staking lockup. |
| **Fee split** | 60% reward pool / 30% burn / 10% treasury (governable). Reward pool: oracles ~55% (stake-at-risk × confirmed-correct, never raw count), submitters ~15% (provenance rebates), challengers ~20% (funded mainly from *slashed stake*), curators/flaggers ~10% (**only on confirmed-mislabel outcomes** — the central anti-spam lever). |
| **Anti-spam (the critical risk)** | Emissions flow only to fingerprints integrators actually queried; per-attester diminishing returns; outcome-gated flagger rewards; at maturity, marginal rewards shift from emissions to fees so there is no inflation subsidy to farm. |
| **Price-independent security floor** | Minimum oracle bond denominated in **fiat/stablecoin** terms (top-up when token price drops); the **licensed-detector credential** (not just stake) is the primary corruption defense, so security does not collapse in a token-price death spiral. |

---

## 8. DAO & progressive decentralization

Governance is **split into two tracks** because Juno's security root is a set of *licensed* detectors under real-world legal agreements — federation membership cannot be a naive token vote.

- **Economic track** (fees, emissions, slashing params, treasury, grants): progressively decentralizes to token holders via Snapshot signaling → OZ Governor + Timelock.
- **Federation / safety track** (admit/remove detectors, dispute DVM, emergency pause): stays under a higher-bar Security Council + detector-credential gate; **never** naive 1-token-1-vote.

### 8.1 Stages & graduation criteria

| Stage | What it is | Graduates when |
|---|---|---|
| **0 — Core-team multisig** | 3-of-5 Safe holds all keys; Snapshot for non-binding signal; published decentralization roadmap. | Testnet contracts deployed; roadmap + graduation criteria public. |
| **1 — Guarded launch (testnet target)** | Security Council Safe (4-of-7: core + detector ops + independents); federation = council-managed allowlist with **asymmetric add/remove**; council-executed economic votes; emergency pause; delegation live; decentralization dashboard. | Governance dry-run + detector-removal drill pass; no single key can add a detector, move treasury over cap, or change slashing without timelock. |
| **2 — On-chain economic governance** | OZ Governor + Timelock (audited) binds the economic track. | External audit passed; value-secured threshold met; N cycles of >X% delegate participation. |
| **3 — Federation decentralization + token DVM** | Federation add-path opened to a structured multi-gate (token signal + foundation credential + council co-sign); UMA-style token DVM; oracle-reputation becomes vote-gating. | Mature reputation data; DVM audit; legal review of federation decentralization; ≥2 independent detectors. |
| **4 — Full token + role governance** | Security Council narrowed to sunset-bound emergency role; federation governed by standing multi-gate; constitutional meta-governance; annual re-ratification of remaining powers. | Demonstrated track record; broad delegate ecosystem; legal sign-off. |

### 8.2 What the DAO governs — and the uniquely sensitive federation power

The DAO governs: economic **parameters** (challenge window, k-of-n threshold, fee rates, slash %, splits, emission curve), the **treasury** (within per-tx caps), **grants**, and the **dispute DVM** (final-instance resolution for contested attestations).

**Federation membership is the uniquely sensitive power** and is *deliberately not* a token vote. The asymmetry is the key safety property:

- **Adding** a detector is slow and multi-gated: valid off-chain license credential (hash-anchored, council-verified) **AND** a passed signal vote **AND** a timelock **AND** Security Council execution. *No single track can add a signer.*
- **Removing** a misbehaving detector is **fast** (council emergency, timelock-exempt) because removal is safe-by-default.

This defeats federation capture (a whale voting in a malicious/unlicensed detector breaks property 1) and lets a rogue signer be ejected before lasting damage. **Critically, allowlist admission, fee-setting, and slashing are moved OUT of any competitor's control** into the neutral Foundation/independent body — this is the antitrust posture, not just a governance nicety (§9).

### 8.3 Anti-plutocracy: reputation separate from token wealth
- **Non-transferable, slashable oracle reputation** (earned by confirmed-correct attestations, decays) gates oracle-policy and slashing-curve votes — so the parties who keep the registry honest have voice **independent of token wealth**.
- On-chain quadratic voting is rejected (Sybil-cheap via wallet-splitting without proof-of-personhood we won't depend on); QV/conviction used **only** for off-chain Snapshot signals and grants.
- Flash-loan defense: ERC-20Votes checkpointed snapshot voting power at proposal creation; mandatory timelock on every execution; council scoped veto during the timelock window; per-tx treasury caps; capped per-holder voting weight; quorum.
- Council powers carry an **annual sunset** requiring token-governance re-ratification or they lapse — preventing "permanent centralization disguised as progressive."

---

## 9. Nonprofit / foundation / legal structure

### 9.1 Recommended entity stack — Foundation / DAO / DevCo separation

The now-standard three-body separation (Uniswap/Aave/Maker):

| Body | Entity | Role | When |
|---|---|---|---|
| **DevCo** | **Juno Labs Inc.** (Delaware C-corp; or Swiss GmbH if team is EU/CH) | Employs core devs, signs the Google API ToS as a data consumer, holds trademark/IP in trust to assign to the Foundation, contracts under an arm's-length dev-and-services agreement. **The ONLY entity that must exist day one.** | MVP |
| **Foundation** | **Cayman Foundation Company** (ownerless, supervisor-governed) | Issues $JUNO, holds treasury + trademark, runs grants. Ownerless structure prevents any single AI firm being seen as beneficial owner — directly serving neutrality. Steward, not operator. | P2 / token launch |
| **DAO wrapper** | **Wyoming DUNA** | US legal personality + limited liability for token holders/contributors; on-chain votes legally bind the entity. Coexists with (does not replace) the Foundation. | Once 100+ members + live token |

**Do NOT over-form early:** the MVP runs on Juno Labs alone. Form the Foundation only at token launch, the DUNA only at 100+ members. Pre-draft the entity map + IP-assignment + dev-services templates so formation is fast when triggered. Premature Cayman+DUNA formation burns capital and creates an empty governance shell that *undercuts* the decentralization narrative.

### 9.2 Google-ToS diligence as item #1
**Before any further build:** obtain the actual SynthID / Content Detection API terms and a written answer (ideally from Google) on whether **on-chain re-attestation, paid relay, and m-of-n federation are permitted.** Many ML/API ToS prohibit using outputs to build a competing/derived service, redistributing/publishing results, or commercial resale/relay. If forbidden, the permissioned-oracle model, the federation, *and* the query-fee business model are illegal-by-contract simultaneously. This is a **binary, potentially fatal, currently-unconfirmed** assumption under the whole protocol. It is **kill-gate #1** (§13). Operate strictly under standard public API ToS as a data source, not a partner; keep licenses at the oracle edge.

### 9.3 Defamation constraints made product-defining
A false "this is AI" label on a real journalist's/artist's genuine work is a textbook defamatory factual imputation, and persistent memory is a liability **aggravator** (it republishes the false label across the long tail forever). We make these constraints *product-defining*, not ToS footnotes:

- **No bare "AI" verdict** is ever rendered. The schema's `verdict` enum is probabilistic with a `confidence` and an `uncertain` value; the UI must render an opinion with disclosed methodology, never a bare factual assertion.
- **No "AI" label on identifiable persons or named authors without human review.** Mandated contractually in the integrator agreement.
- **phash is an advisory, labeled prior** — *"previously attested AI — not re-verified"* — never an auto-mint, auto-slash, or fresh detection. The phash-collision attack is re-classified as a **defamation-injection threat** with legal (not just technical) escalation.
- **Liability aligned with economics:** the slashable staking oracle is the legal wrongdoer; the neutral registry is a passive record. The optimistic-challenge window is the documented **notice-and-correction** process. Integrator ToS requires disclaimed display + indemnity flowing to the Foundation.
- **Revocations must propagate as aggressively as verdicts** so a correction actually un-rings the bell — otherwise the flagship feature is a defamation amplifier.
- **Unanswered question we must answer before launch:** who bears residual liability after the challenge window closes and the slashed oracle's stake is exhausted? Options: Foundation backstop fund, mandatory oracle insurance, or strict caveat-emptor for integrators. A real defamation/Section-230 litigation opinion is required — not just a token-rights memo.

### 9.4 Other legal posture (summary)
- **License:** Apache-2.0 (patent grant) for contracts/SDK/schema; CC-BY for the open schema spec; DCO sign-off (CLA only once the Foundation exists). Patent grant matters in a SynthID/C2PA patent-dense space.
- **Securities:** ship a functional, useful registry *before* the token; usage-based emissions + retroactive/work-based distribution; no priced sale; restrict US persons initially; design as if the token is a security even under friendlier 2025–26 guidance.
- **Antitrust:** if rival firms ever co-participate, run it as an open FRAND standard body with objective non-discriminatory membership; **move allowlist admission, fee-setting, and slashing OUT of competitor control** into the neutral Foundation/independent body; no sharing of competitively sensitive data; Foundation (not a member firm) as convener. The 2000 competitor-collaboration safe harbors were withdrawn (Dec 2024) — there is no safe harbor, so this is counsel-gated before recruiting any second firm. Confirm rival firms' own legal teams will even join a body that can slash them; if not, the federation (and property 1) collapses and we learn it before building.
- **GDPR:** hash-only, no-media-storage is the core control. Treat phash of media depicting identifiable persons as **potentially personal (possibly biometric) data**; keep all person-linkable phashes in the **mutable, redactable application layer** and anchor to Bitcoin only chash/Merkle roots with no person-linkable perceptual data; DPIA; legitimate-interest lawful basis; erasure-tombstone mechanism.

---

## 10. Open-source project

### 10.1 Committed repo layout

A single **monorepo** (`juno-protocol/juno`, pnpm + Cargo workspaces) for code, with one carve-out: a separate **`juno-protocol/jips`** spec repo so standards version independently of code (mirrors how EIPs live apart from go-ethereum).

```
juno-protocol/juno/                 (monorepo)
├── contracts/        # EAS schema + resolver + staking/slashing/challenge (Foundry, Solidity)        [Apache-2.0]
├── oracle-node/      # stake-aware detection oracle; DetectorProvider chain; C2PA verify; signer      [AGPL-3.0]
├── fingerprinting/   # chash + per-modality phash + ANN client                                        [AGPL-3.0]
├── indexer/          # EAS event ingestion → Postgres+pgvector; GraphQL + REST /lookup                [AGPL-3.0]
├── sdk/              # @juno-protocol/sdk (TS) + Python; lookup/submitProvenance/subscribeChallenges  [Apache-2.0]
├── extension/        # MV3 "Is this AI?" reference integrator (client-side WASM hashing)              [Apache-2.0]
├── docs/             # Docusaurus site; quickstart, architecture, JIP index                           [CC-BY-4.0]
├── .github/          # CI workflows, CODEOWNERS, issue/PR templates, dependabot
├── CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md  GOVERNANCE.md  NOTICE  README.md

juno-protocol/jips/                 (separate repo)                                                    [CC-BY-4.0]
├── jip-1.md          # process
├── jip-2.md          # canonical attestation object schema
├── jip-3.md          # dual-fingerprint chash+phash spec
└── template.md
```

### 10.2 Licenses per component (and why)

| Component | License | Why |
|---|---|---|
| `contracts/`, `sdk/`, schema, `extension/` | **Apache-2.0** | Explicit **patent grant + retaliation** — essential in a watermarking/provenance space dense with Google SynthID and C2PA patents; integrators (browsers, platforms) need the legal cover to embed it. (MIT rejected: no patent grant.) |
| `oracle-node/`, `fingerprinting/`, `indexer/` (network services) | **AGPL-3.0-or-later** | Prevents a well-capitalized actor running a **closed hosted clone** of the moat-sensitive infra without upstreaming. AGPL constrains only closed *hosted forks*, not running a node for the public network (the desired behavior). (GPL rejected: doesn't cover the SaaS loophole.) |
| `docs/`, JIP text | **CC-BY-4.0** | Maximizes reuse of the standard so Google/OpenAI/Meta can implement freely. |

### 10.3 Maintainer model & JIP process
- **Staged maintainer model:** BDFL (founder, P0) → 3–5 person core team with merge rights (P1) → elected **Technical Steering Committee (TSC)** (P3).
- **Strict code/DAO separation (GOVERNANCE.md, day one):** the **TSC owns Git, release signing, and interface/schema JIPs**; the **DAO owns on-chain params, emissions, slashing %, and treasury**. Neither can exercise the other's powers. *Tokenomics/slashing changes require BOTH a JIP and an on-chain vote.* This is the same trust-boundary logic as the protocol's core insight: you cannot trustlessly verify a code review, just as you cannot trustlessly verify detection.
- **JIP process** (EIP/Rust-RFC style, in `juno-protocol/jips`): numbered, templated (motivation/spec/rationale/security/backwards-compat), `Draft → Review → Last Call → Final`, category tags (Core schema, Trust-model, Token/economics, Interface/SDK, Meta). Economic JIPs require an on-chain vote to activate; interface JIPs are ratified by TSC rough consensus. CI diffs the deployed EAS schema against canonical JIP-2 and fails on drift.
- **CI / audits-in-CI:** GitHub Actions — Foundry `build/test/snapshot` with pinned solc (reproducible bytecode so anyone can verify deployed bytecode matches source), Slither + semgrep + gas-diff gating every contract PR, TS lint/typecheck/test, DCO check, `semantic-release` for `@juno-protocol/sdk`, SLSA provenance + checksums on releases. A new contributor can `clone → pnpm install → forge test` green in <15 min.

### 10.4 Contributor flywheel
Bounty board funded by the founding nonprofit grant (**not** the DAO treasury), ~15 curated `good first issue`s, a 15-minute onboarding path, and ≥1 merged external (non-founding) PR as a testnet success criterion.

---

## 11. Security & audit program

**Security posture in one sentence:** SynthID detection cannot be verified on-chain, so integrity reduces to keeping the small set of licensed detectors honest and punishing *detectable, provable* wrong attestations faster and cheaper than an attacker can profit — the threat model centers on the **federation and the challenge market**, not cryptographic novelty.

### 11.1 Top threats and mitigations

| Threat | Severity | Mitigation |
|---|---|---|
| **Correlated detector failure** (THE single biggest systemic risk) | Critical | Every honest oracle calls Google's one API with one key set; a Google-side bug/model-update/key-compromise makes the *entire federation simultaneously and identically wrong*, and an optimistic challenge market **cannot slash a unanimous, genuinely-mistaken majority** (no "correct" answer to point to). Counters: never auto-finalize high-stakes changes before the window elapses; emergency pause that quarantines/marks-stale attestations from a declared correlated-failure incident; mandatory `detector_version` on every attestation so a bad version is bulk-flaggable; **push for genuine detector diversity** (≥2 independent implementations) and document loudly that until that exists the federation is one correlated dependency. *This is the four-property weak spot — the chain cannot manufacture detection truth it doesn't have.* **Refined (see [JIP-4](specs/JIP-4-trust-model.md)):** claim-of-record makes a faithfully-reported-but-wrong output *not* a slashable fault (so the market only ever slashes reproducible mismatch); a continuous secret canary catches quiet `detector_version` drift; genuine independent-witness for unlabeled media stays an open, must-be-*measured* problem. |
| **phash collision (defamation injection)** | High | phash **advisory-only** by design — a match never mints/mutates a verdict or triggers a slash; it surfaces a labeled prior and (optionally) a fresh requery. `chash` governs exact identity. Rate-limit phash-triggered queries; multi-algorithm consensus for mainnet. |
| **Oracle collusion** | High | Optimistic challenge lets any bonded watchdog submit a fraud proof for a slice of slashed stake; permissioned licensing means colluders risk a real-world license + reputation; keep m large relative to n; guardian can de-list. Residual risk if collusion is unprovable (overlaps correlated-failure). |
| **Detector key compromise** | High | m-of-n threshold sigs (mainnet) so one share can't forge; **HSM/KMS custody** mandatory before mainnet (software TSS acceptable on testnet); mandated rotation; de-list compromised oracle. |
| **Governance takeover** (flash-loan / low quorum) | High | Doxxed guardian multisig + timelock on all dangerous levers during bootstrap; checkpointed snapshot voting; per-holder weight cap; slash %, window, and allowlist behind a longer timelock + guardian veto even post-handoff. |
| **Frivolous-challenge / griefing DoS** | Medium | Asymmetric bonds (challenger bond ≥ oracle stake-at-risk slice, with a floor); losing-challenger bond burned (small gas refund); escalation game that resolves rather than stalls; rate-limit per key. |
| **MEV / front-running of challenges** | Medium | **Commit-reveal** challenge bonds + **order-independent attestation acceptance** (first valid sig wins, deterministic tie-break) so reordering yields no profit; private-mempool reveal as mainnet hardening. |
| **Replay / duplication** | Medium | Bind every attestation to `{fingerprint, detector_version, timestamp, nonce}`; on-chain uniqueness on `(fingerprint, attester, epoch)`; emissions credited once per unique fingerprint-attestation. |
| **Watermark-stripping** | Inherent | Not solvable on-chain — but this is exactly *why* persistent memory exists: once attested, the chain remembers the verdict keyed by fingerprint even after stripping. Honest framing: we mitigate the consequence (memory survives stripping), we cannot prevent the stripping. |

### 11.2 Staged audits & formal/invariant testing
- **Foundry invariant tests** (stake conservation across slash; no-slash-without-resolved-challenge; `challenger reward ≤ slashed amount`; honest oracle never slashed by a frivolous challenge) + **Echidna** property-based fuzzing of bond/slash arithmetic + a targeted **Certora** spec for the slashing-conservation invariant. Green in CI on every PR.
- **Coverage matrix as a gate:** `SECURITY-THREATMODEL.md` enumerates every attack mapped to a mitigation, the property it leans on, and a specific test/runbook. **No contract deploys until every row has a test or operational control;** CI fails on an uncovered row.
- **Scoped pre-launch external audit** (W8): the 3 economic contracts + EAS integration only — a tight, tractable target. Zero open high/critical at launch; mediums triaged publicly. (Trail of Bits / OpenZeppelin / Spearbit / Zellic.)
- **Second full audit** before any mainnet-only code (Solana program if ever adopted, Bitcoin anchoring).

### 11.3 Incentivized attack-net (hard launch gate)
A public, points/testnet-token chaos program inviting all documented attacks (Sybil spam, frivolous-challenge griefing, a simulated colluding-oracle quorum, phash-collision submissions, front-running) **running ≥4 weeks before mainnet.** Pass condition: no participant can slash an honest oracle without a valid fraud proof, mint a verdict from a phash collision alone, profitably front-run a winning challenge, or drain bonds via griefing. Plus a <30-min pause fire drill and a demonstrated correlated-failure quarantine procedure.

### 11.4 Immunefi bounty & key custody
Funded Immunefi bounty with tiered payouts goes live at **mainnet** (testnet runs the points/testnet-token program instead). Oracle signing keys in HSM/KMS (AWS CloudHSM / GCP Cloud KMS / YubiHSM) with mandated rotation cadence and a published per-oracle custody attestation; guardian multisig pause + short timelock.

### 11.5 The single biggest systemic risk
**Correlated detector failure** (§11.1, row 1). Because detection is 100% Google-keyed, "m-of-n" is *n copies of one correlated dependency* until a genuinely independent second licensed detector exists, and a unanimous-wrong federation is unslashable by an optimistic market that has no on-chain truth oracle to point to. This is why **real federation is gated on independent detectors existing** (§6 Phase C) and why we scope economic liability to **detectable-disagreement faults only** — never the "is-this-AI" verdict that needs Google's secret keys.

---

## 12. Immediate next steps

**First sprint / first 90 days, ordered.** Diligence and demand-validation run *before* heavy engineering, because they can kill the project cheaply.

1. **[Kill-gate #1] Resolve the Google ToS question.** Obtain the actual SynthID / Content Detection API terms; get a written answer on whether on-chain re-attestation, paid relay, and m-of-n federation are permitted. **Do not proceed to mainnet/token spend until answered.** *(Owner: founder + counsel.)*
2. **[Kill-gate #2] Start the LOI motion.** Identify 3–5 design-partner archetypes in ONE beachhead vertical (recommend stock-media marketplaces or newsroom/fact-checker provenance, where a false-real is expensive and a credential is valued). Price-test the **neutral persistent-memory / liability-of-record** service (NOT generic "is this AI") and pursue **≥3 signed paid-pilot LOIs** from buyers who explicitly cannot get the same data free from Google/C2PA.
3. **[Kill-gate #3 setup] Stand up the precision-eval harness early.** Begin assembling the **≥1M hard-negative haystack** + adversarial-evasion dataset now — it is on the critical path to the published phash precision number and does not exist yet.
4. **Form Juno Labs Inc.** (Delaware C-corp or Swiss GmbH); register the "Juno"/"Juno Protocol" wordmark (USPTO + Madrid); secure domains/handles. Obtain a **token-rights/securities MEMO** (not a launch opinion) and a **defamation/Section-230 litigation opinion**.
5. **Scaffold the repos** (W0): monorepo + `jips` repo; per-component LICENSE/NOTICE/SPDX; GOVERNANCE.md with the code/DAO separation written down; CONTRIBUTING (DCO), SECURITY.md, CI with Slither/semgrep/DCO gates; JIP-1/2/3 in Draft.
6. **Publish the schema + spec** (CC-BY) and the canonical attestation object; write the Borsh⇄EAS round-trip equivalence test.
7. **Ship the fingerprinting service** (image + text, REAL) with frozen canonicalization, golden-vector tests, and the adversarial transform suite in CI.
8. **Deploy the read-only registry on EAS** (Base Sepolia): `JunoAttestationModule` resolver (chash dedup, staked-writer gating, k-of-n ECDSA, LSH bucket, refUID) + TS reference read/write.
9. **Write `SECURITY-THREATMODEL.md` + coverage matrix** and the security.txt/PGP disclosure channel before any economic contract deploys.
10. **Pursue partnerships in parallel:** get oracle operators into Google's SynthID partner program (named owner + fallback if rejected); join C2PA as a member/observer; actively recruit a **second independent detector source** to break the correlated-dependency risk.

If kill-gates #1 or #2 fail, **pivot or stop** — do not spend the engineering budget on a beautifully-secured engine with no fuel line.

---

## 13. Key decisions for the founder to ratify

The genuine forks. The first three are **explicit KILL-GATES** — if any fails, the venture pivots to a fiat-funded, grant-backed, stablecoin-or-no-token public-good registry, or stops.

- **🛑 KILL-GATE 1 — Google-ToS legal answer.** Does the SynthID / Content Detection API ToS permit on-chain re-attestation, paid relay, and m-of-n federation? A "no" makes the oracle model, the federation, and the query-fee business simultaneously illegal-by-contract. **No further build past diligence until answered in writing.**
- **🛑 KILL-GATE 2 — ≥3 signed paid-pilot LOIs before any token/mainnet spend.** From liability-bearing buyers who explicitly cannot get equivalent data free from Google/C2PA, pricing the neutral persistent-memory/liability-of-record service. No revenue validation = no token economy.
- **🛑 KILL-GATE 3 — Published phash precision gate.** A precision number against a ≥1M hard-negative haystack (plus an adversarial-evasion rate) that is acceptable for the chosen vertical's false-positive tolerance. Persistence is re-stated as surfacing a labeled prior for incidentally-degraded near-duplicates — never laundering-robust. No acceptable precision = no defamation-safe product.
- **Positioning:** Ratify the repositioning from "AI detector" to **neutral, economically-liable registry of record with persistent memory** (free reads, paid fresh detection in stablecoin, sold to liability-bearing buyers). Google wins "detector"; we own the gap it won't fill.
- **Mainnet chain:** Ratify **defaulting to staying on the L2** for mainnet, with Solana state-compression deferred until a published capacity model justifies it — deleting the ~8–12-wk Solana+BLS+Bitcoin program from the committed roadmap.
- **Token vs no-token:** Ratify the **pre-committed token-drop exit** — ship without a native token (stablecoin-fee + bonded-stablecoin-collateral) if anti-spam demand-gating fails in sim, the securities posture can't be made defensible, or the bootstrap thesis doesn't hold.
- **Federation timing:** Ratify that **real federation (BLS, m-of-n) is gated on ≥2 genuinely independent licensed detectors existing** plus their legal sign-off — a partnerships outcome, not an engineering sprint. MVP ships n=1 ECDSA.
- **Liability scope:** Ratify that economic liability covers **detectable-disagreement faults only** (C2PA manifest mismatch, reproducible detector-output mismatch) — explicitly NOT the "is-this-AI" verdict that needs Google's keys — and that this is stated plainly to integrators.
- **Defamation as product constraint:** Ratify that no bare "AI" label is rendered on identifiable persons or named authors without human review, that phash is an advisory labeled prior, that revocations propagate as aggressively as verdicts, and that the residual-liability question (backstop fund / oracle insurance / caveat emptor) is answered before launch.
- **Beachhead vertical & north-star:** Ratify the single beachhead (recommend stock-media marketplaces or newsroom/fact-checker provenance) and a single north-star metric (recommend **weekly integrator query volume against covered media**) that emissions and grant spend are deployed to move.
- **Entity timing:** Ratify forming **only Juno Labs** at MVP, deferring the Cayman Foundation to token launch and the Wyoming DUNA to 100+ members.
- **Runway:** Ratify producing a phased budget identifying a single credible anchor funder (a large AI-safety/disinfo philanthropic grant is more reliable than RetroPGF lottery) sized to cover the entire pre-token coverage-bootstrap phase — the runway gap, not the smart contracts, is what most plausibly kills a nonprofit here.

---

*This roadmap deliberately leads with its own weak points. If the kill-gates clear, Juno is a defensible neutral registry-of-record with economic liability. If they don't, the honest move is the consortium/stablecoin version — or no build at all. That candor is the asset.*
