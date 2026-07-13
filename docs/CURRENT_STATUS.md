# Current status

Last updated: 2026-07-13 (Asia/Kolkata)

## State

The central Phase 0 event-to-waveform feasibility milestone is achieved for the Apollo 15 S-IVB impact. Verified waveforms were downloaded, loaded, timing/gaps audited, and plotted without preprocessing. Broader archive/legal audit remains open. No models have been trained and no performance results exist.

## Completed

- Inspected the initial workspace: it was empty and was not a Git repository.
- Preserved the complete supplied handoff in `docs/PROJECT_CONTEXT.md`.
- Created the permanent context document set and repository directory skeleton.
- Initialized Git and created commit `2683cd8` (`chore: initialize LunaSeis-1 research repository`).
- Verified waveform bundle `urn:nasa:pds:apollo_pse::1.0`, DOI `10.17189/9ykc-er91`.
- Verified event catalog bundle `urn:nasa:pds:apollo_seismic_event_catalog::1.0`, DOI `10.17189/1520573`.
- Recorded formats, archive layout, timing warning, documented instrument sample rates, and remaining uncertainties in `docs/source_verification.md`.
- Confirmed 47 GiB free before downloading; the catalog required only 2.2 MB.
- Added a manifest-driven catalog downloader and verified all 32 NASA-listed products (2,226,558 bytes) by MD5.
- Audited 11 catalog CSV schemas and generated a machine-readable schema report.
- Inspected the official four-page catalog-description PDF by text extraction and rendered-page review.
- Selected the Apollo 15 S-IVB artificial impact (1971, Julian day 210) as the Phase 0 pilot candidate, with published P arrivals at stations 12 and 14.
- Verified candidate-day availability for S12 and S14 and enumerated all products and official MD5 values.
- Selected MiniSEED plus StationXML/PDS labels: 7,924,909 bytes (about 7.6 MiB), versus over 250 MB for equivalent GeoCSV waveforms.
- Verified product metadata rates: 6.625 Hz mid-period, 53 Hz SHZ, and 1.65625 Hz ATT; corrected the earlier 15 Hz discovery-stage note.
- Documented ATT reception-time semantics, nominal-time drift, uncorrected 1.2-1.4 s Moon-Earth delay, station synchronization risk, and gap sentinels.
- Added and tested a manifest-driven pilot downloader; all 20 products and 7,924,909 planned bytes passed size and NASA MD5 verification.
- Created a Python 3.12 virtual environment with pinned ObsPy/Matplotlib dependencies; pinned setuptools below 81 for ObsPy compatibility.
- Loaded all nine MiniSEED traces and recorded coverage, sample rates, sample counts, full-day sentinels, and event-window sentinels.
- Matched published arrivals through ATT: nominal mapped time is +0.330 s at S12 and +5.233 s at S14 relative to published arrival.
- Generated and visually verified the first unprocessed LunaSeis-1 waveform plot; a strong event signal is visible at both stations.
- Recorded the Phase 0 feasibility result and the scientific limits of this one-event validation.

## Files changed

- Initial context/skeleton files in commit `2683cd8`.
- `docs/source_verification.md`
- `docs/CURRENT_STATUS.md`
- `scripts/download_catalog.py`
- `scripts/audit_catalog.py`
- `tests/test_download_catalog.py`
- `data/manifests/catalog_schema_audit.json`
- `data/manifests/pilot_event.json`
- `docs/catalog_audit.md`
- `docs/DECISIONS.md`
- `docs/decisions/0004-phase-0-pilot-event.md`
- `data/manifests/pilot_waveform_inventory.json`
- `docs/waveform_inventory_audit.md`
- `docs/source_verification.md`
- `docs/decisions/0005-pilot-waveform-format.md`
- `scripts/download_pilot_waveforms.py`
- `tests/test_download_pilot_waveforms.py`
- `scripts/audit_pilot_waveforms.py`
- `results/predictions/phase0_waveform_audit.json`
- `results/figures/phase0_apollo15_sivb_raw_waveforms.png`
- `pyproject.toml`
- `requirements-lock.txt`
- `docs/phase0_alignment_result.md`
- `docs/decisions/0006-att-aware-window-timing.md`
- `docs/ROADMAP.md`

## Commands and verification

- Inspected with `ls -la`, `find`, `rg --files`, and `git status`.
- Compared the permanent context against the supplied handoff byte-for-byte before commit.
- Reviewed repository status and required files before commit.
- Queried official NASA PDS pages and inspected both official PDS4 bundle XML labels and READMEs.
- Inspected the official catalog and waveform collection directory listings without downloading the archive.
- Ran `python3 scripts/download_catalog.py`; all 32 product checksums passed.
- Ran `python3 -m unittest discover -s tests -p 'test_download_catalog.py' -v`; 2 tests passed.
- Ran `python3 scripts/audit_catalog.py`; audited 11 CSV files and wrote the schema manifest.
- Converted Julian day 210 of 1971 independently to 1971-07-29 for the candidate record.
- Inspected official S12/S14 day directories, StationXML, PDS MD5 manifest, and the 41-page 2022 Software Interface Specification.
- Checksum-verified the locally cached StationXML, its PDS label, and the specification PDF.
- Recomputed the planned product total from every listed file size: 7,924,909 bytes.
- Ran five downloader/parser unit tests successfully.
- Reran the pilot downloader after download to verify idempotent integrity checks.
- Ran `scripts/audit_pilot_waveforms.py` with pinned Python dependencies and inspected its JSON output.
- Visually inspected the full-resolution plot for signal visibility, correct channel labeling, markers, gaps, and disclosure of absent preprocessing.

## Decisions

- The supplied handoff is the canonical stable project context.
- Work begins at Phase 0; modelling remains prohibited until event-to-waveform alignment is verified.
- Treat the PDS event catalog as multiple source tables requiring semantic reconciliation, not an immediately usable flat label file.
- Product metadata, not only instrument-level documentation, will determine actual processing sample rates.
- Use a known artificial impact with two published station arrivals for the first alignment test; this is a feasibility choice, not a final taxonomy choice.
- Use MiniSEED with StationXML and PDS labels for the pilot; include ATT and preserve explicit gaps.
- Treat nominal and ATT-derived timestamps as separate provenance fields; no silent global timing shift.

## Unresolved uncertainties

- Exact scalable ATT correction/interpolation policy and catalog-pick time-basis reconciliation remain unresolved.
- Full `levent` class/grade decoding, duplicate reconciliation, and final label mappings remain to be audited.
- The candidate event's time standard and precise relationship to waveform/timing-trace time remain unresolved.
- Redistribution/licensing guidance remains unresolved; no republication is authorized by assumption.
- Full environment portability beyond the tested Apple Silicon Python 3.12 setup remains to be verified later in Colab/Linux.

## Exact next task

Complete the remaining Phase 0 source-policy audit by verifying NASA PDS redistribution, attribution, and processed-derivative guidance from authoritative policy documents, then record what may legally be published on GitHub/Hugging Face.
