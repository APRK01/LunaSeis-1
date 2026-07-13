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
