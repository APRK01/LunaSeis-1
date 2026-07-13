# Decision log

| Date | ID | Decision | Rationale | Status |
|---|---|---|---|---|
| 2026-07-12 | 0001 | Keep Apollo 12, 14, 15, and 16 PSE as the provisional primary scope; exclude Apollo 17 LSPE initially. | Avoid mixing materially different experiments before feasibility and metadata audits. | Provisional pending archive verification |
| 2026-07-12 | 0002 | Use hierarchical detection then classification, with `catalog-negative background` terminology. | Non-catalogued intervals are not proven physical noise; detection validity takes priority over broad multiclass claims. | Provisional pending catalog audit |
| 2026-07-12 | 0003 | Require chronological and station-held-out evaluation, plus continuous-scanning false-alarm measurement. | Random balanced windows do not establish temporal or cross-station generalization and conceal operational false alarms. | Accepted protocol constraint |
| 2026-07-13 | 0004 | Use the Apollo 15 S-IVB artificial impact as the Phase 0 alignment target. | It has a known origin record and published P arrivals at stations 12 and 14, reducing ambiguity during pipeline validation. | Accepted feasibility target; timing interpretation pending |
| 2026-07-13 | 0005 | Use MiniSEED waveforms with StationXML and PDS labels for the Phase 0 pilot. | This preserves the archive's scientific representation and provenance while reducing the selected download from over 250 MB of GeoCSV to about 7.6 MiB. | Accepted |
| 2026-07-13 | 0006 | Preserve nominal and ATT-derived times separately and make later window timing ATT-aware. | The pilot found about +0.33 s nominal offset at S12 but +5.23 s at S14 when matching published arrivals through ATT. | Accepted principle; algorithm pending broader audit |

Formal records live in `docs/decisions/`.
