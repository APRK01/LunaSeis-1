#!/usr/bin/env python3
"""Run the frozen v0.2 operational comparison exactly once."""

from __future__ import annotations

import csv,gzip,hashlib,io,json
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from obspy import UTCDateTime,read

try:
    from scripts.audit_contiguous_evaluation_data import local_gap_fraction,merged_duration_seconds
    from scripts.run_contiguous_scanning_v0_1 import catalog_references,match_triggers,merge_triggers,reconstruct_fold
    from scripts.run_tiny_cnn_pilot import TinyCNN,fixed_length,predict
    from scripts.run_contiguous_scanning_v0_1 import feature_vector
    from scripts.train_artifact_robust_models import robust_transform
except ModuleNotFoundError:  # pragma: no cover
    from audit_contiguous_evaluation_data import local_gap_fraction,merged_duration_seconds
    from run_contiguous_scanning_v0_1 import catalog_references,match_triggers,merge_triggers,reconstruct_fold,feature_vector
    from run_tiny_cnn_pilot import TinyCNN,fixed_length,predict
    from train_artifact_robust_models import robust_transform

ROOT=Path("data/raw/apollo_pse_v1.0")
MODELS=("artifact_robust_cnn","original_tiny_cnn","logistic_handcrafted","sta_lta")


