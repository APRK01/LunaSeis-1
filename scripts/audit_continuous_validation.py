#!/usr/bin/env python3
"""Audit the sealed continuous-validation frame and quantify station/artifact shift."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime, read

try:
    from scripts.audit_contiguous_evaluation_data import full_day_status, local_gap_fraction, merged_duration_seconds
except ModuleNotFoundError:  # pragma: no cover
    from audit_contiguous_evaluation_data import full_day_status, local_gap_fraction, merged_duration_seconds

ROOT=Path("data/raw/apollo_pse_v1.0")


def robust_features(values: np.ndarray) -> dict[str,float]:
    values=np.asarray(values,dtype=float); missing=values==-1; valid=values[~missing]
    if not valid.size:return {key:float("nan") for key in ("median","mad","rms","peak_over_mad","max_step_over_mad","constant_fraction","extreme_fraction")}
    median=float(np.median(valid)); centered=valid-median; mad=float(np.median(np.abs(centered)))+1e-9
    diffs=np.abs(np.diff(valid)); unique,counts=np.unique(valid,return_counts=True)
    return {"median":median,"mad":mad,"rms":float(np.sqrt(np.mean(centered**2))),"peak_over_mad":float(np.max(np.abs(centered))/mad),"max_step_over_mad":float(np.max(diffs)/mad) if diffs.size else 0.,"constant_fraction":float(np.max(counts)/len(valid)),"extreme_fraction":float(np.mean(np.abs(centered)>20*mad))}


def catalog_times() -> list[datetime]:
    values=[]
    for row in csv.DictReader(Path("data/manifests/events_audit.csv").open(newline="")):values.append(datetime.fromisoformat(row["catalog_start_minute"]+":00"))
    for row in csv.DictReader(Path("data/manifests/onodera_2024_shallow_events.csv").open(newline="")):
        h,m,s=map(int,row["start_time_utc"].split(":"));values.append(datetime(int(row["year"]),1,1)+timedelta(days=int(row["doy"])-1,hours=h,minutes=m,seconds=s))
    return values


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days",type=Path,default=Path("data/manifests/continuous_validation_station_days_v0.1.csv"))
    parser.add_argument("--plan",type=Path,default=Path("data/manifests/continuous_validation_download_plan_v0.1.json"))
    parser.add_argument("--day-output",type=Path,default=Path("data/manifests/continuous_validation_day_quality_v0.1.csv"))
    parser.add_argument("--window-output",type=Path,default=Path("data/manifests/continuous_validation_windows_v0.1.csv.gz"))
    parser.add_argument("--summary",type=Path,default=Path("results/predictions/continuous_validation_audit_v0.1.json"))
    parser.add_argument("--figure",type=Path,default=Path("results/figures/continuous_validation_shift_v0.1.png"))
    args=parser.parse_args();days=list(csv.DictReader(args.days.open(newline="")));plan=json.loads(args.plan.read_text());groups=defaultdict(list)
    for item in plan["products"]:
        path=Path(item["path"]);groups[(path.parts[-4].upper(),int(path.parts[-3]),int(path.parts[-2]))].append(item)
    events=catalog_times();events_by_date=defaultdict(list)
    for event in events:
        for delta in (-1,0,1):events_by_date[(event+timedelta(days=delta)).date()].append(event)
    day_rows=[];window_rows=[];station_features=defaultdict(lambda:defaultdict(list));scannable=0
    for number,row in enumerate(days,1):
        station,year,doy=row["station"],int(row["year"]),int(row["doy"]);paths=[ROOT/item["path"] for item in groups[(station,year,doy)] if item["path"].endswith(".mseed")]
        att=read(str(next(path for path in paths if ".att." in path.name)))[0];wave=read(str(next(path for path in paths if ".att." not in path.name)))[0];start=UTCDateTime(datetime(year,1,1)+timedelta(days=doy-1));passing=[]
        att_full=float(np.mean(np.asarray(att.data)==-1));wave_full=float(np.mean(np.asarray(wave.data)==-1));status=full_day_status(att_full,wave_full)
        for offset in range(0,86400-600+1,60):
            window_start=start+offset
            if local_gap_fraction(att,window_start)>.2 or local_gap_fraction(wave,window_start)>.2:continue
            dt=datetime.fromisoformat(str(window_start).replace("Z",""));end=dt+timedelta(seconds=600)
            if any(dt<event+timedelta(hours=1) and end>event-timedelta(hours=1) for event in events_by_date[dt.date()]):continue
            values=np.asarray(wave.slice(window_start,window_start+600,nearest_sample=False).data);feat=robust_features(values);passing.append(offset)
            result={"station":station,"block_id":row["block_id"],"year":year,"doy":f"{doy:03d}","channel":row["selected_primary_channel"],"window_start":dt.isoformat(),"window_end":end.isoformat(),"att_gap_fraction":local_gap_fraction(att,window_start),"waveform_gap_fraction":local_gap_fraction(wave,window_start),**feat}
            window_rows.append(result)
            for key,value in feat.items():station_features[station][key].append(value)
        duration=merged_duration_seconds(passing);scannable+=duration;day_rows.append({**row,"att_gap_fraction":att_full,"waveform_gap_fraction":wave_full,"day_integrity_status":status,"catalog_excluded_passing_windows":len(passing),"scannable_union_seconds":duration})
        print(f"[{number}/{len(days)}] audited {station} {year}-{doy:03d}: {len(passing)} windows",flush=True)
    args.day_output.parent.mkdir(parents=True,exist_ok=True)
    with args.day_output.open("w",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(day_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(day_rows)
    import gzip
    with gzip.open(args.window_output,"wt",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(window_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(window_rows)
    feature_summary={station:{key:{"median":float(np.median(values)),"p95":float(np.quantile(values,.95)),"p99":float(np.quantile(values,.99))} for key,values in metrics.items()} for station,metrics in station_features.items()}
    artifact_counts={station:{"step_like":sum(value>50 for value in metrics["max_step_over_mad"]),"plateau_like":sum(value>.2 for value in metrics["constant_fraction"]),"extreme_like":sum(value>.01 for value in metrics["extreme_fraction"])} for station,metrics in station_features.items()}
    summary={"status":"development_only_unconsumed_continuous_validation","station_days":len(day_rows),"window_count":len(window_rows),"scannable_union_seconds":scannable,"scannable_union_hours":scannable/3600,"day_status_counts":dict(Counter(row["day_integrity_status"] for row in day_rows)),"windows_by_station":dict(Counter(row["station"] for row in window_rows)),"feature_summary_by_station":feature_summary,"artifact_proxy_counts_by_station":artifact_counts,"day_quality_sha256":hashlib.sha256(args.day_output.read_bytes()).hexdigest(),"window_manifest_sha256":hashlib.sha256(args.window_output.read_bytes()).hexdigest(),"warning":"Artifact labels are engineering proxies, not authoritative physical classifications. This frame is development-only and cannot become an untouched test."}
    args.summary.parent.mkdir(parents=True,exist_ok=True);args.summary.write_text(json.dumps(summary,indent=2)+"\n")
    features=("mad","peak_over_mad","max_step_over_mad","constant_fraction");fig,axes=plt.subplots(1,4,figsize=(15,4))
    for axis,key in zip(axes,features):
        data=[np.asarray(station_features[s][key]) for s in ("S12","S14","S15","S16")];axis.boxplot(data,tick_labels=("S12","S14","S15","S16"),showfliers=False);axis.set_title(key);axis.set_yscale("log" if key!="constant_fraction" else "linear");axis.spines[["top","right"]].set_visible(False)
    fig.suptitle("Unconsumed continuous-validation station and artifact proxies");fig.tight_layout();args.figure.parent.mkdir(parents=True,exist_ok=True);fig.savefig(args.figure,dpi=180);plt.close(fig);print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
