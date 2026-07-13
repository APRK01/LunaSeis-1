# Unified positive-event candidate manifest audit

Audit date: 2026-07-13

This stage completes the eight manifest tasks requested before background sampling or split assignment. The output is a candidate registry, not a frozen training set.

## 1. Source combination

`data/manifests/unified_positive_events.csv` combines conservative PDS A/B physical-event candidates with the corrected 74-event Onodera shallow catalog. PDS shallow rows are replaced by corrected records rather than appended: 28 legacy events merge with exact PDS `H` rows and 46 KO events are new. The resulting registry has 1,314 physical events.

## 2. Preserved provenance

Every row preserves source catalog and source IDs, physical class, PDS T2/grade/family where available, corrected reference time and precision, time semantics, reported stations/channels, label provenance, release/licensing note, and candidate status. The 46 KO events explicitly carry `not_assigned_by_onodera` rather than an invented PDS grade. Seven corrected legacy records retain PDS grade C and three remain ungraded; their inclusion is attributable to the corrected discovery catalog, not a silent relaxation of the PDS A/B rule.

## 3. Attached waveform QA

All 74 shallow events carry audited station fields and window counts. All four nonshallow batches are attached: 1,146 nonshallow events have a usable request, three are questionable, ten have only rejected requests, and 81 lack an archive-backed complete request. Positive visibility is not promoted to verified waveform usability.

## 4. Leakage grouping

Each row has an indivisible physical-event group and an evaluation group. The manifest contains 115 deep-family groups covering 604 assigned deep events. KO-SMQ-26 and KO-SMQ-40 share `shallow-repeat:KO-SMQ-26+KO-SMQ-40`. There are 824 unique evaluation groups across 1,314 events.

## 5. Rejected-window handling

Rejected shallow station windows are absent from `usable_stations` but remain recorded in `rejected_stations` and in the row-level window-quality manifest. The one questionable window is likewise preserved separately. All 74 shallow events retain at least one usable station.

## 6. Candidate status

The registry has 1,220 integrity-audited candidates (74 shallow plus 1,146 nonshallow), three questionable, ten failed-integrity exclusions, and 81 archive-unavailable/pending candidates. Pilot background candidates and split assignments now exist, but they are not a final model-ready claim because their day-selection frame is biased toward positive coverage.

## 7. Duplicate, overlap, and conflict audit

The audit found:

- no duplicate unified event ID;
- no source event ID owned by multiple unified events;
- no pair of candidates sharing the same reference minute;
- no same-minute cross-class conflict;
- no corrected legacy shallow record whose matched PDS type is other than `H`.

The machine-readable conflict result is `pass`. This proves consistency under the available time/source keys, not physical completeness of either catalog.

## 8. Exact candidate counts

| Class | Events |
|---|---:|
| Assigned deep moonquake | 604 |
| Unclassified deep moonquake | 5 |
| Natural impact | 623 |
| Shallow moonquake | 74 |
| LM artificial impact | 4 |
| S-IVB artificial impact | 4 |
| **Total** | **1,314** |

Station counts represent positive PDS visibility for nonshallow candidates and integrity-usable SHZ stations for shallow candidates, so they are deliberately not treated as identical evidence:

| Station | Deep | Natural impact | Shallow | Artificial impact |
|---|---:|---:|---:|---:|
| S12 | 407 | 367 | 0 | 7 |
| S14 | 512 | 455 | 30 | 7 |
| S15 | 349 | 337 | 68 | 5 |
| S16 | 367 | 256 | 25 | 2 |

Multi-station events appear in more than one station count but only once in event counts.

Rebuild with:

```bash
.venv/bin/python scripts/build_unified_positive_manifest.py
```
