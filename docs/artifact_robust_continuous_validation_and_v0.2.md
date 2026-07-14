# Artifact-robust development and continuous evaluation v0.2

Date: 2026-07-14

## Development frame

Before inspecting model scores, LunaSeis-1 selected one fixed-seed 14-day block per station after excluding every station-day exposed by prior manifests. All 56 days were archive-complete. All 224 products (84,837,751 bytes) passed official NASA PDS size and MD5 verification.

Gap and catalog-buffer auditing produced 57,823 development windows spanning 993.85 physical station-hours. Engineering artifact proxies showed pronounced station shift: step-like/plateau-like/extreme-value counts were 13,573/14,771/13,485 at S12, 8,977/10,389/8,618 at S14, 6,918/14,126/6,980 at S15, and only 51/397/339 at S16. These are proxy descriptions, not physical artifact labels.

## Development-only model selection

Two predeclared candidates used the same 3,057-parameter tiny CNN:

- robust level: per-window valid-sample median, robust scale `max(1, 1.4826 MAD, p90(|x-median|)/2.5)`, clipping to ±20, and a validity mask;
- robust difference: the same transform after first differencing valid adjacent samples.

Training included deterministic hard negatives from the first half of continuous development blocks at training stations. Thresholds retained at least 90% of prior positive-validation events. Candidate selection used only the second half of training-station development blocks.

| Candidate | Mean validation-event recall | Merged triggers | Fold-hours | Triggers/hour |
|---|---:|---:|---:|---:|
| Robust level | 0.9115 | 820 | 1,998.85 | 0.4102 |
| Robust difference | 0.9115 | 923 | 1,998.85 | 0.4618 |

Robust level was frozen before test v0.2 inference.

## Untouched frame v0.2

A separate seed selected two nonoverlapping 14-day blocks per station after excluding all earlier positive, background, validation, and consumed-test days. No selected day overlapped prior manifests. All 448 products (171,072,240 bytes) passed NASA size and MD5 verification.

Integrity QA retained 157,363 sliding windows covering 9,545,040 union seconds (2,651.4 station-hours). Three prior-unexposed events were prospectively eligible and all passed window integrity. Two had weak raw RMS ratios and one lacked a clear ratio; labels were unchanged.

## Frozen operational result

Primary matching uses ±180 seconds and 300-second trigger merging.

| Method | Event recall | False triggers | FP/hour | Retained duration |
|---|---:|---:|---:|---:|
| Artifact-robust CNN | 0/3 | 847 | 0.3195 | 45.58% |
| Original tiny CNN | 0/3 | 2,448 | 0.9233 | 62.48% |
| Handcrafted logistic | 0/3 | 490 | 0.1848 | 35.22% |
| STA/LTA | 0/3 | 543 | 0.2048 | 96.49% |

Robust preprocessing reduces the original CNN false-trigger burden by 65.4% and retained duration by 27.0% relative, but it does not beat logistic regression and detects none of the three eligible events. This is not operational success and does not support H1 or H6. The three-event recall denominator is too small for a stable headline estimate.

Both continuous test frames are now consumed. Further model work requires a revised research question and new prospectively selected data; neither frame may be used for tuning.
