#!/usr/bin/env python3
"""Build the frozen-v0.1 primary-channel preprocessing manifest."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

PRIMARY = ("MHZ", "MH1", "MH2")


def mapped_time(reference: str, nominal_offset: str) -> datetime:
    return datetime.fromisoformat(reference) + timedelta(seconds=float(nominal_offset))


def main() -> None:
    split_rows = list(csv.DictReader(Path("data/manifests/positive_split_assignments.csv").open(newline="")))
    qualities = defaultdict(list)
    for path in sorted(Path("data/manifests").glob("nonshallow_batch_*_window_quality.csv")):
        for row in csv.DictReader(path.open(newline="")):
            if row["integrity_status"] == "usable_integrity" and row["channel"] in PRIMARY:
                qualities[(row["event_id"], row["station"])].append(row)
    output = []
    for split in split_rows:
        choices = qualities.get((split["event_id"], split["station"]), [])
        if not choices:
            continue
        choice = sorted(choices, key=lambda row: PRIMARY.index(row["channel"]))[0]
        center = mapped_time(choice["reference_time"], choice["nominal_minus_reference_seconds"])
        output.append({
            "fold": split["fold"], "role": split["role"], "label": "event", "event_id": split["event_id"],
            "event_class": split["event_class"], "evaluation_group": split["evaluation_group"],
            "station": split["station"], "channel": choice["channel"],
            "window_start_nominal": (center - timedelta(seconds=120)).isoformat(),
            "window_end_nominal": (center + timedelta(seconds=480)).isoformat(),
            "sample_rate_hz": choice["sample_rate_hz"], "gap_fraction_audited": choice["gap_fraction"],
            "preprocessing_version": "primary-mh-v0.1",
        })
    path = Path("data/manifests/preprocessing_positive_windows.csv")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(output)
    print(f"wrote {len(output)} primary-channel positive windows to {path}")


if __name__ == "__main__":
    main()
