#!/usr/bin/env python3
"""Append the Qwen3.5 model cards' comparison columns to the workbook.

Two gaps this closes.

1. The Qwen3.5-4B/9B card carries five multilingual benchmarks that were
   transcribed for the 0.8B/2B card but not this one, so those instruments
   spanned only 0.8B-2B when they could span 0.8B-9B.

2. The Qwen3.5-0.8B/2B card reports Qwen3-1.7B and Qwen3-4B-2507 alongside the
   new models, evaluated in the same run. Under our entry convention a model
   re-evaluated elsewhere is the SAME entry, so those columns attach to the
   existing Qwen3 entries and give same-harness links across the generation
   boundary -- which is what the Qwen3 -> Qwen3.5 comparison was short of
   (Qwen3-0.6B and Qwen3.5-0.8B shared only three instruments).

MMLU-ProX and MMMLU are the exception. Cross-checking models that appear in
both waves of cards shows the Qwen3.5-wave cards report these differently:

    Qwen3-30B-A3B-Thinking-2507  MMLU-ProX  76.4 (2507 card) vs 69.1 (3.5 card)
    Qwen3-4B-Thinking-2507       MMLU-ProX  64.2 (2507 card) vs 62.4 (3.5 card)
    Qwen3-1.7B                   MMMLU      59.1 (Qwen3 report) vs 57.0 (3.5 card)

while every non-multilingual value matches to the decimal, and INCLUDE -- also
multilingual -- matches exactly (74.4 both). So it is these two specifically,
not the multilingual suite as a whole. They are tagged `src: Qwen3.5 card` here
and split into their own instrument by prep_obs.py's canon(). That also FIXES an
existing mis-merge: MMLU-ProX was pooling 2507-card and 3.5-card rows.

Re-runnable: rows already present are skipped, so it will not duplicate.

    python scripts/add_qwen35_card_rows.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "qwen_gemma_benchmarks.xlsx"
SHEET = "Qwen scores"

SRC_SMALL = ("huggingface.co/Qwen/Qwen3.5-0.8B card table, comparison columns "
             "(same evaluation run as the Qwen3.5 rows; extracted 2026-08)")
SRC_MID = ("huggingface.co/Qwen/Qwen3.5-4B card table (Live HF model card, "
           "extracted 2026-08)")
TAG = "src: Qwen3.5 card"   # canon() keys MMLU-ProX / MMMLU off this

# --- 1. multilingual rows missing for Qwen3.5-4B / -9B (thinking) ------------
MID = {
    "MMMLU":       {"Qwen3.5-4B": 76.1, "Qwen3.5-9B": 81.2},
    "NOVA-63":     {"Qwen3.5-4B": 54.3, "Qwen3.5-9B": 55.9},
    "Global PIQA": {"Qwen3.5-4B": 78.9, "Qwen3.5-9B": 83.2},
    "WMT24++":     {"Qwen3.5-4B": 66.6, "Qwen3.5-9B": 72.6},
    "MAXIFE":      {"Qwen3.5-4B": 78.0, "Qwen3.5-9B": 83.4},
}

# --- 2. comparison columns from the 0.8B/2B card ----------------------------
# The card's "GPQA" column is GPQA-Diamond: it reproduces the Qwen3 report's
# Diamond values exactly (Qwen3-1.7B 40.1). See docs/connectivity_audit.md.
THINK = {  # benchmark -> {model: score}
    "MMLU-Pro":       {"Qwen3-1.7B": 56.5, "Qwen3-4B-Thinking-2507": 74.0},
    "MMLU-Redux":     {"Qwen3-1.7B": 73.9, "Qwen3-4B-Thinking-2507": 86.1},
    "C-Eval":         {"Qwen3-1.7B": 68.1, "Qwen3-4B-Thinking-2507": 82.2},
    "SuperGPQA":      {"Qwen3-1.7B": 31.2, "Qwen3-4B-Thinking-2507": 47.8},
    "GPQA-Diamond":   {"Qwen3-1.7B": 40.1, "Qwen3-4B-Thinking-2507": 65.8},
    "IFEval":         {"Qwen3-1.7B": 72.5, "Qwen3-4B-Thinking-2507": 87.4},
    "IFBench":        {"Qwen3-1.7B": 26.7, "Qwen3-4B-Thinking-2507": 50.4},
    "MultiChallenge": {"Qwen3-1.7B": 27.2, "Qwen3-4B-Thinking-2507": 41.7},
    "AA-LCR":         {"Qwen3-1.7B": 6.7,  "Qwen3-4B-Thinking-2507": 32.0},
    "LongBench v2":   {"Qwen3-1.7B": 26.5, "Qwen3-4B-Thinking-2507": 42.8},
    "HMMT Feb'25":    {"Qwen3-1.7B": 10.2, "Qwen3-4B-Thinking-2507": 57.5},
    "HMMT Nov'25":    {"Qwen3-1.7B": 8.9,  "Qwen3-4B-Thinking-2507": 69.6},
    "BFCL v4":        {"Qwen3-4B-Thinking-2507": 39.9},
    "TAU2-Bench":     {"Qwen3-4B-Thinking-2507": 43.2},
    "MMMLU":          {"Qwen3-1.7B": 57.0, "Qwen3-4B-Thinking-2507": 70.8},
    "MMLU-ProX":      {"Qwen3-1.7B": 49.4, "Qwen3-4B-Thinking-2507": 62.4},
    "NOVA-63":        {"Qwen3-1.7B": 40.3, "Qwen3-4B-Thinking-2507": 47.1},
    "INCLUDE":        {"Qwen3-1.7B": 51.8, "Qwen3-4B-Thinking-2507": 64.4},
    "Global PIQA":    {"Qwen3-1.7B": 63.1, "Qwen3-4B-Thinking-2507": 73.5},
    "PolyMATH":       {"Qwen3-1.7B": 25.2, "Qwen3-4B-Thinking-2507": 46.2},
    "WMT24++":        {"Qwen3-1.7B": 39.3, "Qwen3-4B-Thinking-2507": 58.9},
    "MAXIFE":         {"Qwen3-1.7B": 50.7, "Qwen3-4B-Thinking-2507": 72.1},
}
NONTHINK = {
    "MMLU-Pro":   {"Qwen3-1.7B": 40.2, "Qwen3-4B-Instruct-2507": 69.6},
    "MMLU-Redux": {"Qwen3-1.7B": 64.4, "Qwen3-4B-Instruct-2507": 84.2},
    "C-Eval":     {"Qwen3-1.7B": 61.0, "Qwen3-4B-Instruct-2507": 80.2},
    "SuperGPQA":  {"Qwen3-1.7B": 21.0, "Qwen3-4B-Instruct-2507": 42.8},
    "IFEval":     {"Qwen3-1.7B": 68.2, "Qwen3-4B-Instruct-2507": 83.4},
    "MMMLU":      {"Qwen3-1.7B": 46.7, "Qwen3-4B-Instruct-2507": 64.9},
}
MODE = {"Qwen3-1.7B": {"think": "Thinking mode", "non": "Non-thinking mode"},
        "Qwen3-4B-Thinking-2507": {"think": "Thinking"},
        "Qwen3-4B-Instruct-2507": {"non": "Instruct (non-thinking)"},
        "Qwen3.5-4B": {"think": "Thinking (default)"},
        "Qwen3.5-9B": {"think": "Thinking (default)"}}
# MMLU-ProX / MMMLU always get added even when the entry already has a value:
# the tag puts them in a different instrument, so it is not a duplicate.
RETAG = {"MMLU-ProX", "MMMLU"}


def main():
    df = pd.read_excel(XLSX, sheet_name=SHEET)
    meta = {m: g.iloc[0] for m, g in df.groupby("Model")}
    have = set(map(tuple, df[["Model", "Variant / mode", "Benchmark"]].values))

    rows, skipped = [], 0
    def emit(model, mode_key, bench, score, source):
        nonlocal skipped
        mode = MODE[model][mode_key]
        if (model, mode, bench) in have and bench not in RETAG:
            skipped += 1
            return
        m = meta[model]
        rows.append({"Family": "Qwen", "Generation": m.Generation, "Model": model,
                     "Params (B)": m["Params (B)"], "Architecture": m.Architecture,
                     "Release": m.Release, "Variant / mode": mode, "Benchmark": bench,
                     "Eval config / notes": TAG, "Score": float(score), "Source": source})

    for bench, vals in MID.items():
        for model, s in vals.items():
            emit(model, "think", bench, s, SRC_MID)
    for bench, vals in THINK.items():
        for model, s in vals.items():
            emit(model, "think", bench, s, SRC_SMALL)
    for bench, vals in NONTHINK.items():
        for model, s in vals.items():
            emit(model, "non", bench, s, SRC_SMALL)

    add = pd.DataFrame(rows)
    # Tag the Qwen3.5 rows already in the sheet for the two re-run benchmarks, so
    # they join the same instrument as the ones added here.
    m = df.Benchmark.isin(RETAG) & df.Model.str.startswith("Qwen3.5")
    df.loc[m, "Eval config / notes"] = TAG
    out = pd.concat([df, add], ignore_index=True)

    # replace only this sheet; every other sheet in the workbook is untouched
    with pd.ExcelWriter(XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        out.to_excel(w, sheet_name=SHEET, index=False)

    print(f"added {len(add)} rows, skipped {skipped} already present, "
          f"re-tagged {int(m.sum())} existing MMLU-ProX/MMMLU rows")
    print(add.groupby(["Model", "Variant / mode"]).size().to_string())


if __name__ == "__main__":
    main()
