#!/usr/bin/env python3
"""Build an untouched, fixed-seed contiguous-scanning evaluation plan."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

try:
    from scripts.build_independent_background_plan import directory_numbers
    from scripts.build_shallow_download_plan import BASE_URL, fetch_listing, fetch_md5_manifest
except ModuleNotFoundError:  # pragma: no cover
    from build_independent_background_plan import directory_numbers
    from build_shallow_download_plan import BASE_URL, fetch_listing, fetch_md5_manifest

STATIONS=("S12","S14","S15","S16")
CHANNELS=("ATT","MHZ","MH1","MH2")
SEED="lunaseis-contiguous-evaluation-v0.1"
PATH_DAY=re.compile(r"/(s(?:12|14|15|16))/(\d{4})/(\d{3})/",re.IGNORECASE)


def station_day_from_path(value: str) -> tuple[str,int,int] | None:
    match=PATH_DAY.search("/"+value.lstrip("/"))
    return (match.group(1).upper(),int(match.group(2)),int(match.group(3))) if match else None


def channel_product_names(listing: dict[str,int], channel: str) -> list[str]:
    """Resolve the archive's actual blank/00/01 location code for one channel."""
    mseed=sorted(name for name in listing if f".{channel.lower()}." in name.lower() and name.lower().endswith(".mseed"))
    pairs=[]
    for name in mseed:
        label=name[:-5]+"xml"
        if label in listing:pairs.append([name,label])
    if len(pairs)>1:raise RuntimeError(f"Ambiguous {channel} MiniSEED products: {pairs}")
    return pairs[0] if pairs else []


def prior_station_days(manifest_root: Path, ignored_outputs: set[Path] | None = None) -> set[tuple[str,int,int]]:
    """Collect exposed station-days from committed planning manifests only."""
    days=set()
    ignored_outputs={path.resolve() for path in (ignored_outputs or set())}
    for path in sorted(manifest_root.glob("*.json")):
        if path.resolve() in ignored_outputs:continue
        try:data=json.loads(path.read_text())
        except (json.JSONDecodeError,UnicodeDecodeError):continue
        stack=[data]
        while stack:
            item=stack.pop()
            if isinstance(item,dict):
                for key,value in item.items():
                    if key in {"path","url","relative_path"} and isinstance(value,str):
                        parsed=station_day_from_path(value)
                        if parsed:days.add(parsed)
                    elif isinstance(value,(dict,list)):stack.append(value)
            elif isinstance(item,list):stack.extend(item)
    for path in sorted(manifest_root.glob("*.csv")):
        if path.resolve() in ignored_outputs:continue
        try:rows=csv.DictReader(path.open(newline=""))
        except UnicodeDecodeError:continue
        for row in rows:
            if {"station","year","doy"}.issubset(row) and row["station"] in STATIONS:
                try:days.add((row["station"],int(row["year"]),int(row["doy"])))
                except (TypeError,ValueError):pass
            for value in row.values():
                if isinstance(value,str):
                    parsed=station_day_from_path(value)
                    if parsed:days.add(parsed)
    return days


def candidate_blocks(station: str, archive_days: dict[int,list[int]], excluded: set[tuple[str,int,int]], length: int, seed: str = SEED) -> list[tuple[str,int,int]]:
    candidates=[]
    for year,days in sorted(archive_days.items()):
        available=set(days)
        for start in days:
            block=range(start,start+length)
            if all(day in available and (station,year,day) not in excluded for day in block):
                key=hashlib.sha256(f"{seed}|{station}|{year}|{start:03d}".encode()).hexdigest()
                candidates.append((key,year,start))
    return sorted(candidates)


