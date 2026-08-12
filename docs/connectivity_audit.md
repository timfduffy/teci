# Connectivity audit — model × benchmark matrix

Qwen and Gemma carry full vendor benchmark suites; Llama, Phi, SmolLM and
OLMo were added from the Open LLM Leaderboard and ride the shared OLLv2
instruments only, so their per-family sections are thin by construction —
what matters for them is the cross-family section at the end.


## Qwen

### Regime: strict
- entries: 51, usable instruments: 128, connected components: 1
- main component: 51 entries

### Regime: curated
- entries: 51, usable instruments: 112, connected components: 1
- main component: 51 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- Qwen (v1) <-> Qwen1.5: 6 shared -> C-Eval, GSM8K, HumanEval, MATH, MBPP, MMLU
- Qwen1.5 <-> Qwen2: 12 shared -> C-Eval, GSM8K, HumanEval, MATH, MBPP, MMLU, OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Qwen2 <-> Qwen2.5: 14 shared -> GPQA(-Diamond), GSM8K, HumanEval, IFEval (strict-prompt), MATH, MBPP, MMLU-Pro, MultiPL-E, OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Qwen2.5 <-> Qwen3: 4 shared -> Arena-Hard, GPQA(-Diamond), IFEval (strict-prompt), MMLU-Redux
- Qwen3 <-> Qwen3-2507: 19 shared -> AA-LCR|src: Qwen3.5 card, AIME'25, BFCL v3, GPQA(-Diamond), Global PIQA|src: Qwen3.5 card, HMMT Feb'25|src: Qwen3.5 card, HMMT Nov'25|src: Qwen3.5 card, IFBench|src: Qwen3.5 card, IFEval (strict-prompt), LiveBench-20241125, LongBench v2|src: Qwen3.5 card, MAXIFE|src: Qwen3.5 card, MMLU-ProX|src: Qwen3.5 card, MMLU-Redux, MMMLU|src: Qwen3.5 card, Multi-IF, MultiChallenge|src: Qwen3.5 card, NOVA-63|src: Qwen3.5 card, WMT24++|src: Qwen3.5 card
- Qwen3-2507 <-> Qwen3.5: 15 shared -> GPQA(-Diamond), Global PIQA|src: Qwen3.5 card, HMMT Feb'25, IFEval (strict-prompt), INCLUDE, MAXIFE|src: Qwen3.5 card, MMLU-Pro, MMLU-ProX|src: Qwen3.5 card, MMLU-Redux, MMMLU|src: Qwen3.5 card, NOVA-63|src: Qwen3.5 card, OJBench, PolyMATH, SuperGPQA, WMT24++|src: Qwen3.5 card
- Qwen3.5 <-> Qwen3.6: 10 shared -> AIME'26, C-Eval, GPQA(-Diamond), HMMT Feb'25, HMMT Nov'25, LCB v6 (window unstated), MMLU-Pro, MMLU-Redux, SWE-bench Verified, SuperGPQA


## Gemma

### Regime: strict
- entries: 29, usable instruments: 93, connected components: 1
- main component: 29 entries

### Regime: curated
- entries: 29, usable instruments: 81, connected components: 1
- main component: 29 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- Gemma 1 <-> Gemma 2: 21 shared -> ARC-c, ARC-e, BIG-Bench (BB, not BBH), BoolQ|0-shot, GSM8K (PT), HellaSwag, HumanEval (PT), MATH|4-shot, MBPP|3-shot, MMLU (PT 5-shot), Natural Questions|5-shot, OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100, PIQA|0-shot, SocialIQA|0-shot, TriviaQA|5-shot, WinoGrande
- Gemma 2 <-> Gemma 3: 16 shared -> AGIEval|3-5-shot, ARC-c, ARC-e, BoolQ|0-shot, GSM8K (PT), HellaSwag, HumanEval (PT), LiveBench-20241125|global average, official leaderboard run, MATH|4-shot, MBPP|3-shot, MMLU (PT 5-shot), Natural Questions|5-shot, PIQA|0-shot, SocialIQA|0-shot, TriviaQA|5-shot, WinoGrande
- Gemma 3 <-> Gemma 3n: 19 shared -> ARC-c, ARC-e, BBH (PT few-shot), BoolQ|0-shot, DROP|1-shot, F1, ECLeKTic, GPQA-Diamond (IT), Global-MMLU-Lite, HellaSwag, HumanEval (PT), MBPP|3-shot, MGSM, MMLU-Pro (IT), Natural Questions|5-shot, PIQA|0-shot, SocialIQA|0-shot, TriviaQA|5-shot, WMT24++|ChrF, WinoGrande
- Gemma 3n <-> Gemma 4: 2 shared -> GPQA-Diamond (IT), MMLU-Pro (IT)
- Gemma 3 <-> Gemma 4: 10 shared -> AIME'26|no tools, BigBench Extra Hard, GPQA-Diamond (IT), LCB v6 (Gemma4), MATH-Vision|vision, MMLU-Pro (IT), MMMLU (multilingual MMLU), MMMU-Pro|vision, MRCR v2|8-needle, 128k context, Tau2-bench|avg of 3 domains


