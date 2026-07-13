#!/usr/bin/env python3
"""Audit pilot split/background/preprocessing manifests and hashes."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = {
        "positive_splits": Path("data/manifests/positive_split_assignments.csv"),
        "background_candidates": Path("data/manifests/background_window_candidates.csv"),
        "preprocessing_positives": Path("data/manifests/preprocessing_positive_windows.csv"),
    }
    positive = list(csv.DictReader(paths["positive_splits"].open(newline="")))
    background = list(csv.DictReader(paths["background_candidates"].open(newline="")))
    preprocessed = list(csv.DictReader(paths["preprocessing_positives"].open(newline="")))
    roles = defaultdict(set)
    for row in positive:
        roles[(row["fold"], row["evaluation_group"])].add(row["role"])
    conflicts = {"|".join(key): sorted(value) for key, value in roles.items() if len(value) > 1}
    report = {
        "positive_assignment_count": len(positive),
        "background_candidate_count": len(background),
        "preprocessing_positive_count": len(preprocessed),
        "positive_counts_by_fold_role": {"|".join(k): v for k, v in sorted(Counter((r["fold"], r["role"]) for r in positive).items())},
        "background_counts_by_fold_role": {"|".join(k): v for k, v in sorted(Counter((r["fold"], r["role"]) for r in background).items())},
        "evaluation_group_role_conflicts": conflicts,
        "result": "pass" if not conflicts else "fail",
        "manifest_sha256": {name: sha(path) for name, path in paths.items()},
        "warning": "Background candidates are pilot-only because source days were selected for positive coverage.",
    }
    output = Path("results/predictions/pilot_dataset_audit.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
