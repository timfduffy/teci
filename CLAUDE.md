# Small-model capabilities index (TECI: small models grafted onto Epoch's ECI scale)

Tim's project tracking whether benchmark progress differs across model sizes
(core question: is the 0.5–2B tier plateauing relative to ~30B?), by placing
small models on the Epoch Capabilities Index (ECI) scale. Our resulting numbers
are called TECI, not ECI — see Conventions. Qwen and Gemma are
the backbone (80 entries, full vendor benchmark suites); SmolLM, OLMo, Llama
and Phi were added later from the Open LLM Leaderboard (43 entries) to keep the
low end from being calibrated by Qwen and Gemma alone.
Intended for eventual publication (at least a Twitter post).

## Pipeline (run in this order)

Scripts 1–5 use flat relative paths and must be run **from `data/`**
(e.g. `cd data && python ../scripts/fit_methods.py`); chart PNGs land in
`data/` and get moved to `charts/`. `fetch_epoch.py` resolves paths from its
own location and can be run from anywhere.

0. `scripts/fetch_epoch.py` — downloads Epoch's three published CSVs and builds
   `data/eci_published.csv`, `data/edi_frozen.csv`, `data/eci_benchmarks.csv`.
   Keeps untouched copies plus sha256s in `data/raw/`. Re-run to pick up new
   Epoch releases; everything downstream then needs re-running too.
1. `scripts/build_benchmarks.py` — builds `data/qwen_gemma_benchmarks.xlsx`
   from hardcoded official vendor scores (Qwen blogs/tech report/model cards;
   Google model cards/tech reports). Later sheets (OLL, LiveBench, Gemma 4
   card re-eval, Qwen3.5 thinking rows) were appended by follow-up scripts in
   the original session — the shipped xlsx is the source of truth; do NOT
   regenerate it from build_benchmarks.py alone or those additions are lost.
1b. `scripts/add_oll_models.py` — appends the "OLL cross-family" sheet
   (SmolLM/OLMo/Llama/Phi from the Open LLM Leaderboard, official-provider
   uploads ≤35B) to the xlsx. Re-runnable; replaces the sheet in place.
2. `scripts/audit_connectivity.py` — model×benchmark connectivity audit
   (components, generation bridges, merge assumptions). Output: docs/connectivity_audit.md.
   Covers all six families, plus a cross-family section: which instruments are
   shared between families and how each added family joins the Qwen/Gemma core.
   Adding a family means adding it to `GEN_ORDER`.
2b. `scripts/sensitivity.py` — refits method A with each flagged merge reversed.
   Output: docs/sensitivity.md.
3. `scripts/prep_obs.py` — xlsx → `data/obs_ours.csv` (entry, instrument,
   baseline-corrected performance in [0,1]).
