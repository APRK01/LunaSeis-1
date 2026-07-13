#!/usr/bin/env python3
"""Build an event-independent, checksum-backed continuous-background plan."""

from __future__ import annotations

import argparse
import csv
import hashlib
import http.client
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from scripts.build_nonshallow_download_plan import product_names
    from scripts.build_shallow_download_plan import BASE_URL, SSL_CONTEXT, fetch_listing, fetch_md5_manifest
except ModuleNotFoundError:  # pragma: no cover
    from build_nonshallow_download_plan import product_names
    from build_shallow_download_plan import BASE_URL, SSL_CONTEXT, fetch_listing, fetch_md5_manifest

STATIONS = ("S12", "S14", "S15", "S16")
CHANNELS = ("ATT", "MH1", "MH2", "MHZ")
SEED = "lunaseis-independent-background-v0.1"
DIR_LINK = re.compile(r'>([0-9]{3,4})</A>', re.IGNORECASE)


def directory_numbers(url: str, digits: int) -> list[int]:
    for attempt in range(4):
        request = urllib.request.Request(url, headers={"User-Agent": "LunaSeis-1/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=120, context=SSL_CONTEXT) as response:
                text = response.read().decode("utf-8", errors="replace")
            break
        except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return sorted({int(value) for value in DIR_LINK.findall(text) if len(value) == digits})


def ranked_days(station: str, year: int, days: list[int], count: int) -> list[int]:
    return sorted(days, key=lambda doy: hashlib.sha256(f"{SEED}|{station}|{year}|{doy:03d}".encode()).hexdigest())[:count]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days-per-station-year", type=int, default=32)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--cache", type=Path, default=Path("data/interim/independent_background_listing_cache.json"))
    parser.add_argument("--days-output", type=Path, default=Path("data/manifests/independent_background_station_days.csv"))
    parser.add_argument("--plan-output", type=Path, default=Path("data/manifests/independent_background_download_plan.json"))
    args = parser.parse_args()

    selected = []
    for station in STATIONS:
        years = directory_numbers(f"{BASE_URL}/{station.lower()}/", 4)
        for year in years:
            days = directory_numbers(f"{BASE_URL}/{station.lower()}/{year}/", 3)
            for rank, doy in enumerate(ranked_days(station, year, days, args.days_per_station_year), start=1):
                selected.append((station, year, doy, rank, len(days)))
    if not selected:
        raise RuntimeError("Official archive directory discovery returned no station-days")

    args.cache.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(args.cache.read_text()) if args.cache.exists() else {}
    missing = [(s, y, d) for s, y, d, _, _ in selected if f"{s}:{y}:{d:03d}" not in cache]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch_listing, *key): key for key in missing}
        for number, future in enumerate(as_completed(futures), start=1):
            station, year, doy = futures[future]
            cache[f"{station}:{year}:{doy:03d}"] = future.result()
            if number % 50 == 0 or number == len(missing):
                args.cache.write_text(json.dumps(cache, separators=(",", ":")) + "\n")
            print(f"[{number}/{len(missing)}] inspected {station} {year}-{doy:03d}", flush=True)

    md5 = fetch_md5_manifest()
    products = []
    day_rows = []
    for station, year, doy, rank, available_count in sorted(selected):
        listing = cache[f"{station}:{year}:{doy:03d}"]
        complete_channels = [channel for channel in CHANNELS if all(name in listing for name in product_names(station, year, doy, channel))]
        usable = "ATT" in complete_channels and any(channel.startswith("MH") for channel in complete_channels)
        names = [name for channel in complete_channels for name in product_names(station, year, doy, channel)] if usable else []
        day_bytes = sum(listing[name] for name in names)
        day_rows.append({
            "station": station, "year": year, "doy": f"{doy:03d}", "selection_rank_within_station_year": rank,
            "archive_days_available_in_station_year": available_count, "att_and_at_least_one_mh_available": int(usable),
            "available_selected_channels": ";".join(complete_channels) if usable else "",
            "selected_bytes": day_bytes if usable else 0, "selection_seed": SEED,
        })
        if not usable:
            continue
        for name in names:
            path = f"data/xa/continuous_waveform/{station.lower()}/{year}/{doy:03d}/{name}"
            digest = md5.get(path.lower())
            if not digest:
                raise RuntimeError(f"Official MD5 missing for {path}")
            products.append({"path": path, "url": f"{BASE_URL}/{station.lower()}/{year}/{doy:03d}/{name}", "bytes": listing[name], "md5": digest})

    args.days_output.parent.mkdir(parents=True, exist_ok=True)
    with args.days_output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(day_rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(day_rows)
    products.sort(key=lambda item: item["path"])
    by_day = defaultdict(list)
    for item in products: by_day[str(Path(item["path"]).parent)].append(item)
    batches=[]; current={"batch_id":1,"station_day_count":0,"product_count":0,"bytes":0}; target=2*1024**3
    for _, items in sorted(by_day.items()):
        size=sum(int(item["bytes"]) for item in items)
        if current["station_day_count"] and current["bytes"]+size>target:
            batches.append(current); current={"batch_id":current["batch_id"]+1,"station_day_count":0,"product_count":0,"bytes":0}
        current["station_day_count"]+=1; current["product_count"]+=len(items); current["bytes"]+=size
        for item in items:item["batch_id"]=current["batch_id"]
    if current["station_day_count"]:batches.append(current)
    plan={
        "source_bundle":"urn:nasa:pds:apollo_pse::1.0",
        "selection":"Fixed-seed hash sample of official archive days within each station/year; selected before channel completeness inspection; event catalogs not read",
        "selection_seed":SEED,"days_per_station_year":args.days_per_station_year,
        "station_year_strata":len({(r[0],r[1]) for r in selected}),"station_days_selected":len(selected),
        "station_days_complete":sum(int(r["att_and_at_least_one_mh_available"]) for r in day_rows),
        "station_days_incomplete":sum(not int(r["att_and_at_least_one_mh_available"]) for r in day_rows),
        "station_days_by_station":dict(Counter(r["station"] for r in day_rows if int(r["att_and_at_least_one_mh_available"]))),
        "product_count":len(products),"total_bytes":sum(int(item["bytes"]) for item in products),
        "total_gib":sum(int(item["bytes"]) for item in products)/1024**3,
        "channels":list(CHANNELS),"batch_summaries":batches,
        "station_days_csv_sha256":hashlib.sha256(args.days_output.read_bytes()).hexdigest(),"products":products,
        "notes":["Selection is independent of known-event dates; event buffers are applied only when constructing windows after download.","Incomplete selected days are retained in the station-day audit and are not replaced.","Every planned product has exact archive-listed bytes and an official NASA PDS MD5."],
    }
    args.plan_output.write_text(json.dumps(plan,indent=2)+"\n")
    print(json.dumps({k:v for k,v in plan.items() if k!="products"},indent=2))


if __name__ == "__main__":
    main()
