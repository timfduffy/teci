#!/usr/bin/env python3
"""Cross-family charts.

(1) eci_families.png    — one panel per family, ECI vs release date, points
                          colored by size tier. Faceting by family (rather than
                          coloring by it) keeps the color channel free for the
                          tier, which is what the argument is about, and makes
                          each family's time coverage impossible to miss --
                          SmolLM's twelve entries all land in one quarter, which
                          is why it moves the pooled slope so much.
(2) eci_tier_gap.png    — how the headline number (how many TECI/yr faster the
                          >10B tier improves than the small tier) moves as the
                          sample and the tier definition change.

Palette: reference dataviz palette. Size tier is an ORDERED category, so it uses
the ordinal blue ramp (steps 250/450/650), not categorical hues -- validated with
`validate_palette.js --ordinal`: monotone L, adjacent dL >= 0.06, light end
2.06:1 on the light surface.

Run from data/ (writes PNGs to the working directory, like the other chart
scripts):  cd data && python ../scripts/mk_chart_families.py
"""
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
MUTED, GRID, AXIS = "#898781", "#e1e0d9", "#c3c2b7"

# Our estimates in the units of Epoch's ECI scale; Epoch has not scored these
# models, so the axis must not say "ECI". See mk_chart_qwen.py for the rationale.
TECI_AXIS = "Tim's ECI (TECI)"
TECI_NOTE = ("Tim's ECI: an independent fit of public vendor and leaderboard scores, calibrated to Epoch AI's ECI scale\n"
             "via 204 models Epoch has scored. TECI values are our own estimates, not Epoch's published ECI.")
# ordinal ramp, light -> dark = small -> large
TIER_C = {"≤2B": "#86b6ef", "2–10B": "#2a78d6", ">10B": "#104281"}
TIERS = list(TIER_C)

# A slope needs enough spread in time to mean anything. SmolLM spans four
# months; fitting a per-year rate to that would be noise dressed as a finding.
MIN_N, MIN_SPAN_YRS = 4, 1.0

r = pd.read_csv("results_methods.csv")
r["date"] = pd.to_datetime(r.release.astype(str), format="%Y-%m", errors="coerce")
r = r.dropna(subset=["date", "eci_A", "params_B"]).copy()
r["yrs"] = (r.date - pd.Timestamp("2023-01-01")).dt.days / 365.25
r["tier"] = pd.cut(r.params_B, [0, 2.1, 10, 40], labels=TIERS)

FAMS = ["Qwen", "Gemma", "Llama", "Phi", "SmolLM", "OLMo"]
ORIGIN = {"Qwen", "Gemma"}

# ---------------------------------------------------------------- chart 1
fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.6), facecolor=SURF, sharex=True, sharey=True)
for ax, fam in zip(axes.ravel(), FAMS):
    g = r[r.family == fam]
    ax.set_facecolor(SURF)
    for tier in TIERS:
        s = g[g.tier == tier]
        if not len(s):
            continue
        ax.plot(s.date, s.eci_A, "o", ms=6, color=TIER_C[tier], markeredgecolor=SURF,
                markeredgewidth=1.4, zorder=3, linestyle="none")
        span = s.yrs.max() - s.yrs.min()
        if len(s) >= MIN_N and span >= MIN_SPAN_YRS:
            b, a = np.polyfit(s.yrs, s.eci_A, 1)
            xs = np.array([s.yrs.min(), s.yrs.max()])
            ax.plot(pd.Timestamp("2023-01-01") + pd.to_timedelta(xs * 365.25, "D"),
                    a + b * xs, color=TIER_C[tier], lw=1.6, zorder=2, alpha=.85)
            # stagger by tier so the Qwen >10B and 2-10B labels do not collide
            ax.annotate(f"{b:+.0f}/yr", xy=(s.date.max(), a + b * xs[1]),
                        xytext=(4, {"≤2B": 0, "2–10B": -8, ">10B": 8}[tier]),
                        textcoords="offset points",
                        fontsize=7.5, color=INK2, va="center", zorder=4)
    n_new = "" if fam in ORIGIN else "  · added from OLL"
    ax.set_title(f"{fam}   n={len(g)}{n_new}", color=INK, fontsize=10.5,
                 loc="left", fontweight="bold", pad=6)
    if fam == "SmolLM":
        ax.annotate("all 12 within one quarter —\nno trend fitted",
                    xy=(0.045, 0.055), xycoords="axes fraction", fontsize=7.5,
                    color=MUTED, va="bottom", zorder=4)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.tick_params(colors=MUTED, labelsize=8)
    for s_ in ("top", "right", "left"):
        ax.spines[s_].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(pd.Timestamp("2023-04-01"), pd.Timestamp("2026-10-01"))
    # every panel keeps its year labels: the OLL families stop early, and a
    # reader should not have to look two panels down to place them in time
    ax.tick_params(labelbottom=True)
axes[0, 0].set_ylim(70, 155)
for ax in axes[:, 0]:
    ax.set_ylabel(TECI_AXIS, color=INK2, fontsize=9)

