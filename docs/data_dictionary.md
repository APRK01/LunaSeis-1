# Data dictionary

## `data/manifests/events_audit.csv`

This is a local analytical index derived from `levent.1008weber.csv`; it is not a final training manifest or a replacement for the official catalog.

| Field | Meaning |
|---|---|
| `source_row` | One-based row number in the source CSV after its header |
| `event_key` | Stable LunaSeis audit identifier derived from source row |
| `catalog_start_minute` | Parsed `Y/JD/S` catalog start minute without a timezone suffix; exact time basis remains under audit |
| `type_code_t2` | PDS-defined current event type code |
| `event_class` | Lossless LunaSeis decoding of T2 |
| `family_id` | Deep-moonquake family `A{N2}` where assigned |
| `grade` | Bulow A/B/C grade or `ungraded` |
| `trace_count_reported` | Catalog's reported number of visible traces, when present |
| `positive_visibility_channels` | Semicolon-separated modern station/channel mapping of positive Bulow flags |
| `positive_visibility_stations` | Stations with at least one positive flag |
| `conservative_pilot_eligible` | `1` only under the documented A/B primary-class visibility rule |

Important: blanks in source visibility fields mean unclear/not positively marked, not confirmed absence. `catalog_start_minute` is not a phase pick.

## `data/manifests/event_label_audit.json`

Contains authoritative code/grade decoding, full and conservative counts, year/station/channel breakdowns, exact duplicate-minute checks, assigned deep-family sizes, and limitations. Counts describe catalog metadata and may shrink after waveform availability and gap validation.

## Updated shallow-event manifests

- `onodera_2024_shallow_events.csv`: 74 corrected event records, provenance group, reported/audited stations, positive PDS SP visibility, and row-level reconciliation status.
- `onodera_2024_reconciliation.json`: source DOIs/license, schema, reconciliation counts, limitations, and SHA-256 for the event CSV.
- `onodera_2024_shallow_coverage.csv`: one row per requested event-station pair with ATT/SHZ/label availability and selected daily bytes.
- `shallow_pilot_download_plan.json`: deduplicated official product paths, URLs, exact byte sizes, and NASA manifest MD5 values. This is a plan, not downloaded data.
- `ko_smq_26_sample_download.json`: checksum-verification receipt for the representative S15 day, including local paths, exact bytes, and verified MD5 values.
- `shallow_plan_download_receipt.json`: aggregate proof that all 508 planned products and 779,909,406 bytes passed exact size and MD5 verification.
- `shallow_window_quality.csv`: one row per complete event-station pair with ATT mapping, SHZ/ATT gaps, raw RMS screening values, descriptive signal support, and integrity status.

## Unified positive-event registry

- `unified_positive_events.csv`: one row per physical positive candidate with source/time/label provenance, event and evaluation groups, reported stations/channels, shallow-window QA aggregation, candidate status, and release note. It is not a frozen training manifest.
- `unified_positive_event_audit.json`: exact class/station counts, source reconciliation, QA coverage, leakage-group counts, duplicate/conflict checks, scope warning, and SHA-256 of the unified CSV.

## Nonshallow waveform plan

