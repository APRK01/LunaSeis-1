# LunaSeis-1

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21361572.svg)](https://doi.org/10.5281/zenodo.21361572)

**A reproducible lightweight ML research prototype for Apollo lunar-seismic waveforms.**

Created by **Advaith Praveen (APRK)** under Archeum Studios.

LunaSeis-1 asks a harder question than balanced-window accuracy: can a compact detector trained on Apollo Passive Seismic Experiment data generalize across stations and remain useful during long continuous scans?

The honest answer from the present study is: **not yet operationally**. The selected 2,761-parameter depthwise CNN is a functioning, open inference prototype and performs well on leakage-controlled development events, but two prospectively frozen continuous tests exposed missed events and excessive false alarms. Those failures are preserved rather than hidden.

## Research Paper

### *LunaSeis-1: When Balanced Apollo Seismic Detection Fails Under Cross-Station Continuous Scanning*

**Author:** Advaith Praveen (APRK) · **Publisher:** Archeum Studios · **Version:** 0.1.1

**Permanent archive:** [doi:10.5281/zenodo.21361572](https://doi.org/10.5281/zenodo.21361572)

[**Read the research paper on GitHub**](output/pdf/LunaSeis-1_Research_Paper.pdf) · [**Download the PDF**](https://github.com/archeumstudios/LunaSeis-1/raw/main/output/pdf/LunaSeis-1_Research_Paper.pdf) · [**View the manuscript source**](paper/manuscript.md)

[![First page of the LunaSeis-1 research paper](paper/figures/research_paper_preview.png)](output/pdf/LunaSeis-1_Research_Paper.pdf)

The paper reports the complete study design, data provenance, leakage controls, model training, three frozen continuous evaluations, exact uncertainty intervals, limitations, and negative operational result. Click the paper cover above to open the complete six-page PDF.

## What is scientifically interesting

- 1,314 reconciled physical-event candidates from official PDS and corrected shallow-moonquake sources.
- ATT-aware timing, explicit gap preservation, and checksum-backed NASA provenance.
- Event-, station-, chronology-, and repeating-family-aware leakage controls.
- More than **5,243 station-hours** across two frozen continuous tests.
- Severe station-specific quantization and artifact shift documented directly.
- Robust normalization reduced the original CNN’s test-v0.2 false-trigger rate by 65.4%.
- A depthwise CNN subsequently reduced development false triggers to **0.211/hour at 91.15% development event recall**.
- A frozen 63-event Grade-C impact challenge then yielded only **19.0% recall and 0.868 false triggers/hour**, confirming the development-to-operation gap.
- Every failure, threshold, prediction, trigger, manifest, and checkpoint is retained.

![Frozen continuous results](paper/figures/figure_2_frozen_continuous_results.png)

## Selected research prototype

| Property | Value |
|---|---:|
| Architecture | Depthwise-separable 1D CNN |
| Parameters | 2,761 |
| Input | 600-second MH waveform plus validity mask |
| Preprocessing | Per-window median/robust scale, clipping ±20 |
| Development event recall target | 91.15% mean across LOSO folds |
| Continuous-development false triggers | 0.211/hour |
| Supported stations | Apollo 12, 14, 15, 16 |

The public interface automatically loads the checkpoint trained without the requested station. This preserves the leave-one-station-out intent.

## Frozen continuous results

### Test v0.1 — 2,591.47 station-hours, six eligible events

| Method | Recall | False triggers/hour | Retained duration |
|---|---:|---:|---:|
| Original tiny CNN | 1/6 | 1.131 | 75.50% |
| Logistic regression | 1/6 | 0.121 | 40.28% |
| STA/LTA | 0/6 | 0.282 | 97.92% |

### Test v0.2 — 2,651.4 station-hours, three eligible events

| Method | Recall | False triggers/hour | Retained duration |
|---|---:|---:|---:|
| Artifact-robust tiny CNN | 0/3 | 0.319 | 45.58% |
| Original tiny CNN | 0/3 | 0.923 | 62.48% |
| Logistic regression | 0/3 | 0.185 | 35.22% |
| STA/LTA | 0/3 | 0.205 | 96.49% |

The newer depthwise model was selected only after both frames were consumed and therefore is **not** retroactively evaluated or claimed to succeed on them.

### Challenge v0.3 — 1,505.35 station-hours, 63 unseen Grade-C impacts

| Method | Recall | False triggers/hour | Retained duration |
|---|---:|---:|---:|
| Frozen depthwise CNN | 12/63 | 0.868 | 75.38% |

Grade C is lower-confidence catalog evidence than Grades A/B. This challenge is reported separately and does not convert the prototype into an operational detector.

See [release claims](docs/RELEASE_CLAIMS.md) for the exact evidence boundary. LunaSeis-1 does not claim to be the first lunar ML detector, the first compact raw-waveform model, or an operational detector.

## Quick start

```bash
git clone https://github.com/archeumstudios/LunaSeis-1.git
cd LunaSeis-1
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/predict_lunaseis.py path/to/apollo_mh.mseed --station S15 --output predictions.json
```

Python:

```python
from lunaseis import LunaSeisDetector

detector = LunaSeisDetector("S15")
windows = detector.scan_mseed("path/to/apollo_mh.mseed")
print(detector.metadata())
```

Scores above the included development threshold are candidate triggers—not verified moonquakes.

## Repository map

```text
lunaseis/       Public model and inference interface
scripts/        Download, audit, training, evaluation, and CLI scripts
configs/        Machine-readable data/model/evaluation protocols
data/manifests/ Reproducible source selections and split provenance
models/         Small versioned research checkpoints
results/        Predictions, triggers, metrics, and figures
docs/           Decisions, audits, model/dataset cards, and protocols
literature/     Structured state-of-the-field review
notebooks/      Colab/tutorial reproduction material
paper/          Manuscript sources and tables
tests/          Leakage, integrity, preprocessing, and inference tests
```

## Reproduce the evidence

See [Reproducibility guide](docs/REPRODUCIBILITY.md), [model card](docs/MODEL_CARD.md), [dataset card](docs/DATASET_CARD.md), [Colab-ready inference tutorial](output/jupyter-notebook/lunaseis_inference_colab.ipynb), [research paper](output/pdf/LunaSeis-1_Research_Paper.pdf), and the [full development/test report](docs/artifact_robust_continuous_validation_and_v0.2.md).

Raw NASA files are intentionally excluded from Git. Download scripts reconstruct permitted inputs from official PDS sources and verify exact sizes and MD5 hashes.

## Limitations

- This is a research prototype, not a flight or operational detector.
- Both frozen continuous tests failed the desired recall/false-alarm objective.
- Development thresholds are not calibrated probabilities.
- Catalog-negative windows may contain uncatalogued events.
- Catalog timing semantics and some weak-event labels remain uncertain.
- Checkpoint performance is specific to Apollo PSE MH channels and the documented preprocessing.

## Citation

Use [CITATION.cff](CITATION.cff). Primary author: **Advaith Praveen (APRK)**.

Canonical repository: [archeumstudios/LunaSeis-1](https://github.com/archeumstudios/LunaSeis-1). Development commits are attributed to the `APRK01` GitHub identity.

## License and data

Code is released under the MIT License. The manuscript and original paper figures remain copyright © 2026 Advaith Praveen (APRK), all rights reserved. NASA source data and third-party catalog material retain their original terms; see [copyright and attribution](COPYRIGHT.md) and the [dataset card](docs/DATASET_CARD.md) before redistribution.
