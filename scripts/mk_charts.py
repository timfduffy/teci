#!/usr/bin/env python3
"""Charts: (1) ECI trajectories by size track (Qwen/Gemma panels); (2) method agreement."""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import transforms

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4e0"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

r = pd.read_csv("results_methods.csv")
r["date"] = pd.to_datetime(r.release.astype(str), format="%Y-%m")
rr = r.set_index("entry")

TRACKS_Q = {
    "~0.5-0.8B": ["Qwen1.5-0.5B-Chat [Instruct/chat]", "Qwen2-0.5B-Instruct [Instruct/chat]",
              "Qwen2.5-0.5B-Instruct [Instruct/chat]", "Qwen3-0.6B [Thinking mode]",
              "Qwen3.5-0.8B [Thinking (default)]"],
    "~1.5-2B": ["Qwen1.5-1.8B-Chat [Instruct/chat]", "Qwen2-1.5B-Instruct [Instruct/chat]",
                "Qwen2.5-1.5B-Instruct [Instruct/chat]", "Qwen3-1.7B [Thinking mode]",
                "Qwen3.5-2B [Thinking (default)]"],
    "~4B": ["Qwen1.5-4B-Chat [Instruct/chat]", "Qwen2.5-3B-Instruct [Instruct/chat]",
            "Qwen3-4B [Thinking mode]", "Qwen3-4B-Thinking-2507 [Thinking]",
            "Qwen3.5-4B [Thinking (default)]"],
    "~7-9B": ["Qwen-7B-Chat [Instruct/chat]", "Qwen1.5-7B-Chat [Instruct/chat]",
              "Qwen2-7B-Instruct [Instruct/chat]", "Qwen2.5-7B-Instruct [Instruct/chat]",
              "Qwen3-8B [Thinking mode]", "Qwen3.5-9B [Thinking (default)]"],
    "~14B": ["Qwen-14B-Chat [Instruct/chat]", "Qwen1.5-14B-Chat [Instruct/chat]",
             "Qwen2.5-14B-Instruct [Instruct/chat]", "Qwen3-14B [Thinking mode]"],
    "~30-35B": ["Qwen1.5-32B-Chat [Instruct/chat]", "Qwen2.5-32B-Instruct [Instruct/chat]",
                "Qwen3-32B [Thinking mode]", "Qwen3-30B-A3B-Thinking-2507 [Thinking]",
                "Qwen3.5-35B-A3B [Thinking (default)]", "Qwen3.6-35B-A3B [Thinking (default)]"],
}
TRACKS_G = {
    "~1-2B (E2B)": ["Gemma 2B IT [Instruction-tuned (IT)]", "Gemma 2 2B IT [Instruction-tuned (IT)]",
                    "Gemma 3 1B IT [Instruction-tuned (IT)]", "Gemma 3n E2B IT [Instruction-tuned (IT)]",
                    "Gemma 4 E2B [IT, Thinking mode]"],
    "~7-9B (E4B)": ["Gemma 7B IT [Instruction-tuned (IT)]", "Gemma 2 9B IT [Instruction-tuned (IT)]",
                    "Gemma 3n E4B IT [Instruction-tuned (IT)]", "Gemma 4 E4B [IT, Thinking mode]"],
    "~27-31B": ["Gemma 2 27B IT [Instruction-tuned (IT)]", "Gemma 3 27B IT [Instruction-tuned (IT)]",
                "Gemma 4 31B [IT, Thinking mode]"],
}
REFS = [("GPT-4 (Mar '23)", 125.7), ("Claude 3.5 Sonnet (Jun '24)", 130.0), ("GPT-5 (Aug '25)", 150.0)]
YLIM = (82, 156)

fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), facecolor=SURF)
DIRECT_Q = {"~0.5-0.8B", "~4B", "~7-9B", "~30-35B"}
for ax, tracks, title, direct in ((axes[0], TRACKS_Q, "Qwen", DIRECT_Q),
                                  (axes[1], TRACKS_G, "Gemma (IT)", set(TRACKS_G))):
    ax.set_facecolor(SURF)
    ax.set_ylim(*YLIM)
    blend = transforms.blended_transform_factory(ax.transAxes, ax.transData)
    for lbl, y in REFS:
        ax.axhline(y, color="#cfcec9", lw=1.1, ls=(0, (4, 3)), zorder=1)
        ax.text(0.012, y + 0.8, lbl, transform=blend, fontsize=7.5, color=INK2, zorder=2)
    for i, (name, entries) in enumerate(tracks.items()):
        pts = sorted((rr.loc[e, "date"], float(rr.loc[e, "eci_A"])) for e in entries if e in rr.index)
        xs, ys = zip(*pts)
        ax.plot(list(xs), list(ys), color=C[i], lw=2, marker="o", ms=4.5, zorder=3, label=name,
                markerfacecolor=C[i], markeredgecolor=SURF, markeredgewidth=1)
        if name in direct:
            ax.annotate(name, xy=(xs[-1], ys[-1]), xytext=(5, 0), textcoords="offset points",
                        fontsize=8, color=INK, va="center", fontweight="bold", zorder=4)
    ax.set_title(title, color=INK, fontsize=12, loc="left", fontweight="bold")
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.tick_params(colors=INK2, labelsize=8.5)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(pd.Timestamp("2023-06-01"), pd.Timestamp("2026-12-01"))
    ax.legend(loc="lower right", fontsize=8, frameon=False, labelcolor=INK2,
              title="size track", title_fontsize=8)
axes[0].set_ylabel("ECI (Epoch Capabilities Index scale)", color=INK2, fontsize=9.5)
fig.suptitle("Small Qwen & Gemma models on the ECI scale (method A: joint refit with Epoch data)",
             color=INK, fontsize=13, x=0.02, ha="left", fontweight="bold", y=0.99)
fig.text(0.02, 0.925, "Instruct/thinking entries; dashed refs = published ECI of frontier models",
         color=INK2, fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.91))
fig.savefig("eci_trajectories.png", dpi=170, facecolor=SURF)

# ---- chart 2: method agreement ----
fig2, ax = plt.subplots(figsize=(7.2, 6.4), facecolor=SURF)
ax.set_facecolor(SURF)
v = r.dropna(subset=["eci_A", "eci_B", "eci_C"])
lims = [82, 158]
ax.plot(lims, lims, color="#cfcec9", lw=1.2, ls=(0, (4, 3)), zorder=1)
ax.annotate("y = x", xy=(lims[1] - 4, lims[1] - 3), fontsize=8, color=INK2)
ax.scatter(v.eci_A, v.eci_B, s=26, color=C[0], edgecolors=SURF, linewidths=0.8, zorder=3,
           label="B: frozen Epoch parameters")
ax.scatter(v.eci_A, v.eci_C, s=26, color=C[1], edgecolors=SURF, linewidths=0.8, zorder=3,
           label="C: standalone + bridge")
pubv = r.dropna(subset=["eci_published"])
ax.scatter(pubv.eci_A, pubv.eci_published, s=60, marker="D", color=C[2], edgecolors=SURF,
           linewidths=1, zorder=4, label="Epoch published (8 shared models)")
ax.set_xlim(lims); ax.set_ylim(lims)
ax.set_xlabel("ECI — method A (joint refit)", color=INK2, fontsize=9.5)
ax.set_ylabel("ECI — other methods", color=INK2, fontsize=9.5)
ax.grid(color=GRID, lw=0.7)
ax.tick_params(colors=INK2, labelsize=8.5)
for s in ("top", "right"): ax.spines[s].set_visible(False)
for s in ("bottom", "left"): ax.spines[s].set_color(GRID)
ax.legend(loc="upper left", fontsize=8.5, frameon=False, labelcolor=INK2)
ax.set_title(f"Method agreement: {len(v)} model entries, three grafting methods",
             color=INK, fontsize=12, loc="left", fontweight="bold")
fig2.tight_layout()
fig2.savefig("eci_method_agreement.png", dpi=170, facecolor=SURF)
print("saved")
