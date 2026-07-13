# Research protocol v0.2 — frozen pilot construction

Status: frozen for reproducible pilot baselines; final continuous-scanning frame remains blocked.

- Primary task: event versus `catalog_negative_background`; deep versus natural impact remains exploratory.
- Outer evaluation: four leave-one-station-out folds; physical events and deep families are indivisible; held-out-station groups are removed from other stations.
- Validation: latest 20% of remaining evaluation groups by earliest event time; thresholds and learned scaling use validation/training only.
- Timing: nearest valid ATT Earth-reception value maps the catalog reference to nominal MiniSEED time; all timing fields remain separate.
- Integrity: primary gap thresholds 20% usable / above 50% reject; ATT thresholds 1 s usable / above 10 s reject. Strict and lenient sensitivity results are mandatory.
- Primary waveform: one of MHZ, MH1, MH2 at 6.625 Hz, preference in that order; 600 s window (−120,+480); sentinel mask preserved; no interpolation; valid-sample median centering.
- Background terminology: catalog-negative, never physical noise. Exclude ±1 hour around all known catalog times and sample only after fold assignment.
- Pilot limitation: currently available background days were chosen for positive coverage. Pilot baseline numbers are diagnostic only.
- Pilot neural training: permitted after independent-background v0.1 and the shortcut audit in Decision 0017. Paper-level evaluation remains blocked until continuous-scanning duration, trigger merging, matching tolerance, and untouched final-test rules are frozen.
