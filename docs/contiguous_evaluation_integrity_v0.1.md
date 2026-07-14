# Untouched contiguous evaluation integrity audit v0.1

Date: 2026-07-14

## Download integrity

All 448 planned products totaling 171,375,344 bytes passed exact-size and official NASA-PDS-MD5 verification. A second disk-only run reused and reverified all 448 files. Raw archive files remain ignored by Git.

## Full-day and scanning-window integrity

All 112 ATT/MH day pairs loaded successfully. Under the previously used 20% primary gap gate and a newly recorded 10% sensitivity boundary, 100 days are usable, ten are questionable, and two are rejected at full-day level. These day labels are descriptive summaries; the primary scan gate is applied independently to each 600-second window.

The frozen 600-second/60-second-stride grid contains 160,272 candidate windows. Requiring both ATT and MH local gap fractions to be at most 20% retains 152,986 windows. Their merged underlying-time support is 9,329,280 seconds, or 2,591.4667 station-hours. This union duration—not the overlapping sum of window lengths—is frozen as the false-trigger denominator.

## Untouched candidate events

Six of seven prospective candidates pass the established event-window ATT/gap gate. `levent-10063` at S12 is rejected because its ten-minute waveform is 78.59% gap sentinel and its nearest ATT value is 78.714 seconds from the catalog reference. It cannot contribute to event recall.

The remaining six have zero waveform gaps and nearest ATT offsets between -0.110 and +0.156 seconds. Raw post/pre RMS screening is descriptive: one weak-ratio window and five without a clear increase. Visual review confirms intact traces and timing markers but no uniformly obvious event morphology. Their catalog labels remain unchanged, and integrity acceptance must not be described as visible-signal confirmation.

## Freeze and limitations

The primary untouched scan frame is frozen at 152,986 windows, 2,591.4667 union hours, and six integrity-eligible catalog events. This event count is too small for a stable headline recall estimate. Continuous false triggers per hour/day are primary; event recall must use exact numerator/denominator and uncertainty. No model was loaded or scored during download, QA, signal-ratio calculation, or visual review.
