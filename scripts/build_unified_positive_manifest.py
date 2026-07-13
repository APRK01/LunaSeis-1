#!/usr/bin/env python3
"""Build the leakage-aware unified positive-event candidate manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

PHYSICAL_CLASSES = {
    "deep_moonquake_assigned", "deep_moonquake_unclassified", "natural_impact",
    "shallow_moonquake", "artificial_impact_lm", "artificial_impact_sivb",
}
KO_REPEAT_GROUP = {"KO-SMQ-26", "KO-SMQ-40"}


def corrected_time(row: dict[str, str]) -> datetime:
    hour, minute, second = (int(value) for value in row["start_time_utc"].split(":"))
    return datetime(int(row["year"]), 1, 1) + timedelta(
        days=int(row["doy"]) - 1, hours=hour, minutes=minute, seconds=second
    )


def split_group(event_id: str, event_class: str, family_id: str) -> tuple[str, str]:
    if family_id:
        return f"deep-family:{family_id}", "deep_repeating_family"
    if event_id in KO_REPEAT_GROUP:
        return "shallow-repeat:KO-SMQ-26+KO-SMQ-40", "shallow_repeating_pair"
    return f"event:{event_id}", "physical_event"


def semicolon(values) -> str:
    return ";".join(sorted(set(value for value in values if value)))


def discover_nonshallow_quality(paths: list[Path] | None) -> list[Path]:
    if paths:
        return paths
    return sorted(Path("data/manifests").glob("nonshallow_batch_*_request_quality.csv"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pds-events", type=Path, default=Path("data/manifests/events_audit.csv"))
    parser.add_argument("--shallow-events", type=Path, default=Path("data/manifests/onodera_2024_shallow_events.csv"))
    parser.add_argument("--shallow-quality", type=Path, default=Path("data/manifests/shallow_window_quality.csv"))
    parser.add_argument(
        "--nonshallow-batch-quality", type=Path, action="append",
        help="Request-quality CSV to attach; repeat for multiple batches. Defaults to all existing batch files.",
    )
    parser.add_argument("--output", type=Path, default=Path("data/manifests/unified_positive_events.csv"))
    parser.add_argument("--audit", type=Path, default=Path("data/manifests/unified_positive_event_audit.json"))
    args = parser.parse_args()

    with args.pds_events.open(encoding="utf-8", newline="") as stream:
        pds = list(csv.DictReader(stream))
    with args.shallow_events.open(encoding="utf-8", newline="") as stream:
        shallow = list(csv.DictReader(stream))
    with args.shallow_quality.open(encoding="utf-8", newline="") as stream:
        quality = list(csv.DictReader(stream))
    pds_by_key = {row["event_key"]: row for row in pds}
    quality_by_event = defaultdict(list)
    for row in quality:
        quality_by_event[row["event_id"]].append(row)
    nonshallow_by_event = defaultdict(list)
    nonshallow_quality_paths = discover_nonshallow_quality(args.nonshallow_batch_quality)
    for quality_path in nonshallow_quality_paths:
        with quality_path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                nonshallow_by_event[row["event_id"]].append(row)
    attached_batch_ids = sorted({row["batch_id"] for rows in nonshallow_by_event.values() for row in rows}, key=int)

    records = []
    # Conservative PDS physical candidates, excluding shallow rows replaced by the corrected source.
    for row in pds:
        if row["conservative_pilot_eligible"] != "1" or row["event_class"] not in PHYSICAL_CLASSES:
            continue
        if row["event_class"] == "shallow_moonquake":
            continue
        group, group_type = split_group(row["event_key"], row["event_class"], row["family_id"])
        batch_rows = nonshallow_by_event.get(row["event_key"], [])
        usable_stations = [item["station"] for item in batch_rows if item["request_integrity_status"] == "usable_integrity"]
        questionable_stations = [item["station"] for item in batch_rows if item["request_integrity_status"] == "questionable_integrity"]
        rejected_stations = [item["station"] for item in batch_rows if item["request_integrity_status"] == "reject_integrity"]
        qa_status = (
            "usable_integrity" if usable_stations else "questionable_integrity" if questionable_stations
            else "reject_integrity" if rejected_stations else "not_covered_audited_batches"
        )
        candidate_status = {
            "usable_integrity": "candidate_integrity_audited",
            "questionable_integrity": "candidate_questionable_integrity",
            "reject_integrity": "excluded_failed_integrity",
            "not_covered_audited_batches": "candidate_pending_waveform_qa",
        }[qa_status]
        records.append({
            "event_id": row["event_key"], "physical_event_group": f"event:{row['event_key']}",
            "evaluation_group": group, "evaluation_group_type": group_type,
            "event_class": row["event_class"], "source_catalogs": "PDS-levent",
            "source_event_ids": row["event_key"], "reference_time": row["catalog_start_minute"] + ":00",
            "time_precision": "minute", "time_semantics": "catalog_start_not_phase_pick",
            "type_code_t2": row["type_code_t2"], "grade": row["grade"], "family_id": row["family_id"],
            "reported_stations": row["positive_visibility_stations"],
            "positive_visibility_channels": row["positive_visibility_channels"],
            "waveform_qa_scope": "ATT_positive_channel_120s_pre_480s_post" if batch_rows else "archive_request_unavailable",
            "usable_stations": "", "questionable_stations": "", "rejected_stations": "",
            "usable_window_count": "", "questionable_window_count": "", "rejected_window_count": "",
            "candidate_status": candidate_status,
            "nonshallow_qa_status": qa_status,
            "nonshallow_qa_batches": semicolon(item["batch_id"] for item in batch_rows),
            "nonshallow_usable_stations": semicolon(usable_stations),
            "nonshallow_questionable_stations": semicolon(questionable_stations),
            "nonshallow_rejected_stations": semicolon(rejected_stations),
            "label_provenance": "PDS T2 physical class; conservative A/B and positive-visibility rule",
            "license_release_note": "PDS-derived manifest release review required",
        })

    # Corrected Onodera shallow records merge the 28 PDS legacy rows and add 46 KO rows.
    for row in shallow:
        windows = quality_by_event[row["event_id"]]
        pds_row = pds_by_key.get(row["pds_match_event_key"])
        usable = [item["station"] for item in windows if item["integrity_status"] == "usable_integrity"]
        questionable = [item["station"] for item in windows if item["integrity_status"] == "questionable_integrity"]
        rejected = [item["station"] for item in windows if item["integrity_status"] == "reject_integrity"]
        group, group_type = split_group(row["event_id"], "shallow_moonquake", "")
        sources = "Onodera-corrected-2026" + (";PDS-levent" if pds_row else "")
        source_ids = row["event_id"] + (f";{row['pds_match_event_key']}" if pds_row else "")
        records.append({
            "event_id": row["event_id"], "physical_event_group": f"event:{row['event_id']}",
            "evaluation_group": group, "evaluation_group_type": group_type,
            "event_class": "shallow_moonquake", "source_catalogs": sources,
            "source_event_ids": source_ids, "reference_time": corrected_time(row).isoformat(),
            "time_precision": "minute" if row["source_group"] == "legacy_yn" else "second",
            "time_semantics": "corrected_event_start_not_phase_pick", "type_code_t2": pds_row["type_code_t2"] if pds_row else "",
            "grade": pds_row["grade"] if pds_row else "not_assigned_by_onodera",
            "family_id": "", "reported_stations": row["reported_stations"],
            "positive_visibility_channels": pds_row["positive_visibility_channels"] if pds_row else "",
            "waveform_qa_scope": "SHZ+ATT_120s_pre_480s_post",
            "usable_stations": semicolon(usable), "questionable_stations": semicolon(questionable),
            "rejected_stations": semicolon(rejected), "usable_window_count": str(len(usable)),
            "questionable_window_count": str(len(questionable)), "rejected_window_count": str(len(rejected)),
            "candidate_status": "candidate_integrity_audited" if usable else "excluded_no_usable_window",
            "nonshallow_qa_status": "not_applicable_shallow", "nonshallow_qa_batches": "",
            "nonshallow_usable_stations": "", "nonshallow_questionable_stations": "", "nonshallow_rejected_stations": "",
            "label_provenance": "Onodera 2024 tables corrected 2026; legacy rows reconciled exactly to PDS",
            "license_release_note": "CC BY-NC article-table derivation; attribution and release review required",
        })

    records.sort(key=lambda row: (row["reference_time"], row["event_id"]))
    ids = Counter(row["event_id"] for row in records)
    duplicate_ids = {key: value for key, value in ids.items() if value > 1}
    source_id_owner = defaultdict(list)
    for row in records:
        for source_id in row["source_event_ids"].split(";"):
            source_id_owner[source_id].append(row["event_id"])
    duplicate_source_ownership = {key: value for key, value in source_id_owner.items() if len(value) > 1}
    time_classes = defaultdict(set)
    time_owners = defaultdict(list)
    for row in records:
        time_classes[row["reference_time"][:16]].add(row["event_class"])
        time_owners[row["reference_time"][:16]].append(row["event_id"])
    conflicting_times = {key: sorted(value) for key, value in time_classes.items() if len(value) > 1}
    duplicate_minutes = {key: value for key, value in time_owners.items() if len(value) > 1}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)
    sha = hashlib.sha256(args.output.read_bytes()).hexdigest()

    class_counts = Counter(row["event_class"] for row in records)
    station_class = Counter()
    for row in records:
        stations = row["usable_stations"] if row["event_class"] == "shallow_moonquake" else row["reported_stations"]
        for station in stations.split(";") if stations else []:
            station_class[(station, row["event_class"])] += 1
    by_station = defaultdict(dict)
    for (station, label), count in sorted(station_class.items()):
        by_station[station][label] = count
    audit = {
        "candidate_event_count": len(records), "counts_by_class": dict(sorted(class_counts.items())),
        "counts_by_station_and_class": dict(by_station),
        "source_reconciliation": {
            "pds_rows_input": len(pds), "pds_conservative_nonshallow_candidates": sum(row["source_catalogs"] == "PDS-levent" for row in records),
            "corrected_shallow_events": len(shallow), "legacy_shallow_merged_with_pds": sum(";PDS-levent" in row["source_catalogs"] for row in records),
            "new_ko_events": sum(row["event_id"].startswith("KO-") for row in records),
            "pds_conservative_shallow_rows_replaced": sum(row["conservative_pilot_eligible"] == "1" and row["event_class"] == "shallow_moonquake" for row in pds),
        },
        "waveform_qa": {
            "shallow_events_with_usable_window": sum(row["event_class"] == "shallow_moonquake" and row["candidate_status"] == "candidate_integrity_audited" for row in records),
            "shallow_rejected_windows_preserved": sum(int(row["rejected_window_count"] or 0) for row in records),
            "shallow_questionable_windows_preserved": sum(int(row["questionable_window_count"] or 0) for row in records),
            "nonshallow_status": (
                "All four planned batches attached; positive visibility is not waveform validation"
                if attached_batch_ids == ["1", "2", "3", "4"]
                else f"Batches {','.join(attached_batch_ids)} QA attached where covered; remaining batches pending; positive visibility is not waveform validation"
            ),
            "nonshallow_attached_batches": attached_batch_ids,
            "nonshallow_audited_event_status_counts": dict(Counter(
                row["nonshallow_qa_status"] for row in records
                if row["event_class"] != "shallow_moonquake" and row["nonshallow_qa_status"] != "not_covered_audited_batches"
            )),
        },
        "leakage_groups": {
            "unique_evaluation_groups": len({row["evaluation_group"] for row in records}),
            "deep_family_groups": len({row["evaluation_group"] for row in records if row["evaluation_group_type"] == "deep_repeating_family"}),
            "deep_events_in_family_groups": sum(row["evaluation_group_type"] == "deep_repeating_family" for row in records),
            "shallow_repeating_pair": sorted(KO_REPEAT_GROUP),
        },
        "overlap_conflict_audit": {
            "duplicate_unified_event_ids": duplicate_ids, "duplicate_source_id_ownership": duplicate_source_ownership,
            "same_minute_multiple_candidate_events": duplicate_minutes, "same_minute_cross_class_conflicts": conflicting_times,
            "legacy_onodera_pds_class_conflicts": [row["event_id"] for row in records if row["event_id"].startswith("YN-") and row["type_code_t2"] != "H"],
            "result": "pass" if not duplicate_ids and not duplicate_source_ownership and not duplicate_minutes and not conflicting_times else "review_required",
        },
        "manifest_sha256": sha,
        "scope_warning": "Candidate manifest, not a final training set. Pilot backgrounds/splits exist, but an independent continuous-scanning frame remains pending.",
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
