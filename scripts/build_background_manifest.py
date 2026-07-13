#!/usr/bin/env python3
"""Construct deterministic catalog-negative candidates after fold assignment."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

STATIONS = ("S12", "S14", "S15", "S16")


def overlaps_event(start: datetime, end: datetime, events: list[datetime], buffer: timedelta) -> bool:
    return any(start < event + buffer and end > event - buffer for event in events)


def main() -> None:
    plan = json.loads(Path("data/manifests/nonshallow_download_plan.json").read_text())
    event_times = [datetime.fromisoformat(row["catalog_start_minute"] + ":00") for row in csv.DictReader(Path("data/manifests/events_audit.csv").open(newline=""))]
    shallow = list(csv.DictReader(Path("data/manifests/onodera_2024_shallow_events.csv").open(newline="")))
    for row in shallow:
        event_times.append(datetime(int(row["year"]), 1, 1) + timedelta(days=int(row["doy"]) - 1, hours=int(row["start_time_utc"][:2]), minutes=int(row["start_time_utc"][3:5]), seconds=int(row["start_time_utc"][6:])))
    by_date = defaultdict(list)
    for event in event_times:
        for delta in (-1, 0, 1):
            by_date[(event + timedelta(days=delta)).date()].append(event)

    available = set()
    for item in plan["products"]:
        if not item["path"].endswith(".mseed") or "..att." in item["path"]:
            continue
        parts = item["path"].split("/")
        station, year, doy = parts[-4].upper(), int(parts[-3]), int(parts[-2])
        name = parts[-1].split(".")
        channel = name[3].upper()
        available.add((station, year, doy, channel))

    all_days = sorted({datetime(year, 1, 1) + timedelta(days=doy - 1) for _, year, doy, _ in available})
    cutoff = all_days[round(0.8 * len(all_days))] if all_days else datetime.max
    candidates = []
    duration = timedelta(minutes=10); buffer = timedelta(hours=1)
    for station, year, doy, channel in sorted(available):
        day = datetime(year, 1, 1) + timedelta(days=doy - 1)
        valid = []
        for minute in range(0, 24 * 60 - 10, 30):
            start = day + timedelta(minutes=minute); end = start + duration
            if not overlaps_event(start, end, by_date[day.date()], buffer):
                valid.append(start)
        valid.sort(key=lambda value: hashlib.sha256(f"{station}|{channel}|{value.isoformat()}|lunaseis-v0.1".encode()).hexdigest())
        for start in sorted(valid[:4]):
            for heldout in STATIONS:
                role = "test" if station == heldout else "validation" if day >= cutoff else "train"
                candidates.append({
                    "fold": f"holdout_{heldout}", "held_out_station": heldout, "station": station,
                    "channel": channel, "start_time": start.isoformat(), "end_time": (start + duration).isoformat(),
                    "role": role, "label": "catalog_negative_background", "event_exclusion_buffer_seconds": 3600,
                    "selection_seed": "lunaseis-v0.1", "source_day_bias_warning": "days_selected_for_positive-coverage_audit",
                })
    path = Path("data/manifests/background_window_candidates.csv")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(candidates[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(candidates)
    print(f"wrote {len(candidates)} catalog-negative candidates to {path}")


if __name__ == "__main__":
    main()
