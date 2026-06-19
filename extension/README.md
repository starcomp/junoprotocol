# `extension/` — Reference "Is this AI?" browser extension

> **License:** Apache-2.0 · **Status:** PLANNED · **Stack:** TypeScript, Manifest V3, WASM

A Manifest-V3 reference integrator and demo. It hashes media **client-side** (WASM — raw media never uploaded), calls the indexer's free `/lookup`, and renders a verdict badge with model lineage and challenge status. It also doubles as the flag/curator entry point.

## This is a reference and demo — NOT the revenue surface

Google ships SynthID detection natively into Search and Chrome for free; we do **not** compete for the consumer browser label. This extension exists to (a) demonstrate the registry end-to-end and (b) give integrators a working reference. Revenue comes from **liability-bearing buyers** paying for fresh detection in stablecoin — not from browsers. See [`docs/FAQ.md`](../docs/FAQ.md) ("Isn't this just what Chrome does for free?").

## UX commitments

- **No crypto in the face of the user.** Wallet / token / "on-chain" language is hidden from the end-user surface.
- **Labeled priors, not assertions.** A near-duplicate (phash) hit renders as *"previously attested AI — not re-verified,"* never as a fresh factual claim. No bare "AI" label is shown on identifiable persons or named authors without human review (a defamation constraint — see [`ROADMAP.md`](../ROADMAP.md) §9.3).
- **Honesty markers.** `provenance=mock` results are rendered distinctly so a stubbed verdict is never mistaken for a real one.
