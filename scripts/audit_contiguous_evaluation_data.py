#!/usr/bin/env python3
"""Audit untouched contiguous days and eligible events without model inference."""

from __future__ import annotations

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
    from scripts.audit_pilot_waveforms import att_mapping
    from scripts.audit_shallow_windows import gap_statistics, integrity_status, robust_rms
except ModuleNotFoundError:  # pragma: no cover
    from audit_pilot_waveforms import att_mapping
    from audit_shallow_windows import gap_statistics, integrity_status, robust_rms

ROOT=Path("data/raw/apollo_pse_v1.0")


def full_day_status(att_gap: float, waveform_gap: float) -> str:
    maximum=max(att_gap,waveform_gap)
    return "reject_integrity" if maximum>0.2 else "questionable_integrity" if maximum>0.1 else "usable_integrity"


def local_gap_fraction(trace, start: UTCDateTime, seconds: int = 600) -> float:
    rate=float(trace.stats.sampling_rate);count=max(1,round(seconds*rate))
    left=round((start-trace.stats.starttime)*rate);right=left+count
    inside_left=max(0,left);inside_right=min(len(trace.data),right)
    outside=max(0,-left)+max(0,right-len(trace.data))
    inside=np.asarray(trace.data[inside_left:inside_right])
    return float((outside+np.count_nonzero(inside==-1))/count)


def merged_duration_seconds(starts: list[int], window_seconds: int = 600) -> int:
    if not starts:return 0
    total=0;left=starts[0];right=left+window_seconds
    for start in starts[1:]:
        if start<=right:right=max(right,start+window_seconds)
        else:total+=right-left;left=start;right=start+window_seconds
    return total+right-left


