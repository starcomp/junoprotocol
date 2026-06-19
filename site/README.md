# `site/` — Juno Protocol landing page

> **License:** CC-BY-4.0 (content) / Apache-2.0 (markup) · A single, self-contained static site for GitHub Pages. No build step, no framework, no external/CDN dependencies, no trackers.

```
site/
├── index.html     # the landing page (inline CSS + ~20 lines of vanilla JS)
├── 404.html       # styled not-found page
├── favicon.svg    # logo / favicon
├── .nojekyll      # disable Jekyll processing
└── README.md
```

## Preview locally

It's a static file — just open it, or serve it:

```sh
# open directly
open site/index.html            # macOS

# or serve (any static server works)
python3 -m http.server -d site 8080   # → http://localhost:8080
```

## Deploy to GitHub Pages

A workflow at [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) deploys `site/` on every push to `main`.

**One-time setup:** repo **Settings → Pages → Build and deployment → Source: “GitHub Actions.”**
Once enabled, the site publishes at `https://starcomp.github.io/junoprotocol/`.

> The base path is `/junoprotocol/` (project Pages). The `404.html` "back home" link and the canonical `og:url` already use it; update them if the repo is renamed or moved to a user/org `*.github.io` repo (which serves from `/`).

## ⚠️ Visibility caveat (read before publishing)

This repository is currently **private** (until kill-gate #1 — the Google ToS question — clears; see [`ROADMAP.md`](../ROADMAP.md) §13). That interacts with Pages:

- **GitHub Pages on a private repo requires a paid plan** (Pro / Team / Enterprise), and the **published site is public regardless** (private Pages is Enterprise-only). So publishing from this repo while private both needs a paid plan *and* exposes the marketing page publicly.
- Publishing the page is the same decision as making the project public — and the honest position is to hold that until the kill-gate clears.

**Options:**
1. **Wait** — keep the page in-repo, publish when the repo goes public (`gh repo edit starcomp/junoprotocol --visibility public`, then enable Pages). *(Recommended.)*
2. **Separate public site repo** — push just `site/` to a public `starcomp.github.io` or `junoprotocol-site` repo to publish now without exposing the code. (Update the base path to `/` for a user/org Pages repo.)
3. **Paid plan** — enable Pages on the private repo (still publicly visible).

The page is written to be ready for any of these — it makes no claim that presupposes the kill-gates have cleared, and carries the pre-alpha + no-affiliation disclaimers prominently.

## Editing

All styles are inline in `index.html` under `:root` CSS variables (colors, radius, max-width) near the top — change those to re-theme. Content sections are plain semantic HTML. Keep it dependency-free.
