#!/usr/bin/env python3
"""Append the Qwen3.8-27B model card to the workbook.

Qwen3.8-27B (released 2026-08-14, dense multimodal, 27.8B, thinking by default)
is the newest entry in the ~27-32B dense track. The only other Qwen3.8 checkpoint
is Qwen3.8-Max (2.4T), far outside this project's <=35B scope.

Two things this adds:

1. Qwen3.8-27B itself, from the card's text and vision tables.
2. The card's Qwen3.6-27B comparison column. Under our entry convention a model
   re-evaluated elsewhere is the SAME entry, so those values attach to the
   existing Qwen3.6-27B entry. This matters more than usual here: most of the
   3.8 card's benchmarks are new to the project, and an instrument observed on a
   single entry constrains nothing while still feeling the ridge prior. Adding
   the 3.6 column makes them two-point instruments and, for IFBench, joins the
   27B pair to instrument shared with Qwen3-1.7B and Qwen3-4B-Thinking-2507.

Is the comparison column a re-run or a copy? The card says "Except for Opus4.6
Max, which uses the officially reported score, all models are evaluated with the
Claude Code harness", which reads as a re-run. It makes no difference on the
overlap: every value we can check against the Qwen3.6 card matches to the
decimal --

    GPQA-Diamond 87.8   HLE 24.0   LiveCodeBench v6 83.9   SWE-bench Pro 53.5

-- 4 of 4, so no split tag is needed (contrast MMLU-ProX/MMMLU in
add_qwen35_card_rows.py, which did diverge and had to be split).

The one benchmark that does NOT match is the check that proves the rule.
Terminal Bench: our Qwen3.6 row is 59.3 on 2.0, this card reports 63.4 on 2.1 --
same model, same vendor, different score, so the versions are genuinely
different instruments. Recorded as `Terminal-Bench 2.1`, separate from the
existing `Terminal-Bench 2.0`.

Naming decisions, because prep_obs.py's canon() IGNORES the config column for
Qwen benchmarks it does not special-case (it returns the bare benchmark name).
Anything that needs to stay a separate instrument must carry the distinction in
the *name*:

  - `MathVision`: the card splits Without/With CI. An earlier plain `MathVision`
    already exists for Qwen3.5-27B (86.0) and would silently pool with the
    "Without CI" rows. The card's own gloss of CI is ambiguous and we cannot
    confirm the 3.5 row used the same condition, so both are named explicitly
    (`MathVision (no CI)` / `(with CI)`) and neither merges with it. Same for
    CharXiv and BabyVision.
  - `ClawEval-MM` and `Agents' Last Exam` each report two different quantities;
    named separately for the same reason.

Baselines: the new instruments are not in prep_obs.py's OWN_BASE, so they are
chance-corrected against 0. Right for the agentic and open-ended ones, and
consistent with how Qwen3.6's agentic rows were already handled. RealWorldQA,
ERQA and MathVision are multiple-choice and arguably deserve a nonzero floor,
but the option counts are not stated on the card and guessing one is worse than
leaving it; at 27B-scale scores (62-90) the choice moves little.

Flagged for the reader, not acted on: QwenSWEBench is a Qwen-authored benchmark
on which the new model jumps 49.3 -> 79.0, by far the largest move in the table.
It is transcribed as published and enters the fit like any other Qwen::
instrument.

Re-runnable: rows already present are skipped, so it will not duplicate.

    python scripts/add_qwen38_rows.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "qwen_gemma_benchmarks.xlsx"
SHEET = "Qwen scores"

SRC = "huggingface.co/Qwen/Qwen3.8-27B (live card, extracted 2026-08)"
SRC_CMP = ("huggingface.co/Qwen/Qwen3.8-27B card table, comparison column "
           "(Claude Code harness re-run; matches the Qwen3.6 card on all four "
           "overlapping benchmarks; extracted 2026-08)")

NEW = {  # Model / Params (B) / Architecture / Release / Variant / mode
    "Qwen3.8-27B": ("Qwen3.8", 27, "Dense (multimodal)", "2026-08", "Thinking (default)"),
}
CMP_MODEL = "Qwen3.6-27B"
CMP_MODE = "Thinking (default)"

# benchmark -> (eval config, Qwen3.8-27B, Qwen3.6-27B)   None = not reported
TEXT = [
    ("Terminal-Bench 2.1",           "Terminus scaffold",  73.0, 63.4),
    ("SWE-bench Pro",                "Claude Code harness", 61.7, 53.5),
    ("NL2Repo-Bench",                "",                   42.3, 36.2),
    ("DeepSWE 1.1",                  "Claude Code harness", 42.2, 13.3),
    ("QwenSWEBench",                 "Claude Code harness", 79.0, 49.3),
    ("CoWorkBench",                  "avg@3, 8h timeout",  70.7, 61.0),
    ("JobBench",                     "",                   33.4, 21.8),
    ("Agents' Last Exam (Pass@1)",   "",                   20.4, 10.6),
    ("Agents' Last Exam (Score)",    "",                   42.9, 27.3),
    ("IFBench",                      "",                   79.5, 69.1),
    # canon(): GPQA-Diamond and HLE map to Epoch instruments, LiveCodeBench v6
    # to `LCB v6 (late)`. All three already carry the Qwen3.6 value.
    ("GPQA-Diamond",                 "",                   89.2, 87.8),
    ("HLE",                          "no tools",           30.8, 24.0),
    ("LiveCodeBench",                "v6",                 90.3, 83.9),
]
VISION = [
    ("OSWorld-Verified",             "",                   84.3, 63.9),
    ("WebArena-Verified",            "",                   64.8, 48.8),
    ("AndroidWorld",                 "",                   81.9, 70.3),
    ("RecreationBench",              "",                   47.1, 29.8),
    ("ClawEval-MM (Pass@3)",         "",                   57.4, 56.9),
    ("ClawEval-MM (Average)",        "",                   50.4, 42.6),
    ("SWE-MM",                       "",                   38.6, 25.7),
    ("Vision2Web",                   "",                   62.9, 45.0),
    ("MathVision (no CI)",           "vision",             90.0, 85.1),
    ("MathVision (with CI)",         "vision, CI",         94.6, 90.0),
    ("BabyVision (no CI)",           "vision",             65.7, 28.9),
    ("BabyVision (with CI)",         "vision, CI",         85.6, None),
    ("CharXiv (no CI)",              "vision",             83.7, 78.4),
    ("CharXiv (with CI)",            "vision, CI",         90.2, None),
    # dropped by prep_obs.py's EXCLUDE_BENCH (different scale); kept for the record
    ("OmniDocBench 1.5",             "",                   91.1, 89.4),
    ("RealWorldQA",                  "vision",             85.9, 84.1),
    ("ERQA",                         "vision",             65.5, 62.5),
]


def main():
    df = pd.read_excel(XLSX, sheet_name=SHEET)
    meta = {m: g.iloc[0] for m, g in df.groupby("Model")}
    have = set(map(tuple, df[["Model", "Variant / mode", "Benchmark"]].values))

    rows, skipped = [], 0

    def emit(model, mode, params, arch, gen, release, bench, cfg, score, source):
        nonlocal skipped
        if (model, mode, bench) in have:
            skipped += 1
            return
        rows.append({"Family": "Qwen", "Generation": gen, "Model": model,
                     "Params (B)": params, "Architecture": arch, "Release": release,
                     "Variant / mode": mode, "Benchmark": bench,
                     "Eval config / notes": cfg, "Score": float(score),
                     "Source": source})

    gen, params, arch, release, mode = NEW["Qwen3.8-27B"]
    cmp_meta = meta[CMP_MODEL]
    for bench, cfg, new, cmp in TEXT + VISION:
        emit("Qwen3.8-27B", mode, params, arch, gen, release, bench, cfg, new, SRC)
        if cmp is not None:
            emit(CMP_MODEL, CMP_MODE, cmp_meta["Params (B)"], cmp_meta.Architecture,
                 cmp_meta.Generation, cmp_meta.Release, bench, cfg, cmp, SRC_CMP)

    add = pd.DataFrame(rows)
    out = pd.concat([df, add], ignore_index=True)
    with pd.ExcelWriter(XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        out.to_excel(w, sheet_name=SHEET, index=False)

    print(f"added {len(add)} rows, skipped {skipped} already present")
    print(add.groupby(["Model", "Variant / mode"]).size().to_string())


if __name__ == "__main__":
    main()
