"""
Precision / recall evaluation + report (pure stdlib) — the S1 deliverable.

A "trial" is one query (a transformed variant of a known original, OR a hard
negative) matched against the candidate pool. We record the best tier it landed
in and whether that match was TRUE (the retrieved candidate is the query's real
origin). From trials we compute, PER TIER:

  precision = true matches at tier / all matches at tier      <- the headline
  recall@>=tier = true matches at tier-or-better / total positives

Precision is also broken out PER CLUSTER and per haystack SPLIT (clean / current),
because a blended aggregate hides exactly where matching fails (JIP-2).
"""
from dataclasses import dataclass, field
from typing import Optional

from .match import TIER_A, TIER_A_PLUS, TIER_B, tier_rank

TIERS = [TIER_A, TIER_A_PLUS, TIER_B]


@dataclass(frozen=True)
class Trial:
    query_id: str
    tier: Optional[str]        # best tier achieved (None = no match)
    is_true_match: bool        # was the matched candidate the true origin?
    is_positive: bool          # does this query HAVE a true origin in the pool?
    cluster: str = "default"   # hard-negative cluster / content type
    split: str = "current"     # "clean" or "current" haystack


def _precision(tp: int, fp: int) -> Optional[float]:
    n = tp + fp
    return None if n == 0 else tp / n


@dataclass
class Report:
    trials: int
    positives: int
    per_tier: dict = field(default_factory=dict)        # tier -> {tp,fp,precision,recall_at_or_better}
    per_cluster: dict = field(default_factory=dict)      # cluster -> tier -> precision
    per_split: dict = field(default_factory=dict)        # split -> tier -> precision
    thresholds: dict = field(default_factory=dict)


def evaluate(trials, thresholds: Optional[dict] = None) -> Report:
    positives = sum(1 for t in trials if t.is_positive)

    def tier_pr(subset):
        out = {}
        for tier in TIERS:
            tp = sum(1 for t in subset if t.tier == tier and t.is_true_match)
            fp = sum(1 for t in subset if t.tier == tier and not t.is_true_match)
            atb_tp = sum(1 for t in subset
                         if t.is_true_match and tier_rank(t.tier) >= tier_rank(tier))
            pos = sum(1 for t in subset if t.is_positive)
            out[tier] = {
                "tp": tp, "fp": fp,
                "precision": _precision(tp, fp),
                "recall_at_or_better": (atb_tp / pos) if pos else None,
            }
        return out

    rep = Report(trials=len(trials), positives=positives, thresholds=thresholds or {})
    rep.per_tier = tier_pr(trials)

    clusters = sorted({t.cluster for t in trials})
    for cl in clusters:
        sub = [t for t in trials if t.cluster == cl]
        rep.per_cluster[cl] = {tier: tier_pr(sub)[tier]["precision"] for tier in TIERS}

    for sp in sorted({t.split for t in trials}):
        sub = [t for t in trials if t.split == sp]
        rep.per_split[sp] = {tier: tier_pr(sub)[tier]["precision"] for tier in TIERS}

    return rep


def _fmt_p(p: Optional[float]) -> str:
    return "—" if p is None else f"{p:.4f}"


def to_markdown(rep: Report, title: str = "S1 — exact + recompression-invariance precision") -> str:
    L = [f"# {title}", ""]
    L.append(f"- Trials: **{rep.trials}**  ·  Positives (true near-dups): **{rep.positives}**")
    if rep.thresholds:
        L.append(f"- Thresholds: `{rep.thresholds}`")
    L.append("")
    L.append("## Precision & recall by tier")
    L.append("")
    L.append("| Tier | TP | FP | Precision | Recall @≥tier |")
    L.append("|---|---:|---:|---:|---:|")
    labels = {TIER_A: "A (exact)", TIER_A_PLUS: "A+ (recompress-invariant)", TIER_B: "B (advisory near-dup)"}
    for tier in TIERS:
        d = rep.per_tier[tier]
        rb = d["recall_at_or_better"]
        L.append(f"| {labels[tier]} | {d['tp']} | {d['fp']} | {_fmt_p(d['precision'])} | "
                 f"{'—' if rb is None else f'{rb:.3f}'} |")
    L.append("")
    L.append("## Precision by hard-negative cluster")
    L.append("")
    L.append("| Cluster | A | A+ | B |")
    L.append("|---|---:|---:|---:|")
    for cl, tp in sorted(rep.per_cluster.items()):
        L.append(f"| {cl} | {_fmt_p(tp[TIER_A])} | {_fmt_p(tp[TIER_A_PLUS])} | {_fmt_p(tp[TIER_B])} |")
    L.append("")
    L.append("## Precision by haystack split")
    L.append("")
    L.append("| Split | A | A+ | B |")
    L.append("|---|---:|---:|---:|")
    for sp, tp in sorted(rep.per_split.items()):
        L.append(f"| {sp} | {_fmt_p(tp[TIER_A])} | {_fmt_p(tp[TIER_A_PLUS])} | {_fmt_p(tp[TIER_B])} |")
    L.append("")
    L.append("> Tiers A and A+ are the **provable** persistence tiers and may render as fact of record. "
             "Tier B is **advisory only** (human-reviewed, person-presence-gated) and is not gated by this "
             "number. Persistence surfaces a *labeled prior* for incidentally-degraded near-duplicates — "
             "it is **not** robust to motivated regeneration-laundering (report the adversarial-evasion "
             "rate separately). See JIP-2 / JIP-4.")
    return "\n".join(L)


def to_dict(rep: Report) -> dict:
    return {
        "trials": rep.trials,
        "positives": rep.positives,
        "thresholds": rep.thresholds,
        "per_tier": rep.per_tier,
        "per_cluster": rep.per_cluster,
        "per_split": rep.per_split,
    }
