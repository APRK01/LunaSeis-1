#!/usr/bin/env python3
"""Consolidate all nonshallow QA and quantify provisional threshold sensitivity."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def classify(gap: float, offset: float, usable_gap: float, reject_gap: float, usable_att: float, reject_att: float) -> str:
    if gap > reject_gap or abs(offset) > reject_att:
        return "reject_integrity"
    if gap > usable_gap or abs(offset) > usable_att:
        return "questionable_integrity"
    return "usable_integrity"


def aggregate(rows: list[dict[str, str]], thresholds: tuple[float, float, float, float]) -> Counter:
    by_request: dict[tuple[str, str], list[str]] = defaultdict(list)
    ug, rg, ua, ra = thresholds
    for row in rows:
        by_request[(row["event_id"], row["station"])].append(classify(float(row["gap_fraction"]), float(row["nearest_att_minus_reference_seconds"]), ug, rg, ua, ra))
    by_event: dict[str, list[str]] = defaultdict(list)
    for (event, _), statuses in by_request.items():
        status = "usable_integrity" if "usable_integrity" in statuses else "questionable_integrity" if "questionable_integrity" in statuses else "reject_integrity"
        by_event[event].append(status)
    return Counter("usable_integrity" if "usable_integrity" in values else "questionable_integrity" if "questionable_integrity" in values else "reject_integrity" for values in by_event.values())


def main() -> None:
    paths = sorted(Path("data/manifests").glob("nonshallow_batch_*_window_quality.csv"))
    rows = [row for path in paths for row in csv.DictReader(path.open(newline=""))]
    grids = {
        "strict": (0.10, 0.40, 0.5, 5.0),
        "primary_v0_1": (0.20, 0.50, 1.0, 10.0),
        "lenient": (0.30, 0.60, 2.0, 20.0),
    }
    report = {
        "batch_count": len(paths),
        "channel_window_count": len(rows),
        "unique_event_station_requests": len({(r["event_id"], r["station"]) for r in rows}),
        "unique_events": len({r["event_id"] for r in rows}),
        "timing_mapping_policy": "Map catalog Earth-reception reference to the nominal MiniSEED sample time at the nearest valid ATT value; preserve reference, ATT, nominal, and offsets separately.",
        "threshold_sensitivity_event_counts": {name: dict(aggregate(rows, values)) for name, values in grids.items()},
        "primary_thresholds": {"usable_max_gap_fraction": 0.20, "reject_above_gap_fraction": 0.50, "usable_max_abs_att_offset_seconds": 1.0, "reject_above_abs_att_offset_seconds": 10.0},
        "scientific_limit": "This freezes a reproducible engineering mapping, not the unresolved physical time standard or phase-pick meaning of catalog start times.",
    }
    output = Path("results/predictions/nonshallow_all_batches_audit.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
