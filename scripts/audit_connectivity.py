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
for sheet in ("Qwen scores", "Gemma scores", "OLL scores", "LiveBench scores",
              "OLL cross-family"):
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
              "is confirmed. The Qwen3.5 cards are confirmed too: their comparison columns "
              "copy earlier published numbers verbatim -- 10 of 11 cross-checkable values "
              "match to the decimal (Qwen3-1.7B C-Eval 68.1, IFEval 72.5, MMLU-Redux 73.9; "
              "Qwen3-4B-2507 MMLU-Pro 74.0, SuperGPQA 47.8, PolyMATH 46.2, ...), and their "
              "'GPQA' column gives Qwen3-1.7B 40.1, exactly the Qwen3 report's GPQA-Diamond. "
              "Qwen2/2.5 'GPQA' remains unverified -> assume Diamond, verify.")
merge("Qwen", [("IFEval","prompt strict-acc."), ("IFEval","strict-prompt"), ("IFEval","")],
      "IFEval (strict-prompt)", "flag",
      "Downgraded from 'high'. IFEval is reported four ways (prompt- vs "
      "instruction-level, strict vs loose) and instruction-level typically runs "
      "8-12 pts above prompt-level. The Qwen3 tech report and the Qwen3.5 model "
      "cards state no variant, and the rows come from different sources. This is "
      "load-bearing: IFEval is one of only 3 instruments shared between "
      "Qwen3-0.6B and Qwen3.5-0.8B, and it alone produces the apparent "
      "capability decline between them (drop the observation and the two "
      "entries fit identically).")
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

# OLL and LiveBench are one harness run across families, so those instruments are
# GLOBAL (no family prefix) -- which is what makes the cross-family entries
# connect at all. Vendor instruments stay family-scoped. Mirrors prep_obs.py.
GLOBAL_PREFIXES = ("OLLv1:", "OLLv2:", "LiveBench")


def instrument(row, regime):
    fam, b, c = row["Family"], row["Benchmark"], row["Eval config / notes"]
    if regime == "curated" and (fam, b, c) in M:
        return fam + "::" + M[(fam, b, c)]
    key = b + ("|" + c if c else "")
    if b.startswith(GLOBAL_PREFIXES):
        if regime == "curated" and "; " in c:
            # OLL cross-family rows carry the run precision in the config. The
            # leaderboard ran one harness, so bfloat16 and float16 are the same
            # instrument and prep_obs.py's duplicates->max rule picks one. Kept
            # separate under strict because precision has changed a score at
            # least once (Qwen2.5-0.5B MATH Lvl 5: 0.00 bf16 vs 10.35 fp16).
            key = b + "|" + c.split("; ")[0]
        return key
    return fam + "::" + key


NOTES.append(("cross-family", "OLLv2:* (precision)", "flag",
              "bfloat16 and float16 runs of the same model merged as one "
              "instrument; precision has changed an OLL score at least once."))

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
    "Qwen": ["Qwen (v1)", "Qwen1.5", "Qwen2", "Qwen2.5", "Qwen3", "Qwen3-2507", "Qwen3.5",
             "Qwen3.6", "Qwen3.8"],
    "Gemma": ["Gemma 1", "Gemma 2", "Gemma 3", "Gemma 3n", "Gemma 4"],
    # families added from the Open LLM Leaderboard by add_oll_models.py
    "Llama": ["Llama 2", "Llama 3", "Llama 3.1", "Llama 3.2"],
    "Phi": ["Phi-1", "Phi-1.5", "Phi-2", "Phi-3", "Phi-3.5", "Phi-4"],
    "SmolLM": ["SmolLM", "SmolLM2"],
    "OLMo": ["OLMo", "OLMo 2", "OLMoE"],
}
CORE = ("Qwen", "Gemma")
FAMILIES = [f for f in GEN_ORDER if f in set(df.Family)]

report = []
out = report.append
out("# Connectivity audit — model × benchmark matrix\n")
out("Qwen and Gemma carry full vendor benchmark suites; Llama, Phi, SmolLM and")
out("OLMo were added from the Open LLM Leaderboard and ride the shared OLLv2")
out("instruments only, so their per-family sections are thin by construction —")
out("what matters for them is the cross-family section at the end.\n")

for fam in FAMILIES:
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
        shared = inst_by_gen.get(a, set()) & inst_by_gen.get(b, set())
        names = sorted(s.split("::")[-1] for s in shared)
        out(f"- {a} <-> {b}: {len(shared)} shared -> {', '.join(names) if names else 'NONE'}")
    # key non-adjacent bridge: Qwen2.5 <-> Qwen3 era boundary already adjacent; for Gemma also check 3<->4
    out("")

# ----------------------------------------------------------------------------
# Cross-family connectivity: does the whole matrix hang together as one graph,
# and which instruments actually carry the joins between families?
# ----------------------------------------------------------------------------
out("\n## Cross-family connectivity (all families, curated)\n")
allsub = df[df.scale == "usable"].copy()
allsub["inst"] = allsub.apply(lambda r: instrument(r, "curated"), axis=1)
comps = sorted(components(list(allsub[["entry", "inst"]].itertuples(index=False, name=None))),
               key=len, reverse=True)
out(f"- entries: {allsub.entry.nunique()}, instruments: {allsub.inst.nunique()}, "
    f"connected components: {len(comps)}")
out(f"- main component: {len(comps[0])} entries")
for c in comps[1:]:
    out(f"- ISOLATED component ({len(c)}): {', '.join(c)}")
counts = allsub.groupby("entry").inst.nunique()
weak = counts[counts < 4]
out(f"- entries below Epoch's 4-instrument rule: {len(weak) if len(weak) else 'none'}"
    + (": " + ", ".join(weak.index) if len(weak) else ""))

out("\n### Instruments shared between families")
fams_by_inst = allsub.groupby("inst").Family.unique()
shared_inst = {i: sorted(f) for i, f in fams_by_inst.items() if len(f) > 1}
out(f"- {len(shared_inst)} of {allsub.inst.nunique()} instruments are seen by more than one family\n")
for i, fams in sorted(shared_inst.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    n = allsub[allsub.inst == i].entry.nunique()
    out(f"- `{i}` — {len(fams)} families ({', '.join(fams)}), {n} entries")

out("\n### How each added family joins the Qwen/Gemma core")
core_inst = set(allsub[allsub.Family.isin(CORE)].inst)
for fam in [f for f in FAMILIES if f not in CORE]:
    fi = set(allsub[allsub.Family == fam].inst)
    join = sorted(fi & core_inst)
    out(f"- **{fam}**: {allsub[allsub.Family == fam].entry.nunique()} entries, "
        f"{len(join)} of its {len(fi)} instruments shared with Qwen/Gemma"
        + (f" -> {', '.join(join)}" if join else " -> NONE (would be isolated)"))
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
with open("./connectivity_audit.md", "w", encoding="utf-8") as f:
    f.write(text)
print(text)
