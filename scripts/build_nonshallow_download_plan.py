#!/usr/bin/env python3
"""Build an exact, checksum-backed nonshallow waveform download plan."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

try:
    from scripts.build_shallow_download_plan import BASE_URL, fetch_listing, fetch_md5_manifest
except ModuleNotFoundError:  # pragma: no cover
    from build_shallow_download_plan import BASE_URL, fetch_listing, fetch_md5_manifest


def required_dates(reference: datetime, pre_seconds: int = 120, post_seconds: int = 480) -> list[datetime]:
    dates = {reference.date(), (reference - timedelta(seconds=pre_seconds)).date(), (reference + timedelta(seconds=post_seconds)).date()}
    return [datetime.combine(date, datetime.min.time()) for date in sorted(dates)]


def product_names(station: str, year: int, doy: int, channel: str) -> tuple[str, str]:
    location = "00" if channel.upper().startswith("MH") else ""
    stem = f"xa.{station.lower()}.{location}.{channel.lower()}.{year}.{doy:03d}.0"
    return f"{stem}.mseed", f"{stem}.xml"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=Path("data/manifests/unified_positive_events.csv"))
    parser.add_argument("--requests-output", type=Path, default=Path("data/manifests/nonshallow_waveform_requests.csv"))
    parser.add_argument("--plan-output", type=Path, default=Path("data/manifests/nonshallow_download_plan.json"))
    parser.add_argument("--cache", type=Path, default=Path("data/interim/nonshallow_listing_cache.json"))
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    with args.events.open(encoding="utf-8", newline="") as stream:
        events = [row for row in csv.DictReader(stream) if row["candidate_status"] == "candidate_pending_waveform_qa"]

    requests = []
    station_day_channels = defaultdict(set)
    for row in events:
        reference = datetime.fromisoformat(row["reference_time"])
        station_channels = defaultdict(set)
        for token in filter(None, row["positive_visibility_channels"].split(";")):
            station, channel = token.split(".")
            station_channels[station].add(channel)
        for station, channels in sorted(station_channels.items()):
            dates = required_dates(reference)
            for date in dates:
                doy = date.timetuple().tm_yday
                station_day_channels[(station, date.year, doy)].update(channels | {"ATT"})
            requests.append({
                "event_id": row["event_id"], "event_class": row["event_class"], "reference_time": row["reference_time"],
                "station": station, "positive_channels": ";".join(sorted(channels)),
                "required_station_days": ";".join(f"{date.year}-{date.timetuple().tm_yday:03d}" for date in dates),
                "crosses_day_boundary": "1" if len(dates) > 1 else "0",
            })

    args.cache.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(args.cache.read_text()) if args.cache.exists() else {}
    keys = sorted(station_day_channels)
    missing = [key for key in keys if f"{key[0]}:{key[1]}:{key[2]:03d}" not in cache]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch_listing, *key): key for key in missing}
        for number, future in enumerate(as_completed(futures), start=1):
            key = futures[future]
            cache_key = f"{key[0]}:{key[1]}:{key[2]:03d}"
            cache[cache_key] = future.result()
            if number % 50 == 0 or number == len(missing):
                args.cache.write_text(json.dumps(cache, separators=(",", ":")) + "\n")
            print(f"[{number}/{len(missing)}] inspected {cache_key}: {len(cache[cache_key])} products", flush=True)

    md5 = fetch_md5_manifest()
    products = {}
    channel_day_status = {}
    for station, year, doy in keys:
        listing = cache[f"{station}:{year}:{doy:03d}"]
        for channel in sorted(station_day_channels[(station, year, doy)]):
            names = product_names(station, year, doy, channel)
            complete = all(name in listing for name in names)
            channel_day_status[(station, year, doy, channel)] = complete
            if complete:
                for name in names:
                    path = f"data/xa/continuous_waveform/{station.lower()}/{year}/{doy:03d}/{name}"
                    digest = md5.get(path.lower(), "")
                    if not digest:
                        raise RuntimeError(f"Official MD5 missing for {path}")
                    products[path] = {"path": path, "url": f"{BASE_URL}/{station.lower()}/{year}/{doy:03d}/{name}", "bytes": listing[name], "md5": digest}

    for request in requests:
        complete_channels = []
        missing_channels = []
        dates = [datetime.strptime(value, "%Y-%j") for value in request["required_station_days"].split(";")]
        for channel in request["positive_channels"].split(";"):
            complete = all(
                channel_day_status.get((request["station"], date.year, date.timetuple().tm_yday, channel), False)
                and channel_day_status.get((request["station"], date.year, date.timetuple().tm_yday, "ATT"), False)
                for date in dates
            )
            (complete_channels if complete else missing_channels).append(channel)
        request["complete_positive_channels"] = ";".join(complete_channels)
        request["missing_positive_channels"] = ";".join(missing_channels)
        request["station_request_usable"] = "1" if complete_channels else "0"

    args.requests_output.parent.mkdir(parents=True, exist_ok=True)
    with args.requests_output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(requests[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(requests)
    requests_sha256 = hashlib.sha256(args.requests_output.read_bytes()).hexdigest()

    event_requests = defaultdict(list)
    for row in requests:
        event_requests[row["event_id"]].append(row)
    missing_events = sorted(event_id for event_id, rows in event_requests.items() if not any(row["station_request_usable"] == "1" for row in rows))
    product_list = [products[path] for path in sorted(products)]
    bytes_by_channel = Counter()
    products_by_channel = Counter()
    for item in product_list:
        channel = Path(item["path"]).name.split(".")[3].upper()
        bytes_by_channel[channel] += int(item["bytes"])
        products_by_channel[channel] += 1
    total = sum(int(item["bytes"]) for item in product_list)
    batch_target = 2 * 1024 ** 3
    by_directory = defaultdict(list)
    for item in product_list:
        by_directory[str(Path(item["path"]).parent)].append(item)
    batches = []
    current = {"batch_id": 1, "station_days": [], "product_count": 0, "bytes": 0}
    for directory, items in sorted(by_directory.items()):
        day_bytes = sum(int(item["bytes"]) for item in items)
        if current["station_days"] and current["bytes"] + day_bytes > batch_target:
            batches.append(current)
            current = {"batch_id": current["batch_id"] + 1, "station_days": [], "product_count": 0, "bytes": 0}
        current["station_days"].append(directory)
        current["product_count"] += len(items)
        current["bytes"] += day_bytes
        for item in items:
            item["batch_id"] = current["batch_id"]
    if current["station_days"]:
        batches.append(current)
    for batch in batches:
        batch["station_day_count"] = len(batch.pop("station_days"))
    plan = {
        "source_bundle": "urn:nasa:pds:apollo_pse::1.0",
        "selection": "Nonshallow conservative candidates; positive visibility channels plus ATT; include boundary days for [-120,+480] s windows",
        "event_count": len(events), "event_station_requests": len(requests),
        "requests_csv_sha256": requests_sha256,
        "events_with_at_least_one_usable_station_request": len(events) - len(missing_events),
        "events_without_usable_station_request": missing_events,
        "unique_station_days_requested": len(keys),
        "station_day_channel_requests_including_att": sum(len(value) for value in station_day_channels.values()),
        "product_count": len(product_list), "total_bytes": total,
        "total_mib": total / 1024 ** 2, "total_gib": total / 1024 ** 3,
        "products_by_channel": dict(sorted(products_by_channel.items())),
        "bytes_by_channel": dict(sorted(bytes_by_channel.items())),
        "recommended_batch_target_bytes": batch_target,
        "recommended_batch_count": len(batches), "batch_summaries": batches,
        "products": product_list,
        "notes": [
            "This is an availability/storage plan, not downloaded data.",
            "Positive channel flags are catalog evidence, not proof of a gap-free event window.",
            "Every selected product has exact listed bytes and an official PDS MD5.",
            "Batch recommendation limits resumable raw downloads to about 2 GiB each.",
        ],
    }
    args.plan_output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in plan.items() if key != "products"}, indent=2))


if __name__ == "__main__":
    main()
