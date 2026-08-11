#!/usr/bin/env python3
"""Sensitivity pass over the flagged instrument-identity assumptions.

docs/connectivity_audit.md grades every curated merge [HIGH] (confident) or
[FLAG] (uncertain). Each [FLAG] is a judgment call that could be wrong: if two
vendor rows we treat as one instrument are really two tests of different
difficulty, the fitted difficulty and every entry scored on it are distorted.

This re-runs method A with each flagged assumption reversed and reports how far
the answer moves -- both per entry and, more importantly, for the headline
claim (how much faster the >10B tier improves than the <=2B tier). An
assumption that moves nothing is one you can stop worrying about; one that
moves the conclusion needs resolving from source documents before publication.

Run from data/:   cd data && python ../scripts/sensitivity.py
Writes ../docs/sensitivity.md. Method A only, no bootstrap -- point estimates
are what matter here, and it keeps a 10-variant sweep to about a minute.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fitlib
from fitlib import affine_from_pairs, fit_raw

OUT = Path(__file__).resolve().parent.parent / "docs" / "sensitivity.md"

BRIDGE = {
    "Gemma 2B": "Gemma 2B [Pretrained (PT)]",
    "Gemma 7B": "Gemma 7B [Pretrained (PT)]",
    "Gemma 2 9B": "Gemma 2 9B [Pretrained (PT)]",
    "Gemma 2 27B": "Gemma 2 27B [Pretrained (PT)]",
    "Gemma 3 27B": "Gemma 3 27B IT [Instruction-tuned (IT)]",
    "Gemma 4 31B IT": "Gemma 4 31B [IT, Thinking mode]",
    "Qwen 3.6 35B-A3B": "Qwen3.6-35B-A3B [Thinking (default)]",
    "Qwen 3.5 Flash (hosted 35B-A3B)": "Qwen3.5-35B-A3B [Thinking (default)]",
}

ours = pd.read_csv("obs_ours.csv")
pub = pd.read_csv("eci_published.csv").set_index("model")["eci"].to_dict()
epoch_sub = pd.read_csv("eci_benchmarks.csv")


def run_method_a(obs):
    """Method A exactly as in fit_methods.py, minus the bootstrap."""
    fitlib.RNG = np.random.default_rng(42)  # identical start across variants
    ep = epoch_sub[["model", "benchmark", "performance"]].rename(columns={"model": "entry"}).copy()
    ep["entry"] = ep["entry"].map(lambda m: BRIDGE.get(m, "EPOCH::" + m))
    join = pd.concat([obs[["entry", "benchmark", "performance"]], ep], ignore_index=True)
    join = join.groupby(["entry", "benchmark"], as_index=False).performance.max()
    caps, _, _, _, _ = fit_raw(join, "Winogrande")
    pure = [m for m in join.entry.unique() if m.startswith("EPOCH::") and m[7:] in pub]
    a, b, _ = affine_from_pairs(caps, {("EPOCH::" + k): v for k, v in pub.items()}, pure)
    return {m: a + b * c for m, c in caps.items() if not m.startswith("EPOCH::")}


# ---------------------------------------------------------------- variants
def split(benchmark, gens, label):
    """Break `gens` out of `benchmark` into their own instrument."""
    def f(o):
        o = o.copy()
        m = (o.benchmark == benchmark) & (o.generation.isin(gens))
        o.loc[m, "benchmark"] = f"{benchmark} [{label}]"
        return o
    return f


def merge(a, b):
    """Treat two instruments we currently keep separate as one."""
    def f(o):
        o = o.copy()
        o.loc[o.benchmark == b, "benchmark"] = a
        return o
    return f


VARIANTS = [
    ("gpqa-split", "Qwen2/2.5 'GPQA' may not be Diamond -> separate instrument",
     split("GPQA diamond", ["Qwen2", "Qwen2.5"], "Qwen2/2.5 unverified")),
    ("hmmt-split", "Qwen 2507 'HMMT25' may not be the Feb'25 set -> separate",
     split("Qwen::HMMT Feb'25", ["Qwen3-2507"], "2507")),
    ("livebench-split", "Qwen3 report's LiveBench release date unconfirmed -> separate",
     split("LiveBench-20241125", ["Qwen3"], "Qwen3 unconfirmed")),
    ("arenahard-split", "Arena-Hard version may differ across Qwen2.5/3 -> separate",
     split("Qwen::Arena-Hard", ["Qwen3"], "Qwen3")),
    ("gemma-hellaswag-split", "Gemma 1 0-shot vs Gemma 2/3 10-shot",
     split("HellaSwag", ["Gemma 1"], "Gemma1 0-shot")),
    ("gemma-winogrande-split", "scoring scheme differs Gemma 1/2 vs Gemma 3",
     split("Winogrande", ["Gemma 1", "Gemma 2"], "Gemma1/2")),
    ("gemma-arcc-split", "Gemma 1 ARC-c config unstated vs Gemma 2/3 25-shot",
     split("ARC AI2", ["Gemma 1"], "Gemma1 unstated")),
    ("gemma-gsm8k-split", "GSM8K (PT) shot counts differ across Gemma generations",
     split("GSM8K", ["Gemma 1"], "Gemma1")),
    ("qwen-gsm8k-split", "Qwen v1 8-shot GSM8K vs later unstated",
     split("GSM8K", ["Qwen (v1)"], "Qwen-v1 8-shot")),
    ("qwen-mmlu-split", "Qwen v1 explicitly 5-shot MMLU; Qwen2 unstated",
     split("MMLU", ["Qwen (v1)"], "Qwen-v1 5-shot")),
    ("lcb-v6-merge", "opposite direction: treat Qwen 3.5/3.6 'v6' as the 2507 window",
     merge("Qwen::LCB v6 (2507)", "Qwen::LCB v6 (late)")),
]


# ---------------------------------------------------------------- trend metric
meta = ours.groupby("entry").agg(params=("params", "first"), release=("release", "first"))
meta["rel"] = pd.to_datetime(meta.release, errors="coerce")
meta["yrs"] = (meta.rel - pd.Timestamp("2023-01-01")).dt.days / 365.25


def tier_gap(eci):
    """ECI/yr advantage of the >10B tier over the <=2B tier."""
    d = meta.dropna(subset=["rel"]).copy()
    d["eci"] = pd.Series(eci)
    d = d.dropna(subset=["eci", "params"])
    small = d[d.params <= 2.1]; large = d[d.params > 10]
    if len(small) < 3 or len(large) < 3:
        return np.nan
    return np.polyfit(large.yrs, large.eci, 1)[0] - np.polyfit(small.yrs, small.eci, 1)[0]


base = run_method_a(ours)
base_gap = tier_gap(base)
print(f"baseline: {len(base)} entries, tier gap {base_gap:.2f} ECI/yr\n")

rows = []
for name, desc, fn in VARIANTS:
    obs = fn(ours)
    n_moved = int((obs.benchmark != ours.benchmark).sum())
    if n_moved == 0:
        print(f"  {name}: NO ROWS MATCHED -- check the generation labels")
        continue
    eci = run_method_a(obs)
    common = [e for e in base if e in eci]
    d = np.array([eci[e] - base[e] for e in common])
    worst = max(common, key=lambda e: abs(eci[e] - base[e]))
    gap = tier_gap(eci)
    rows.append({"variant": name, "what": desc, "obs_moved": n_moved,
                 "mean_abs": np.abs(d).mean(), "max_abs": np.abs(d).max(),
                 "worst_entry": worst, "worst_delta": eci[worst] - base[worst],
                 "tier_gap": gap, "gap_delta": gap - base_gap})
    print(f"  {name:24s} {n_moved:3d} obs moved  mean|d| {np.abs(d).mean():5.2f}  "
          f"max|d| {np.abs(d).max():5.2f}  gap {gap:5.2f} ({gap - base_gap:+.2f})")

res = pd.DataFrame(rows).sort_values("max_abs", ascending=False)

lines = [
    "# Sensitivity pass — flagged instrument-identity assumptions",
    "",
    "Method A refit with each flagged merge from `docs/connectivity_audit.md`",
    "reversed. `mean|d|` / `max|d|` are shifts in fitted ECI across our entries;",
    "`tier gap` is the headline quantity — how many ECI/yr faster the >10B tier",
    f"improves than the <=2B tier (baseline **{base_gap:.2f}**). A variant that barely",
    "moves the gap is an assumption the conclusion does not rest on.",
    "",
    "| variant | obs moved | mean\\|d\\| | max\\|d\\| | worst-moved entry | tier gap | gap shift |",
    "|---|---:|---:|---:|---|---:|---:|",
]
for r in res.itertuples():
    lines.append(f"| `{r.variant}` | {r.obs_moved} | {r.mean_abs:.2f} | {r.max_abs:.2f} | "
                 f"{r.worst_entry} ({r.worst_delta:+.1f}) | {r.tier_gap:.2f} | {r.gap_delta:+.2f} |")
lines += ["", "## What each variant tests", ""]
for r in res.itertuples():
    lines.append(f"- **`{r.variant}`** — {r.what}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nbaseline tier gap: {base_gap:.2f} ECI/yr")
print(f"largest gap shift: {res.gap_delta.abs().max():.2f} ECI/yr ({res.loc[res.gap_delta.abs().idxmax(), 'variant']})")
print(f"wrote {OUT}")
