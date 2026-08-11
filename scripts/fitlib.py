#!/usr/bin/env python3
"""Shared IRT fitting routines.

Extracted verbatim from fit_methods.py so that sensitivity.py can reuse the
exact same estimator rather than keeping a second copy of it. Model spec mirrors
eci-public/src/eci/fitting.py: performance = sigmoid(slope*(cap-diff)), ridge
0.1, clip 1e-3, bounds, trf least squares, anchor benchmark slope pinned to 1.
"""
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.sparse import coo_matrix

RNG = np.random.default_rng(42)
CLIP = 1e-3
REG = 0.1

# Epoch node -> our entry. Bridged on Epoch's `model_version` column, NOT on the
# display name: Epoch's names silently drop the base/instruct distinction that
# our entry convention depends on. 14 of their 222 nodes mix base and instruct
# observations under one name, and instruction tuning is worth a median +11 ECI
# in our own fit, so a mismatch here is worth several points.
#   Gemma 2 27B  -> Epoch's node is purely gemma-2-27b-it, so it maps to our IT
#                   entry despite the unqualified display name.
#   Gemma 2 9B   -> genuinely pooled, but instruct-dominant (4 of 6 obs:
#                   GPQA/MATH/AIME/MMLU vs base PIQA/GSM8K), so likewise IT.
BRIDGE = {
    "Gemma 2B": "Gemma 2B [Pretrained (PT)]",
    "Gemma 7B": "Gemma 7B [Pretrained (PT)]",
    "Gemma 2 9B": "Gemma 2 9B IT [Instruction-tuned (IT)]",
    "Gemma 2 27B": "Gemma 2 27B IT [Instruction-tuned (IT)]",
    "Gemma 3 27B": "Gemma 3 27B IT [Instruction-tuned (IT)]",
    "Gemma 4 31B IT": "Gemma 4 31B [IT, Thinking mode]",
    "Qwen 3.6 35B-A3B": "Qwen3.6-35B-A3B [Thinking (default)]",
    "Qwen 3.5 Flash (hosted 35B-A3B)": "Qwen3.5-35B-A3B [Thinking (default)]",
}


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


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
