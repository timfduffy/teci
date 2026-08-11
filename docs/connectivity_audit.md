# Connectivity audit — Qwen/Gemma official-score matrix


## Qwen

### Regime: strict
- entries: 49, usable instruments: 97, connected components: 1
- main component: 49 entries

### Regime: curated
- entries: 49, usable instruments: 86, connected components: 1
- main component: 49 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- Qwen (v1) <-> Qwen1.5: 6 shared -> C-Eval, GSM8K, HumanEval, MATH, MBPP, MMLU
- Qwen1.5 <-> Qwen2: 12 shared -> C-Eval, GSM8K, HumanEval, MATH, MBPP, MMLU, OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Qwen2 <-> Qwen2.5: 14 shared -> GPQA(-Diamond), GSM8K, HumanEval, IFEval (strict-prompt), MATH, MBPP, MMLU-Pro, MultiPL-E, OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100
- Qwen2.5 <-> Qwen3: 4 shared -> Arena-Hard, GPQA(-Diamond), IFEval (strict-prompt), MMLU-Redux
- Qwen3 <-> Qwen3-2507: 7 shared -> AIME'25, BFCL v3, GPQA(-Diamond), IFEval (strict-prompt), LiveBench-20241125, MMLU-Redux, Multi-IF
- Qwen3-2507 <-> Qwen3.5: 10 shared -> GPQA(-Diamond), HMMT Feb'25, IFEval (strict-prompt), INCLUDE, MMLU-Pro, MMLU-ProX, MMLU-Redux, OJBench, PolyMATH, SuperGPQA
- Qwen3.5 <-> Qwen3.6: 10 shared -> AIME'26, C-Eval, GPQA(-Diamond), HMMT Feb'25, HMMT Nov'25, LCB v6 (window unstated), MMLU-Pro, MMLU-Redux, SWE-bench Verified, SuperGPQA


## Gemma

### Regime: strict
- entries: 29, usable instruments: 87, connected components: 1
- main component: 29 entries

### Regime: curated
- entries: 29, usable instruments: 75, connected components: 1
- main component: 29 entries

### Entries with <4 usable instruments (Epoch's inclusion rule)
- none

### Adjacent-generation bridges (curated; shared usable instruments)
- Gemma 1 <-> Gemma 2: 21 shared -> ARC-c, ARC-e, BIG-Bench (BB, not BBH), BoolQ|0-shot, GSM8K (PT), HellaSwag, HumanEval (PT), MATH|4-shot, MBPP|3-shot, MMLU (PT 5-shot), Natural Questions|5-shot, OLLv2: BBH|normalized 0-100, OLLv2: GPQA|normalized 0-100, OLLv2: IFEval|normalized 0-100, OLLv2: MATH Lvl 5|normalized 0-100, OLLv2: MMLU-PRO|normalized 0-100, OLLv2: MUSR|normalized 0-100, PIQA|0-shot, SocialIQA|0-shot, TriviaQA|5-shot, WinoGrande
- Gemma 2 <-> Gemma 3: 15 shared -> AGIEval|3-5-shot, ARC-c, ARC-e, BoolQ|0-shot, GSM8K (PT), HellaSwag, HumanEval (PT), MATH|4-shot, MBPP|3-shot, MMLU (PT 5-shot), Natural Questions|5-shot, PIQA|0-shot, SocialIQA|0-shot, TriviaQA|5-shot, WinoGrande
- Gemma 3 <-> Gemma 3n: 19 shared -> ARC-c, ARC-e, BBH (PT few-shot), BoolQ|0-shot, DROP|1-shot, F1, ECLeKTic, GPQA-Diamond (IT), Global-MMLU-Lite, HellaSwag, HumanEval (PT), MBPP|3-shot, MGSM, MMLU-Pro (IT), Natural Questions|5-shot, PIQA|0-shot, SocialIQA|0-shot, TriviaQA|5-shot, WMT24++|ChrF, WinoGrande
- Gemma 3n <-> Gemma 4: 2 shared -> GPQA-Diamond (IT), MMLU-Pro (IT)
- Gemma 3 <-> Gemma 4: 10 shared -> AIME'26|no tools, BigBench Extra Hard, GPQA-Diamond (IT), LCB v6 (Gemma4), MATH-Vision|vision, MMLU-Pro (IT), MMMLU (multilingual MMLU), MMMU-Pro|vision, MRCR v2|8-needle, 128k context, Tau2-bench|avg of 3 domains


