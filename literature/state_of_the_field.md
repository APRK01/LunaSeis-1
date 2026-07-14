# Initial state of the field

Last updated: 2026-07-14

Status: release-candidate claim audit complete for the direct Apollo ML predecessors. This is not an exhaustive systematic review of all planetary or terrestrial detector literature.

## What is already established

Apollo lunar seismic detection is not a new ML application. Deep-event template/correlation searches expanded catalogs substantially by 2003-2005. Hidden Markov models performed automated detection and broad classification on Apollo 16 by 2015. Civilini et al. (2021) used small CNNs trained on terrestrial spectrograms, evaluated them across PSE stations, applied them continuously to LSPE, discussed false detections, and explicitly motivated telemetry prioritization.

Most importantly for LunaSeis-1, Al-Qadasi and Bin Waheed (2026) already evaluate compact Fourier Neural Operators using both raw 1D waveforms and spectrograms, compare efficiency with CNNs, include Earth-only and Earth-plus-small-lunar-sample regimes, and discuss fast near-real-time use. Therefore LunaSeis-1 cannot present lightweight raw-waveform modelling, low parameter count, cross-domain application, or telemetry motivation alone as novelty.

## Data and label state has changed

The 2019 expanded PDS event bundle contains 28 traditional shallow-moonquake rows. Onodera (2024), using the restored short-period archive, reports 46 additional shallow moonquakes (74 total) and more than 22,000 newly detected short-period events. The PDS catalog currently audited by LunaSeis-1 is therefore not the latest complete scientific event inventory for every class.

Deep moonquakes repeat within source nests, and historic work is built on waveform correlation. A 2026 paper also reports repeating shallow moonquakes. Random event/window splitting would reward memorization and is scientifically unacceptable.

Liu et al. (2024) identifies temperature-related long-period signals across multiple PSE stations, probably instrument/heater induced. These can become station/time shortcuts or contaminate catalog-negative background. Artifact auditing is a central research requirement, not cleanup.

## Current defensible LunaSeis-1 direction

The strongest candidate contribution is a rigorously combined evaluation/reproducibility protocol:

- direct waveform compact baselines, acknowledging prior FNO/raw-waveform work;
- event-disjoint and repeating-family-disjoint leave-one-station-out evaluation;
- chronological validation without final-station tuning;
- continuous scanning with false positives per hour/day;
- calibrated confidence, abstention, and risk-coverage analysis;
- transparent event-recall versus retained-duration simulation;
- an authoritative PDS4/ATT-aware, provenance-rich construction pipeline;
- explicit artifact, gap, station, timing, and catalog-negative ambiguity controls.

The reviewed direct Apollo predecessors did not reveal a study combining strict family/event-disjoint PSE leave-one-station-out testing, independently selected background days, prospectively frozen continuous scans, operational false-trigger rates, and retained-duration reporting. This supports the study positioning but not an absolute first/novelty claim; absence from the reviewed set is not proof that no such work exists.

## Implications for experiments

1. Binary event detection stays primary.
2. Deep versus natural-impact classification is exploratory.
3. Shallow/artificial multiclass results are not a headline target in the initial PDS-only pilot.
4. The Onodera catalog must be obtained, licensed, and reconciled before final shallow-event conclusions.
5. Deep family IDs must be grouped; the same physical event must never cross station splits.
6. FNO is now a relevant published comparison, but implementing it is optional until simple baselines are stable.
7. Accuracy on balanced windows cannot establish operational value; continuous false-alarm measurement is mandatory.

## Literature gaps remaining

- Exhaustive citation chaining from the 2015, 2021, 2024, and 2026 direct predecessors.
- Exact FNO split construction, false-alarm units, parameter counts, code/weight availability, and moonquake sample provenance.
- Calibration and abstention studies for seismic detectors.
- Cross-station/domain-generalization protocols in terrestrial seismology.
- Event-triggered sensing/retention literature and realistic telemetry accounting.
- Access and schema audit for the Onodera 2024 updated catalog.

Public wording is governed by `docs/RELEASE_CLAIMS.md`. No absolute priority or state-of-the-art claim is authorized.
