#!/usr/bin/env python3
"""Build the observation table for ECI-style fitting from the workbook.

Output: obs_ours.csv with columns
  entry, family, generation, params, release, benchmark (instrument key),
  scope ('epoch' if mapped to a frozen Epoch benchmark, else 'own'),
  performance (baseline-corrected, in [0,1])
"""
import pandas as pd
import numpy as np

XLSX = "./qwen_gemma_benchmarks.xlsx"

frames = [pd.read_excel(XLSX, sheet_name=s) for s in ("Qwen scores", "Gemma scores", "OLL scores", "LiveBench scores")]
df = pd.concat(frames, ignore_index=True)
df["Eval config / notes"] = df["Eval config / notes"].fillna("")

def norm_variant(v):
    return "Instruction-tuned (IT)" if "re-evaluated" in v else v
df["variant"] = df["Variant / mode"].map(norm_variant)
df["entry"] = df["Model"] + " [" + df["variant"] + "]"

# ---- exclusions ----
EXCLUDE_BENCH = {"MT-Bench", "AlignBench", "AlignBench v1.1", "CodeForces rating", "CFEval",
                 "CodeForces Elo", "LMSYS Chatbot Arena Elo", "LMArena Elo",
                 "Average (official table)", "OmniDocBench 1.5", "FLEURS", "CoVoST"}
df = df[~df.Benchmark.isin(EXCLUDE_BENCH)]
df = df[~df["Eval config / notes"].str.contains("ANOMALY")]

# ---- canonicalization (mirrors audit curated map, family-scoped) ----
def canon(row):
    f, b, c = row.Family, row.Benchmark, row["Eval config / notes"]
    if f == "Qwen":
        if b in ("MMLU", "MATH", "GSM8K", "HumanEval", "MBPP", "C-Eval"): return b
        if b in ("GPQA", "GPQA-Diamond"): return "GPQA-Diamond"
        if b == "IFEval": return "IFEval"
        if b == "LiveBench": return "LiveBench-20241125" if ("20241125" in c or c == "") else "LiveBench-0831"
        if b == "HMMT'25": return "HMMT Feb'25"
        if b == "LiveCodeBench":
            if "25.02" in c: return "LCB v6 (2507)"
            if c == "v6": return "LCB v6 (late)"
            if c == "v5": return "LCB v5"
            if "2305" in c: return "LCB 2305-2409"
            return "LCB (Qwen2)"
    if f == "Gemma":
        if b == "HellaSwag": return "HellaSwag"
        if b == "WinoGrande": return "WinoGrande"
        if b == "ARC-c": return "ARC-c"
        if b == "ARC-e": return "ARC-e"
        if b == "HumanEval": return "HumanEval (PT/IT 0-shot)"
        if b == "GSM8K": return "GSM8K (IT 0-shot)" if c == "0-shot" else "GSM8K (PT)"
        if b == "BIG-Bench": return "BIG-Bench (BB)"
        if b == "BIG-Bench Hard": return "BBH"
        if b == "GPQA-Diamond": return "GPQA-Diamond"
        if b == "MMLU-Pro": return "MMLU-Pro (IT)"
        if b == "MMLU": return "MMLU (IT 0-shot)" if c == "0-shot" else "MMLU (PT)"
        if b == "LiveCodeBench": return {"0-shot": "LCB (G3)", "v5": "LCB v5 (3n)", "v6": "LCB v6 (G4)"}.get(c, "LCB (G?)")
    return b + ("|" + c if c and b.startswith("OLL") is False and f == "OLL" else "")

# simpler: OLL sheet family col is Qwen/Gemma; benchmark names already OLLvX-prefixed
df["canon"] = df.apply(canon, axis=1)

