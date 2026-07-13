# 0012 — Download minimum positive channels in four station-day-preserving batches

Date: 2026-07-13

## Decision

For nonshallow candidate QA, select PDS location-`00` MiniSEED only for positively reported mid-period channels, positively reported SHZ where applicable, and ATT, with XML labels. Include adjacent days only when the fixed `[-120,+480]` s audit window crosses midnight. If download is authorized, execute the 7.11 GiB plan in four deterministic batches of at most about 2 GiB without splitting station-days.

## Rationale

This is the smallest provenance-complete selection that can test the catalog-positive observations and timing. Downloading every channel or whole archive would add cost without being required for the first QA gate. Batching supports resumability, checksum isolation, early failure detection, and bounded storage.

## Consequences

Eighty-one candidates have no archive-backed positive station request under this rule and remain excluded from the availability-qualified pool unless a later source-specific investigation justifies another path. The remaining 1,159 events are still candidates—not usable training events—until local ATT/gap integrity QA passes.
