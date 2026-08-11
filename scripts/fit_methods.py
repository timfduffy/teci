#!/usr/bin/env python3
"""Fit ECI-style capability scores for our Qwen/Gemma entries via three methods.

A: joint refit  — our obs + full Epoch matrix (222 models), bridge nodes
                  merged; rescaled to ECI units by regressing the pure-Epoch
                  models' fitted capabilities on their published ECI.
B: frozen graft — Epoch's published EDI/slope held fixed (ECI units); our
                  entries scored on overlapping instruments; own instruments'
                  (edi, slope) then estimated; alternated.
C: standalone   — fit our obs alone; affine-map to ECI via the 8 bridge
                  entries' published ECI values.

Model spec mirrors eci-public/src/eci/fitting.py: performance =
sigmoid(slope*(cap-diff)), ridge 0.1, clip 1e-3, bounds, trf least squares,
anchor benchmark slope pinned to 1 (raw scale).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares, minimize_scalar

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fitlib import BRIDGE, CLIP, affine_from_pairs, bootstrap_caps, fit_raw, sigmoid

# ---------------------------------------------------------------- load data
ours = pd.read_csv("obs_ours.csv")
pub = pd.read_csv("eci_published.csv").set_index("model")["eci"].to_dict()
frozen = pd.read_csv("edi_frozen.csv").set_index("benchmark")
epoch_sub = pd.read_csv("eci_benchmarks.csv")

BRIDGE_INV = {v: k for k, v in BRIDGE.items()}

# ================================================================ METHOD A
ep = epoch_sub[["model", "benchmark", "performance"]].rename(columns={"model": "entry"}).copy()
ep["entry"] = ep["entry"].map(lambda m: BRIDGE.get(m, "EPOCH::" + m))
ours_a = ours[["entry", "benchmark", "performance"]].copy()
join = pd.concat([ours_a, ep], ignore_index=True)
join = join.groupby(["entry", "benchmark"], as_index=False).performance.max()
caps_a, _, _, xhat_a, _ = fit_raw(join, "Winogrande")
pure = [m for m in join.entry.unique() if m.startswith("EPOCH::") and m[7:] in pub]
a_a, b_a, r_a = affine_from_pairs(caps_a, {("EPOCH::" + k): v for k, v in pub.items()}, pure)
eci_a = {m: a_a + b_a * c for m, c in caps_a.items()}
bs_a = bootstrap_caps(join, "Winogrande", xhat_a, n=100)
ci_a = {m: (a_a + b_a * np.quantile(v, .05), a_a + b_a * np.quantile(v, .95)) if len(v) > 10 else (np.nan, np.nan)
        for m, v in bs_a.items()}
print(f"[A] joint fit: {join.entry.nunique()} nodes, {join.benchmark.nunique()} instruments, "
      f"{len(join)} obs; rescale on {len(pure)} pure-Epoch models, r={r_a:.4f}")

# ================================================================ METHOD C
caps_c, _, _, xhat_c, _ = fit_raw(ours[["entry", "benchmark", "performance"]], "MMLU")
bridge_here = [e for e in BRIDGE_INV if e in caps_c and BRIDGE_INV[e] in pub]
a_c, b_c, r_c = affine_from_pairs(caps_c, {e: pub[BRIDGE_INV[e]] for e in bridge_here}, bridge_here)
eci_c = {m: a_c + b_c * c for m, c in caps_c.items()}
bs_c = bootstrap_caps(ours[["entry", "benchmark", "performance"]], "MMLU", xhat_c, n=100)
ci_c = {m: (a_c + b_c * np.quantile(v, .05), a_c + b_c * np.quantile(v, .95)) if len(v) > 10 else (np.nan, np.nan)
        for m, v in bs_c.items()}
print(f"[C] standalone: bridge models used: {len(bridge_here)}, r={r_c:.4f}, map eci={a_c:.1f}+{b_c:.3f}*cap")

# ================================================================ METHOD B
epoch_obs = ours[ours.scope == "epoch"]
own_obs = ours[ours.scope == "own"]

def fit_entry_eci(rows, inst_params):
    """1-D least squares for one entry's eci given instrument params."""
    ed = np.array([inst_params[b][0] for b in rows.benchmark])
    sl = np.array([inst_params[b][1] for b in rows.benchmark])
    y = rows.performance.clip(CLIP, 1 - CLIP).values
    def loss(e): return np.sum((sigmoid(sl * (e - ed)) - y) ** 2)
    res = minimize_scalar(loss, bounds=(30, 200), method="bounded")
    return res.x

