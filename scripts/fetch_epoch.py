#!/usr/bin/env python3
"""Fetch Epoch's published ECI/EDI/benchmark CSVs and build the repo's copies.

Replaces the WebFetch-relayed files from the original Cowork session. Unlike the
other scripts this one resolves paths from its own location, so it can be run
from anywhere:

    python scripts/fetch_epoch.py

Writes, under data/:
  raw/eci_scores.csv, raw/edi_scores.csv, raw/eci_benchmarks.csv
      untouched downloads, kept for provenance, with raw/FETCHED.txt recording
      the URL, timestamp, byte count and sha256 of each.
  eci_published.csv          model, eci, date + Epoch's published CIs
  edi_frozen.csv             benchmark, edi, slope + chance baseline
  eci_benchmarks.csv         the full model x benchmark matrix

The baseline column is not part of Epoch's CSV: it is chance level per benchmark,
taken from RANDOM_BASELINES in eci-upstream/src/eci/dataloader.py so that our
chance-correction in prep_obs.py matches the correction Epoch already applied to
the published matrix.
"""
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"

# Epoch's own chance-level table, so we correct scores exactly as they do.
sys.path.insert(0, str(ROOT / "eci-upstream" / "src"))
from eci.dataloader import RANDOM_BASELINES  # noqa: E402

URLS = {
    "eci_scores.csv": "https://epoch.ai/data/eci_scores.csv",
    "edi_scores.csv": "https://epoch.ai/data/edi_scores.csv",
    "eci_benchmarks.csv": "https://epoch.ai/data/eci_benchmarks.csv",
}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [f"fetched: {stamp}", ""]
    for name, url in URLS.items():
        with urlopen(url) as r:
            blob = r.read()
        (RAW / name).write_bytes(blob)
        digest = hashlib.sha256(blob).hexdigest()
        lines.append(f"{name}\n  url:    {url}\n  bytes:  {len(blob)}\n  sha256: {digest}")
        print(f"  {name:22s} {len(blob):>8,d} bytes")
    (RAW / "FETCHED.txt").write_text("\n".join(lines) + "\n")
    return stamp


def build():
    # ---- ECI scores: keep the repo's column names, carry the published CIs.
    sc = pd.read_csv(RAW / "eci_scores.csv")
    (sc[["Model", "eci", "date", "eci_ci_low", "eci_ci_high"]]
       .rename(columns={"Model": "model"})
       .to_csv(DATA / "eci_published.csv", index=False))

    # ---- EDI: Epoch's difficulty/slope, plus chance baseline from upstream.
    edi = (pd.read_csv(RAW / "edi_scores.csv")
             .rename(columns={"benchmark_name": "benchmark",
                              "estimated_slope_scaled": "slope"}))
    edi["baseline"] = edi.benchmark.map(RANDOM_BASELINES).fillna(0.0)
    edi[["benchmark", "edi", "slope", "baseline"]].to_csv(DATA / "edi_frozen.csv", index=False)

    # Benchmarks Epoch scores but upstream has no baseline for: default 0.0 is
    # right for generative/agentic evals, wrong for anything multiple-choice.
    unknown = sorted(set(edi.benchmark) - set(RANDOM_BASELINES))
    if unknown:
        print(f"  no upstream baseline (defaulted to 0.0): {', '.join(unknown)}")

    # ---- Full matrix.
    bench = pd.read_csv(RAW / "eci_benchmarks.csv")
    bench.to_csv(DATA / "eci_benchmarks.csv", index=False)
    print(f"\n  eci_published.csv  {len(sc):>5,d} models")
    print(f"  edi_frozen.csv     {len(edi):>5,d} benchmarks "
          f"({(edi.baseline > 0).sum()} with nonzero baseline)")
    print(f"  eci_benchmarks.csv {len(bench):>5,d} obs, "
          f"{bench.model.nunique()} models x {bench.benchmark.nunique()} benchmarks")


if __name__ == "__main__":
    print("downloading:")
    stamp = fetch()
    print("\nbuilding:")
    build()
    print(f"\ndone ({stamp})")