handles = [plt.Line2D([], [], marker="o", ms=6.5, linestyle="none", color=c,
                      markeredgecolor=SURF, markeredgewidth=1.4, label=t)
           for t, c in TIER_C.items()]
fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.995, 0.978),
           ncol=3, fontsize=8.5, frameon=False, labelcolor=INK2,
           title="parameter size", title_fontsize=8.5)
fig.suptitle("Small-model progress by family, on the TECI scale",
             color=INK, fontsize=13.5, x=0.012, ha="left", fontweight="bold", y=0.985)
fig.text(0.012, 0.932,
         "Trend lines fitted only where a tier has ≥4 entries spanning ≥1 year. "
         "The four families added from the Open LLM Leaderboard stop at 2025-03, when it froze.",
         color=INK2, fontsize=9)
fig.text(0.012, 0.008, TECI_NOTE, color=MUTED, fontsize=7.5, va="bottom")
fig.tight_layout(rect=(0, 0.052, 1, 0.918))
fig.savefig("eci_families.png", dpi=170, facecolor=SURF)

# ---------------------------------------------------------------- chart 2
def gap(d, lo=0.0):
    sm = d[(d.params_B <= 2.1) & (d.params_B >= lo)]
    lg = d[d.params_B > 10]
    return np.polyfit(lg.yrs, lg.eci_A, 1)[0] - np.polyfit(sm.yrs, sm.eci_A, 1)[0], len(sm)

qg = r[r.family.isin(ORIGIN)]
# The first row is the pre-cross-family fit, which this script cannot recompute:
# it is the value from the "Fix two mis-specified bridge nodes" commit (5b74cd6).
STEPS = [("Qwen/Gemma only, previous fit", 3.30, 25),
         ("same entries, recalibrated instruments", *gap(qg)),
         ("+ cross-family models ≥0.5B", *gap(r, 0.5)),
         ("+ SmolLM's sub-0.5B models", *gap(r))]

fig2, ax = plt.subplots(figsize=(10.2, 3.9), facecolor=SURF)
ax.set_facecolor(SURF)
ys = np.arange(len(STEPS))[::-1]
vals = [s[1] for s in STEPS]
ax.hlines(ys, 0, vals, color="#2a78d6", lw=2.4, zorder=2)
ax.plot(vals, ys, "o", ms=9, color="#2a78d6", markeredgecolor=SURF,
        markeredgewidth=1.6, linestyle="none", zorder=3)
for y, (_, v, _) in zip(ys, STEPS):
    ax.annotate(f"{v:.2f}", xy=(v, y), xytext=(11, 0), textcoords="offset points",
                fontsize=11, color=INK, va="center", fontweight="bold")
ax.set_yticks(ys)
# the sample size rides in the row label, so nothing trails off the right edge
ax.set_yticklabels([f"{lbl}\nsmall tier n={n}" for lbl, _, n in STEPS],
                   fontsize=9.5, color=INK2)
ax.set_ylim(-0.6, len(STEPS) - 0.4)
ax.set_xlim(0, 3.9)
ax.set_xlabel("gap in TECI/yr  (how much faster the >10B tier improves than the small tier)",
              color=INK2, fontsize=9)
ax.grid(axis="x", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.tick_params(colors=MUTED, labelsize=8.5)
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
ax.spines["bottom"].set_color(AXIS)
fig2.suptitle("The size gap shrinks once the low end is not calibrated by two vendors",
              color=INK, fontsize=12.5, x=0.012, ha="left", fontweight="bold", y=0.975)
fig2.text(0.012, 0.885,
          "Each row adds one change to the row above. The project's question names the 0.5–2B tier, "
          "so the third row is the comparable estimate.",
          color=INK2, fontsize=8.8)
fig2.tight_layout(rect=(0, 0, 1, 0.86))
fig2.savefig("eci_tier_gap.png", dpi=170, facecolor=SURF)

# ---- table-view twin (relief for the sub-3:1 palette steps, and the numbers) --
rows = ["# Tier trends (method A)", "", "| family | tier | n | span (yrs) | slope TECI/yr | mean TECI |",
        "|---|---|---:|---:|---:|---:|"]
for fam in FAMS:
    for tier in TIERS:
        s = r[(r.family == fam) & (r.tier == tier)]
        if not len(s):
            continue
        span = s.yrs.max() - s.yrs.min()
        sl = (f"{np.polyfit(s.yrs, s.eci_A, 1)[0]:+.2f}"
              if len(s) >= MIN_N and span >= MIN_SPAN_YRS else "—")
        rows.append(f"| {fam} | {tier} | {len(s)} | {span:.2f} | {sl} | {s.eci_A.mean():.1f} |")
rows += ["", "## Size-gap estimate under each sample / tier definition", "",
         "| definition | small-tier n | gap (TECI/yr) |", "|---|---:|---:|"]
rows += [f"| {lbl} | {n} | {v:.2f} |" for lbl, v, n in STEPS]
open("../docs/tier_trends.md", "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("saved eci_families.png, eci_tier_gap.png, docs/tier_trends.md")
