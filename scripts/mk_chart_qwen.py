#!/usr/bin/env python3
"""Single-panel Qwen trajectory chart, starting at Qwen1.5 (Feb 2024)."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4e0"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

r = pd.read_csv("results_methods.csv")
r["date"] = pd.to_datetime(r.release.astype(str), format="%Y-%m")
rr = r.set_index("entry")

TRACKS = {
    "~0.5-0.8B": ["Qwen1.5-0.5B-Chat [Instruct/chat]", "Qwen2-0.5B-Instruct [Instruct/chat]",
                  "Qwen2.5-0.5B-Instruct [Instruct/chat]", "Qwen3-0.6B [Thinking mode]",
                  "Qwen3.5-0.8B [Thinking (default)]"],
    "~1.5-2B": ["Qwen1.5-1.8B-Chat [Instruct/chat]", "Qwen2-1.5B-Instruct [Instruct/chat]",
                "Qwen2.5-1.5B-Instruct [Instruct/chat]", "Qwen3-1.7B [Thinking mode]",
                "Qwen3.5-2B [Thinking (default)]"],
    "~4B": ["Qwen1.5-4B-Chat [Instruct/chat]", "Qwen2.5-3B-Instruct [Instruct/chat]",
            "Qwen3-4B [Thinking mode]", "Qwen3-4B-Thinking-2507 [Thinking]",
            "Qwen3.5-4B [Thinking (default)]"],
    "~7-9B": ["Qwen1.5-7B-Chat [Instruct/chat]", "Qwen2-7B-Instruct [Instruct/chat]",
              "Qwen2.5-7B-Instruct [Instruct/chat]", "Qwen3-8B [Thinking mode]",
              "Qwen3.5-9B [Thinking (default)]"],
    "~14B": ["Qwen1.5-14B-Chat [Instruct/chat]", "Qwen2.5-14B-Instruct [Instruct/chat]",
             "Qwen3-14B [Thinking mode]"],
    "~30-35B": ["Qwen1.5-32B-Chat [Instruct/chat]", "Qwen2.5-32B-Instruct [Instruct/chat]",
                "Qwen3-32B [Thinking mode]", "Qwen3-30B-A3B-Thinking-2507 [Thinking]",
                "Qwen3.5-35B-A3B [Thinking (default)]", "Qwen3.6-35B-A3B [Thinking (default)]"],
}

fig, ax = plt.subplots(figsize=(9.5, 6.6), facecolor=SURF)
ax.set_facecolor(SURF)
# derived from the data: a hardcoded floor clipped the smallest entries off the
# bottom once the Epoch refresh pushed them down
_plotted = [float(rr.loc[e, "eci_A"]) for es in TRACKS.values() for e in es if e in rr.index]
ax.set_ylim(min(_plotted) - 4, max(_plotted) + 10)

# ---- generation markers -----------------------------------------------------
# Every model in a Qwen generation ships in the same month, so each generation is
# a single x position and the markers are already vertically aligned. A hairline
# through each one names the release wave without adding a colour or a shape:
# the date axis keeps the real calendar spacing, and the labels say what the
# clusters are. Labels alternate between two rows because Qwen3.5 (2026-02) and
# Qwen3.6 (2026-04) are two months apart and would otherwise collide.
plotted = {e for es in TRACKS.values() for e in es if e in rr.index}
gen_date = (r[r.entry.isin(plotted)].groupby("generation").date.min().sort_values())
for k, (gen, d) in enumerate(gen_date.items()):
    ax.axvline(d, color=GRID, lw=0.8, zorder=1)
    # date2num: annotate's xy goes through the affine transform directly and
    # will not accept a Timestamp
    ax.annotate(gen, xy=(mdates.date2num(d), 1.0), xycoords=ax.get_xaxis_transform(),
                xytext=(0, 7 + (k % 2) * 12), textcoords="offset points",
                ha="center", va="bottom", fontsize=8, color=INK2, zorder=4)

DIRECT = {"~0.5-0.8B", "~1.5-2B", "~4B", "~30-35B"}
for i, (name, entries) in enumerate(TRACKS.items()):
    pts = sorted((rr.loc[e, "date"], float(rr.loc[e, "eci_A"])) for e in entries if e in rr.index)
    xs, ys = zip(*pts)
    ax.plot(list(xs), list(ys), color=C[i], lw=2, marker="o", ms=5, zorder=3, label=name,
            markerfacecolor=C[i], markeredgecolor=SURF, markeredgewidth=1)
    if name in DIRECT:
        ax.annotate(name, xy=(xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
                    fontsize=8.5, color=INK, va="center", fontweight="bold", zorder=4)
ax.grid(axis="y", color=GRID, lw=0.7)
ax.tick_params(colors=INK2, labelsize=9)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.set_xlim(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-09-01"))
ax.set_ylabel("ECI (Epoch Capabilities Index scale)", color=INK2, fontsize=10)
ax.legend(loc="lower right", fontsize=8.5, frameon=False, labelcolor=INK2,
          title="size track", title_fontsize=8.5)
ax.set_title("Qwen models on the ECI scale, by size track (Qwen1.5 onward)",
             color=INK, fontsize=13, loc="left", fontweight="bold", pad=34)
fig.tight_layout()
fig.savefig("eci_trajectories_qwen.png", dpi=170, facecolor=SURF)
print("saved")
