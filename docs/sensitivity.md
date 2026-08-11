# Sensitivity pass — flagged instrument-identity assumptions

Method A refit with each flagged merge from `docs/connectivity_audit.md`
reversed. `mean|d|` / `max|d|` are shifts in fitted ECI across our entries;
`tier gap` is the headline quantity — how many ECI/yr faster the >10B tier
improves than the <=2B tier (baseline **3.46**). A variant that barely
moves the gap is an assumption the conclusion does not rest on.

| variant | obs moved | mean\|d\| | max\|d\| | worst-moved entry | tier gap | gap shift |
|---|---:|---:|---:|---|---:|---:|
| `gemma-arcc-split` | 5 | 0.05 | 1.33 | Gemma 2B IT [Instruction-tuned (IT)] (-1.3) | 3.33 | -0.12 |
| `gemma-gsm8k-split` | 5 | 0.08 | 1.27 | Gemma 2B IT [Instruction-tuned (IT)] (+1.3) | 3.56 | +0.10 |
| `livebench-split` | 14 | 0.12 | 1.17 | Qwen3-0.6B [Non-thinking mode] (-1.2) | 3.60 | +0.15 |
| `qwen-gsm8k-split` | 3 | 0.05 | 1.06 | Qwen-1.8B-Chat [Instruct/chat] (-1.1) | 3.42 | -0.03 |
| `hmmt-split` | 4 | 0.07 | 0.53 | Qwen3.5-2B [Thinking (default)] (-0.5) | 3.53 | +0.07 |
| `gemma-winogrande-split` | 8 | 0.05 | 0.45 | Gemma 1.1 7B IT [Instruction-tuned (IT)] (-0.5) | 3.52 | +0.06 |
| `arenahard-split` | 14 | 0.07 | 0.38 | Qwen2.5-32B-Instruct [Instruct/chat] (+0.4) | 3.43 | -0.03 |
| `qwen-mmlu-split` | 3 | 0.02 | 0.36 | Qwen-14B-Chat [Instruct/chat] (-0.4) | 3.51 | +0.06 |
| `gpqa-split` | 7 | 0.07 | 0.28 | Qwen2-7B-Instruct [Instruct/chat] (+0.3) | 3.44 | -0.02 |
| `lcb-v6-merge` | 6 | 0.03 | 0.26 | Qwen3.5-4B [Thinking (default)] (-0.3) | 3.47 | +0.01 |
| `gemma-hellaswag-split` | 5 | 0.01 | 0.19 | Gemma 2B [Pretrained (PT)] (+0.2) | 3.46 | +0.00 |

## What each variant tests

- **`gemma-arcc-split`** — Gemma 1 ARC-c config unstated vs Gemma 2/3 25-shot
- **`gemma-gsm8k-split`** — GSM8K (PT) shot counts differ across Gemma generations
- **`livebench-split`** — Qwen3 report's LiveBench release date unconfirmed -> separate
- **`qwen-gsm8k-split`** — Qwen v1 8-shot GSM8K vs later unstated
- **`hmmt-split`** — Qwen 2507 'HMMT25' may not be the Feb'25 set -> separate
- **`gemma-winogrande-split`** — scoring scheme differs Gemma 1/2 vs Gemma 3
- **`arenahard-split`** — Arena-Hard version may differ across Qwen2.5/3 -> separate
- **`qwen-mmlu-split`** — Qwen v1 explicitly 5-shot MMLU; Qwen2 unstated
- **`gpqa-split`** — Qwen2/2.5 'GPQA' may not be Diamond -> separate instrument
- **`lcb-v6-merge`** — opposite direction: treat Qwen 3.5/3.6 'v6' as the 2507 window
- **`gemma-hellaswag-split`** — Gemma 1 0-shot vs Gemma 2/3 10-shot