def main() -> None:
    plan=json.loads(Path("data/manifests/contiguous_evaluation_download_plan.json").read_text())
    days=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_station_days.csv").open(newline="")))
    products=defaultdict(list)
    for row in plan["products"]:
        path=Path(row["path"]);products[(path.parts[-4].upper(),int(path.parts[-3]),int(path.parts[-2]))].append(row)
    day_rows=[];traces={};total_windows=0;passing_windows=0;scannable_seconds=0
    for number,row in enumerate(days,1):
        key=(row["station"],int(row["year"]),int(row["doy"]));items=products[key]
        mseed=[ROOT/item["path"] for item in items if item["path"].endswith(".mseed")]
        att_path=next(path for path in mseed if ".att." in path.name);wave_path=next(path for path in mseed if ".att." not in path.name)
        att=read(str(att_path))[0];wave=read(str(wave_path))[0];traces[key]=(att,wave)
        att_stats=gap_statistics(att.data);wave_stats=gap_statistics(wave.data)
        status=full_day_status(float(att_stats["gap_fraction"]),float(wave_stats["gap_fraction"]))
        day_start=UTCDateTime(datetime(key[1],1,1)+timedelta(days=key[2]-1));starts=[]
        for offset in range(0,86400-600+1,60):
            total_windows+=1
            if local_gap_fraction(att,day_start+offset)<=0.2 and local_gap_fraction(wave,day_start+offset)<=0.2:
                passing_windows+=1;starts.append(offset)
        duration=merged_duration_seconds(starts);scannable_seconds+=duration
        day_rows.append({**row,"att_sample_rate_hz":float(att.stats.sampling_rate),"waveform_sample_rate_hz":float(wave.stats.sampling_rate),"att_trace_start":str(att.stats.starttime),"att_trace_end":str(att.stats.endtime),"waveform_trace_start":str(wave.stats.starttime),"waveform_trace_end":str(wave.stats.endtime),"att_gap_fraction":att_stats["gap_fraction"],"att_longest_gap_seconds":att_stats["longest_gap_samples"]/float(att.stats.sampling_rate),"waveform_gap_fraction":wave_stats["gap_fraction"],"waveform_longest_gap_seconds":wave_stats["longest_gap_samples"]/float(wave.stats.sampling_rate),"day_integrity_status":status,"candidate_scan_window_count":1431,"passing_scan_window_count":len(starts),"scannable_union_seconds":duration})
        print(f"[{number}/{len(days)}] audited {key[0]} {key[1]}-{key[2]:03d} {status}",flush=True)
    day_path=Path("data/manifests/contiguous_evaluation_day_quality.csv")
    with day_path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(day_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(day_rows)

    eligible=[row for row in csv.DictReader(Path("data/manifests/contiguous_evaluation_catalog_audit.csv").open(newline="")) if row["prospective_event_recall_eligibility"]=="eligible_pending_waveform_QA"]
    event_rows=[];plot_data=[]
    for row in eligible:
        target=UTCDateTime(row["reference_time"]+"Z");key=(row["station"],target.year,target.julday);att,wave=traces[key]
        mapping=att_mapping(att,target);mapped=UTCDateTime(mapping["nominal_time_at_nearest_att"])
        window=np.asarray(wave.slice(mapped-120,mapped+480,nearest_sample=False).data);att_window=np.asarray(att.slice(mapped-120,mapped+480,nearest_sample=False).data)
        gaps=gap_statistics(window);att_gaps=gap_statistics(att_window);status=integrity_status(float(gaps["gap_fraction"]),float(mapping["att_minus_target_seconds"]))
        before=wave.slice(mapped-120,mapped-20,nearest_sample=False).data;after=wave.slice(mapped,mapped+480,nearest_sample=False).data
        pre,post=robust_rms(before),robust_rms(after);ratio=post/pre if pre and post is not None else None
        support="not_quantifiable" if ratio is None else "strong_ratio" if ratio>=2 else "weak_ratio" if ratio>=1.2 else "no_clear_ratio"
        event_rows.append({**row,"nearest_att_minus_reference_seconds":mapping["att_minus_target_seconds"],"nominal_minus_reference_seconds":mapping["nominal_minus_target_seconds"],"waveform_sample_rate_hz":float(wave.stats.sampling_rate),"waveform_gap_fraction":gaps["gap_fraction"],"waveform_longest_gap_seconds":gaps["longest_gap_samples"]/float(wave.stats.sampling_rate),"att_window_gap_fraction":att_gaps["gap_fraction"],"pre_reference_rms":pre,"post_reference_rms":post,"post_to_pre_rms_ratio":ratio if ratio is not None else "","signal_support_descriptive":support,"event_window_integrity_status":status})
        values=window.astype(float);values[values==-1]=np.nan;seconds=np.arange(len(values))/float(wave.stats.sampling_rate)-120;plot_data.append((row,seconds,values,mapping["nominal_minus_target_seconds"]))
    event_path=Path("data/manifests/contiguous_evaluation_eligible_event_quality.csv")
    with event_path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(event_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(event_rows)
    fig,axes=plt.subplots(len(plot_data),1,figsize=(12,2.0*len(plot_data)),sharex=True)
    for axis,(row,seconds,values,offset) in zip(axes,plot_data):
        axis.plot(seconds,values,color="#17324d",linewidth=.55,rasterized=True);axis.axvline(0,color="#d1495b",linewidth=1,label="catalog reference");axis.axvline(float(offset),color="#e9a23b",linewidth=1,label="ATT-mapped nominal")
        axis.set_ylabel(f"{row['station']}\ncounts");axis.set_title(f"{row['unified_candidate_id']} — {row['event_class']}",loc="left",fontsize=9);axis.spines[["top","right"]].set_visible(False)
    axes[-1].set_xlabel("Seconds relative to catalog reference");axes[0].legend(frameon=False,fontsize=8,ncol=2);fig.suptitle("Untouched candidate windows: raw MH, no model inference");fig.tight_layout();figure=Path("results/figures/contiguous_evaluation_eligible_events.png");fig.savefig(figure,dpi=180);plt.close(fig)
    counts=Counter(row["day_integrity_status"] for row in day_rows);event_counts=Counter(row["event_window_integrity_status"] for row in event_rows);support=Counter(row["signal_support_descriptive"] for row in event_rows)
    summary={"status":"integrity_audited_no_model_inference","verified_product_count":plan["product_count"],"verified_total_bytes":plan["total_bytes"],"selected_station_days":len(day_rows),"day_integrity_counts":dict(counts),"day_integrity_by_station":{"|".join(key):value for key,value in sorted(Counter((row["station"],row["day_integrity_status"]) for row in day_rows).items())},"candidate_scan_windows":total_windows,"passing_scan_windows":passing_windows,"scannable_union_seconds":scannable_seconds,"scannable_union_hours":scannable_seconds/3600,"eligible_event_count":len(event_rows),"eligible_event_integrity_counts":dict(event_counts),"eligible_event_signal_support_descriptive":dict(support),"day_quality_sha256":hashlib.sha256(day_path.read_bytes()).hexdigest(),"eligible_event_quality_sha256":hashlib.sha256(event_path.read_bytes()).hexdigest(),"warning":"Signal ratios are descriptive and do not change catalog labels or integrity. No model was loaded or scored."}
    Path("results/predictions/contiguous_evaluation_integrity_summary.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
