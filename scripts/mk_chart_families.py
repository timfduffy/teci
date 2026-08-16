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
(3) eci_all_models.png  — every entry on one panel, coloured by parameter count
                          in five bands. Finer banding than the tiers used
                          elsewhere, deliberately: the slopes come out near
                          parallel, which is the point.
(3b) eci_all_models_one_per_model.png — the same chart with one entry per model
                          (thinking over non-thinking, instruct over base), 87
                          of 123. Kept alongside rather than replacing (3): the
                          filter is defensible but it reverses the band ordering,
                          and the pair is the honest way to show how much the
                          rate comparison depends on which entries you count.
(4) eci_small_models.png — the <=2B tier alone, every entry named, against
                          release date. No trend line. One entry per model,
                          preferring what a user would reach for: thinking over
                          non-thinking, instruct over base. That takes 42 rows to
                          26 and lets every label lose its mode suffix, which is
                          most of what makes the chart legible. Labels are then
                          placed by rectangle-overlap search rather than
                          per-release-month nudging: a label is wider than the
                          gap between neighbouring releases, so grouping by month
                          cannot see the collisions that actually happen.

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

# Our estimates in the units of Epoch's ECI scale, so the axis must not say
# plain "ECI". Note Epoch HAS scored 18 of these 123 entries (the bridge nodes);
# the true claim is that the plotted number is ours, not theirs. Rationale and
# naming convention in mk_chart_qwen.py.
TECI_AXIS = "Tim's ECI (TECI)"
TECI_NOTE = ("Tim's ECI: an independent fit of public vendor and leaderboard scores, calibrated to Epoch AI's ECI scale via\n"
             "204 models Epoch has scored. TECI values are our (Tim and Claude's) own estimates, not Epoch's published ECI.")
# ordinal ramp, light -> dark = small -> large
TIER_C = {"≤2B": "#86b6ef", "2–10B": "#2a78d6", ">10B": "#104281"}
TIERS = list(TIER_C)

# A slope needs enough spread in time to mean anything. SmolLM spans four
# months; fitting a per-year rate to that would be noise dressed as a finding.
MIN_N, MIN_SPAN_YRS = 4, 1.0


def one_per_model(df):
    """Keep the entry a user would reach for: thinking over non-thinking,
    instruct over base. Our entry convention deliberately splits those, which is
    right for fitting but double-counts a model when you plot or fit a trend.

    Instruct/base pairs are matched by name prefix, an instruct release being the
    base name plus a suffix (" IT", "-Chat", "-Instruct"). Models with no
    instruct release (phi-1, phi-1_5, OLMo-1B-hf) are kept as they are.
    """
    df = df.copy()
    df["model"] = df.entry.str.partition(" [")[0]
    v = df.entry.str.partition(" [")[2].str.rstrip("]")
    think = v.str.contains("Thinking") & ~v.str.contains("Non-thinking")
    nonthink = v.str.contains("Non-thinking")
    df = df[~(nonthink & df.model.isin(set(df[think].model)))]

    v = df.entry.str.partition(" [")[2].str.rstrip("]")
    base = v.str.startswith("Pretrained") | v.str.startswith("Base (")
    inst = list(df[v.str.startswith("Instruct")].model)
    paired = {m for m in df[base].model if any(i != m and i.startswith(m) for i in inst)}
    return df[~(base & df.model.isin(paired))]

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

# ---------------------------------------------------------------- chart 3
# Every entry on one panel. Size is the question, so it takes the colour channel
# (five ordinal steps, validated with --ordinal); family is not encoded at all --
# with six families no categorical scheme clears the all-pairs gate, and the
# per-family view already exists as chart 1. Finer banding than the <=2B/2-10B/
# >10B cut used elsewhere, deliberately: it shows how much the "small models lag"
# result depends on where the tier boundary is drawn.
BANDS = ["<1B", "1–2B", "2–5B", "5–15B", "15–35B"]
BAND_C = dict(zip(BANDS, ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]))
r["band"] = pd.cut(r.params_B, [0, 1, 2.1, 5, 15, 40], labels=BANDS)


