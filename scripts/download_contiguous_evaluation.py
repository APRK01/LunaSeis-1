#!/usr/bin/env python3
"""Download and verify the frozen contiguous-evaluation product plan."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from scripts.download_shallow_plan import verify_one
except ModuleNotFoundError:  # pragma: no cover
    from download_shallow_plan import verify_one


def reconcile_plan(plan: dict) -> list[dict]:
    products=plan.get("products",[])
    if plan.get("status")!="planned_not_downloaded":raise ValueError("Expected a frozen, not-yet-downloaded plan")
    if len(products)!=int(plan["product_count"]):raise ValueError("Product count does not reconcile")
    if sum(int(row["bytes"]) for row in products)!=int(plan["total_bytes"]):raise ValueError("Byte total does not reconcile")
    if len({row["path"] for row in products})!=len(products):raise ValueError("Duplicate product path")
    return products


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,default=Path("data/manifests/contiguous_evaluation_download_plan.json"))
    parser.add_argument("--destination",type=Path,default=Path("data/raw/apollo_pse_v1.0"))
    parser.add_argument("--receipt",type=Path,default=Path("data/manifests/contiguous_evaluation_download_receipt.json"))
    parser.add_argument("--workers",type=int,default=4)
    args=parser.parse_args();plan=json.loads(args.plan.read_text());products=reconcile_plan(plan);results=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(verify_one,row,args.destination):row for row in products}
        for number,future in enumerate(as_completed(futures),1):
            path,size,reused=future.result();results.append((path,size,reused))
            print(f"[{number}/{len(products)}] {'reused' if reused else 'downloaded'} {path} ({size:,} bytes)",flush=True)
    receipt={"source_plan":str(args.plan),"verified_product_count":len(results),"verified_total_bytes":sum(row[1] for row in results),"downloaded_product_count_this_run":sum(not row[2] for row in results),"reused_product_count_this_run":sum(row[2] for row in results),"integrity":"exact size and official NASA PDS MD5 verified for every product"}
    if receipt["verified_product_count"]!=plan["product_count"] or receipt["verified_total_bytes"]!=plan["total_bytes"]:raise RuntimeError("Receipt does not reconcile with plan")
    args.receipt.write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps(receipt,indent=2))


if __name__=="__main__":main()
