# LunaSeis-1 roadmap

The detailed roadmap and constraints are in `PROJECT_CONTEXT.md`, section 26.

## Current phase: Phase 1 — literature and data audit

Success criterion: starting from one verified catalogued event timestamp, automatically identify and obtain its Apollo waveform, load it with correct station/channel metadata, and produce a scientifically valid waveform plot. **Achieved for the Apollo 15 S-IVB pilot on 2026-07-13.**

1. Establish permanent context and repository foundation.
2. Verify official waveform bundle and event catalog identifiers, versions, formats, archive structure, stations, channels, timestamps, sample rates, and redistribution guidance.
3. Implement and test a catalog/metadata downloader.
4. Select one verified event and download the smallest practical corresponding waveform sample. Completed for Apollo 15 S-IVB.
5. Validate metadata, align the event, and plot the waveform window. Completed with explicit nominal/ATT timing and gap audit.
6. Record the feasibility decision before proceeding to Phase 1. Completed in `docs/phase0_alignment_result.md`.

Phase 1 initial scoping completed on 2026-07-13:

- decoded PDS event types, grades, visibility fields, and initial counts;
- audited exact duplicate minutes and repeating deep-family structure;
- froze binary detection as primary and broad multiclass as unsupported for the PDS-only pilot;
- designed event/family-disjoint leave-one-station-out evaluation;
- completed the first systematic literature search pass and revised candidate novelty;
- recorded conservative publication policy pending written PDS clarification for catalog-derived datasets.
- reconciled the corrected 74-event Onodera shallow catalog against PDS (28 exact legacy matches and 46 new events), verified at least one SHZ+ATT station-day per event, and produced an MD5-backed 0.73 GiB download plan;
- retained shallow classification as descriptive/exploratory pending event-window QA.
- checksum-downloaded and visually audited KO-SMQ-26 as the first updated-catalog waveform; its emergent SHZ signal is visible with explicit ATT mapping and isolated gap sentinels.
- downloaded and MD5-verified all 508 shallow-plan products, audited 128 event-station windows, and retained at least one usable raw window for every one of the 74 events.
- built a 1,314-event unified positive candidate registry with corrected source merging, exact provenance, rejected-window retention, and event/family leakage groups; overlap/conflict checks passed.
- audited nonshallow PDS availability and produced an exact 15,106-product, 7.11 GiB checksum-backed plan in four bounded batches; 1,159 of 1,240 candidates retain an archive-backed positive station request.
- downloaded and MD5-verified all 5,398 Batch 1 products and audited 658 events: 648 usable, two questionable, and eight rejected for raw gap/ATT integrity.
- downloaded and MD5-verified all 3,270 Batch 2 products and audited 599 events: 586 usable, three questionable, and ten rejected within the batch; cross-station aggregation now leaves nine rejected-only events.
- completed Batches 3 and 4, closing all 15,106 planned products and all 1,159 archive-backed events; final aggregation is 1,146 usable, three questionable, ten rejected-only, and 81 archive-unavailable nonshallow candidates.
- froze pilot ATT mapping, integrity sensitivities, leakage-safe LOSO assignments, primary MH preprocessing, and catalog-negative candidate construction.
- ran three classical pilot baselines; high false-alarm rates and an anomalous S12 handcrafted result triggered a neural-training gate pending an independent continuous background frame and shortcut audit.
- selected 928 official-archive days independently of event dates, verified 1.586 GB of ATT/MH products, retained 710 integrity-usable days, and built 22,444 event-buffered catalog-negative windows.
- reran all baselines on the independent frame; the S12 result degraded materially, confirming the shortcut concern and opening only pilot neural training while final claims remain blocked.
- trained a deterministic 3,057-parameter tiny CNN across all four LOSO folds, preserved a failed temporal-averaging ablation, and found mixed station-dependent results that do not support consistent superiority over logistic regression.
- completed waveform/missingness shortcut counterfactuals, measured local efficiency, saved checkpoints/predictions/configuration, and froze continuous-scanning protocol v0.1 before any contiguous evaluation.
- selected two untouched 14-day blocks per station without event/model conditioning, verified zero prior station-day overlap, and produced a 448-product, 163.4 MiB NASA-MD5-backed plan covering 2,688 station-hours.
- audited catalog coverage only after selection: seven events remain prospectively recall-eligible pending waveform QA, so false-trigger measurement is primary and recall will be descriptive.
- downloaded and twice size/MD5-verified all 448 contiguous-frame products, loaded all 112 ATT/MH pairs, and audited full-day plus 60-second-stride window integrity without model inference.
- froze 152,986 scan windows spanning 2,591.47 union station-hours and six integrity-eligible events; one candidate was rejected for severe gaps/ATT displacement.

Phase 1 remains active for exhaustive literature chaining, untouched contiguous scanning, and release/licensing clarification. Pilot neural development is permitted; final claims remain blocked.

Later phases: literature/data audit; reproducible preprocessing; baselines; compact neural models; generalization/calibration; continuous scanning/retention simulation; reproduction audit; paper; public release.