4. `scripts/fit_methods.py` — fits methods A/B/C → `data/results_methods.csv`.
5. `scripts/mk_charts.py`, `scripts/mk_chart_qwen.py` — Qwen/Gemma charts.
   `scripts/mk_chart_families.py` — cross-family charts (per-family small
   multiples; the size-gap estimate under each sample/tier definition) plus
   `docs/tier_trends.md`, the table-view twin. All dataviz-styled PNGs; size
   tier is an ordered category so it uses the ordinal blue ramp, not
   categorical hues.

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
- **Our numbers are TECI ("Tim's ECI"), never plain "ECI".** Epoch has published
  no ECI for any model we score; our values are estimates calibrated onto their
  scale via the 204 models they *have* scored (method A's rescale, r=0.9998).
  Charts and generated docs say `Tim's ECI (TECI)` on the axis, `TECI/yr` for
  rates, and carry the footnote in `TECI_NOTE` (defined per chart script).
  Naming follows Anthropic's convention for their own variant ("Anthropic ECI"):
  owner's name in front of the metric. The footnote deliberately does NOT copy
  Anthropic's "not directly comparable" caveat — theirs uses internal benchmarks,
  ours is calibrated onto Epoch's scale on purpose. What differs is *coverage*,
  not comparability. Reserve unqualified "ECI" for Epoch's own published values
  (`data/eci_published.csv`, and the diamonds on the method-agreement chart).
- **Bridge on Epoch's `model_version` column, never on the display name.**
  Epoch's names drop the base/instruct distinction that the entry convention
  depends on: 14 of their 222 nodes pool base and instruct observations under
  one name, and instruction tuning is worth a median +11 TECI in our own fit.
  Two bridges were wrong on exactly this before the "Fix two mis-specified
  bridge nodes" commit. `Llama 3-8B` is the one bridge knowingly left pooled
  (1 base observation out of 9).

## Fit methods

- **A (headline): joint refit** of our obs + `data/eci_benchmarks.csv`
  (Epoch's full 222-model matrix; 18 bridge nodes merged), rescaled via the
  remaining 204 pure-Epoch models against `data/eci_published.csv`, r=0.9998.
  327 nodes × 176 instruments, 3,652 observations. Every difficulty and slope
  is re-estimated — nothing of Epoch's published EDI/slope is held fixed; their
  role is the observation matrix plus the final affine rescale.
- **B: frozen graft** — `data/edi_frozen.csv` (Epoch's published EDI/slope, ECI
  units) held fixed; our-only instruments estimated by alternation.
  Known bias: runs 3–8 pts high for top thinking entries (vendor-reported
  scores vs Epoch's own harness on GPQA/HLE/Aider).
- **C: standalone** fit + affine map via the 18 bridge models. Degrades for
  thin-observation entries: the OLL cross-family entries carry only six
  observations each, and phi-4 lands ~12 pts low under C (and ~10 low under B)
  against its published ECI, where A — which also sees Epoch's data for that
  node — is within 2.4.
- Model spec mirrors `eci-upstream/` (epoch-research/eci-public, MIT):
  performance = σ(slope·(cap − difficulty)), ridge 0.1, scipy trf least
  squares, Winogrande slope pinned; scale anchors Claude 3.5 Sonnet=130, GPT-5=150.

## Data provenance / caveats

- All three Epoch files are now downloaded directly by `fetch_epoch.py`
  (2026-08-11); `data/raw/FETCHED.txt` records URL, size and sha256 for each.
  The WebFetch-relayed versions are gone — see git history before the
  "Refresh Epoch data" commit if you need to compare.
- The `baseline` column in `edi_frozen.csv` is **not** Epoch's data: it is
  chance level per benchmark, read from `RANDOM_BASELINES` in
  `eci-upstream/src/eci/dataloader.py` so our chance-correction matches the
  one Epoch already applied to their published matrix. 12 of 57 benchmarks
  have a nonzero baseline; the rest default to 0.0, which is right for
  generative/agentic evals but would be wrong for any new multiple-choice
  benchmark Epoch adds — check new names against upstream when re-fetching.
- Epoch's published `performance` values are **already chance-corrected**
  (verified: Winogrande ranges down to 0.030, MMLU to 0.011), so they merge
  directly with `prep_obs.py` output in method A's joint fit.
- What the refresh corrected, for the record: the old 348-row matrix was
  truncated alphabetically (Amazon→Grok), so every Qwen model was missing —
  including 12 sub-35B Qwen entries with published ECI (86.6–118.8) that now
  anchor the low-capability end, and the two Qwen bridge nodes which had been
  listed in BRIDGE but contributed no Epoch observations. It also carried a
  row-shift error giving Gemma 2B (a bridge node) Gemma 7B's ARC AI2 value.
  The old `edi_frozen.csv` tracked an **earlier Epoch EDI revision** rather
  than being garbled — its two extra benchmarks (GBAEval, "SWE-Bench Verified
  (Bash Only)") are both real Epoch names since renamed or dropped.
- Flagged identity assumptions to re-verify before publishing: Qwen2/2.5
  "GPQA" == Diamond (2507 confirmed, 2.5 not); HMMT'25 (2507) vs HMMT Feb'25
  (card shows 57.5 vs 55.5 — keep separate or flag); Qwen3 LiveBench release
  == 2024-11-25; Arena-Hard version across Qwen2.5/3; LCB "v6" windows.
- OLL v1 GSM8K anomalies (Qwen1.5-4B/32B-Chat) and Qwen2.5-0.5B MATH=0.00
  are excluded via ANOMALY notes in the xlsx.
- LiveBench Qwen2.5-7B rows = hosted "turbo" variant (flagged; matches vendor
  0831 value closely).

## Open TODOs

- ~~Re-download full Epoch matrix + exact CSVs~~ — done 2026-08-11 via
  `fetch_epoch.py`.
- Consider adding Epoch's sub-35B Qwen models as *entries* rather than only as
  calibration nodes. They are base/code models (`Qwen-1_8B`, `Qwen2.5-Coder-*`)
  and so are NOT the same entry as our Chat/Instruct rows under the
  entry convention — they cannot be merged as bridges without breaking it.
- Sensitivity pass on flagged merges (fit with/without GPQA + HMMT merges).
- Weighted index variants (knowledge-heavy vs instruction-following-heavy).
- ~~Add cross-family small models (SmolLM, Llama 3.2 1B/3B, Phi-mini, OLMo)~~ —
  done via `add_oll_models.py` (43 entries, 17 sub-2B). **Partial fix only:**
  OLL froze 2025-03-13, so this de-biases the 2023–2024 span of the trend, not
  its most recent points. Our 2025+ small entries still rest almost entirely on
  family-scoped `Qwen::*`/`Gemma::*` instruments, and no available source fixes
  that — LiveBench (the one modern cross-family harness we use) has nothing
  below ~3.8B, and Epoch's low-end coverage is all 2018–2022 instruments.
  State this as a known limitation when publishing.
- Extend `audit_connectivity.py` past Qwen/Gemma so the cross-family entries
  appear in the audit (connectivity itself is verified: 1 component, 123
  entries, none below 4 instruments).
- Liquid AI's LFM2/LFM2.5 (230M–8B) sit right in the tier of interest but have
  no shared-harness coverage at all — absent from OLL, Epoch and LiveBench.
  Only route is vendor cards, which reintroduces the vendor-vs-harness bias.
- Consider LMArena dated snapshots as an external validity check (not fit input).
- Artificial Analysis: check ToS before using API/scraped data in anything published.
