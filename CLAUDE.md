# Small-model capabilities index (Qwen/Gemma ≤35B, ECI-grafted)

Tim's project tracking whether benchmark progress differs across model sizes
(core question: is the 0.5–2B tier plateauing relative to ~30B?), by placing
small Qwen and Gemma models on the Epoch Capabilities Index (ECI) scale.
Intended for eventual publication (at least a Twitter post).

## Pipeline (run in this order; all paths relative to repo root)

1. `scripts/build_benchmarks.py` — builds `data/qwen_gemma_benchmarks.xlsx`
   from hardcoded official vendor scores (Qwen blogs/tech report/model cards;
   Google model cards/tech reports). Later sheets (OLL, LiveBench, Gemma 4
   card re-eval, Qwen3.5 thinking rows) were appended by follow-up scripts in
   the original session — the shipped xlsx is the source of truth; do NOT
   regenerate it from build_benchmarks.py alone or those additions are lost.
2. `scripts/audit_connectivity.py` — model×benchmark connectivity audit
   (components, generation bridges, merge assumptions). Output: docs/connectivity_audit.md.
3. `scripts/prep_obs.py` — xlsx → `data/obs_ours.csv` (entry, instrument,
   baseline-corrected performance in [0,1]).
4. `scripts/fit_methods.py` — fits methods A/B/C → `data/results_methods.csv`.
5. `scripts/mk_charts.py`, `scripts/mk_chart_qwen.py` — charts (dataviz-styled PNGs).

## Conventions (load-bearing — keep consistent)

- **Entry = model + inference mode.** Thinking and non-thinking are separate
  entries. Same weights + same mode re-evaluated elsewhere = same entry
  (e.g., Gemma 3 27B IT re-evaluated in the Gemma 4 card).
- **Instrument = benchmark + config.** Same-name-different-config rows are
  separate instruments (LiveCodeBench windows, 0-shot vs 5-shot MMLU,
  LiveBench question releases, OLL v1 vs v2). Curated merges + confidence
  flags live in `audit_connectivity.py` (NOTES) and `prep_obs.py` (canon()).
- **Scores are chance-corrected** before fitting: (raw − baseline)/(1 − baseline),
  clipped to [1e-3, 1−1e-3]; below-chance observations dropped; duplicates → max
  (all per Epoch's eci-public conventions).
- OLL and LiveBench instruments are cross-family (same harness); vendor
  instruments are family-scoped.

## Fit methods

- **A (headline): joint refit** of our obs + `data/eci_benchmarks_reconstructed.csv`
  (partial 31-model subset of Epoch's matrix; 6 Gemma bridge nodes merged),
  rescaled via 25 pure-Epoch models against `data/eci_published.csv`.
- **B: frozen graft** — `data/edi_frozen.csv` (Epoch's published EDI/slope, ECI
  units) held fixed; our-only instruments estimated by alternation.
  Known bias: runs 3–8 pts high for top thinking entries (vendor-reported
  scores vs Epoch's own harness on GPQA/HLE/Aider).
- **C: standalone** fit + affine map via 8 shared models (6 Gemma,
  Qwen3.5/3.6-35B-A3B).
- Model spec mirrors `eci-upstream/` (epoch-research/eci-public, MIT):
  performance = σ(slope·(cap − difficulty)), ridge 0.1, scipy trf least
  squares, Winogrande slope pinned; scale anchors Claude 3.5 Sonnet=130, GPT-5=150.

## Data provenance / caveats

- `eci_published.csv` + `edi_frozen.csv`: relayed from epoch.ai CSVs via
  WebFetch extraction (2-decimal rounding; small transcription risk).
  Re-download cleanly from https://epoch.ai/data/eci_scores.csv and
  edi_scores.csv when on an unrestricted network.
- `eci_benchmarks_reconstructed.csv`: first 348 rows of
  https://epoch.ai/data/eci_benchmarks.csv (WebFetch window cutoff).
  **Re-download the full file when possible** — method A currently rescales
  on a 31-model subset.
- Flagged identity assumptions to re-verify before publishing: Qwen2/2.5
  "GPQA" == Diamond (2507 confirmed, 2.5 not); HMMT'25 (2507) vs HMMT Feb'25
  (card shows 57.5 vs 55.5 — keep separate or flag); Qwen3 LiveBench release
  == 2024-11-25; Arena-Hard version across Qwen2.5/3; LCB "v6" windows.
- OLL v1 GSM8K anomalies (Qwen1.5-4B/32B-Chat) and Qwen2.5-0.5B MATH=0.00
  are excluded via ANOMALY notes in the xlsx.
- LiveBench Qwen2.5-7B rows = hosted "turbo" variant (flagged; matches vendor
  0831 value closely).

## Open TODOs

- Re-download full Epoch matrix + exact CSVs (unrestricted network makes
  this trivial: curl the three epoch.ai URLs and hf datasets).
- Sensitivity pass on flagged merges (fit with/without GPQA + HMMT merges).
- Weighted index variants (knowledge-heavy vs instruction-following-heavy).
- Add cross-family small models (SmolLM, Llama 3.2 1B/3B, Phi-mini, OLMo) to
  de-bias new-era instrument parameters and sharpen the low-end trend.
- Consider LMArena dated snapshots as an external validity check (not fit input).
- Artificial Analysis: check ToS before using API/scraped data in anything published.
