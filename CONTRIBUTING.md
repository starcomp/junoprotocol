# Contributing to Juno Protocol

Thanks for your interest in Juno. This is a **pre-alpha, design-stage** project (see the warning in
[README.md](README.md)) — which means the highest-value contributions right now are **review,
discussion, and proposals**, not yet large feature PRs against code that doesn't exist.

This document covers how to contribute, the DCO sign-off requirement, the PR process, the
Juno Improvement Proposal (JIP) process, coding standards, and how code-maintainer authority is
kept **separate** from on-chain DAO governance.

## Code of Conduct

All participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md) (Contributor Covenant
v2.1). By participating you agree to uphold it. Report unacceptable behavior to
`conduct@junoprotocol.org`.

## Developer Certificate of Origin (DCO) — required

Juno uses the **DCO**, not a CLA. **Every commit** must be signed off, certifying you have the
right to submit it under the project's license (see [LICENSING.md](LICENSING.md) for per-component
licenses).

Sign off by adding the `-s` / `--signoff` flag:

```sh
git commit -s -m "Your commit message"
```

This appends a trailer to your commit message:

```
Signed-off-by: Your Name <you@example.com>
```

By signing off you certify the [Developer Certificate of Origin 1.1](https://developercertificate.org/):

> By making a contribution to this project, I certify that:
>
> (a) The contribution was created in whole or in part by me and I have the right to submit it
>     under the open source license indicated in the file; or
> (b) The contribution is based upon previous work that, to the best of my knowledge, is covered
>     under an appropriate open source license and I have the right under that license to submit
>     that work with modifications, whether created in whole or in part by me, under the same open
>     source license (unless I am permitted to submit under a different license), as indicated in
>     the file; or
> (c) The contribution was provided directly to me by some other person who certified (a), (b) or
>     (c) and I have not modified it.
> (d) I understand and agree that this project and the contribution are public and that a record
>     of the contribution (including all personal information I submit with it, including my
>     sign-off) is maintained indefinitely and may be redistributed consistent with this project
>     or the open source license(s) involved.

> [!NOTE]
> **PLANNED:** A DCO check will gate every PR in CI (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).
> PRs with unsigned commits will be blocked.

## Development setup

> [!NOTE]
> **PLANNED / STUB.** The monorepo tooling is not yet wired up. When it is, this section will
> document the full setup. The intended shape:
>
> - **Workspace:** pnpm (TypeScript packages) + Cargo (Rust components) + Foundry (Solidity).
> - **Target:** `git clone`, install, and `forge test` green in under 15 minutes.
> - **Per-package** setup instructions will live in each directory's `README.md`.

## Pull request process

1. **Open an issue first** for anything non-trivial, so the approach can be discussed before you
   invest in a PR. Look for the **`good first issue`** label to get started.
   *(PLANNED: a curated set of good-first-issues will be maintained once code lands.)*
2. **Fork and branch.** Do not push directly to the default branch. Use a descriptive branch name.
3. **Sign off every commit** (DCO, above).
4. **Keep PRs focused.** One logical change per PR. Cross-cutting changes that touch the attestation
   schema in `contracts/` + `sdk/` + `indexer/` at once are welcome as a single atomic PR (that is a
   benefit of the monorepo) — but unrelated changes should be separate.
5. **Pass CI.** Lint, typecheck, tests, contract static analysis, and the DCO check must be green.
   *(PLANNED — see the CI stub.)*
6. **Get review.** At least one maintainer review is required. Merge is blocked on red CI or an
   unresolved review.

### What needs a JIP instead of (or alongside) a PR

Changes to the **attestation schema**, the **trust model**, **tokenomics/slashing economics**, or any
**public interface** that every implementer depends on require a **Juno Improvement Proposal** — see below.
A code PR that implements such a change should reference its JIP.

## The JIP process (Juno Improvement Proposals)

Juno uses an EIP / Rust-RFC-style process for any change to a shared standard. Full lifecycle and
template live in [`specs/`](specs/):

- [`specs/jip-process.md`](specs/jip-process.md) — the lifecycle (Draft → Review → Last Call →
  Final / Stagnant / Withdrawn) and categories (Core, Interface, Economic, Meta).
- [`specs/jip-template.md`](specs/jip-template.md) — copy this to start a JIP.
- [`specs/JIP-1-attestation-schema.md`](specs/JIP-1-attestation-schema.md) — the canonical attestation schema.

**Which body ratifies a JIP depends on its category** (this is the heart of the
code-vs-DAO separation; see [GOVERNANCE.md](GOVERNANCE.md)):

- **Core / Interface / Meta** JIPs are ratified by **Technical Steering Committee (TSC) rough consensus** —
  these are code and standards decisions.
- **Economic** JIPs (anything touching staking, slashing, emissions, fees, or treasury) require **both**
  a JIP **and** an on-chain DAO governance vote to activate. Maintainers cannot silently change economics,
  and token holders cannot push code.

## Coding standards

> [!NOTE]
> **PLANNED — to be hardened as code lands.** Intended standards:

- **Solidity (`contracts/`):** Foundry; deterministic `solc` pinning for reproducible bytecode;
  Slither + semgrep static analysis and gas snapshots gating every PR; OpenZeppelin where applicable;
  invariant tests for any value-handling logic.
- **TypeScript (`sdk/`, `indexer/`, `extension/`):** strict TypeScript; lint + typecheck + tests in CI;
  conventional-commit messages (enables automated SDK releases).
- **Python (`oracle-node/`, `fingerprinting/`):** typed (pydantic models for the attestation object);
  formatted and linted; tests in CI.
- **All:** SPDX license header matching the component (see [LICENSING.md](LICENSING.md)); no secrets in
  source; security-sensitive changes flagged for extra review.

## Code-maintainer authority vs. on-chain DAO governance

This is a core principle, stated plainly so neither side can quietly capture the other:

- The **Technical Steering Committee (TSC)** owns **code authority**: the Git repository, release
  signing, merge rights, and acceptance of Core/Interface/Meta JIPs. You cannot trustlessly verify a
  code review on-chain, so code quality and security live with accountable human maintainers — not a
  token vote.
- The **on-chain DAO** owns **protocol authority**: economic parameters (fees, emissions, slashing
  percentages) and the treasury. These are economic decisions where token-weighted legitimacy matters.
- **Neither body can unilaterally exercise the other's powers.** Tokenomics changes require **both** a
  JIP (code/spec artifact) **and** an on-chain vote (economic legitimacy).

Full detail in [GOVERNANCE.md](GOVERNANCE.md).

## Security

**Do not** open public issues for security vulnerabilities. Follow the responsible-disclosure process
in [SECURITY.md](SECURITY.md) (`security@junoprotocol.org`).

## License of contributions

By contributing, you agree your contribution is licensed under the license of the component you are
modifying (see [LICENSING.md](LICENSING.md)), and you certify the DCO. You retain your copyright.