## Curated merge decisions (every assumption, with confidence)

- [FLAG] Qwen :: MMLU — Qwen1 explicitly 5-shot; Qwen2 blog doesn't state shots.
- [FLAG] Qwen :: MATH — Qwen1 4-shot; Qwen2/2.5 config unstated.
- [FLAG] Qwen :: GSM8K — Qwen1 8-shot; Qwen2/2.5 unstated.
- [HIGH] Qwen :: HumanEval — 0-shot pass@1 throughout Qwen reporting.
- [FLAG] Qwen :: MBPP — Qwen1 3-shot; later unstated.
- [FLAG] Qwen :: C-Eval — Qwen1 5-shot; later unstated.
- [FLAG] Qwen :: GPQA(-Diamond) — Qwen3 report says Diamond; 2507 cards' 'GPQA' column reproduces the Qwen3 GPQA-Diamond values (e.g. 30B-A3B non-thinking 54.8), so 2507=Diamond is confirmed. Qwen2/2.5 'GPQA' unverified -> assume Diamond, verify.
- [HIGH] Qwen :: IFEval (strict-prompt) — Same metric, naming varies.
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

## Scale-class inventory

- transform: Gemma:OmniDocBench 1.5, Gemma:CoVoST, Gemma:FLEURS
- exclude: Qwen:MT-Bench, Qwen:AlignBench, Qwen:AlignBench v1.1, Qwen:CodeForces rating, Qwen:CFEval, Gemma:Average (official table), Gemma:LMSYS Chatbot Arena Elo, Gemma:LMArena Elo, Gemma:CodeForces Elo
## Status after OLL integration (2026-08-09)

- Qwen: 49 entries, ONE connected component under both strict and curated regimes; no entry below 4 usable instruments. OLL v2's re-runs of the Qwen1.5-Chat line (all 6 sizes) connected the former chat island and added 3 new low-end chat entries (0.5B/1.8B/4B).
- Gemma: 29 entries, ONE connected component under both regimes; no entry below 4 usable instruments. The Gemma 1/1.1/2 IT models connect via OLL v1+v2; the base gemma/gemma-2 OLL rows tie that cluster into the main component through the PT entries.
- New entries added by OLL: Qwen1.5-0.5B/1.8B/4B-Chat, Gemma 1.1 2B IT, Gemma 1.1 7B IT.
- Data-quality flags carried in the OLL sheet: OLL v1 GSM8K for Qwen1.5-4B-Chat (2.43) and Qwen1.5-32B-Chat (7.05) look like answer-format parsing failures - treat as missing in the fit; Qwen2.5-0.5B-Instruct OLLv2 MATH Lvl 5 = 0.00 in the bfloat16 run (float16 run scored 10.35).
- IMPORTANT for interpretation: OLL v2 scores are the leaderboard's NORMALIZED values (random chance rescaled to ~0), NOT raw accuracy - they are separate instruments from any official GPQA/MMLU-Pro/BBH numbers and are named OLLv2:* accordingly.
- Remaining known limits: Qwen (v1) chat models appear in neither OLL version (their link to the rest still runs through vendor benchmarks + the Qwen1.5 base bridge); Gemma 3/3n/4 postdate the OLL freeze (their linkage relies on Google's PT/IT suites and the Gemma 4 card's re-evaluation of Gemma 3 27B). Optional reinforcements: LiveBench releases, AA components, LMArena snapshots.
