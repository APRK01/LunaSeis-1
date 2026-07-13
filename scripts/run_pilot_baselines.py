#!/usr/bin/env python3
"""Run leakage-aware pilot energy, STA/LTA, and logistic baselines."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from obspy import Stream, UTCDateTime, read
from scipy.optimize import minimize

try:
    from scripts.build_nonshallow_download_plan import product_names
except ModuleNotFoundError:  # pragma: no cover
    from build_nonshallow_download_plan import product_names

ROOT = Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform")


@lru_cache(maxsize=4096)
def load_day(station: str, year: int, doy: int, channel: str):
    name = product_names(station, year, doy, channel)[0]
    return read(str(ROOT / station.lower() / str(year) / f"{doy:03d}" / name))[0]


def features(station: str, channel: str, start: datetime) -> np.ndarray | None:
    utc = UTCDateTime(start.isoformat() + "Z")
    end = utc + 600
    days = [(utc.year, utc.julday)]
    if (end.year, end.julday) != days[0]:
        days.append((end.year, end.julday))
    try:
        stream = Stream([load_day(station, year, doy, channel).copy() for year, doy in days])
    except FileNotFoundError:
        return None
    stream.merge(method=0, fill_value=-1)
    if len(stream) != 1:
        return None
    trace = stream[0]
    values = np.asarray(trace.slice(utc, utc + 600, nearest_sample=False).data, dtype=float)
    if not values.size:
        return None
    missing = values == -1
    if missing.mean() > 0.2:
        return None
    valid = values[~missing]
    values[missing] = np.median(valid)
    values -= np.median(valid)
    rms = float(np.sqrt(np.mean(values * values))) + 1e-12
    abs_values = np.abs(values)
    short = max(1, round(5 * float(trace.stats.sampling_rate)))
    long = max(short + 1, round(60 * float(trace.stats.sampling_rate)))
    energy = values * values
    cs = np.concatenate([[0.0], np.cumsum(energy)])
    sta = (cs[short:] - cs[:-short]) / short
    lta = (cs[long:] - cs[:-long]) / long
    aligned = sta[long - short:long - short + len(lta)]
    stalta = float(np.max(aligned / (lta + 1e-12))) if len(lta) else 0.0
    return np.array([
        np.log(rms), np.log(float(abs_values.max()) + 1e-12),
        np.log(float(np.mean(np.abs(np.diff(values)))) + 1e-12),
        float(np.mean(np.signbit(values[1:]) != np.signbit(values[:-1]))), stalta,
    ])


def best_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    choices = np.unique(scores)
    best = (-1.0, float(choices[0]))
    for threshold in choices:
        predicted = scores >= threshold
        tp = np.sum(predicted & (labels == 1)); fp = np.sum(predicted & (labels == 0)); fn = np.sum(~predicted & (labels == 1))
        f1 = 2 * tp / max(1, 2 * tp + fp + fn)
        if f1 > best[0]: best = (float(f1), float(threshold))
    return best[1]


def metrics(scores: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, float | int]:
    predicted = scores >= threshold
    tp = int(np.sum(predicted & (labels == 1))); fp = int(np.sum(predicted & (labels == 0)))
    fn = int(np.sum(~predicted & (labels == 1))); tn = int(np.sum(~predicted & (labels == 0)))
    precision = tp / max(1, tp + fp); recall = tp / max(1, tp + fn)
    return {"threshold": threshold, "tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall, "f1": 2 * precision * recall / max(1e-12, precision + recall), "false_positives_per_hour": fp / max(1e-12, (fp + tn) * 600 / 3600)}


def logistic_fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    def objective(w):
        z = np.clip(x @ w, -30, 30)
        return float(np.mean(np.logaddexp(0, z) - y * z) + 1e-3 * np.sum(w[1:] ** 2))
    return minimize(objective, np.zeros(x.shape[1]), method="L-BFGS-B").x


def main() -> None:
    positives = list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")))
    backgrounds = [r for r in csv.DictReader(Path("data/manifests/background_window_candidates.csv").open(newline="")) if r["channel"] in {"MHZ", "MH1", "MH2"}]
    report = {"status": "pilot_only_not_paper_result", "background_bias_warning": "available days were selected for positive coverage; continuous-scanning evaluation remains required", "folds": {}}
    for fold in sorted({r["fold"] for r in positives}):
        datasets = {}
        for role in ("train", "validation", "test"):
            pos = [r for r in positives if r["fold"] == fold and r["role"] == role]
            neg = [r for r in backgrounds if r["fold"] == fold and r["role"] == role]
            neg.sort(key=lambda r: hashlib.sha256(("baseline-v0.1|" + r["station"] + r["channel"] + r["start_time"]).encode()).hexdigest())
            neg = neg[:len(pos)]
            vectors=[]; labels=[]
            for row in pos:
                value=features(row["station"], row["channel"], datetime.fromisoformat(row["window_start_nominal"]))
                if value is not None: vectors.append(value); labels.append(1)
            for row in neg:
                value=features(row["station"], row["channel"], datetime.fromisoformat(row["start_time"]))
                if value is not None: vectors.append(value); labels.append(0)
            datasets[role]=(np.asarray(vectors),np.asarray(labels))
        train_x, train_y=datasets["train"]; val_x,val_y=datasets["validation"]; test_x,test_y=datasets["test"]
        fold_report={"counts": {role:{"event":int(np.sum(y==1)),"background":int(np.sum(y==0))} for role,(_,y) in datasets.items()}}
        for name,index in (("energy_rms",0),("sta_lta",4)):
            threshold=best_threshold(val_x[:,index],val_y)
            fold_report[name]=metrics(test_x[:,index],test_y,threshold)
        mean=train_x.mean(axis=0); std=train_x.std(axis=0); std[std==0]=1
        tx=np.column_stack([np.ones(len(train_x)),(train_x-mean)/std]); vx=np.column_stack([np.ones(len(val_x)),(val_x-mean)/std]); qx=np.column_stack([np.ones(len(test_x)),(test_x-mean)/std])
        weights=logistic_fit(tx,train_y); val_scores=1/(1+np.exp(-np.clip(vx@weights,-30,30))); test_scores=1/(1+np.exp(-np.clip(qx@weights,-30,30)))
        threshold=best_threshold(val_scores,val_y); fold_report["logistic_handcrafted"]=metrics(test_scores,test_y,threshold)
        report["folds"][fold]=fold_report
        print(f"completed {fold}", flush=True)
    path=Path("results/predictions/pilot_baselines_v0.1.json"); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,indent=2)+"\n")
    names=("energy_rms","sta_lta","logistic_handcrafted"); folds=list(report["folds"])
    fig,axes=plt.subplots(1,2,figsize=(11,4.2)); x=np.arange(len(folds)); width=0.25
    for index,name in enumerate(names):
        axes[0].bar(x+(index-1)*width,[report["folds"][fold][name]["f1"] for fold in folds],width,label=name)
        axes[1].bar(x+(index-1)*width,[report["folds"][fold][name]["false_positives_per_hour"] for fold in folds],width,label=name)
    for axis,title,ylabel in ((axes[0],"Held-out-station F1","F1"),(axes[1],"Catalog-negative false alarms","False positives/hour")):
        axis.set_xticks(x,folds,rotation=20); axis.set_title(title); axis.set_ylabel(ylabel); axis.spines[["top","right"]].set_visible(False)
    axes[0].legend(frameon=False,fontsize=8); fig.suptitle("LunaSeis-1 pilot baselines v0.1 (biased background frame; not paper results)"); fig.tight_layout()
    figure=Path("results/figures/pilot_baselines_v0.1.png"); figure.parent.mkdir(parents=True,exist_ok=True); fig.savefig(figure,dpi=180); plt.close(fig)
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