- `nonshallow_waveform_requests.csv`: one row per event/station request with positive channels, boundary-complete station-days, complete/missing channel results, and station-request usability.
- `nonshallow_download_plan.json`: exact selected product paths, URLs, bytes, official MD5 values, deterministic batch IDs/summaries, missing-event list, channel totals, and request-manifest SHA-256. It is a plan, not downloaded data.
- `nonshallow_batch_1_download_receipt.json`: exact-size/MD5 verification receipt for all 5,398 Batch 1 products.
- `nonshallow_batch_1_window_quality.csv`: one row per audited positive channel with ATT mapping, gaps, raw range/edge occupancy, descriptive RMS, and integrity status.
- `nonshallow_batch_1_request_quality.csv`: channel-integrity aggregation per physical event/station request.
- `nonshallow_batch_2_download_receipt.json`: exact-size/MD5 verification receipt for all 3,270 Batch 2 products.
- `nonshallow_batch_2_window_quality.csv`: Batch 2 positive-channel ATT/gap audit with descriptive raw metrics.
- `nonshallow_batch_2_request_quality.csv`: Batch 2 channel-integrity aggregation per physical event/station request.
- `nonshallow_batch_{3,4}_download_receipt.json`: exact-size/MD5 receipts for the remaining planned products.
- `nonshallow_batch_{3,4}_window_quality.csv`: ATT-aware positive-channel audits for the remaining batches.
- `nonshallow_batch_{3,4}_request_quality.csv`: event/station channel-integrity aggregations.
- `positive_split_assignments.csv`: fold-specific leakage-safe usable positive event/station assignments.
- `background_window_candidates.csv`: deterministic fold-specific catalog-negative candidates with exclusion-buffer and bias provenance.
- `preprocessing_positive_windows.csv`: primary MH v0.1 positive windows mapped onto nominal MiniSEED time.
- `results/predictions/pilot_dataset_audit.json`: manifest counts, hashes, fold/role counts, and evaluation-group leakage audit.
- `results/predictions/pilot_baselines_v0.1.json`: validation-thresholded classical diagnostic results; explicitly not paper results.
- `independent_background_station_days.csv`: fixed-seed official-archive station/day selections, including unavailable days without replacement.
- `independent_background_download_plan.json`: exact bytes, URLs, NASA MD5s, channels, and batching for independent ATT/MH products.
- `independent_background_day_quality.csv`: selected-channel and ATT full-day gap audit for every preselected day.
- `independent_background_windows.csv`: fold-specific ten-minute catalog-negative windows from usable independent days.
- `results/predictions/independent_background_audit.json`: day/window counts and integrity summary.
- `results/predictions/independent_background_baselines_v0.1.json`: classical shortcut-audit results on independent days; still diagnostic rather than final scanning results.
- `results/predictions/tiny_cnn_pilot_v0.1.json`: fold training histories, train-only scales, validation-selected thresholds, held-out metrics, hashes, and efficiency measurements.
- `results/predictions/tiny_cnn_pilot_v0.1/*_predictions.csv`: sample-level held-out scores and labels for reproducible pilot analysis.
- `results/predictions/tiny_cnn_shortcut_audit_v0.1.json`: coverage-channel and waveform-zero counterfactual inference audit.
- `models/checkpoints/tiny_cnn_pilot_v0.1/`: small state-dict and TorchScript pilot checkpoints; not final release weights.
- `configs/evaluation/continuous_scanning_v0.1.yaml`: prospectively frozen window, stride, threshold, trigger merging, event matching, and reporting rules.
- `contiguous_evaluation_station_days.csv`: fixed-seed untouched 14-day block membership, completeness, selected channel, bytes, and explicit zero prior-day overlap.
- `contiguous_evaluation_download_plan.json`: exact 448-product paths, URLs, bytes, NASA MD5s, blocks, and selection provenance; planned but not downloaded.
- `contiguous_evaluation_catalog_audit.csv`: post-selection catalog references, prior fold exposure, and prospective recall eligibility.
- `results/predictions/contiguous_evaluation_plan_audit.json`: compact overlap, catalog, and eligibility audit with CSV checksum.
- `contiguous_evaluation_download_receipt.json`: second-pass disk reconciliation for all 448 files and 171,375,344 bytes.
- `contiguous_evaluation_day_quality.csv`: ATT/MH rates, coverage, full-day gaps, day sensitivity status, passing 600-second windows, and scannable union duration.
- `contiguous_evaluation_eligible_event_quality.csv`: ATT mapping, event-window gaps, descriptive RMS support, and integrity status for the seven prospective events.
- `results/predictions/contiguous_evaluation_integrity_summary.json`: frozen window count, union duration, day/event status counts, and artifact hashes; contains no model inference.
- `results/predictions/continuous_scanning_thresholds_v0.1.json`: validation-only primary and max-F1 sensitivity thresholds reconstructed before scan inference.
- `results/predictions/continuous_scanning_window_scores_v0.1.csv.gz`: all 152,986 qualified windows with gap metadata and three method scores.
- `results/predictions/continuous_scanning_triggers_v0.1.csv`: all primary ±180-second merged triggers and one-to-one match outcomes.
- `results/predictions/continuous_scanning_results_v0.1.json`: primary and ±60/±300 sensitivity metrics, station results, retention, and artifact hashes.
- `results/predictions/continuous_scanning_error_audit_v0.1.json`: positive-window fractions, gap correlations, block concentrations, run sizes, and top false triggers.
- `continuous_validation_station_days_v0.1.csv`: 56 fixed-seed development-only station-days excluded from both test frames.
- `continuous_validation_download_plan_v0.1.json` and `continuous_validation_download_receipt_v0.1.json`: NASA-MD5-backed development-frame plan and verified receipt.
- `continuous_validation_day_quality_v0.1.csv` and `continuous_validation_windows_v0.1.csv.gz`: integrity results and artifact-proxy features for development-only windows.
- `results/predictions/artifact_robust_model_selection_v0.1.json`: robust-level versus robust-difference selection evidence using training-station development data only.
- `models/checkpoints/artifact_robust_v0.1/`: per-fold development checkpoints; robust-level checkpoints are selected for test v0.2.
- `contiguous_evaluation_*_v0.2.*`: second untouched frame selection, checksums, catalog audit, integrity QA, and eligible-event evidence.
- `results/predictions/continuous_scanning_window_scores_v0.2.csv.gz`: all four frozen model scores for 157,363 qualified test-v0.2 windows.
- `results/predictions/continuous_scanning_triggers_v0.2.csv` and `continuous_scanning_results_v0.2.json`: merged triggers and final operational comparison.
