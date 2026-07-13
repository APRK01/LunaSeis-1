# Nonshallow waveform audit: all four batches

Date: 2026-07-13

All 15,106 planned products (7,636,136,244 bytes across 2,496 station-days) were independently re-read from disk and passed exact-size and official NASA-MD5 verification. Raw data remains ignored by Git.

The ATT-aware audit contains 6,236 positive-channel windows, 2,476 event-station requests, and all 1,159 archive-backed nonshallow events. Under the primary v0.1 thresholds, 1,146 events have at least one usable station, three are questionable, and ten have only rejected requests. The remaining 81 of 1,240 nonshallow candidates lack an archive-backed complete request and remain explicitly unavailable rather than silently excluded.

Batch 3 covered 560 events (553 usable, two questionable, five rejected at event level). Batch 4 covered 385 events (383 usable, two questionable, none rejected). All suspicious Batch 3/4 requests and both aggregate figures were reviewed; gap loss and ATT displacement explain the statuses. Amplitude and RMS never changed a label or integrity outcome.

Threshold sensitivity at physical-event level is:

| Policy | Usable | Questionable | Rejected |
|---|---:|---:|---:|
| Strict (10%/40% gap, 0.5/5 s ATT) | 1,107 | 41 | 11 |
| Primary v0.1 (20%/50%, 1/10 s) | 1,146 | 3 | 10 |
| Lenient (30%/60%, 2/20 s) | 1,146 | 4 | 9 |

The frozen computational mapping treats catalog time as an Earth-reception reference, locates the nearest valid ATT value, and uses the corresponding nominal MiniSEED time for waveform slicing. Reference, ATT value, nominal time, and both offsets remain separate provenance. This resolves reproducible computation, not the catalog start time's physical phase meaning or absolute time standard.
