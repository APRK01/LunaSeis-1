#!/usr/bin/env python3
"""Audit independent background days and construct event-buffered windows."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from obspy import read

try:
    from scripts.build_nonshallow_download_plan import product_names
except ModuleNotFoundError:  # pragma: no cover
    from build_nonshallow_download_plan import product_names

ROOT = Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform")
PREFERENCE = ("MHZ", "MH1", "MH2")
STATIONS = ("S12", "S14", "S15", "S16")


def gap_fraction(values: np.ndarray) -> float:
    values = np.asarray(values)
    return float(np.mean(values == -1)) if values.size else 1.0


def overlaps(start: datetime, end: datetime, events: list[datetime], buffer: timedelta) -> bool:
    return any(start < event + buffer and end > event - buffer for event in events)


def main() -> None:
    selected = list(csv.DictReader(Path("data/manifests/independent_background_station_days.csv").open(newline="")))
    events = [datetime.fromisoformat(r["catalog_start_minute"] + ":00") for r in csv.DictReader(Path("data/manifests/events_audit.csv").open(newline=""))]
    for row in csv.DictReader(Path("data/manifests/onodera_2024_shallow_events.csv").open(newline="")):
        h, m, s = map(int, row["start_time_utc"].split(":"))
        events.append(datetime(int(row["year"]), 1, 1) + timedelta(days=int(row["doy"]) - 1, hours=h, minutes=m, seconds=s))
    events_by_date = defaultdict(list)
    for event in events:
        for delta in (-1, 0, 1): events_by_date[(event + timedelta(days=delta)).date()].append(event)

    day_rows=[]; usable_days=[]
    for number, row in enumerate(selected, start=1):
        if row["att_and_at_least_one_mh_available"] != "1":
            day_rows.append({**row, "selected_primary_channel":"", "att_gap_fraction":"", "channel_gap_fraction":"", "day_integrity_status":"archive_incomplete"})
            continue
        station, year, doy = row["station"], int(row["year"]), int(row["doy"])
        channels=row["available_selected_channels"].split(";")
        channel=next(value for value in PREFERENCE if value in channels)
        directory=ROOT/station.lower()/str(year)/f"{doy:03d}"
        att=read(str(directory/product_names(station,year,doy,"ATT")[0]))[0]
        trace=read(str(directory/product_names(station,year,doy,channel)[0]))[0]
        att_gap=gap_fraction(att.data); channel_gap=gap_fraction(trace.data)
        status="usable_integrity" if att_gap<=0.2 and channel_gap<=0.2 else "reject_integrity"
        result={**row,"selected_primary_channel":channel,"att_gap_fraction":att_gap,"channel_gap_fraction":channel_gap,"day_integrity_status":status}
        day_rows.append(result)
        if status=="usable_integrity": usable_days.append(result)
        if number%100==0: print(f"[{number}/{len(selected)}] audited independent days",flush=True)

    # Chronological validation days are assigned before window selection.
    validation_days={}
    for station in STATIONS:
        keys=sorted((int(r["year"]),int(r["doy"])) for r in usable_days if r["station"]==station)
        count=max(1,round(0.2*len(keys))) if keys else 0
        validation_days[station]=set(keys[-count:])
    windows=[]; duration=timedelta(minutes=10); buffer=timedelta(hours=1)
    for row in usable_days:
        station,year,doy=row["station"],int(row["year"]),int(row["doy"])
        day=datetime(year,1,1)+timedelta(days=doy-1)
        for minute in range(0,24*60-10,30):
            start=day+timedelta(minutes=minute); end=start+duration
            if overlaps(start,end,events_by_date[day.date()],buffer): continue
            for heldout in STATIONS:
                role="test" if station==heldout else "validation" if (year,doy) in validation_days[station] else "train"
                windows.append({
                    "fold":f"holdout_{heldout}","held_out_station":heldout,"station":station,
                    "channel":row["selected_primary_channel"],"start_time":start.isoformat(),"end_time":end.isoformat(),
                    "role":role,"label":"catalog_negative_background","event_exclusion_buffer_seconds":3600,
                    "source_day_selection":"fixed_seed_independent_archive_day_sample_v0.1",
                })
    day_path=Path("data/manifests/independent_background_day_quality.csv")
    with day_path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(day_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(day_rows)
    window_path=Path("data/manifests/independent_background_windows.csv")
    with window_path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(windows[0]),lineterminator="\n");writer.writeheader();writer.writerows(windows)
    summary={
        "selected_station_days":len(day_rows),"archive_complete_station_days":sum(r["att_and_at_least_one_mh_available"]=="1" for r in day_rows),
        "usable_station_days":len(usable_days),"day_integrity_counts":dict(Counter(r["day_integrity_status"] for r in day_rows)),
        "usable_days_by_station":dict(Counter(r["station"] for r in usable_days)),"fold_window_rows":len(windows),
        "unique_physical_windows":len(windows)//4,"window_counts_by_fold_role":{"|".join(k):v for k,v in sorted(Counter((r["fold"],r["role"]) for r in windows).items())},
        "warning":"Catalog-negative does not mean physical noise; windows exclude known catalog times but may contain uncatalogued events or artifacts.",
    }
    path=Path("results/predictions/independent_background_audit.json");path.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
