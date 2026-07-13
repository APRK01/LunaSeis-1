#!/usr/bin/env python3
"""Resumably download and verify one batch of the nonshallow waveform plan."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from scripts.download_shallow_plan import verify_one
except ModuleNotFoundError:  # pragma: no cover
    from download_shallow_plan import verify_one


def select_batch(plan: dict, batch_id: int) -> list[dict]:
    products = [item for item in plan["products"] if int(item["batch_id"]) == batch_id]
    expected = next((item for item in plan["batch_summaries"] if int(item["batch_id"]) == batch_id), None)
    if expected is None or len(products) != int(expected["product_count"]):
        raise RuntimeError(f"Batch {batch_id} does not reconcile with its summary")
    if sum(int(item["bytes"]) for item in products) != int(expected["bytes"]):
        raise RuntimeError(f"Batch {batch_id} byte total does not reconcile")
    return products


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-id", type=int, required=True)
    parser.add_argument("--plan", type=Path, default=Path("data/manifests/nonshallow_download_plan.json"))
    parser.add_argument("--destination", type=Path, default=Path("data/raw/apollo_pse_v1.0"))
    parser.add_argument("--receipt-dir", type=Path, default=Path("data/manifests"))
    parser.add_argument("--receipt-prefix", default="nonshallow_batch")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    products = select_batch(plan, args.batch_id)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(verify_one, item, args.destination): item for item in products}
        for number, future in enumerate(as_completed(futures), start=1):
            path, size, reused = future.result()
            results.append((path, size, reused))
            print(f"[{number}/{len(products)}] {'reused' if reused else 'downloaded'} {path} ({size:,} bytes)", flush=True)
    receipt = {
        "source_plan": str(args.plan), "batch_id": args.batch_id,
        "verified_product_count": len(results), "verified_total_bytes": sum(item[1] for item in results),
        "downloaded_product_count_this_run": sum(not item[2] for item in results),
        "reused_product_count_this_run": sum(item[2] for item in results),
        "integrity": "exact size and MD5 verified for every batch product",
    }
    args.receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = args.receipt_dir / f"{args.receipt_prefix}_{args.batch_id}_download_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