def all_models_chart(data, fname, headline, note):
    fig3, ax = plt.subplots(figsize=(11.5, 6.6), facecolor=SURF)
    ax.set_facecolor(SURF)
    for b in BANDS:
        s = data[data.band == b]
        if not len(s):
            continue
        ax.plot(s.date, s.eci_A, "o", ms=5, color=BAND_C[b], markeredgecolor=SURF,
                markeredgewidth=1.1, linestyle="none", zorder=3, label=f"{b}  (n={len(s)})")
        span = s.yrs.max() - s.yrs.min()
        if len(s) >= MIN_N and span >= MIN_SPAN_YRS:
            m, c = np.polyfit(s.yrs, s.eci_A, 1)
            xs = np.array([s.yrs.min(), s.yrs.max()])
            ax.plot(pd.Timestamp("2023-01-01") + pd.to_timedelta(xs * 365.25, "D"),
                    c + m * xs, color=BAND_C[b], lw=1.8, zorder=2, alpha=.9)
            # the two largest bands finish close together and their labels
            # overlap; nudge them apart vertically
            ax.annotate(f"{b}  {m:+.1f}/yr", xy=(s.date.max(), c + m * xs[1]),
                        xytext=(6, {"5–15B": -9, "15–35B": 9}.get(b, 0)),
                        textcoords="offset points", fontsize=8,
                        color=BAND_C[b], va="center", fontweight="bold", zorder=4)
    ax.set_ylabel(TECI_AXIS, color=INK2, fontsize=10)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    for s_ in ("top", "right", "left"):
        ax.spines[s_].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(pd.Timestamp("2023-05-01"), pd.Timestamp("2026-12-01"))
    ax.set_ylim(r.eci_A.min() - 4, r.eci_A.max() + 4)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False, labelcolor=INK2,
              title="parameters", title_fontsize=8.5)
    fig3.suptitle(headline, color=INK, fontsize=13, x=0.012, ha="left",
                  fontweight="bold", y=0.975)
    fig3.text(0.012, 0.905, note, color=INK2, fontsize=8.8, va="top")
    fig3.text(0.012, 0.012, TECI_NOTE, color=MUTED, fontsize=7.5, va="bottom")
    fig3.tight_layout(rect=(0, 0.055, 1, 0.87))
    fig3.savefig(fname, dpi=170, facecolor=SURF)


all_models_chart(
    r, "eci_all_models.png",
    f"All {len(r)} entries: TECI against release date, by parameter count",
    "Six families (Qwen, Gemma, Llama, Phi, SmolLM, OLMo). Every entry, so a model with base, "
    "instruct and thinking\nreleases appears three times. Under this banding every size advances "
    "at a similar rate.")

# Same chart, one entry per model. Worth having both: the filter is defensible
# but it moves the slopes a lot, and the two side by side are the honest way to
# show how much the rate comparison depends on which entries you count.
rd = one_per_model(r)
all_models_chart(
    rd, "eci_all_models_one_per_model.png",
    f"One entry per model ({len(rd)} of {len(r)} entries): TECI against release date",
    "Thinking preferred over non-thinking, instruct over base. Removing the duplicates reverses "
    "the ordering:\nthe two smallest bands become the fastest and 15–35B the slowest — compare "
    "eci_all_models.png.")

# ---------------------------------------------------------------- chart 4
# The <=2B tier alone, every entry named. No trend line: with 42 points across
# six families and a lopsided release calendar, a fitted line here would imply
# more than the data supports (see the banding note in docs/tier_trends.md).
SMALL_BANDS = ["<0.5B", "0.5–1B", "1–2B"]
SMALL_C = dict(zip(SMALL_BANDS, ["#86b6ef", "#2a78d6", "#104281"]))


def short(entry):
    """'Qwen3-0.6B [Thinking mode]' -> 'Qwen3-0.6B'.

    No "(think)" suffix: where a model has both modes only the thinking entry is
    plotted, so the distinction never needs spelling out. "(base)" stays --
    Qwen1.5-1.8B and Qwen1.5-1.8B-Chat are both on the chart.
    """
    name, _, variant = entry.partition(" [")
    name = name.replace("-Instruct", "-Inst")
    return name + " (base)" if variant.startswith("Base (") else name


