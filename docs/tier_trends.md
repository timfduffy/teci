# Tier trends (method A)

| family | tier | n | span (yrs) | slope TECI/yr | mean TECI |
|---|---|---:|---:|---:|---:|
| Qwen | ≤2B | 16 | 2.25 | +13.21 | 108.2 |
| Qwen | 2–10B | 16 | 2.51 | +18.68 | 122.5 |
| Qwen | >10B | 20 | 2.92 | +16.07 | 131.7 |
| Gemma | ≤2B | 9 | 1.33 | +6.26 | 98.9 |
| Gemma | 2–10B | 11 | 2.08 | +10.70 | 114.6 |
| Gemma | >10B | 9 | 2.00 | +14.49 | 128.9 |
| Llama | ≤2B | 2 | 0.00 | — | 94.6 |
| Llama | 2–10B | 8 | 1.17 | +5.34 | 104.2 |
| Llama | >10B | 2 | 0.00 | — | 103.0 |
| Phi | ≤2B | 2 | 0.00 | — | 88.6 |
| Phi | 2–10B | 7 | 1.17 | +8.75 | 117.4 |
| Phi | >10B | 3 | 0.59 | — | 123.6 |
| SmolLM | ≤2B | 12 | 0.25 | — | 90.7 |
| OLMo | ≤2B | 1 | 0.00 | — | 88.9 |
| OLMo | 2–10B | 6 | 0.75 | — | 102.8 |

## Size-gap estimate under each sample / tier definition

| definition | small-tier n | gap (TECI/yr) |
|---|---:|---:|
| Qwen/Gemma only, previous fit | 25 | 3.30 |
| same entries, recalibrated instruments | 25 | 2.77 |
| + cross-family models ≥0.5B | 34 | 1.90 |
| + SmolLM's sub-0.5B models | 42 | 1.21 |

## The same models in finer bands

| band | n | slope TECI/yr | mean TECI | mean release |
|---|---:|---:|---:|---|
| <1B | 17 | +16.8 | 95.3 | 2024-11 |
| 1–2B | 25 | +15.4 | 101.8 | 2024-08 |
| 2–5B | 21 | +13.8 | 118.9 | 2025-01 |
| 5–15B | 41 | +15.8 | 114.1 | 2024-06 |
| 15–35B | 20 | +15.2 | 134.5 | 2025-05 |

Banded this way there is no consistent size gradient in *rate* — every band sits
between +13.8 and +16.8 TECI/yr. Size sets the level, not the slope.

That contradicts the pooled tier gap above, and the reason is composition inside the
small tier. `<1B` fits +16.8/yr and `1–2B` fits +15.4/yr, but pooled as
`≤2B` they fit +14.0/yr — below both. The `<1B` models sit lower (mean 95.3 vs 101.8)
and later (mean release 2024-11 vs 2024-08), so a single line through both is dragged
down at its recent end. The large tier has no such split: `5–15B` and `15–35B` fit
+15.8 and +15.2, and pooled `>10B` fits +15.2.

So a good part of the reported size gap is unequal time-sampling within the small
tier rather than a difference in how fast small models improve. Treat the pooled
tier gap as an upper bound.