## Llama

### Regime: strict
- entries: 12, usable instruments: 12, connected components: 1
- main component: 12 entries

### Regime: curated
- entries: 12, usable instruments: 6, connected components: 1
- main component: 12 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- Llama 2 <-> Llama 3: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Llama 3 <-> Llama 3.1: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Llama 3.1 <-> Llama 3.2: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100


## Phi

### Regime: strict
- entries: 12, usable instruments: 12, connected components: 1
- main component: 12 entries

### Regime: curated
- entries: 12, usable instruments: 6, connected components: 1
- main component: 12 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- Phi-1 <-> Phi-1.5: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Phi-1.5 <-> Phi-2: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Phi-2 <-> Phi-3: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Phi-3 <-> Phi-3.5: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Phi-3.5 <-> Phi-4: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100


## SmolLM

### Regime: strict
- entries: 12, usable instruments: 12, connected components: 1
- main component: 12 entries

### Regime: curated
- entries: 12, usable instruments: 6, connected components: 1
- main component: 12 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- SmolLM <-> SmolLM2: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100


## OLMo

### Regime: strict
- entries: 7, usable instruments: 12, connected components: 2
- main component: 5 entries
- ISOLATED component (2): OLMo-2-1124-7B-Instruct [Instruct/chat], OLMoE-1B-7B-0125-Instruct [Instruct/chat]

### Regime: curated
- entries: 7, usable instruments: 6, connected components: 1
- main component: 7 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- OLMo <-> OLMo 2: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- OLMo 2 <-> OLMoE: 6 shared -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100


## Cross-family connectivity (all families, curated)

- entries: 123, instruments: 179, connected components: 1
- main component: 123 entries
- entries below Epoch's 4-instrument rule: none

### Instruments shared between families
- 14 of 179 instruments are seen by more than one family

- `OLLv2: BBH|normalized 0-100` — 6 families (Gemma, Llama, OLMo, Phi, Qwen, SmolLM), 70 entries
- `OLLv2: GPQA|normalized 0-100` — 6 families (Gemma, Llama, OLMo, Phi, Qwen, SmolLM), 70 entries
- `OLLv2: IFEval|normalized 0-100` — 6 families (Gemma, Llama, OLMo, Phi, Qwen, SmolLM), 70 entries
- `OLLv2: MATH Lvl 5|normalized 0-100` — 6 families (Gemma, Llama, OLMo, Phi, Qwen, SmolLM), 70 entries
- `OLLv2: MMLU-PRO|normalized 0-100` — 6 families (Gemma, Llama, OLMo, Phi, Qwen, SmolLM), 70 entries
- `OLLv2: MUSR|normalized 0-100` — 6 families (Gemma, Llama, OLMo, Phi, Qwen, SmolLM), 70 entries
- `LiveBench-20250425|global average, official leaderboard run` — 2 families (Gemma, Qwen), 4 entries
- `LiveBench-20260108|global average, official leaderboard run` — 2 families (Gemma, Qwen), 4 entries
- `OLLv1: ARC-Challenge|25-shot, acc_norm` — 2 families (Gemma, Qwen), 11 entries
- `OLLv1: GSM8K|5-shot, acc` — 2 families (Gemma, Qwen), 11 entries
- `OLLv1: HellaSwag|10-shot, acc_norm` — 2 families (Gemma, Qwen), 11 entries
- `OLLv1: MMLU|5-shot, acc (mean of 57 subtasks)` — 2 families (Gemma, Qwen), 11 entries
- `OLLv1: TruthfulQA|0-shot, mc2` — 2 families (Gemma, Qwen), 11 entries
- `OLLv1: Winogrande|5-shot, acc` — 2 families (Gemma, Qwen), 11 entries

### How each added family joins the Qwen/Gemma core
- **Llama**: 12 entries, 6 of its 6 instruments shared with Qwen/Gemma -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- **Phi**: 12 entries, 6 of its 6 instruments shared with Qwen/Gemma -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- **SmolLM**: 12 entries, 6 of its 6 instruments shared with Qwen/Gemma -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- **OLMo**: 7 entries, 6 of its 6 instruments shared with Qwen/Gemma -> OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100


## Curated merge decisions (every assumption, with confidence)

