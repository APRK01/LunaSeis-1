# LunaSeis-1 workspace operating instructions

Before meaningful work, read these files in order:

1. `docs/PROJECT_CONTEXT.md`
2. `docs/ROADMAP.md`
3. `docs/CURRENT_STATUS.md`
4. `docs/DECISIONS.md`
5. `docs/research_protocol_v0.1.md`

Scientific honesty, leakage prevention, reproducibility, zero-cost operation, and the scope limits in those documents are binding. Do not train a model until the Phase 0 event-to-waveform alignment milestone is verified. Do not fabricate or silently promote assumptions to facts.

After every meaningful task, update `docs/CURRENT_STATUS.md` with work completed, exact files changed, commands/tests run, unresolved uncertainties, and exactly one next task. Record consequential scientific or engineering choices in `docs/DECISIONS.md`; add a formal record under `docs/decisions/` when appropriate.

Preserve user work and raw data. Inspect before destructive actions. Never commit credentials, large datasets, uncontrolled checkpoints, or temporary notebook output.
