# LunaSeis-1: When Balanced Apollo Seismic Detection Fails Under Cross-Station Continuous Scanning

**Advaith Praveen (APRK)**
Archeum Studios

## Abstract

Machine-learning models for lunar seismic detection are commonly developed from isolated event and background windows, but operational use requires low false-alarm rates across long continuous recordings and transfer to unseen stations. LunaSeis-1 constructs a checksum-verifiable Apollo Passive Seismic Experiment pipeline, reconciles 1,314 physical-event candidates, preserves Apollo timing/gap provenance, and evaluates lightweight detectors under event-, family-, chronology-, and station-aware controls. A 3,057-parameter tiny CNN appeared competitive on balanced windows but failed two prospectively frozen continuous evaluations. In the first frame (2,591.47 station-hours; six integrity-eligible events), the CNN recovered one event and produced 2,932 false triggers. In the second frame (2,651.4 station-hours; three events), an artifact-robust CNN recovered none and produced 847 false triggers. Station-specific quantization and acquisition artifacts caused persistent activation and severe background shift. A later 2,761-parameter depthwise CNN reduced development triggers to 0.2106/hour at 0.9115 mean development-event recall, but no untouched event-rich evaluation remained and a full-day smoke scan showed persistent activation. These results do not establish an operational lunar detector. Instead, they demonstrate that balanced-window evaluation can substantially overstate Apollo cross-station detection utility and provide a reproducible benchmark, failure analysis, and open research prototype for future work.

## 1. Introduction

Apollo seismic recordings remain a uniquely important record of lunar interior activity. Compact automatic detectors could assist archive analysis and, in simulation, prioritize waveform retention. However, lunar signals are emergent, instrument characteristics differ across stations and years, catalog timing semantics are imperfect, and background recordings contain substantial acquisition artifacts.

LunaSeis-1 asks whether a lightweight raw-waveform model can generalize to an excluded Apollo station while maintaining useful continuous false-alarm behavior. The study prioritizes operational falsification over balanced-window accuracy. Its contribution is the combined reproducible data pipeline, strict leakage controls, continuous scanning, artifact diagnosis, and preservation of negative evidence.

This is not the first application of automated learning to Apollo seismic detection. Knapmeyer-Endrun and Hammer (2015) used hidden Markov models for Apollo 16 event detection and classification. Civilini et al. (2021) applied CNNs trained on a terrestrial station to Apollo PSE and LSPE data and motivated telemetry prioritization. Al-Qadasi and Bin Waheed (2026) subsequently evaluated compact Fourier Neural Operators on raw waveforms and spectrograms. Onodera (2024) also demonstrated that short-period archive analysis materially expands the known shallow-moonquake inventory. LunaSeis-1 therefore does not claim architectural priority. Its study focus is the combined cross-station, family-aware, continuous operational stress test and the transparent preservation of its negative outcome.

## 2. Data

Waveforms come from NASA PDS bundle `urn:nasa:pds:apollo_pse::1.0`. Labels originate from `urn:nasa:pds:apollo_seismic_event_catalog::1.0` and the corrected Onodera shallow-moonquake tables. The unified candidate registry contains 609 deep moonquakes, 623 natural impacts, 74 shallow moonquakes, and eight artificial impacts.

All downloaded products are checked against official sizes and NASA MD5 hashes. Raw products are not redistributed. MiniSEED nominal timestamps and ATT-derived timing remain separate. Gap sentinels are never silently interpolated.

## 3. Leakage controls

Physical events and known repeating families are indivisible within folds. Station-held-out models cannot use statistics from the test station. Background dates are selected independently of event dates. Architecture and threshold decisions use training/validation data only. Two continuous test frames were selected and frozen before their corresponding inference runs; both are now permanently consumed.

## 4. Models

Comparisons include energy, STA/LTA, handcrafted logistic regression, a 3,057-parameter tiny CNN, robust variants, a 2,761-parameter depthwise CNN, and a compact dilated TCN. Neural inputs contain robust-normalized waveform values and a separate validity mask.

## 5. Continuous-scanning protocol

