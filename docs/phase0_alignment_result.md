# Phase 0 event-to-waveform alignment result

Result date: 2026-07-13

Status: technical feasibility milestone achieved; broader Phase 0 archive/legal audit remains open.

## Question

Can LunaSeis-1 start from a verified catalog event, obtain the corresponding official Apollo products, load them with station/channel metadata, account explicitly for timing traces and gaps, and produce a valid waveform plot?

## Result

Yes, for the Apollo 15 S-IVB artificial impact on 1971-07-29 (Julian day 210).

- Catalog origin: `20:58:42.9` as published.
- Published station P arrivals: S12 `20:59:37.9`; S14 `20:59:19.5`.
- Nine MiniSEED traces were downloaded for the two stations: ATT and three mid-period channels at S12; ATT, SHZ, and three mid-period channels at S14.
- All waveform, metadata, and PDS-label products passed expected byte-size and NASA MD5 verification.
- StationXML confirms the station/channel identities and sample rates.
- The unprocessed waveforms show a strong emergent signal beginning near the published/ATT-mapped arrivals at both stations.

This demonstrates event-to-waveform feasibility. It does not yet establish a detection model, dataset correctness at scale, final timing corrections, or research novelty.

## Timing result

The ATT samples are Unix-like epoch timestamps representing Earth reception at frame heads. Matching the published arrival timestamps to the nearest valid ATT samples gives:

| Station | Nearest ATT minus published arrival | Nominal MiniSEED time at that ATT sample minus published arrival | ATT minus nominal at match |
|---|---:|---:|---:|
| S12 | -0.011 s | +0.330 s | -0.341 s |
| S14 | +0.285 s | +5.233 s | -4.948 s |

ATT samples occur at 1.65625 Hz, so nearest-sample matching itself has roughly 0.30 s half-sample resolution. The approximately five-second S14 nominal offset is materially larger and visibly aligns the ATT-mapped marker with signal onset better than the uncorrected nominal marker. This confirms that ATT-aware timing must be part of later window construction.

We have not applied the uncorrected 1.2-1.4 s Moon-to-Earth propagation adjustment, because the relationship between each historical catalog pick and archive time basis must be established before choosing a correction policy.

## Gap and signal observations

- No ATT gap sentinel occurs within the plotted ten-minute windows at either station.
- Seismic-channel `-1` sentinels do occur within both windows and are counted in `results/predictions/phase0_waveform_audit.json`.
- Sentinels are converted to `NaN` only for display so lines do not draw through missing data. No samples are interpolated.
- S14 MH1/MH2 reach the digital range boundaries in the raw plot. This may represent clipping/saturation and must be treated as a quality flag rather than useful amplitude information.
- The plot is raw digital counts. No detrending, filtering, normalization, interpolation, resampling, response removal, or amplitude calibration was performed.

## Reproducible artifacts

- Downloader: `scripts/download_pilot_waveforms.py`
- Audit/plot script: `scripts/audit_pilot_waveforms.py`
- Pinned source inventory: `data/manifests/pilot_waveform_inventory.json`
- Machine-readable audit: `results/predictions/phase0_waveform_audit.json`
- Plot: `results/figures/phase0_apollo15_sivb_raw_waveforms.png`
- Locked Python environment: `requirements-lock.txt`

## Scientific boundary

This single controlled impact is a pipeline validation case, not an evaluation dataset. It cannot support performance metrics, class claims, novelty claims, or conclusions about natural moonquake detection.
