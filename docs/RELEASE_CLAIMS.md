# Release claims and evidence boundary

Last reviewed: 2026-07-14

This document controls public wording for the LunaSeis-1 repository, model card, manuscript, and future release pages.

## Claims supported by repository evidence

- LunaSeis-1 is a functioning research-software prototype that scores Apollo PSE MH MiniSEED waveforms with a compact depthwise-separable 1D CNN.
- The selected public model has 2,761 trainable parameters and one leave-one-station-out checkpoint for each of Apollo stations 12, 14, 15, and 16.
- The data pipeline verifies downloaded products against official NASA PDS sizes and MD5 digests, preserves gap sentinels, and records nominal and ATT-derived timing separately.
- The candidate registry contains 1,314 reconciled physical events and applies physical-event and known repeating-family grouping.
- Two prospectively frozen continuous evaluations totaling 5,242.87 station-hours failed the intended recall/false-alarm objective.
- The selected depthwise model reduced development trigger rate relative to the tiny CNN and compact TCN at matched development recall. This is development evidence only.
- A real full-day command-line smoke scan completed successfully but showed persistent activation, which is a documented model limitation.

## Claims prohibited by current evidence

- Do not call LunaSeis-1 an operational, flight-ready, production-ready, reliable, or validated moonquake detector.
- Do not claim that it detects moonquakes accurately on unseen continuous Apollo data.
- Do not describe development thresholds as calibrated probabilities.
- Do not claim state of the art, first lunar ML detector, first lunar CNN, first raw-waveform lunar model, first lightweight lunar model, or first telemetry-prioritization approach.
- Do not promote post-test depthwise development results to untouched-test evidence.
- Do not imply that catalog-negative windows are guaranteed physical noise.
- Do not claim that artifact proxy categories establish physical instrument causes.
- Do not publish catalog-derived labeled windows until redistribution terms are cleared.

## Literature-backed positioning

Knapmeyer-Endrun and Hammer (2015) already demonstrated automated Apollo 16 detection and broad classification with hidden Markov models. Civilini et al. (2021) applied compact CNNs trained on terrestrial data to Apollo PSE/LSPE recordings and discussed telemetry prioritization. Al-Qadasi and Bin Waheed (2026) evaluated compact FNO models on raw lunar waveforms and spectrograms, including small lunar training sets and efficiency comparisons. Onodera (2024) expanded the known shallow-moonquake inventory using short-period Apollo data.

LunaSeis-1 therefore positions its contribution as the combined, openly auditable protocol and negative result: checksum-backed reconstruction; ATT/gap provenance; event-, family-, chronology-, and station-aware leakage controls; independently selected background days; prospectively frozen continuous scans; false-trigger and retained-duration reporting; artifact diagnosis; and preservation of failed operational hypotheses.

This combination is a defensible study focus, not an absolute priority claim. The manuscript must say that the reviewed literature did not reveal an equivalent combined protocol, not that none exists.

