# LunaSeis-1 roadmap

The detailed roadmap and constraints are in `PROJECT_CONTEXT.md`, section 26.

## Current phase: Phase 0 — scope and feasibility

Success criterion: starting from one verified catalogued event timestamp, automatically identify and obtain its Apollo waveform, load it with correct station/channel metadata, and produce a scientifically valid waveform plot. **Achieved for the Apollo 15 S-IVB pilot on 2026-07-13.**

1. Establish permanent context and repository foundation.
2. Verify official waveform bundle and event catalog identifiers, versions, formats, archive structure, stations, channels, timestamps, sample rates, and redistribution guidance.
3. Implement and test a catalog/metadata downloader.
4. Select one verified event and download the smallest practical corresponding waveform sample. Completed for Apollo 15 S-IVB.
5. Validate metadata, align the event, and plot the waveform window. Completed with explicit nominal/ATT timing and gap audit.
6. Record the feasibility decision before proceeding to Phase 1.

Later phases: literature/data audit; reproducible preprocessing; baselines; compact neural models; generalization/calibration; continuous scanning/retention simulation; reproduction audit; paper; public release.