def select_nonoverlapping(candidates: list[tuple[str,int,int]], count: int, length: int) -> list[tuple[int,int]]:
    selected=[]
    for _,year,start in candidates:
        days=set(range(start,start+length))
        if any(year==old_year and days & set(range(old_start,old_start+length)) for old_year,old_start in selected):continue
        selected.append((year,start))
        if len(selected)==count:break
    return sorted(selected)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block-days",type=int,default=14)
    parser.add_argument("--blocks-per-station",type=int,default=2)
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--seed",default=SEED)
    parser.add_argument("--cache",type=Path,default=Path("data/interim/contiguous_evaluation_listing_cache.json"))
    parser.add_argument("--days-output",type=Path,default=Path("data/manifests/contiguous_evaluation_station_days.csv"))
    parser.add_argument("--plan-output",type=Path,default=Path("data/manifests/contiguous_evaluation_download_plan.json"))
    args=parser.parse_args()
    excluded=prior_station_days(Path("data/manifests"),{args.days_output,args.plan_output})
    selected=[]
    for station in STATIONS:
        archive={year:directory_numbers(f"{BASE_URL}/{station.lower()}/{year}/",3) for year in directory_numbers(f"{BASE_URL}/{station.lower()}/",4)}
        blocks=select_nonoverlapping(candidate_blocks(station,archive,excluded,args.block_days,args.seed),args.blocks_per_station,args.block_days)
        if len(blocks)!=args.blocks_per_station:raise RuntimeError(f"Could not select {args.blocks_per_station} untouched blocks for {station}")
        for block_number,(year,start) in enumerate(blocks,1):
            for offset in range(args.block_days):selected.append((station,year,start+offset,f"{station}_B{block_number}",offset+1))
    if any((s,y,d) in excluded for s,y,d,_,_ in selected):raise RuntimeError("Selected frame overlaps a prior station-day")
    args.cache.parent.mkdir(parents=True,exist_ok=True);cache=json.loads(args.cache.read_text()) if args.cache.exists() else {}
    missing=[(s,y,d) for s,y,d,_,_ in selected if f"{s}:{y}:{d:03d}" not in cache]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(fetch_listing,*key):key for key in missing}
        for number,future in enumerate(as_completed(futures),1):
            s,y,d=futures[future];cache[f"{s}:{y}:{d:03d}"]=future.result()
            if number%20==0 or number==len(missing):args.cache.write_text(json.dumps(cache,separators=(",",":"))+"\n")
            print(f"[{number}/{len(missing)}] inspected {s} {y}-{d:03d}",flush=True)
    official_md5=fetch_md5_manifest();products=[];rows=[]
    for station,year,doy,block_id,day_in_block in sorted(selected):
        listing=cache[f"{station}:{year}:{doy:03d}"]
        resolved={channel:channel_product_names(listing,channel) for channel in CHANNELS}
        complete_channels=[channel for channel in CHANNELS if resolved[channel]]
        usable="ATT" in complete_channels and any(channel.startswith("MH") for channel in complete_channels)
        chosen=[]
        if usable:
            primary=next(channel for channel in ("MHZ","MH1","MH2") if channel in complete_channels)
            for channel in ("ATT",primary):chosen.extend(resolved[channel])
        row={"station":station,"year":year,"doy":f"{doy:03d}","block_id":block_id,"day_in_block":day_in_block,"selection_seed":args.seed,"prior_station_day_overlap":0,"att_and_primary_mh_available":int(usable),"selected_primary_channel":primary if usable else "","selected_bytes":sum(listing[name] for name in chosen)}
        rows.append(row)
        for name in chosen:
            relative=f"data/xa/continuous_waveform/{station.lower()}/{year}/{doy:03d}/{name}"
            digest=official_md5.get(relative.lower())
            if not digest:raise RuntimeError(f"Official MD5 missing for {relative}")
            products.append({"path":relative,"url":f"{BASE_URL}/{station.lower()}/{year}/{doy:03d}/{name}","bytes":listing[name],"md5":digest,"block_id":block_id})
    args.days_output.parent.mkdir(parents=True,exist_ok=True)
    with args.days_output.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    products.sort(key=lambda row:row["path"]);counts=Counter(row["station"] for row in rows if row["att_and_primary_mh_available"]==1)
    block_summary=[]
    for block in sorted({row["block_id"] for row in rows}):
        chosen=[row for row in rows if row["block_id"]==block]
        block_summary.append({"block_id":block,"station":chosen[0]["station"],"year":int(chosen[0]["year"]),"start_doy":int(chosen[0]["doy"]),"end_doy":int(chosen[-1]["doy"]),"selected_days":len(chosen),"complete_days":sum(row["att_and_primary_mh_available"]==1 for row in chosen),"bytes":sum(int(row["selected_bytes"]) for row in chosen)})
    plan={"status":"planned_not_downloaded","source_bundle":"urn:nasa:pds:apollo_pse::1.0","selection_seed":args.seed,"selection":f"{args.blocks_per_station} hash-ranked nonoverlapping {args.block_days}-day block(s) per station, selected from official archive days after excluding all station-days exposed by prior manifests; no event catalogs, channel quality, or model scores used for selection","prior_station_days_excluded":len(excluded),"station_days_selected":len(rows),"station_days_complete":sum(row["att_and_primary_mh_available"]==1 for row in rows),"station_days_incomplete":sum(row["att_and_primary_mh_available"]==0 for row in rows),"complete_days_by_station":dict(counts),"product_count":len(products),"total_bytes":sum(int(row["bytes"]) for row in products),"total_gib":sum(int(row["bytes"])/1024**3 for row in products),"block_summaries":block_summary,"station_days_csv_sha256":hashlib.sha256(args.days_output.read_bytes()).hexdigest(),"products":products,"notes":["Selected blocks are never replaced for missing channels.","Catalog event coverage is audited only after selection and cannot alter the frame.","No waveform is downloaded by this planning script."]}
    args.plan_output.write_text(json.dumps(plan,indent=2)+"\n");print(json.dumps({key:value for key,value in plan.items() if key!="products"},indent=2))


if __name__=="__main__":main()
