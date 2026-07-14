# Decision 0022: select robust-level preprocessing on continuous development data

Date: 2026-07-14

Use 56 fixed-seed, previously unexposed station-days exclusively as continuous development validation. Quantized plateaus and step-like behavior are strongly station-dependent, so replace global training-fold amplitude scaling with per-window robust centering/scaling and clipping. Add deterministic continuous hard negatives from training stations only.

Select robust level rather than robust first differences. Both retain mean positive-validation recall 0.9115, while robust level produces 820 merged triggers over 1,998.85 fold-hours (0.4102 per hour), compared with 923 (0.4618 per hour) for first differences. Neither consumed test v0.1 nor untouched test v0.2 was read during selection.
