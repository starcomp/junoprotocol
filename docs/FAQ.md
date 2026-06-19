# Juno Protocol — FAQ

> **Status:** Draft. These are the hard questions, answered honestly. If an answer here ever conflicts with [`ROADMAP.md`](../ROADMAP.md), the roadmap wins.

### Isn't this just what Chrome and Google Search already do for free?

For the *consumer browser label* — yes, and we don't compete there. Google is shipping SynthID detection and C2PA verification natively into Search and Chrome, for free. Trying to be a better free "is this AI?" button is a losing position.

Juno is **not an AI detector.** It is the one thing a vendor structurally will not build: a **neutral, cross-vendor, economically-liable registry of record with persistent memory.** Google will not host OpenAI's provenance claims (or vice versa), will not make itself *financially liable* for a wrong label, and will not run a neutral record its competitors can write to and cite. Juno sells to **liability-bearing buyers** — stock-media marketplaces, ad-verification firms, insurers, election-integrity programs — who need a neutral record they can point to in a dispute, not a label that lives only inside one company's browser. **Reads are free; only fresh detection is paid.**

If, after real diligence, that distinction doesn't command revenue (we gate on **≥3 signed paid-pilot LOIs** before any token/mainnet spend), the honest answer is not to build it. See [`ROADMAP.md`](../ROADMAP.md) §1.1 and §13.

### Are you affiliated with or endorsed by Google?

**No.** Juno is not affiliated with, sponsored by, or endorsed by Google, Alphabet, Adobe, or the C2PA / Content Authenticity Initiative. "SynthID" and "C2PA" / "Content Credentials" are the property of their respective owners and are used here **nominatively** — only to name the third-party tools Juno oracles run, strictly under those tools' own terms of service, at the oracle edge. We use no third-party logos and claim no partnership.

Whether the Google AI Content Detection API's terms even *permit* on-chain re-attestation, paid relay, and federation is an **open, load-bearing diligence question** and our **kill-gate #1**. A "no" would make the oracle model, the federation, and the query-fee business simultaneously unworkable. We resolve this in writing before building past diligence.

### Does the chain run SynthID? Can it prove a watermark?

No. SynthID's detector needs Google's secret keys, so it **cannot** be verified on-chain. The chain stores signed verdicts and makes attesters liable for *detectable, provable* errors after the fact. It never claims to detect. See [`docs/ARCHITECTURE.md`](ARCHITECTURE.md).

### Does the token have value? Do I need it to read?

You never need a token to **read** — reads are free, and fresh-detection fees are paid in **stablecoin**, so `$JUNO` is never a "read tax." The token's only defensible jobs are (3) staking collateral for economic liability and (4) bootstrap emissions to cover the long tail. Properties 1 and 2 don't need a token, and we say so. We have **pre-committed, in writing, to shipping without a native token** (a stablecoin-fee + bonded-collateral model) if anti-spam demand-gating fails in simulation or the securities posture can't be made defensible. See [`ROADMAP.md`](../ROADMAP.md) §7.

### What stops Juno from falsely branding real media as "AI"?

This is the defamation risk, and we treat it as product-defining. No bare "AI" verdict is ever rendered (verdicts are probabilistic, with confidence and an `uncertain` value); a perceptual-hash match is shown as a **labeled prior** ("previously attested AI — not re-verified"), never a fresh assertion; no "AI" label is applied to identifiable persons or named authors without human review; and a published precision number against a ≥1M hard-negative haystack is a hard launch gate. Revocations propagate as aggressively as verdicts. See [`docs/THREAT_MODEL.md`](THREAT_MODEL.md) and [`ROADMAP.md`](../ROADMAP.md) §9.3.

### Why a blockchain instead of a shared database?

Because the value is exactly the part a shared database can't provide: a neutral record **no single company owns**, that's **economically liable** via stake/slashing, with **persistent perceptual memory**, that **rivals can all write to**. The indexer is just a rebuildable cache. We're candid that two of the four justifying properties are conditional — and that if they don't hold, a multi-org consortium with stablecoin collateral is the honest alternative.

### What's the status? Can I use it?

**Pre-alpha. Unaudited. No token. No live network. Do not use in production.** This repository is a design-stage skeleton published for transparency and review.
