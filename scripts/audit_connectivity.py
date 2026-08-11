#!/usr/bin/env python3
"""Connectivity audit of the Qwen/Gemma official-score matrix for ECI-style IRT fitting.

Entry  = model + variant/mode (thinking vs non-thinking = separate entries).
Instrument = family-scoped benchmark + config, under two regimes:
  STRICT : exact (benchmark, config) string identity.
  CURATED: explicit merge map below; every merge carries a confidence note.
Scale classes: 'usable' (bounded 0-100, higher better), 'transform' (bounded, lower
better or odd unit — usable after transform), 'exclude' (unbounded ratings / Elo /
0-10 judge scales / synthetic averages).
"""
import pandas as pd
from collections import defaultdict

XLSX = "./qwen_gemma_benchmarks.xlsx"

frames = []
for sheet in ("Qwen scores", "Gemma scores", "OLL scores"):
    frames.append(pd.read_excel(XLSX, sheet_name=sheet))
df = pd.concat(frames, ignore_index=True)
df["Eval config / notes"] = df["Eval config / notes"].fillna("")

# ----------------------------------------------------------------------------
# Scale classification (by benchmark name)
# ----------------------------------------------------------------------------
EXCLUDE = {  # unbounded ratings, judge 0-10 scales, Elo, synthetic rows
    "MT-Bench", "AlignBench", "AlignBench v1.1", "CodeForces rating", "CFEval",
    "CodeForces Elo", "LMSYS Chatbot Arena Elo", "LMArena Elo",
    "Average (official table)",
}
TRANSFORM = {  # bounded / metric but lower-better or non-% unit
    "OmniDocBench 1.5", "FLEURS", "CoVoST",
}
def scale_class(b):
    if b in EXCLUDE: return "exclude"
    if b in TRANSFORM: return "transform"
    return "usable"

# ----------------------------------------------------------------------------
# CURATED merge map: (family, benchmark, config) -> canonical instrument name.
# Anything not listed keeps strict identity (benchmark + config).
# conf: 'high' = confident same instrument; 'flag' = assumption, verify before fit.
# ----------------------------------------------------------------------------
M = {}
NOTES = []
def merge(family, pairs, canon, conf, note):
    for bench, cfg in pairs:
        M[(family, bench, cfg)] = canon
    NOTES.append((family, canon, conf, note))

# ---- Qwen merges ----
merge("Qwen", [("MMLU","5-shot"), ("MMLU","")], "MMLU",
      "flag", "Qwen1 explicitly 5-shot; Qwen2 blog doesn't state shots.")
merge("Qwen", [("MATH","4-shot"), ("MATH","")], "MATH",
      "flag", "Qwen1 4-shot; Qwen2/2.5 config unstated.")
merge("Qwen", [("GSM8K","8-shot"), ("GSM8K","")], "GSM8K",
      "flag", "Qwen1 8-shot; Qwen2/2.5 unstated.")
merge("Qwen", [("HumanEval","0-shot"), ("HumanEval","")], "HumanEval",
      "high", "0-shot pass@1 throughout Qwen reporting.")
merge("Qwen", [("MBPP","3-shot"), ("MBPP","")], "MBPP",
      "flag", "Qwen1 3-shot; later unstated.")
merge("Qwen", [("C-Eval","5-shot"), ("C-Eval","")], "C-Eval",
      "flag", "Qwen1 5-shot; later unstated.")
merge("Qwen", [("GPQA",""), ("GPQA-Diamond","")], "GPQA(-Diamond)",
      "flag", "Qwen3 report says Diamond; 2507 cards' 'GPQA' column reproduces the "
              "Qwen3 GPQA-Diamond values (e.g. 30B-A3B non-thinking 54.8), so 2507=Diamond "
              "is confirmed. Qwen2/2.5 'GPQA' unverified -> assume Diamond, verify.")
merge("Qwen", [("IFEval","prompt strict-acc."), ("IFEval","strict-prompt"), ("IFEval","")],
      "IFEval (strict-prompt)", "high", "Same metric, naming varies.")
merge("Qwen", [("LiveBench",""), ("LiveBench","release 20241125")], "LiveBench-20241125",
      "flag", "Qwen3 tech report's LiveBench is believed to be the 2024-11-25 release "
              "(same as 2507 cards). Verify in report before merging for the fit.")
merge("Qwen", [("HMMT'25",""), ("HMMT Feb'25","")], "HMMT Feb'25",
      "flag", "2507 'HMMT25' presumed = Feb 2025 contest set used later as 'HMMT Feb'25'.")
