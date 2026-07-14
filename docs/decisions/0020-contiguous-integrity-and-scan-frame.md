# Decision 0020: freeze the integrity-qualified contiguous scan frame

Date: 2026-07-14

Accept 152,986 locally integrity-qualified 600-second windows and their 9,329,280-second union duration as untouched continuous-scan frame v0.1. Apply the 20% ATT-and-MH local gap gate per window; retain 10% as a full-day sensitivity boundary rather than an exclusion rule. Use union duration as the false-trigger denominator.

Reject `levent-10063` from event-recall accounting for severe waveform gaps and ATT displacement. Retain the other six candidates as integrity-eligible without claiming visible signal confirmation. Authorize frozen model and baseline inference next, while keeping paper-level conclusions blocked by the small event denominator and pending trigger/error analysis.
