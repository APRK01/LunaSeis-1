#!/usr/bin/env python3
"""Train/select artifact-robust tiny CNNs using development data only."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from obspy import Stream, UTCDateTime, read
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

try:
    from scripts.run_contiguous_scanning_v0_1 import merge_triggers, recall_threshold
    from scripts.run_tiny_cnn_pilot import TinyCNN, average_precision, deterministic_negative_rows, predict
except ModuleNotFoundError:  # pragma: no cover
    from run_contiguous_scanning_v0_1 import merge_triggers, recall_threshold
    from run_tiny_cnn_pilot import TinyCNN, average_precision, deterministic_negative_rows, predict

ROOT=Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform")
SEED=20260714
TARGET=4096
CANDIDATES=("robust_level","robust_difference")


def set_deterministic() -> None:
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.use_deterministic_algorithms(True)


@lru_cache(maxsize=2048)
def load_trace(station: str, year: int, doy: int, channel: str):
    directory=ROOT/station.lower()/str(year)/f"{doy:03d}"
    matches=sorted(directory.glob(f"*.{channel.lower()}.*.mseed"))
    if len(matches)!=1:raise FileNotFoundError(f"Expected one {station} {year}-{doy:03d} {channel}, found {matches}")
    return read(str(matches[0]))[0]


def robust_transform(values: np.ndarray, mode: str, length: int = TARGET) -> np.ndarray | None:
    values=np.asarray(values,dtype=np.float64);missing=values==-1
    if not values.size or np.mean(missing)>.2 or np.all(missing):return None
    if mode=="robust_difference":
        valid_pair=(~missing[1:])&(~missing[:-1]);transformed=np.zeros(len(values)-1);transformed[valid_pair]=np.diff(values)[valid_pair];missing=~valid_pair;values=transformed
    valid=values[~missing];center=float(np.median(valid));centered=valid-center
    mad=float(np.median(np.abs(centered)));p90=float(np.quantile(np.abs(centered),.9));scale=max(1.,1.4826*mad,p90/2.5)
    signal=np.zeros(length,dtype=np.float32);coverage=np.zeros(length,dtype=np.float32);count=min(length,len(values));good=~missing[:count]
    signal[:count][good]=np.clip((values[:count][good]-center)/scale,-20,20);coverage[:count][good]=1
    return np.stack([signal,coverage])


def extract(row: dict[str,str], key: str, mode: str) -> np.ndarray | None:
    start=datetime.fromisoformat(row[key]);utc=UTCDateTime(start.isoformat()+"Z");end=utc+600;days=[(utc.year,utc.julday)]
    if (end.year,end.julday)!=days[0]:days.append((end.year,end.julday))
    try:stream=Stream([load_trace(row["station"],year,doy,row["channel"]).copy() for year,doy in days])
    except FileNotFoundError:return None
    stream.merge(method=0,fill_value=-1)
    if len(stream)!=1:return None
    return robust_transform(np.asarray(stream[0].slice(utc,end,nearest_sample=False).data),mode)


def build(rows: list[dict[str,str]], label: int, key: str, mode: str) -> tuple[list[np.ndarray],list[int]]:
    x=[];y=[]
    for row in rows:
        sample=extract(row,key,mode)
        if sample is not None:x.append(sample);y.append(label)
    return x,y


def train_model(x: np.ndarray,y: np.ndarray,epochs: int=12) -> tuple[TinyCNN,list[float]]:
    set_deterministic();model=TinyCNN();optimizer=torch.optim.AdamW(model.parameters(),lr=8e-4,weight_decay=2e-4);loss_fn=nn.BCEWithLogitsLoss();history=[]
    generator=torch.Generator().manual_seed(SEED);loader=DataLoader(TensorDataset(torch.from_numpy(x),torch.from_numpy(y.astype(np.float32))),batch_size=64,shuffle=True,generator=generator)
    for _ in range(epochs):
        model.train();losses=[]
        for batch,labels in loader:
            optimizer.zero_grad();loss=loss_fn(model(batch),labels);loss.backward();optimizer.step();losses.append(float(loss.detach()))
        history.append(float(np.mean(losses)))
    return model,history


def ranked(rows: list[dict[str,str]], count: int, salt: str) -> list[dict[str,str]]:
    return sorted(rows,key=lambda row:hashlib.sha256(f"{salt}|{row['station']}|{row.get('window_start',row.get('start_time',''))}".encode()).hexdigest())[:count]


def scan_scores(model: nn.Module, rows: list[dict[str,str]], mode: str) -> list[dict]:
    output=[]
    for station_day in sorted({(r["station"],r["year"],r["doy"]) for r in rows}):
        chosen=[r for r in rows if (r["station"],r["year"],r["doy"])==station_day];samples=[];kept=[]
        for row in chosen:
            sample=extract(row,"window_start",mode)
            if sample is not None:samples.append(sample);kept.append(row)
        if not samples:continue
        scores=predict(model,np.asarray(samples,dtype=np.float32),batch_size=256)
        for row,score in zip(kept,scores):output.append({**row,"score":float(score),"inferred_reference_time":(datetime.fromisoformat(row["window_start"])+__import__('datetime').timedelta(seconds=120)).isoformat()})
    return output


def main() -> None:
    set_deterministic();positives=list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")));independent=list(csv.DictReader(Path("data/manifests/independent_background_windows.csv").open(newline="")))
    with gzip.open("data/manifests/continuous_validation_windows_v0.1.csv.gz","rt",newline="") as stream:continuous=list(csv.DictReader(stream))
    days_by_station=defaultdict(list)
    for row in continuous:days_by_station[row["station"]].append((int(row["year"]),int(row["doy"])))
    cutoff={station:sorted(set(days))[len(set(days))//2] for station,days in days_by_station.items()}
    report={"status":"development_only_model_selection_without_consumed_test_v0.1","seed":SEED,"candidates":{},"folds":{}}
    checkpoint_root=Path("models/checkpoints/artifact_robust_v0.1");checkpoint_root.mkdir(parents=True,exist_ok=True)
    for mode in CANDIDATES:
        report["candidates"][mode]={};aggregate_fp=0;aggregate_hours=0;aggregate_recall=[]
        for heldout in ("S12","S14","S15","S16"):
            fold=f"holdout_{heldout}";train_stations={"S12","S14","S15","S16"}-{heldout}
            pos_train=[r for r in positives if r["fold"]==fold and r["role"]=="train"]
            pos_val=[r for r in positives if r["fold"]==fold and r["role"]=="validation"]
            neg_base=[r for r in independent if r["fold"]==fold and r["role"]=="train"]
            hard_train=[r for r in continuous if r["station"] in train_stations and (int(r["year"]),int(r["doy"]))<cutoff[r["station"]]]
            hard_val=[r for r in continuous if r["station"] in train_stations and (int(r["year"]),int(r["doy"]))>=cutoff[r["station"]]]
            neg_base=deterministic_negative_rows(neg_base,len(pos_train));hard_train=ranked(hard_train,len(pos_train),f"{mode}|{fold}|hard")
            px,py=build(pos_train,1,"window_start_nominal",mode);nx,ny=build(neg_base,0,"start_time",mode);hx,hy=build(hard_train,0,"window_start",mode)
            x=np.asarray(px+nx+hx,dtype=np.float32);y=np.asarray(py+ny+hy,dtype=np.int64);model,history=train_model(x,y)
            vx,vy=build(pos_val,1,"window_start_nominal",mode);val_event_scores=predict(model,np.asarray(vx,dtype=np.float32));threshold=recall_threshold(val_event_scores,np.asarray(vy),.9)
            scored=scan_scores(model,hard_val,mode);trigger_rows=[{**r,f"{mode}_score":r["score"],"block_id":f"{r['station']}_VAL"} for r in scored];triggers=merge_triggers(trigger_rows,mode,threshold)
            starts_by_station=defaultdict(list)
            for r in hard_val:starts_by_station[r["station"]].append(datetime.fromisoformat(r["window_start"]))
            hours=sum((max(v)-min(v)).total_seconds()/3600+10/60 for v in starts_by_station.values() if v)
            fp_rate=len(triggers)/hours if hours else float("inf");recall=float(np.mean(val_event_scores>=threshold));aggregate_fp+=len(triggers);aggregate_hours+=hours;aggregate_recall.append(recall)
            checkpoint=checkpoint_root/f"{mode}_{fold}.pt";torch.save({"state_dict":model.state_dict(),"preprocessing":mode,"seed":SEED,"threshold":threshold},checkpoint)
            report["candidates"][mode][fold]={"train_counts":{"event":len(px),"independent_background":len(nx),"continuous_hard_background":len(hx)},"validation_event_count":len(vy),"validation_event_recall":recall,"threshold":threshold,"continuous_validation_windows":len(scored),"continuous_validation_hours":hours,"merged_false_triggers":len(triggers),"false_triggers_per_hour":fp_rate,"positive_window_fraction":float(np.mean([r["score"]>=threshold for r in scored])) if scored else None,"validation_event_pr_auc":average_precision(val_event_scores,np.asarray(vy)),"history":history,"checkpoint_sha256":hashlib.sha256(checkpoint.read_bytes()).hexdigest()}
            print(f"{mode} {fold}: recall={recall:.3f} FP/h={fp_rate:.3f}",flush=True)
        report["candidates"][mode]["aggregate"]={"validation_event_recall_mean":float(np.mean(aggregate_recall)),"merged_false_triggers":aggregate_fp,"continuous_validation_hours":aggregate_hours,"false_triggers_per_hour":aggregate_fp/aggregate_hours}
    selected=min(CANDIDATES,key=lambda mode:(report["candidates"][mode]["aggregate"]["false_triggers_per_hour"],-report["candidates"][mode]["aggregate"]["validation_event_recall_mean"]));report["selected_candidate"]=selected;report["selection_rule"]="lowest merged false triggers per hour after each fold threshold retained at least 90% prior positive-validation event recall; consumed test v0.1 was not read"
    report["selected_checkpoints"]={fold:str(checkpoint_root/f"{selected}_{fold}.pt") for fold in ("holdout_S12","holdout_S14","holdout_S15","holdout_S16")}
    path=Path("results/predictions/artifact_robust_model_selection_v0.1.json");path.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"selected_candidate":selected,"aggregates":{m:report['candidates'][m]['aggregate'] for m in CANDIDATES}},indent=2))


if __name__=="__main__":main()
