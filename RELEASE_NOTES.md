# LunaSeis-1 v0.1.1

Public archival release by Advaith Praveen (APRK), published under Archeum Studios.

Permanent archive: https://doi.org/10.5281/zenodo.21361572

## Included

- A 2,761-parameter depthwise-separable 1D CNN with one leave-one-station-out checkpoint for each Apollo PSE station S12, S14, S15, and S16.
- Public Python inference API and `lunaseis-predict` command-line interface.
- Checksum-backed source reconstruction, ATT/gap provenance, leakage-controlled manifests, and reproducible protocols.
- Three prospectively frozen continuous evaluations totaling 6,748.22 station-hours.
- Prominently linked six-page research paper, publication figures, statistical tables, model card, dataset card, and exact release checksums.
- Permanent Zenodo archival with DOI `10.5281/zenodo.21361572`.

## Evidence boundary

This is a functioning research prototype, not an operational or flight-ready moonquake detector. The frozen evaluations exposed low event recall, excessive false triggers, and extensive stream retention. See `docs/RELEASE_CLAIMS.md` and `docs/MODEL_CARD.md` before using or describing the model.

Raw NASA waveform files are not redistributed. Use the documented download scripts and official PDS sources.
