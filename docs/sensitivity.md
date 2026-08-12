# Sensitivity pass — flagged instrument-identity assumptions

Method A refit with each flagged merge from `docs/connectivity_audit.md`
reversed. `mean|d|` / `max|d|` are shifts in fitted TECI across our entries;
`tier gap` is the headline quantity — how many TECI/yr faster the >10B tier
improves than the <=2B tier (baseline **1.04**). A variant that barely
moves the gap is an assumption the conclusion does not rest on.

| variant | obs moved | mean\|d\| | max\|d\| | worst-moved entry | tier gap | gap shift |
|---|---:|---:|---:|---|---:|---:|
| `gemma-arcc-split` | 5 | 0.06 | 1.40 | Gemma 2B IT [Instruction-tuned (IT)] (-1.4) | 0.95 | -0.09 |
| `gemma-gsm8k-split` | 5 | 0.12 | 1.26 | Gemma 7B IT [Instruction-tuned (IT)] (+1.3) | 1.16 | +0.12 |
| `livebench-split` | 14 | 0.09 | 1.12 | Qwen3-0.6B [Non-thinking mode] (-1.1) | 1.20 | +0.16 |
| `qwen-gsm8k-split` | 3 | 0.04 | 1.00 | Qwen-1.8B-Chat [Instruct/chat] (-1.0) | 1.03 | -0.01 |
| `ifeval-split` | 7 | 0.04 | 0.54 | Qwen3.5-0.8B [Non-thinking rows] (-0.5) | 1.07 | +0.03 |
| `gemma-winogrande-split` | 8 | 0.05 | 0.54 | Gemma 1.1 7B IT [Instruction-tuned (IT)] (-0.5) | 1.08 | +0.04 |
| `arenahard-split` | 14 | 0.10 | 0.45 | Qwen2.5-32B-Instruct [Instruct/chat] (+0.5) | 1.01 | -0.03 |
| `qwen-mmlu-split` | 3 | 0.02 | 0.37 | Qwen-14B-Chat [Instruct/chat] (-0.4) | 1.08 | +0.04 |
| `lcb-v6-merge` | 6 | 0.03 | 0.33 | Qwen3.6-27B [Thinking (default)] (+0.3) | 1.05 | +0.01 |
| `hmmt-split` | 4 | 0.01 | 0.26 | Qwen3-30B-A3B-Thinking-2507 [Thinking] (+0.3) | 1.07 | +0.03 |
| `gpqa-split` | 7 | 0.05 | 0.23 | Qwen2-7B-Instruct [Instruct/chat] (+0.2) | 1.04 | -0.00 |
| `gemma-hellaswag-split` | 5 | 0.01 | 0.19 | Gemma 2B [Pretrained (PT)] (+0.2) | 1.04 | -0.00 |

## What each variant tests

- **`gemma-arcc-split`** — Gemma 1 ARC-c config unstated vs Gemma 2/3 25-shot
- **`gemma-gsm8k-split`** — GSM8K (PT) shot counts differ across Gemma generations
- **`livebench-split`** — Qwen3 report's LiveBench release date unconfirmed -> separate
- **`qwen-gsm8k-split`** — Qwen v1 8-shot GSM8K vs later unstated
- **`ifeval-split`** — Qwen3.5/3.6 IFEval variant unstated (prompt- vs instruction-level)
- **`gemma-winogrande-split`** — scoring scheme differs Gemma 1/2 vs Gemma 3
- **`arenahard-split`** — Arena-Hard version may differ across Qwen2.5/3 -> separate
- **`qwen-mmlu-split`** — Qwen v1 explicitly 5-shot MMLU; Qwen2 unstated
- **`lcb-v6-merge`** — opposite direction: treat Qwen 3.5/3.6 'v6' as the 2507 window
- **`hmmt-split`** — Qwen 2507 'HMMT25' may not be the Feb'25 set -> separate
- **`gpqa-split`** — Qwen2/2.5 'GPQA' may not be Diamond -> separate instrument
- **`gemma-hellaswag-split`** — Gemma 1 0-shot vs Gemma 2/3 10-shot

## The Qwen3-0.6B → Qwen3.5-0.8B comparison

Fitted at 114.2 and 114.7 TECI (+0.5).

An earlier fit put this at −1.3, a visible dip on the size-class chart, and it was
worth chasing. The two entries share only three instruments (C-Eval, MMLU-Redux,
IFEval); on two of them the newer model is equal or better (50.4→50.5, 55.6→59.5)
and IFEval alone falls 59.2→44.0. Dropping that one observation made the two
entries fit identically, so nothing else supported the dip.

It resolved without touching the data point. Adding the Qwen3.5 cards' comparison
columns (`add_qwen35_card_rows.py`) gave the `Qwen::` instruments this entry sits
on far more anchoring observations, and the estimate moved up on its own. The
`ifeval-split` variant above, which was the largest mover in this sweep before
that addition, is now a minor one.

The IFEval drop itself is real, not a transcription error: Qwen's card shows the
0.8B scoring *lower* in thinking mode than non-thinking (44.0 vs 52.1) while every
larger sibling gains — a documented failure mode where a very small model's
reasoning trace crowds out strict format compliance.
