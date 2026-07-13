# Nonshallow waveform availability and storage audit

Audit date: 2026-07-13

No waveform data was downloaded during this audit.

## Scope and minimum selection

The input is the 1,240 nonshallow candidates still pending waveform QA. Each PDS positive visibility token was converted into an event/station/channel request. The plan selects only the positively reported channel(s), the matching PDS XML label, ATT MiniSEED, and its label. Mid-period channels use location `00` (peaked mode), matching the Phase 0 format decision; ATT and SHZ use blank location codes.

Audit windows are defined as 120 s before through 480 s after the catalog reference. Thirteen events cross midnight, adding 22 adjacent station-days. This prevents truncated windows while avoiding arbitrary adjacent-day downloads.

## Deduplication and availability

- Input candidates: 1,240.
- Event-station requests: 3,071.
- Unique requested station-days after boundary handling: 2,496.
- Usable event-station requests: 2,476; unavailable requests: 595.
- Archive-backed station-days selected: 2,354; 142 requested station-days have no selected products.
- Events with at least one usable positive station request: 1,159.
- Events without one: 81 (57 assigned deep moonquakes and 24 natural impacts).

The usable event pool before local gap/timing QA is therefore:

| Class | Events |
|---|---:|
| Assigned deep moonquake | 547 |
| Unclassified deep moonquake | 5 |
| Natural impact | 599 |
| LM artificial impact | 4 |
| S-IVB artificial impact | 4 |
| **Total** | **1,159** |

The 81 unavailable candidates remain preserved in the request manifest and plan summary. They are not silently deleted or relabeled. Positive catalog visibility is historical evidence and is not guaranteed to correspond to a modern PDS daily product.

## Exact storage plan

- Products: 15,106 MiniSEED/XML files.
- Exact bytes: 7,636,136,244.
- Size: 7,282.39 MiB / 7.11171 GiB.

| Channel | Products | Bytes | Approx. GiB |
|---|---:|---:|---:|
| ATT | 4,708 | 2,739,427,132 | 2.551 |
| MH1 | 3,094 | 558,573,483 | 0.520 |
| MH2 | 3,626 | 655,226,929 | 0.610 |
| MHZ | 2,244 | 404,194,029 | 0.376 |
| SHZ | 1,434 | 3,278,714,671 | 3.053 |

Every selected product includes exact listed bytes and an official PDS MD5. Availability still does not establish a gap-free, correctly timed event window.

## Download decision

Do not download as one monolithic job. Use the deterministic `batch_id` attached to every product:

| Batch | Station-days | Products | Bytes |
|---|---:|---:|---:|
| 1 | 845 | 5,398 | 2,142,346,643 |
| 2 | 502 | 3,270 | 2,145,595,149 |
| 3 | 620 | 4,014 | 2,145,641,669 |
| 4 | 387 | 2,424 | 1,202,552,783 |

Each station-day remains inside one batch. This makes downloads resumable and permits QA after each approximately 2 GiB block. With roughly 44 GiB free after the shallow download, the 7.11 GiB raw selection fits, but later processed artifacts must remain storage-bounded.

Artifacts:

- `data/manifests/nonshallow_waveform_requests.csv`
- `data/manifests/nonshallow_download_plan.json`
- `scripts/build_nonshallow_download_plan.py`
