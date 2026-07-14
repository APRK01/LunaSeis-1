#!/usr/bin/env python3
"""Audit selected contiguous days after selection, without reading model scores."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def calendar_time(year: int, doy: int, clock: str) -> datetime:
    hour,minute,second=map(int,clock.split(":"))
    return datetime(year,1,1)+timedelta(days=doy-1,hours=hour,minutes=minute,seconds=second)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days",type=Path,default=Path("data/manifests/contiguous_evaluation_station_days.csv"))
    parser.add_argument("--catalog-output",type=Path,default=Path("data/manifests/contiguous_evaluation_catalog_audit.csv"))
    parser.add_argument("--summary-output",type=Path,default=Path("results/predictions/contiguous_evaluation_plan_audit.json"))
    args=parser.parse_args()
    days=list(csv.DictReader(args.days.open(newline="")))
    selected={(row["station"],datetime(int(row["year"]),1,1).date()+timedelta(days=int(row["doy"])-1)):row["block_id"] for row in days}
    unified=list(csv.DictReader(Path("data/manifests/unified_positive_events.csv").open(newline="")))
    candidates_by_minute=defaultdict(list)
    for row in unified:candidates_by_minute[datetime.fromisoformat(row["reference_time"]).replace(second=0)].append(row)
    roles=defaultdict(set)
    for row in csv.DictReader(Path("data/manifests/positive_split_assignments.csv").open(newline="")):
        roles[(row["fold"],row["evaluation_group"])].add(row["role"])
    catalog=[]
    for row in csv.DictReader(Path("data/manifests/events_audit.csv").open(newline="")):
        catalog.append((row["event_key"],datetime.fromisoformat(row["catalog_start_minute"]+":00"),"PDS-levent"))
    for row in csv.DictReader(Path("data/manifests/onodera_2024_shallow_events.csv").open(newline="")):
        if row["source_group"]=="new_ko":catalog.append((row["event_id"],calendar_time(int(row["year"]),int(row["doy"]),row["start_time_utc"]),"Onodera-corrected-new"))
    output=[]
    for source_id,reference,source in catalog:
        for station in ("S12","S14","S15","S16"):
            block=selected.get((station,reference.date()))
            if not block:continue
            matches=candidates_by_minute.get(reference.replace(second=0),[])
            candidate=next((row for row in matches if source_id in row["source_event_ids"].split(";")),matches[0] if len(matches)==1 else None)
            fold=f"holdout_{station}";group=candidate["evaluation_group"] if candidate else ""
            fold_roles=roles.get((fold,group),set()) if group else set()
            exposed=bool(fold_roles)
            output.append({"station":station,"block_id":block,"catalog_source":source,"source_event_id":source_id,"reference_time":reference.isoformat(),"unified_candidate_id":candidate["event_id"] if candidate else "","event_class":candidate["event_class"] if candidate else "","evaluation_group":group,"existing_fold_roles":";".join(sorted(fold_roles)),"prior_pilot_fold_exposed":int(exposed),"prospective_event_recall_eligibility":"eligible_pending_waveform_QA" if candidate and not exposed else "exclude_prior_pilot_exposed" if exposed else "catalog_exclusion_only"})
    path=args.catalog_output
    with path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(output[0]),lineterminator="\n");writer.writeheader();writer.writerows(output)
    eligibility=Counter(row["prospective_event_recall_eligibility"] for row in output)
    summary={"status":"post_selection_audit_no_model_scores_read","selected_station_days":len(days),"prior_station_day_overlaps":sum(int(row["prior_station_day_overlap"]) for row in days),"catalog_references_in_selected_station_days":len(output),"unique_catalog_references":len({(row["catalog_source"],row["source_event_id"]) for row in output}),"catalog_references_by_station":dict(Counter(row["station"] for row in output)),"eligibility_counts":dict(eligibility),"eligible_candidate_ids":sorted({row["unified_candidate_id"] for row in output if row["prospective_event_recall_eligibility"]=="eligible_pending_waveform_QA"}),"catalog_audit_csv_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"rules":["Every catalog reference is excluded from false-positive accounting within the frozen matching sensitivity windows.","Any group previously exposed in train, validation, or inspected pilot test outputs cannot contribute to untouched event-recall claims.","Unexposed candidates remain only prospectively eligible until downloaded waveform integrity and station visibility are audited.","Selection is not changed after this catalog audit."]}
    args.summary_output.write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