inst = {b: (frozen.loc[b, "edi"], frozen.loc[b, "slope"]) for b in frozen.index}
# stage 1: entries with epoch obs
eci_b = {}
for e, g in epoch_obs.groupby("entry"):
    eci_b[e] = fit_entry_eci(g, inst)

SLOPE_MED = 0.09
for it in range(3):
    # stage 2: estimate own instruments from current eci_b
    own_params = {}
    for b, g in own_obs.groupby("benchmark"):
        g = g[g.entry.isin(eci_b)]
        if len(g) == 0: continue
        e = np.array([eci_b[x] for x in g.entry])
        y = g.performance.clip(CLIP, 1 - CLIP).values
        if len(g) < 3 or (e.max() - e.min()) < 5:
            # slope prior; fit edi only
            def loss_d(d): return np.sum((sigmoid(SLOPE_MED * (e - d)) - y) ** 2)
            d = minimize_scalar(loss_d, bounds=(30, 220), method="bounded").x
            own_params[b] = (d, SLOPE_MED)
        else:
            def resid(p): return sigmoid(p[1] * (e - p[0])) - y
            r = least_squares(resid, [np.median(e) + 5, 0.1],
                              bounds=([30, 0.005], [220, 0.8]), method="trf")
            own_params[b] = (r.x[0], r.x[1])
    inst_all = {**inst, **own_params}
    # stage 3: refit every entry on all covered instruments
    new_eci = {}
    for e, g in ours.groupby("entry"):
        g = g[g.benchmark.isin(inst_all)]
        if len(g) == 0: continue
        new_eci[e] = fit_entry_eci(g, inst_all)
    eci_b = new_eci

# bootstrap B (conditional on instrument params)
ci_b = {}
for e, g in ours.groupby("entry"):
    g = g[g.benchmark.isin(inst_all)]
    if len(g) == 0: continue
    vals = []
    for k in range(200):
        samp = g.sample(len(g), replace=True, random_state=5000 + k)
        vals.append(fit_entry_eci(samp, inst_all))
    ci_b[e] = (np.quantile(vals, .05), np.quantile(vals, .95))
print(f"[B] frozen graft: {len(eci_b)} entries scored; {len(own_params)} own instruments estimated")

# ================================================================ OUTPUT
meta = ours.groupby("entry").agg(family=("family", "first"), generation=("generation", "first"),
                                 params=("params", "first"), release=("release", "first"),
                                 n_obs=("performance", "size")).reset_index().set_index("entry")
rows = []
for e in sorted(set(ours.entry)):
    m = meta.loc[e]
    pubv = pub.get(BRIDGE_INV.get(e, ""), np.nan)
    rows.append({
        "entry": e, "family": m.family, "generation": m.generation, "params_B": m.params,
        "release": m.release, "n_obs": m.n_obs,
        "eci_A": eci_a.get(e, np.nan), "eci_A_lo": ci_a.get(e, (np.nan,)*2)[0], "eci_A_hi": ci_a.get(e, (np.nan,)*2)[1],
        "eci_B": eci_b.get(e, np.nan), "eci_B_lo": ci_b.get(e, (np.nan,)*2)[0], "eci_B_hi": ci_b.get(e, (np.nan,)*2)[1],
        "eci_C": eci_c.get(e, np.nan), "eci_C_lo": ci_c.get(e, (np.nan,)*2)[0], "eci_C_hi": ci_c.get(e, (np.nan,)*2)[1],
        "eci_published": pubv,
    })
res = pd.DataFrame(rows)
res.to_csv("results_methods.csv", index=False)

# agreement + validation
v = res.dropna(subset=["eci_A", "eci_B", "eci_C"])
print("\nAgreement (n=%d): r(A,B)=%.3f r(A,C)=%.3f r(B,C)=%.3f" % (
    len(v), np.corrcoef(v.eci_A, v.eci_B)[0, 1], np.corrcoef(v.eci_A, v.eci_C)[0, 1],
    np.corrcoef(v.eci_B, v.eci_C)[0, 1]))
print("Mean abs diff: |A-B|=%.2f |A-C|=%.2f |B-C|=%.2f" % (
    (v.eci_A - v.eci_B).abs().mean(), (v.eci_A - v.eci_C).abs().mean(), (v.eci_B - v.eci_C).abs().mean()))
print("\nValidation vs published ECI (bridge models):")
bv = res.dropna(subset=["eci_published"])
print(bv[["entry", "eci_A", "eci_B", "eci_C", "eci_published"]].round(1).to_string(index=False))
