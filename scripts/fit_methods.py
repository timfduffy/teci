#!/usr/bin/env python3
"""Fit ECI-style capability scores for our Qwen/Gemma entries via three methods.

A: joint refit  — our obs + reconstructed Epoch subset (31 models), bridge nodes
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
import numpy as np
import pandas as pd
from scipy.optimize import least_squares, minimize_scalar
from scipy.sparse import coo_matrix

RNG = np.random.default_rng(42)
CLIP = 1e-3
REG = 0.1

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

# ---------------------------------------------------------------- raw IRT fit
def fit_raw(obs, anchor_benchmark, x0=None):
    """obs: DataFrame with entry, benchmark, performance. Returns dicts."""
    models = obs.entry.unique(); benches = obs.benchmark.unique()
    n_m, n_b = len(models), len(benches)
    m_idx = {m: i for i, m in enumerate(models)}
    b_idx = {b: i for i, b in enumerate(benches)}
    mi = obs.entry.map(m_idx).values
    bi = obs.benchmark.map(b_idx).values
    perf = obs.performance.clip(CLIP, 1 - CLIP).values
    a_idx = b_idx[anchor_benchmark]
    n_params = n_m + n_b + (n_b - 1)

    def unpack(p):
        cap = p[:n_m]; diff = p[n_m:n_m + n_b]
        disc = np.insert(p[n_m + n_b:], a_idx, 1.0)
        return cap, diff, disc

    def resid(p):
        cap, diff, disc = unpack(p)
        r = sigmoid(disc[bi] * (cap[mi] - diff[bi])) - perf
        pen = REG * np.sum(p ** 2) / n_params
        return np.append(r, np.sqrt(pen))

    def jac(p):
        cap, diff, disc = unpack(p)
        s = sigmoid(disc[bi] * (cap[mi] - diff[bi])); ds = s * (1 - s)
        n_obs = len(mi); orows = np.arange(n_obs)
        free = bi != a_idx
        dcols = n_m + n_b + np.where(bi < a_idx, bi, bi - 1)
        rows = [orows, orows, orows[free]]
        cols = [mi, n_m + bi, dcols[free]]
        vals = [ds * disc[bi], -ds * disc[bi], (ds * (cap[mi] - diff[bi]))[free]]
        pen = REG * np.sum(p ** 2) / n_params
        nr = n_obs
        if pen > 0:
            nr += 1
            scale = REG / (n_params * np.sqrt(pen))
            rows.append(np.full(n_params, n_obs)); cols.append(np.arange(n_params))
            vals.append(scale * p)
        return coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                          shape=(nr, n_params)).tocsr()

    lower = np.concatenate([np.full(n_m, -10.), np.full(n_b, -10.), np.full(n_b - 1, 0.1)])
    upper = np.concatenate([np.full(n_m, 10.), np.full(n_b, 10.), np.full(n_b - 1, 10.)])
    if x0 is None:
        x0 = np.concatenate([RNG.normal(0, .1, n_m), RNG.normal(0, .1, n_b), np.full(n_b - 1, 1.)])
    res = least_squares(resid, x0, jac=jac, bounds=(lower, upper), method="trf")
    if not res.success:
        raise RuntimeError(res.message)
    cap, diff, disc = unpack(res.x)
    return ({m: cap[i] for m, i in m_idx.items()},
            {b: diff[i] for b, i in b_idx.items()},
            {b: disc[i] for b, i in b_idx.items()}, res.x, (mi, bi, perf, m_idx, b_idx))

def affine_from_pairs(caps, published, names):
    x = np.array([caps[n] for n in names]); y = np.array([published[n] for n in names])
    b, a = np.polyfit(x, y, 1)
    return a, b, np.corrcoef(x, y)[0, 1]

def bootstrap_caps(obs, anchor_benchmark, x_hat, n=100):
    """Their exact scheme: keep the parameter vector/index maps fixed and
    resample row indices within each model (fitting.py lines 302-315)."""
    models = obs.entry.unique(); benches = obs.benchmark.unique()
    m_idx = {m: i for i, m in enumerate(models)}
    b_idx = {b: i for i, b in enumerate(benches)}
    mi = obs.entry.map(m_idx).values
    bi = obs.benchmark.map(b_idx).values
    perf = obs.performance.clip(CLIP, 1 - CLIP).values
    rows_by_model = [np.flatnonzero(mi == m) for m in range(len(models))]
    rng = np.random.default_rng(12345)
    out = {m: [] for m in models}
    for k in range(n):
        idx = np.concatenate([rng.choice(r, size=r.size, replace=True) for r in rows_by_model])
        samp = pd.DataFrame({"entry": obs.entry.values[idx], "benchmark": obs.benchmark.values[idx],
                             "performance": obs.performance.values[idx]})
        try:
            caps, _, _, _, _ = fit_raw(samp, anchor_benchmark,
                                       x0=None if samp.benchmark.nunique() != len(benches) else x_hat)
            for m, v in caps.items(): out[m].append(v)
        except (RuntimeError, KeyError):
            continue
    return out

# ---------------------------------------------------------------- load data
ours = pd.read_csv("obs_ours.csv")
pub = pd.read_csv("eci_published.csv").set_index("model")["eci"].to_dict()
frozen = pd.read_csv("edi_frozen.csv").set_index("benchmark")
epoch_sub = pd.read_csv("eci_benchmarks_reconstructed.csv")

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
