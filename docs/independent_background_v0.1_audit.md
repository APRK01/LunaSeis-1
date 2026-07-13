# Independent continuous-background audit v0.1

Date: 2026-07-13

## Selection and storage

The selection script reads the official PDS station/year/day directory frame, not an event-derived day list. Within each of 29 station-year strata it selects the first 32 days under fixed SHA-256 seed `lunaseis-independent-background-v0.1`. Days are selected before channel completeness inspection; unavailable days are retained and never replaced.

The fixed selection contains 928 station-days. ATT plus at least one primary MH channel is archive-complete for 727 days; 201 incomplete days remain in the audit. The download plan contains 5,554 MiniSEED/XML products totaling 1,585,898,632 bytes. Every product passed exact-size and official NASA-MD5 verification, including a final disk-only reconciliation. Of the 710 integrity-usable days, 516 are new relative to the prior positive audit plans and 194 overlap by chance/reuse after selection.

## Day and window integrity

Full-day gap auditing retains 710 days and rejects 17 complete days under the frozen 20% gap rule. Usable counts are S12 210, S14 203, S15 164, and S16 133. Applying a ±1-hour exclusion around every PDS and corrected shallow catalog time produces 22,444 distinct ten-minute catalog-negative windows (89,776 fold-specific rows). Catalog-negative remains an epistemic label; uncatalogued events and artifacts may remain.

## Shortcut audit

Validation-thresholded baseline comparison changed materially relative to the positive-conditioned pilot frame:

| Held-out station | Energy F1 / FP h⁻¹ | STA/LTA F1 / FP h⁻¹ | Logistic F1 / FP h⁻¹ |
|---|---:|---:|---:|
| S12 | 0.691 / 5.370 | 0.684 / 5.632 | 0.795 / 2.123 |
| S14 | 0.699 / 3.038 | 0.678 / 5.307 | 0.766 / 2.954 |
| S15 | 0.651 / 5.933 | 0.646 / 5.327 | 0.651 / 5.274 |
| S16 | 0.707 / 4.633 | 0.658 / 5.628 | 0.754 / 1.805 |

S12 logistic performance fell from F1 0.870 / 0.284 FP h⁻¹, confirming material background-frame inflation. S15 also deteriorated, while S16 improved. The independent results replace the old frame for future pilot model development, but remain diagnostic because false alarms are measured on sampled windows rather than merged triggers from fully contiguous scanning.

## Gate result

The independent-background and shortcut-audit conditions in Decision 0016 are satisfied for starting a small pilot neural experiment. No paper-level performance claim is authorized. Continuous full-day scanning rules, trigger merging, event matching, and the final untouched test execution must be frozen before headline evaluation.