# LiveCodeBench: NEVER merged across windows, even curated:
#   Qwen2 '' | 2.5 '2305-2409' | Qwen3 v5 | 2507 'v6 25.02-25.05' | 3.5/3.6 'v6' (window unstated)
merge("Qwen", [("LiveCodeBench","v6, questions 25.02-25.05")], "LCB v6 (25.02-25.05)",
      "high", "Kept separate from 3.5/3.6 'v6' whose question window is unstated.")
merge("Qwen", [("LiveCodeBench","v6")], "LCB v6 (window unstated)",
      "flag", "Qwen3.5/3.6 'v6' may or may not equal the 2507 window - kept SEPARATE.")
merge("Qwen", [("LiveCodeBench","v5")], "LCB v5", "high", "Qwen3 tech report window.")
merge("Qwen", [("LiveCodeBench","questions 2305-2409")], "LCB 2305-2409", "high", "Qwen2.5 window.")
merge("Qwen", [("LiveCodeBench","")], "LCB (Qwen2, window unstated)", "high", "Kept separate.")

# ---- Gemma merges (PT suite across generations; IT suite Gemma3->3n->4) ----
merge("Gemma", [("HellaSwag","0-shot"), ("HellaSwag","10-shot")], "HellaSwag",
      "flag", "Gemma1 0-shot vs Gemma2/3 10-shot - shot count differs.")
merge("Gemma", [("WinoGrande","partial score"), ("WinoGrande","5-shot")], "WinoGrande",
      "flag", "Scoring scheme differs between Gemma1/2 and Gemma3.")
merge("Gemma", [("ARC-c",""), ("ARC-c","25-shot")], "ARC-c",
      "flag", "Gemma1 config unstated; Gemma2/3 25-shot.")
merge("Gemma", [("ARC-e",""), ("ARC-e","0-shot")], "ARC-e",
      "high", "0-shot throughout where stated.")
merge("Gemma", [("HumanEval","pass@1"), ("HumanEval","0-shot")], "HumanEval (PT)",
      "flag", "Gemma1/2 'pass@1' vs Gemma3 '0-shot' - presumed same 0-shot pass@1. "
              "NOTE: IT 0-shot HumanEval (Gemma3 IT / 3n IT) merges here too by config; "
              "instrument is shared PT/IT, which is fine for IRT.")
merge("Gemma", [("GSM8K","maj@1"), ("GSM8K","5-shot, maj@1"), ("GSM8K","8-shot")], "GSM8K (PT)",
      "flag", "maj@1 vs 5-shot maj@1 vs 8-shot - configs differ across generations.")
merge("Gemma", [("GSM8K","0-shot")], "GSM8K (IT 0-shot)", "high", "Gemma3 IT only.")
merge("Gemma", [("BIG-Bench","3-shot, CoT"), ("BIG-Bench","")], "BIG-Bench (BB, not BBH)",
      "high", "Gemma1/2 'BIG-Bench' kept separate from Gemma3+ 'BIG-Bench Hard'.")
merge("Gemma", [("BIG-Bench Hard","few-shot")], "BBH (PT few-shot)", "high", "")
merge("Gemma", [("BIG-Bench Hard","0-shot")], "BBH (IT 0-shot)", "high", "")
merge("Gemma", [("GPQA-Diamond","0-shot"), ("GPQA-Diamond","relaxed accuracy"),
                ("GPQA-Diamond","no tools")], "GPQA-Diamond (IT)",
      "flag", "Gemma3 IT 0-shot vs 3n 'relaxed accuracy' vs Gemma4 'no tools' - scoring "
              "and mode differ (Gemma4 = thinking).")
merge("Gemma", [("MMLU-Pro","0-shot"), ("MMLU-Pro","")], "MMLU-Pro (IT)",
      "flag", "Gemma3/3n IT 0-shot; Gemma4 config unstated + thinking mode.")
merge("Gemma", [("MMLU","0-shot")], "MMLU (IT 0-shot)", "high", "3n IT only.")
merge("Gemma", [("MMLU","5-shot"), ("MMLU","5-shot, top-1")], "MMLU (PT 5-shot)",
      "high", "Gemma1/2/3 PT.")
merge("Gemma", [("LiveCodeBench","0-shot")], "LCB (Gemma3 IT, window unstated)", "high", "Kept separate.")
merge("Gemma", [("LiveCodeBench","v5")], "LCB v5 (3n)", "high", "Kept separate.")
merge("Gemma", [("LiveCodeBench","v6")], "LCB v6 (Gemma4)", "high", "Kept separate.")

