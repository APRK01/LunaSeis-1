#!/usr/bin/env python3
"""Build deterministic event/family-disjoint LOSO positive-window assignments."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

STATIONS = ("S12", "S14", "S15", "S16")


def assign_groups(group_times: dict[str, datetime], test_groups: set[str], validation_fraction: float = 0.2) -> dict[str, str]:
    eligible = sorted(((time, group) for group, time in group_times.items() if group not in test_groups))
    count = max(1, round(len(eligible) * validation_fraction)) if eligible else 0
    validation = {group for _, group in eligible[-count:]}
    return {group: "test" if group in test_groups else "validation" if group in validation else "train" for group in group_times}


def main() -> None:
    registry = list(csv.DictReader(Path("data/manifests/unified_positive_events.csv").open(newline="")))
    by_event = {row["event_id"]: row for row in registry}
    usable: set[tuple[str, str]] = set()
    for path in sorted(Path("data/manifests").glob("nonshallow_batch_*_request_quality.csv")):
        for row in csv.DictReader(path.open(newline="")):
            if row["request_integrity_status"] == "usable_integrity":
                usable.add((row["event_id"], row["station"]))
    for row in csv.DictReader(Path("data/manifests/shallow_window_quality.csv").open(newline="")):
        if row["integrity_status"] == "usable_integrity":
            usable.add((row["event_id"], row["station"]))

    group_times: dict[str, datetime] = {}
    for event, _ in usable:
        row = by_event[event]
        time = datetime.fromisoformat(row["reference_time"])
        group_times[row["evaluation_group"]] = min(time, group_times.get(row["evaluation_group"], time))

    output = []
    for heldout in STATIONS:
        test_groups = {by_event[event]["evaluation_group"] for event, station in usable if station == heldout}
        assignment = assign_groups(group_times, test_groups)
        for event, station in sorted(usable):
            source = by_event[event]
            group = source["evaluation_group"]
            role = assignment[group]
            included = role == "test" and station == heldout or role in {"train", "validation"} and station != heldout
            if included:
                output.append({
                    "fold": f"holdout_{heldout}", "held_out_station": heldout, "event_id": event,
                    "station": station, "event_class": source["event_class"], "evaluation_group": group,
                    "reference_time": source["reference_time"], "role": role,
                })

    path = Path("data/manifests/positive_split_assignments.csv")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(output)
    print(f"wrote {len(output)} positive assignments to {path}")


if __name__ == "__main__":
    main()
