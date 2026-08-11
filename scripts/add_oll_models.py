#!/usr/bin/env python3
"""Append cross-family small models from the Open LLM Leaderboard to the workbook.

Why: our 2025+ small entries rest almost entirely on family-scoped vendor
instruments (`Qwen::*`, `Gemma::*`), so the low end of the scale is calibrated
by Qwen and Gemma alone. OLL v2 ran one uniform harness over thousands of
models, including the sub-2B tier, on six instruments already present in our
fit -- so these models connect without introducing any new instrument-identity
assumptions.

Adds SmolLM, OLMo, Llama and Phi (official-provider uploads only, <=35B). Writes
a new "OLL cross-family" sheet; the Qwen/Gemma "OLL scores" sheet is untouched.

    python scripts/add_oll_models.py          # run from anywhere

Caveats carried into the sheet's notes column:
  - OLL v2 scores are the leaderboard's NORMALIZED values, not raw accuracy, so
    they are the same instruments as the existing OLLv2:* rows and must not be
    merged with any vendor-reported GPQA/MMLU-Pro/BBH number.
  - OLL froze 2025-03-13, so nothing here postdates that. This de-biases the
    2023-2024 span of the trend, not its most recent points.
  - Where a model was run at more than one precision the rows are kept and
    prep_obs.py's duplicates->max rule picks one, matching how the existing
    sheet handles the Qwen2.5-0.5B bfloat16/float16 split.
"""
import re
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "qwen_gemma_benchmarks.xlsx"
RAW = ROOT / "data" / "raw" / "oll_contents.parquet"
URL = "https://huggingface.co/api/datasets/open-llm-leaderboard/contents/parquet/default/train/0.parquet"
SHEET = "OLL cross-family"
SOURCE = ("Open LLM Leaderboard v2 (HF dataset open-llm-leaderboard/contents), "
          "Official Providers only; normalized scores per the leaderboard's own "
          "aggregation; retrieved 2026-08-11")

# org -> (family label, name filter) so that e.g. microsoft/DialoGPT is not Phi
ORGS = {
    "HuggingFaceTB": ("SmolLM", r"^SmolLM"),
    "allenai": ("OLMo", r"^OLMo"),
    "meta-llama": ("Llama", r"Llama"),
    "microsoft": ("Phi", r"^phi|^Phi"),
}

# OLL v2 column -> instrument name, matching the existing "OLL scores" sheet.
BENCHMARKS = {
    "IFEval": "OLLv2: IFEval",
    "BBH": "OLLv2: BBH",
    "MATH Lvl 5": "OLLv2: MATH Lvl 5",
    "GPQA": "OLLv2: GPQA",
    "MUSR": "OLLv2: MUSR",
    "MMLU-PRO": "OLLv2: MMLU-PRO",
}

GENERATIONS = [
    (r"^SmolLM2", "SmolLM2"), (r"^SmolLM3", "SmolLM3"), (r"^SmolLM", "SmolLM"),
    (r"^OLMoE", "OLMoE"), (r"^OLMo-?2", "OLMo 2"), (r"^OLMo", "OLMo"),
    (r"Llama-2", "Llama 2"), (r"Llama-3\.1", "Llama 3.1"), (r"Llama-3\.2", "Llama 3.2"),
    (r"Llama-3\.3", "Llama 3.3"), (r"Llama-3", "Llama 3"),
    (r"^Phi-4|^phi-4", "Phi-4"), (r"^Phi-3\.5", "Phi-3.5"), (r"^Phi-3", "Phi-3"),
    (r"^phi-2", "Phi-2"), (r"^phi-1_5", "Phi-1.5"), (r"^phi-1", "Phi-1"),
]

INSTRUCT = re.compile(r"instruct|chat|-it$|sft|dpo|zephyr|tulu", re.I)


def generation(name):
    for pat, label in GENERATIONS:
        if re.search(pat, name):
            return label
    return name


def main():
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {URL}")
        RAW.write_bytes(urlopen(URL).read())
    d = pd.read_parquet(RAW)

    d = d[d["Official Providers"] == True].copy()  # noqa: E712
    d["org"] = d.fullname.str.split("/").str[0]
    d["name"] = d.fullname.str.split("/").str[-1]
    keep = []
    for org, (fam, pat) in ORGS.items():
        s = d[(d.org == org) & d.name.str.contains(pat, regex=True, na=False)].copy()
        s["Family"] = fam
        keep.append(s)
    d = pd.concat(keep, ignore_index=True)
    d = d[(d["#Params (B)"] > 0) & (d["#Params (B)"] <= 35)]

    rows = []
    for rec in d.to_dict("records"):
        name = rec["name"]
        rel = pd.to_datetime(rec.get("Upload To Hub Date"), errors="coerce")
        common = {
            "Family": rec["Family"], "Generation": generation(name), "Model": name,
            "Params (B)": rec["#Params (B)"],
            "Architecture": "MoE" if rec.get("MoE") else "Dense",
            "Release": rel.strftime("%Y-%m") if pd.notna(rel) else "",
            "Variant / mode": "Instruct/chat" if INSTRUCT.search(name) else "Pretrained (PT)",
            "Eval config / notes": f"normalized 0-100; {rec['Precision']}",
            "Source": SOURCE,
        }
        for col, bench in BENCHMARKS.items():
            if pd.isna(rec.get(col)):
                continue
            rows.append({**common, "Benchmark": bench, "Score": float(rec[col])})
    out = pd.DataFrame(rows)[["Family", "Generation", "Model", "Params (B)", "Architecture",
                              "Release", "Variant / mode", "Benchmark",
                              "Eval config / notes", "Score", "Source"]]

    with pd.ExcelWriter(XLSX, engine="openpyxl", mode="a",
                        if_sheet_exists="replace") as w:
        out.to_excel(w, sheet_name=SHEET, index=False)

    print(f"wrote sheet '{SHEET}': {len(out)} rows, {out.Model.nunique()} models")
    print(out.groupby(["Family", "Variant / mode"]).Model.nunique().to_string())
    sub2 = out[out["Params (B)"] <= 2.1]
    print(f"\nsub-2B models added: {sub2.Model.nunique()}")
    print(f"release range: {out.Release.replace('', pd.NA).min()} -> {out.Release.max()}")


if __name__ == "__main__":
    main()