# ---- map to Epoch frozen benchmarks (global instruments) ----
EPOCH_MAP = {
    ("Qwen", "MMLU"): "MMLU", ("Qwen", "GSM8K"): "GSM8K", ("Qwen", "BBH"): "BBH",
    ("Qwen", "GPQA-Diamond"): "GPQA diamond", ("Qwen", "Aider-Polyglot"): "Aider polyglot",
    ("Qwen", "HLE"): "HLE",
    ("Gemma", "MMLU (PT)"): "MMLU", ("Gemma", "MMLU (IT 0-shot)"): "MMLU",
    ("Gemma", "GSM8K (PT)"): "GSM8K", ("Gemma", "GSM8K (IT 0-shot)"): "GSM8K",
    ("Gemma", "HellaSwag"): "HellaSwag", ("Gemma", "WinoGrande"): "Winogrande",
    ("Gemma", "ARC-c"): "ARC AI2", ("Gemma", "PIQA"): "PIQA",
    ("Gemma", "TriviaQA"): "TriviaQA", ("Gemma", "OpenBookQA"): "OpenBookQA",
    ("Gemma", "BBH"): "BBH", ("Gemma", "GPQA-Diamond"): "GPQA diamond",
    ("Gemma", "HLE"): "HLE",
    # OLL sheet rows (family is Qwen/Gemma there; canon = raw benchmark name)
    ("Qwen", "OLLv1: MMLU"): "MMLU", ("Gemma", "OLLv1: MMLU"): "MMLU",
    ("Qwen", "OLLv1: GSM8K"): "GSM8K", ("Gemma", "OLLv1: GSM8K"): "GSM8K",
    ("Qwen", "OLLv1: HellaSwag"): "HellaSwag", ("Gemma", "OLLv1: HellaSwag"): "HellaSwag",
    ("Qwen", "OLLv1: Winogrande"): "Winogrande", ("Gemma", "OLLv1: Winogrande"): "Winogrande",
    ("Qwen", "OLLv1: ARC-Challenge"): "ARC AI2", ("Gemma", "OLLv1: ARC-Challenge"): "ARC AI2",
    ("Qwen", "OLLv2: MATH Lvl 5"): "MATH level 5", ("Gemma", "OLLv2: MATH Lvl 5"): "MATH level 5",
}
EPOCH_BASE = pd.read_csv("./edi_frozen.csv").set_index("benchmark")["baseline"].to_dict()

# ---- baselines for own instruments (fraction of 1) ----
OWN_BASE = {
    "MMLU-Redux": .25, "MMLU-Pro": .1, "MMLU-Pro (IT)": .1, "MMLU-ProX": .1,
    "C-Eval": .25, "CMMLU": .25, "MMMLU": .25, "Global-MMLU-Lite": .25,
    "SuperGPQA": .25, "INCLUDE": .25, "AGIEval": .25, "ARC-e": .25,
    "BoolQ": .5, "SocialIQA": 1/3, "CommonsenseQA": .2,
    "MMMU (val)": .25, "MMMU": .25, "MMStar": .25, "VideoMME": .25,
    "MMMU-Pro": .1, "MedXPertQA MM": .2, "MGSM": 0.0,
    "Global PIQA": .5, "LongBench v2": .25,
}

rows = []
for r in df.itertuples():
    fam, cn = r.Family, r.canon
    raw = float(r.Score) / 100.0
    key = (fam, cn)
    if key in EPOCH_MAP:
        bench = EPOCH_MAP[key]
        scope = "epoch"
        base = EPOCH_BASE.get(bench, 0.0)
        # OLLv2 MATH Lvl5 is already chance-normalized (baseline 0 anyway)
    else:
        scope = "own"
        # OLL instruments are shared across families (same harness) -> global key
        if cn.startswith("OLLv") or cn.startswith("LiveBench"):
            bench = cn
            base = 0.0  # v1 handled below; v2 already normalized
            if cn == "OLLv1: MMLU": base = .25          # (unreachable: mapped above)
            if cn == "OLLv1: TruthfulQA": base = 0.0    # mc2, no clean chance level
        else:
            bench = f"{fam}::{cn}"
            base = OWN_BASE.get(cn, 0.0)
    perf = (raw - base) / (1.0 - base)
    if not (0.0 <= perf <= 1.0):
        continue  # below-chance or invalid -> drop (Epoch convention)
    rows.append([r.entry, fam, r.Generation, r._4, str(r.Release), bench, scope, perf])

obs = pd.DataFrame(rows, columns=["entry", "family", "generation", "params", "release",
                                  "benchmark", "scope", "performance"])
# aggregate duplicates: max (Epoch convention)
meta_cols = ["family", "generation", "params", "release"]
obs = obs.groupby(["entry", "benchmark", "scope"], as_index=False).agg(
    performance=("performance", "max"), family=("family", "first"),
    generation=("generation", "first"), params=("params", "first"), release=("release", "first"))

obs.to_csv("./obs_ours.csv", index=False)
print(f"observations: {len(obs)}, entries: {obs.entry.nunique()}, "
      f"instruments: {obs.benchmark.nunique()} (epoch-mapped: {obs[obs.scope=='epoch'].benchmark.nunique()})")
print("dropped-below-chance handled; entries with no epoch-mapped obs:")
has_epoch = obs[obs.scope == "epoch"].entry.unique()
print(sorted(set(obs.entry) - set(has_epoch)))