def main() -> None:
    positives=list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")));backgrounds=list(csv.DictReader(Path("data/manifests/independent_background_windows.csv").open(newline="")))
    original={};robust={};thresholds={}
    for station in ("S12","S14","S15","S16"):
        fold=f"holdout_{station}";old_thresholds,model,scale,mean,std,weights=reconstruct_fold(fold,positives,backgrounds);original[station]=(model,scale,mean,std,weights)
        checkpoint=torch.load(f"models/checkpoints/artifact_robust_v0.1/robust_level_{fold}.pt",weights_only=True);new=TinyCNN();new.load_state_dict(checkpoint["state_dict"]);new.eval();robust[station]=new
        thresholds[fold]={"artifact_robust_cnn":float(checkpoint["threshold"]),"original_tiny_cnn":old_thresholds["tiny_cnn"]["primary"],"logistic_handcrafted":old_thresholds["logistic_handcrafted"]["primary"],"sta_lta":old_thresholds["sta_lta"]["primary"]}
    threshold_path=Path("results/predictions/continuous_scanning_thresholds_v0.2.json");threshold_path.write_text(json.dumps({"status":"frozen_from_v0.1_development_validation_before_v0.2_inference","folds":thresholds},indent=2)+"\n")
    plan=json.loads(Path("data/manifests/contiguous_evaluation_download_plan_v0.2.json").read_text());days=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_day_quality_v0.2.csv").open(newline="")));groups=defaultdict(list)
    for item in plan["products"]:
        path=Path(item["path"]);groups[(path.parts[-4].upper(),int(path.parts[-3]),int(path.parts[-2]))].append(item)
    predictions=[]
    for number,day in enumerate(days,1):
        station,year,doy=day["station"],int(day["year"]),int(day["doy"]);paths=[ROOT/item["path"] for item in groups[(station,year,doy)] if item["path"].endswith(".mseed")];att=read(str(next(p for p in paths if ".att." in p.name)))[0];wave=read(str(next(p for p in paths if ".att." not in p.name)))[0]
        old,scale,mean,std,weights=original[station];new=robust[station];start=UTCDateTime(datetime(year,1,1)+timedelta(days=doy-1));old_x=[];new_x=[];features=[];meta=[]
        for offset in range(0,86400-600+1,60):
            left=start+offset;ag=local_gap_fraction(att,left);wg=local_gap_fraction(wave,left)
            if ag>.2 or wg>.2:continue
            values=np.asarray(wave.slice(left,left+600,nearest_sample=False).data,dtype=float);missing=values==-1;valid=values[~missing];centered=values.copy();centered[~missing]-=np.median(valid);signal,coverage=fixed_length(centered,missing);old_x.append(np.stack([signal,coverage]));new_x.append(robust_transform(values,"robust_level"));vector=feature_vector(values,float(wave.stats.sampling_rate));features.append(vector);meta.append((left,ag,wg))
        ox=np.asarray(old_x,dtype=np.float32);ox[:,0]/=scale;old_scores=predict(old,ox,batch_size=256);new_scores=predict(new,np.asarray(new_x,dtype=np.float32),batch_size=256);f=np.asarray(features);logistic=1/(1+np.exp(-np.clip(np.column_stack([np.ones(len(f)),(f-mean)/std])@weights,-30,30)))
        for (left,ag,wg),a,b,c,d in zip(meta,new_scores,old_scores,logistic,f[:,4]):predictions.append({"station":station,"block_id":day["block_id"],"year":year,"doy":f"{doy:03d}","window_start":str(left).replace("Z",""),"window_end":str(left+600).replace("Z",""),"inferred_reference_time":str(left+120).replace("Z",""),"att_gap_fraction":ag,"waveform_gap_fraction":wg,"artifact_robust_cnn_score":float(a),"original_tiny_cnn_score":float(b),"logistic_handcrafted_score":float(c),"sta_lta_score":float(d)})
        print(f"[{number}/{len(days)}] scored {station} {year}-{doy:03d}: {len(meta)}",flush=True)
    expected=sum(int(row["passing_scan_window_count"]) for row in days)
    if len(predictions)!=expected:raise RuntimeError(f"Expected {expected} predictions, got {len(predictions)}")
    prediction_path=Path("results/predictions/continuous_scanning_window_scores_v0.2.csv.gz")
    with prediction_path.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as compressed:
            with io.TextIOWrapper(compressed,newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(predictions[0]),lineterminator="\n");writer.writeheader();writer.writerows(predictions)
    catalog_rows=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_catalog_audit_v0.2.csv").open(newline="")));quality=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_eligible_event_quality_v0.2.csv").open(newline="")));eligible={r["unified_candidate_id"] for r in quality if r["event_window_integrity_status"]=="usable_integrity"};catalogs=catalog_references(catalog_rows,eligible)
    total_seconds=sum(int(r["scannable_union_seconds"]) for r in days);hours=total_seconds/3600;station_hours={s:sum(int(r["scannable_union_seconds"]) for r in days if r["station"]==s)/3600 for s in ("S12","S14","S15","S16")};report={"status":"frozen_untouched_contiguous_scan_v0.2_final_pilot_comparison","eligible_event_count":len(eligible),"scannable_union_hours":hours,"models":{}};all_triggers=[]
    for name in MODELS:
        triggers=[];retention=0
        for station in ("S12","S14","S15","S16"):
            rows=[r for r in predictions if r["station"]==station];threshold=thresholds[f"holdout_{station}"][name];triggers.extend(merge_triggers(rows,name,threshold))
            for block in {r["block_id"] for r in rows}:
                chosen=[r for r in rows if r["block_id"]==block];base=min(datetime.fromisoformat(r["window_start"]) for r in chosen);starts=sorted(int((datetime.fromisoformat(r["window_start"])-base).total_seconds()) for r in chosen if r[f"{name}_score"]>=threshold);retention+=merged_duration_seconds(starts)
        for index,row in enumerate(triggers,1):row["trigger_id"]=f"{name}-{index:05d}"
        sensitivities={};primary=[]
        for tolerance in (60,180,300):
            annotated,count=match_triggers(triggers,catalogs,tolerance);tp=count["eligible_true_triggers"];fp=count["false_triggers"];recall=tp/max(1,len(eligible));precision=tp/max(1,tp+fp);count.update({"eligible_event_recall":recall,"precision_excluding_protected_catalog_triggers":precision,"f1":2*precision*recall/max(1e-12,precision+recall),"false_triggers_per_hour":fp/hours,"false_triggers_per_day":fp/(hours/24),"median_latency_seconds":float(np.median(count["latencies_seconds"])) if count["latencies_seconds"] else None});sensitivities[str(tolerance)]=count
            if tolerance==180:primary=annotated
        report["models"][name]={"trigger_count":len(triggers),"retained_union_seconds":retention,"retained_fraction_of_scannable_duration":retention/total_seconds,"matching_sensitivities":sensitivities,"primary_180s_by_station":{s:{"false_triggers":sum(r["station"]==s and r["match_status"]=="false_trigger" for r in primary),"scan_hours":station_hours[s]} for s in station_hours}};all_triggers.extend(primary)
    trigger_path=Path("results/predictions/continuous_scanning_triggers_v0.2.csv")
    with trigger_path.open("w",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(all_triggers[0]),lineterminator="\n");writer.writeheader();writer.writerows(all_triggers)
    report.update({"window_score_sha256":hashlib.sha256(prediction_path.read_bytes()).hexdigest(),"trigger_csv_sha256":hashlib.sha256(trigger_path.read_bytes()).hexdigest(),"threshold_json_sha256":hashlib.sha256(threshold_path.read_bytes()).hexdigest()});Path("results/predictions/continuous_scanning_results_v0.2.json").write_text(json.dumps(report,indent=2)+"\n")
    primary=[report["models"][m]["matching_sensitivities"]["180"] for m in MODELS];fig,axes=plt.subplots(1,3,figsize=(14,4));labels=["robust CNN","original CNN","logistic","STA/LTA"]
    for axis,values,title,ylabel in ((axes[0],[r["false_triggers_per_hour"] for r in primary],"False-trigger burden","False triggers/hour"),(axes[1],[r["eligible_event_recall"] for r in primary],"Descriptive recall (n=3)","Event recall"),(axes[2],[report["models"][m]["retained_fraction_of_scannable_duration"] for m in MODELS],"Retention simulation","Retained fraction")):
        axis.bar(labels,values,color=["#d95f02","#7570b3","#1b9e77","#666666"]);axis.tick_params(axis="x",rotation=25);axis.set_title(title);axis.set_ylabel(ylabel);axis.spines[["top","right"]].set_visible(False)
    axes[1].set_ylim(0,1);axes[2].set_ylim(0,1)
    fig.suptitle("LunaSeis-1 frozen continuous comparison v0.2");fig.tight_layout();fig.savefig("results/figures/continuous_scanning_results_v0.2.png",dpi=180);plt.close(fig);print(json.dumps(report,indent=2))


if __name__=="__main__":main()