- [FLAG] Qwen :: MMLU — Qwen1 explicitly 5-shot; Qwen2 blog doesn't state shots.
- [FLAG] Qwen :: MATH — Qwen1 4-shot; Qwen2/2.5 config unstated.
- [FLAG] Qwen :: GSM8K — Qwen1 8-shot; Qwen2/2.5 unstated.
- [HIGH] Qwen :: HumanEval — 0-shot pass@1 throughout Qwen reporting.
- [FLAG] Qwen :: MBPP — Qwen1 3-shot; later unstated.
- [FLAG] Qwen :: C-Eval — Qwen1 5-shot; later unstated.
- [FLAG] Qwen :: GPQA(-Diamond) — Qwen3 report says Diamond; 2507 cards' 'GPQA' column reproduces the Qwen3 GPQA-Diamond values (e.g. 30B-A3B non-thinking 54.8), so 2507=Diamond is confirmed. The Qwen3.5 cards are confirmed too: their comparison columns copy earlier published numbers verbatim -- 10 of 11 cross-checkable values match to the decimal (Qwen3-1.7B C-Eval 68.1, IFEval 72.5, MMLU-Redux 73.9; Qwen3-4B-2507 MMLU-Pro 74.0, SuperGPQA 47.8, PolyMATH 46.2, ...), and their 'GPQA' column gives Qwen3-1.7B 40.1, exactly the Qwen3 report's GPQA-Diamond. Qwen2/2.5 'GPQA' remains unverified -> assume Diamond, verify.
- [FLAG] Qwen :: IFEval (strict-prompt) — Downgraded from 'high'. IFEval is reported four ways (prompt- vs instruction-level, strict vs loose) and instruction-level typically runs 8-12 pts above prompt-level. The Qwen3 tech report and the Qwen3.5 model cards state no variant, and the rows come from different sources. This is load-bearing: IFEval is one of only 3 instruments shared between Qwen3-0.6B and Qwen3.5-0.8B, and it alone produces the apparent capability decline between them (drop the observation and the two entries fit identically).
- [FLAG] Qwen :: LiveBench-20241125 — Qwen3 tech report's LiveBench is believed to be the 2024-11-25 release (same as 2507 cards). Verify in report before merging for the fit.
- [FLAG] Qwen :: HMMT Feb'25 — 2507 'HMMT25' presumed = Feb 2025 contest set used later as 'HMMT Feb'25'.
- [HIGH] Qwen :: LCB v6 (25.02-25.05) — Kept separate from 3.5/3.6 'v6' whose question window is unstated.
- [FLAG] Qwen :: LCB v6 (window unstated) — Qwen3.5/3.6 'v6' may or may not equal the 2507 window - kept SEPARATE.
- [HIGH] Qwen :: LCB v5 — Qwen3 tech report window.
- [HIGH] Qwen :: LCB 2305-2409 — Qwen2.5 window.
- [HIGH] Qwen :: LCB (Qwen2, window unstated) — Kept separate.
- [FLAG] Gemma :: HellaSwag — Gemma1 0-shot vs Gemma2/3 10-shot - shot count differs.
- [FLAG] Gemma :: WinoGrande — Scoring scheme differs between Gemma1/2 and Gemma3.
- [FLAG] Gemma :: ARC-c — Gemma1 config unstated; Gemma2/3 25-shot.
- [HIGH] Gemma :: ARC-e — 0-shot throughout where stated.
- [FLAG] Gemma :: HumanEval (PT) — Gemma1/2 'pass@1' vs Gemma3 '0-shot' - presumed same 0-shot pass@1. NOTE: IT 0-shot HumanEval (Gemma3 IT / 3n IT) merges here too by config; instrument is shared PT/IT, which is fine for IRT.
- [FLAG] Gemma :: GSM8K (PT) — maj@1 vs 5-shot maj@1 vs 8-shot - configs differ across generations.
- [HIGH] Gemma :: GSM8K (IT 0-shot) — Gemma3 IT only.
- [HIGH] Gemma :: BIG-Bench (BB, not BBH) — Gemma1/2 'BIG-Bench' kept separate from Gemma3+ 'BIG-Bench Hard'.
- [FLAG] Gemma :: GPQA-Diamond (IT) — Gemma3 IT 0-shot vs 3n 'relaxed accuracy' vs Gemma4 'no tools' - scoring and mode differ (Gemma4 = thinking).
- [FLAG] Gemma :: MMLU-Pro (IT) — Gemma3/3n IT 0-shot; Gemma4 config unstated + thinking mode.
- [HIGH] Gemma :: MMLU (IT 0-shot) — 3n IT only.
- [HIGH] Gemma :: MMLU (PT 5-shot) — Gemma1/2/3 PT.
- [HIGH] Gemma :: LCB (Gemma3 IT, window unstated) — Kept separate.
- [HIGH] Gemma :: LCB v5 (3n) — Kept separate.
- [HIGH] Gemma :: LCB v6 (Gemma4) — Kept separate.
- [FLAG] cross-family :: OLLv2:* (precision) — bfloat16 and float16 runs of the same model merged as one instrument; precision has changed an OLL score at least once.

## Scale-class inventory

- transform: Gemma:OmniDocBench 1.5, Gemma:CoVoST, Gemma:FLEURS
- exclude: Qwen:MT-Bench, Qwen:AlignBench, Qwen:AlignBench v1.1, Qwen:CodeForces rating, Qwen:CFEval, Gemma:Average (official table), Gemma:LMSYS Chatbot Arena Elo, Gemma:LMArena Elo, Gemma:CodeForces Elo