def stack(vals, gap):
    """Nudge overlapping label positions apart, keeping the group centred."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    last = -1e9
    for i in order:
        out[i] = max(vals[i], last + gap)
        last = out[i]
    shift = (sum(vals) - sum(out)) / len(vals)
    return [v + shift for v in out]


sm = r[r.params_B <= 2.1].copy()
sm["band"] = pd.cut(sm.params_B, [0, 0.5, 1.0, 2.1], labels=SMALL_BANDS)

# One entry per model: 42 rows become 26, which is most of what makes the labels
# fit. See one_per_model() for the rule.
sm = one_per_model(sm)

# Back on a date axis, at a larger canvas. Labels sit beside their point,
# de-collided vertically within each release month, and the side alternates
# month to month so neighbouring releases do not label into each other.
fig4, ax = plt.subplots(figsize=(18, 11), facecolor=SURF)
ax.set_facecolor(SURF)
for b in SMALL_BANDS:
    s_ = sm[sm.band == b]
    ax.plot(s_.date, s_.eci_A, "o", ms=7, color=SMALL_C[b], markeredgecolor=SURF,
            markeredgewidth=1.3, linestyle="none", zorder=3, label=f"{b}  (n={len(s_)})")
# Label placement. Grouping by release month is not enough -- a label is wider
# than the gap between neighbouring releases, so labels from different months
# collide (2024-02's ran into 2024-04's, and both into 2024-07's). Instead every
# label is treated as the rectangle it actually occupies and nudged vertically
# until it clears the ones already placed, densest region first.
GAP, OFF, CHAR_DAYS = 1.15, 16, 4.6  # TECI, days, days per character at size 8
placed = []
sm_lab = sm.assign(lab=[short(e) for e in sm.entry])
# place the crowded rows first: they have the least freedom
order = sm_lab.assign(_n=sm_lab.groupby("date").eci_A.transform("size")) \
              .sort_values(["_n", "eci_A"], ascending=[False, True])
for row in order.itertuples():
    x0 = mdates.date2num(row.date) + OFF
    x1 = x0 + len(row.lab) * CHAR_DAYS
    for step in [0] + [s * d for s in np.arange(0.25, 12, 0.25) for d in (1, -1)]:
        y = row.eci_A + step
        if not any(x0 < px1 and px0 < x1 and abs(y - py) < GAP for px0, px1, py in placed):
            break
    placed.append((x0, x1, y))
    ax.annotate(row.lab, xy=(row.date, row.eci_A), xytext=(x0, y), textcoords="data",
                ha="left", fontsize=8, color=INK2, va="center", zorder=4,
                arrowprops=dict(arrowstyle="-", color=GRID, lw=0.6, shrinkA=1, shrinkB=2)
                if abs(y - row.eci_A) >= 0.05 else None)
ax.set_ylabel(TECI_AXIS, color=INK2, fontsize=10.5)
ax.grid(axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.tick_params(colors=MUTED, labelsize=9)
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
ax.spines["bottom"].set_color(AXIS)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.set_xlim(pd.Timestamp("2023-06-01"), pd.Timestamp("2026-09-01"))
ax.set_ylim(sm.eci_A.min() - 5, sm.eci_A.max() + 5)
ax.legend(loc="upper left", fontsize=9.5, frameon=False, labelcolor=INK2,
          title="parameters", title_fontsize=9.5)
fig4.suptitle(f"Every model at or below 2B ({len(sm)} entries)",
              color=INK, fontsize=14, x=0.008, ha="left", fontweight="bold", y=0.982)
fig4.text(0.008, 0.952,
          "One entry per model: thinking preferred over non-thinking, instruct over base. "
          "phi-1, phi-1_5 and OLMo-1B have no instruct release.",
          color=INK2, fontsize=9.5, va="top")
fig4.text(0.008, 0.008, TECI_NOTE, color=MUTED, fontsize=8, va="bottom")
fig4.tight_layout(rect=(0, 0.035, 1, 0.938))
fig4.savefig("eci_small_models.png", dpi=170, facecolor=SURF)

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

# Finer bands, and why they disagree with the pooled tiers.
def fit(g):
    return np.polyfit(g.yrs, g.eci_A, 1)[0]


rows += ["", "## The same models in finer bands", "",
         "| band | n | slope TECI/yr | mean TECI | mean release |",
         "|---|---:|---:|---:|---|"]
for b in BANDS:
    g = r[r.band == b]
    if len(g) >= MIN_N and (g.yrs.max() - g.yrs.min()) >= MIN_SPAN_YRS:
        rows.append(f"| {b} | {len(g)} | {fit(g):+.1f} | {g.eci_A.mean():.1f} | "
                    f"{g.date.mean():%Y-%m} |")
lo, hi = r[r.band == "<1B"], r[r.band == "1–2B"]
pooled = r[r.params_B <= 2.1]
rows += ["",
         f"Banded this way there is no consistent size gradient in *rate* — every band sits",
         f"between {min(fit(r[r.band == b]) for b in BANDS):+.1f} and "
         f"{max(fit(r[r.band == b]) for b in BANDS):+.1f} TECI/yr. Size sets the level, not the slope.",
         "",
         "That contradicts the pooled tier gap above, and the reason is composition inside the",
         f"small tier. `<1B` fits {fit(lo):+.1f}/yr and `1–2B` fits {fit(hi):+.1f}/yr, but pooled as",
         f"`≤2B` they fit {fit(pooled):+.1f}/yr — below both. The `<1B` models sit lower "
         f"(mean {lo.eci_A.mean():.1f} vs {hi.eci_A.mean():.1f})",
         f"and later (mean release {lo.date.mean():%Y-%m} vs {hi.date.mean():%Y-%m}), so a single line "
         "through both is dragged",
         "down at its recent end. The large tier has no such split: `5–15B` and `15–35B` fit",
         f"{fit(r[r.band == '5–15B']):+.1f} and {fit(r[r.band == '15–35B']):+.1f}, and pooled `>10B` fits "
         f"{fit(r[r.params_B > 10]):+.1f}.",
         "",
         "So a good part of the reported size gap is unequal time-sampling within the small",
         "tier rather than a difference in how fast small models improve. Treat the pooled",
         "tier gap as an upper bound."]
open("../docs/tier_trends.md", "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("saved eci_families.png, eci_tier_gap.png, eci_all_models.png, eci_small_models.png, docs/tier_trends.md")