Models scan 600-second windows at a 60-second stride. Candidate reference time is window start plus 120 seconds. Positive windows merge when adjacent inferred references are separated by at most 300 seconds. Primary one-to-one catalog matching uses ±180 seconds, with ±60 and ±300-second sensitivity analyses. False alarms are normalized by the union of locally integrity-qualified duration.

## 6. Results

### 6.1 First frozen test

Over 2,591.47 station-hours, the tiny CNN, logistic regression, and STA/LTA recovered 1/6, 1/6, and 0/6 eligible events. False-trigger rates were 1.131, 0.121, and 0.282 per hour; retained-duration fractions were 75.50%, 40.28%, and 97.92%.

### 6.2 Artifact diagnosis and second frozen test

Development data revealed strong station differences in quantized plateaus, steps, and extreme-value occupancy. Robust normalization reduced the tiny CNN’s second-test false-trigger rate from 0.923 to 0.319/hour and retention from 62.48% to 45.58%. Nevertheless, robust CNN, original CNN, logistic, and STA/LTA all recovered 0/3 eligible events. Logistic regression remained best by false-trigger rate at 0.185/hour.

### 6.3 Later architecture development

At identical mean positive-development recall of 0.9115, the depthwise CNN produced 0.2106 merged triggers/hour, compared with 0.4102 for robust tiny CNN and 0.4558 for compact TCN. This selection occurred after both tests and cannot be promoted to untouched-test evidence. A full-day CLI smoke scan also revealed persistent activation.

## 7. Discussion

Balanced event/background windows did not predict continuous behavior. Station and acquisition regimes create powerful shortcuts, and trigger merging can hide nearly continuous positive-window activation behind apparently moderate trigger counts. Retained-duration reporting is therefore essential alongside trigger frequency.

The small event denominators prevent stable recall estimates, but the long background exposure robustly demonstrates operational false-alarm problems. The missed-event audit does not support a universal timing correction: score peaks occur widely over ±2 hours and expanding tolerance would mainly relabel background triggers.

## 8. Limitations

- No untouched event-rich set remains after the iterative pilot program.
- Catalog references may not correspond to consistent physical arrivals.
- Many eligible test windows have weak raw signal evidence.
- Artifact proxy categories are not authoritative physical diagnoses.
- Calibration is not meaningful evidence when final-test recall is zero.
- The release model remains an experimental prototype.

## 9. Conclusion

LunaSeis-1 does not demonstrate an operational moonquake detector. It demonstrates why apparently successful compact models can fail on continuous Apollo data and supplies a reproducible platform for improving them. Future confirmation requires better arrival-aligned labels, explicit artifact taxonomy, event-rich prospective reservation, and a new untouched evaluation.

## Data and code availability

Code, manifests, small checkpoints, configurations, predictions, and derived figures are prepared for public release. Raw NASA files are reconstructed from official PDS sources and are not mirrored. Release URLs and archival DOI will be inserted only after explicit publication authorization.

## References

- Al-Qadasi, B., & Bin Waheed, U. (2026). Fourier Neural Operator for Moonquake Detection. *Earth and Space Science*, 13, e2025EA004792. https://doi.org/10.1029/2025EA004792
- Civilini, F., Weber, R. C., Jiang, Z., Phillips, D., & Pan, W. D. (2021). Detecting moonquakes using convolutional neural networks, a non-local training set, and transfer learning. *Geophysical Journal International*, 225(3), 2120–2134. https://doi.org/10.1093/gji/ggab083
- Knapmeyer-Endrun, B., & Hammer, C. (2015). Identification of new events in Apollo 16 lunar seismic data by Hidden Markov Model-based event detection and classification. *Journal of Geophysical Research: Planets*. https://doi.org/10.1002/2015JE004862
- Nunn, C., Nakamura, Y., Kedar, S., & Panning, M. P. (2022). A New Archive of Apollo's Lunar Seismic Data. *The Planetary Science Journal*. https://doi.org/10.3847/PSJ/ac87af
- Onodera, K. (2024). New Views of Lunar Seismicity Brought by Analysis of Newly Discovered Moonquakes in Apollo Short-Period Seismic Data. *Journal of Geophysical Research: Planets*. https://doi.org/10.1029/2023JE008153
