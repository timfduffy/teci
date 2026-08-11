# Qwen/Gemma small-model capabilities index

Official + third-party benchmark scores for Qwen and Gemma models (<=35B, 2023-2026),
fitted onto the Epoch Capabilities Index scale three ways. See CLAUDE.md for the full
pipeline, conventions, and caveats.

Requires: python3, pandas, numpy, scipy, openpyxl, matplotlib.

## Running it

Refresh Epoch's published data (run from anywhere):

```bash
python scripts/fetch_epoch.py
```

The remaining scripts use flat relative paths and must be run from `data/`:

```bash
cd data && python ../scripts/prep_obs.py && python ../scripts/fit_methods.py
```

`fit_methods.py` takes roughly ten minutes: method A jointly fits ~3,400
observations and then bootstraps it 100 times. Chart scripts write PNGs into the
working directory, so move them to `charts/` afterwards.