def instrument(row, regime):
    fam, b, c = row["Family"], row["Benchmark"], row["Eval config / notes"]
    if regime == "curated" and (fam, b, c) in M:
        return fam + "::" + M[(fam, b, c)]
    return fam + "::" + b + ("|" + c if c else "")

# Same weights + same inference mode = same entry: the Gemma-4-card re-evaluation
# of Gemma 3 27B IT (non-thinking, like all Gemma 3 IT scores) is the SAME node.
def norm_variant(v):
    return "Instruction-tuned (IT)" if "re-evaluated" in v else v
df["entry"] = df["Model"] + " [" + df["Variant / mode"].map(norm_variant) + "]"
df["scale"] = df["Benchmark"].map(scale_class)

# ----------------------------------------------------------------------------
# Union-find
# ----------------------------------------------------------------------------
def components(edges):
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for e, i in edges:
        union(("E", e), ("I", i))
    comps = defaultdict(set)
    for node in parent:
        comps[find(node)].add(node)
    return [sorted(n[1] for n in c if n[0] == "E") for c in comps.values()]

GEN_ORDER = {
    "Qwen": ["Qwen (v1)", "Qwen1.5", "Qwen2", "Qwen2.5", "Qwen3", "Qwen3-2507", "Qwen3.5", "Qwen3.6"],
    "Gemma": ["Gemma 1", "Gemma 2", "Gemma 3", "Gemma 3n", "Gemma 4"],
}

report = []
out = report.append
out("# Connectivity audit — Qwen/Gemma official-score matrix\n")

for fam in ("Qwen", "Gemma"):
    sub = df[(df.Family == fam) & (df.scale == "usable")].copy()
    out(f"\n## {fam}\n")
    n_entries = sub.entry.nunique()
    for regime in ("strict", "curated"):
        sub["inst"] = sub.apply(lambda r: instrument(r, regime), axis=1)
        edges = list(sub[["entry", "inst"]].itertuples(index=False, name=None))
        comps = sorted(components(edges), key=len, reverse=True)
        out(f"### Regime: {regime}")
        out(f"- entries: {n_entries}, usable instruments: {sub.inst.nunique()}, "
            f"connected components: {len(comps)}")
        for i, c in enumerate(comps):
            if i == 0:
                out(f"- main component: {len(c)} entries")
            else:
                out(f"- ISOLATED component ({len(c)}): {', '.join(c)}")
        out("")
    # per-entry usable score count (curated)
    sub["inst"] = sub.apply(lambda r: instrument(r, "curated"), axis=1)
    counts = sub.groupby("entry").inst.nunique().sort_values()
    weak = counts[counts < 4]
    out("### Entries with <4 usable instruments (Epoch's inclusion rule)")
    if len(weak):
        for e, n in weak.items(): out(f"- {e}: {n}")
    else:
        out("- none")
    out("")
    # generation-adjacency bridge table (curated)
    out("### Adjacent-generation bridges (curated; shared usable instruments)")
    gens = GEN_ORDER[fam]
    inst_by_gen = {g: set(sub[sub.Generation == g].inst) for g in gens}
    entry_inst = sub.groupby("inst").entry.nunique()
    pairs = list(zip(gens, gens[1:]))
    if fam == "Gemma":
        pairs.append(("Gemma 3", "Gemma 4"))
    for a, b in pairs:
        shared = inst_by_gen[a] & inst_by_gen[b]
        names = sorted(s.split("::")[1] for s in shared)
        out(f"- {a} <-> {b}: {len(shared)} shared -> {', '.join(names) if names else 'NONE'}")
    # key non-adjacent bridge: Qwen2.5 <-> Qwen3 era boundary already adjacent; for Gemma also check 3<->4
    out("")

out("\n## Curated merge decisions (every assumption, with confidence)\n")
for fam, canon, conf, note in NOTES:
    if note:
        out(f"- [{conf.upper()}] {fam} :: {canon} — {note}")

out("\n## Scale-class inventory\n")
for cls in ("transform", "exclude"):
    rows = df[df.scale == cls][["Family", "Benchmark"]].drop_duplicates()
    items = [f"{r.Family}:{r.Benchmark}" for r in rows.itertuples()]
    out(f"- {cls}: {', '.join(items)}")

text = "\n".join(report)
with open("./connectivity_audit.md", "w") as f:
    f.write(text)
print(text)
