# 0006 - ATT-aware window timing

Date: 2026-07-13

Status: accepted principle; exact correction algorithm pending broader audit.

Window construction must preserve nominal MiniSEED time and ATT-derived Earth-reception time separately. The pilot shows negligible-to-subsecond nominal offset at S12 but approximately five seconds at S14 near the same event. A single silent global shift is therefore unjustified. Later data construction must record the timing basis, local ATT mapping, uncertainty, and any applied propagation correction per station/window.
