# Pilot dataset, splits, preprocessing, and baselines v0.1

Date: 2026-07-13

## Leakage-safe split assignment

Four LOSO folds hold out S12, S14, S15, or S16. Physical-event and repeating-family groups are indivisible. Any group present at the held-out station is test-only and removed from every other station's training/validation data. Remaining groups are ordered by earliest reference time; the latest 20% form validation. The generated manifest contains 4,747 positive event-station assignments and passes the one-role-per-evaluation-group invariant within every fold.

## Catalog-negative candidates

Background sampling occurs after fold assignment. The 81,980 deterministic ten-minute candidates use a ±1-hour exclusion around every PDS and corrected shallow catalog time, never claim physical noise, and preserve station/channel/time/fold provenance. Their source days were selected originally for positive-event coverage, so this is a biased pilot frame and cannot replace independently selected long-duration continuous scanning.

## Frozen primary preprocessing v0.1

The primary pilot uses one available mid-period channel in order MHZ, MH1, MH2 at native 6.625 Hz. Windows are 120 s before through 480 s after the ATT-mapped reference. Gap sentinels are preserved as a mask, never interpolated, and replaced by zero only after valid-sample median centering. SHZ remains available for sensitivity/descriptive work but is excluded from the primary representation because its 53 Hz rate is materially different. The positive preprocessing manifest contains 3,910 fold-specific windows.

## Preliminary baselines

Energy/RMS, STA/LTA, and regularized logistic regression on five handcrafted features were run with validation-only threshold selection. Test results are pilot diagnostics, not paper results:

| Held-out station | Energy F1 / FP h⁻¹ | STA/LTA F1 / FP h⁻¹ | Logistic F1 / FP h⁻¹ |
|---|---:|---:|---:|
| S12 | 0.680 / 5.674 | 0.679 / 5.779 | 0.870 / 0.284 |
| S14 | 0.685 / 4.272 | 0.681 / 5.680 | 0.729 / 3.868 |
| S15 | 0.686 / 5.613 | 0.676 / 5.972 | 0.748 / 1.949 |
| S16 | 0.679 / 5.867 | 0.680 / 5.642 | 0.680 / 1.912 |

The anomalously strong S12 logistic result triggers a shortcut audit. Likely risks include positive-day selection, temporal/channel distribution mismatch, station-specific acquisition artifacts, and catalog-conditioned background construction. No neural model will be trained and none of these metrics will be promoted until an independently selected continuous background frame and shortcut audit exist.
