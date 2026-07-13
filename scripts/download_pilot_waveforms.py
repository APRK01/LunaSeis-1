#!/usr/bin/env python3
"""Download and verify the manifest-pinned LunaSeis-1 Phase 0 waveforms."""

from __future__ import annotations

import argparse
import json
import urllib.parse
from pathlib import Path, PurePosixPath

try:  # Support both `python scripts/...py` and package-style test imports.
    from scripts.download_catalog import fetch, md5sum
except ModuleNotFoundError:  # pragma: no cover - exercised by direct CLI execution
    from download_catalog import fetch, md5sum

DEFAULT_MANIFEST = Path("data/manifests/pilot_waveform_inventory.json")
DEFAULT_DESTINATION = Path("data/raw/apollo_pse_v1.0")


def validate_product(product: dict[str, object]) -> tuple[PurePosixPath, int, str]:
    """Validate an inventory record before it can influence a local path."""
    relative = PurePosixPath(str(product["path"]))
    expected_bytes = int(product["bytes"])
    expected_md5 = str(product["md5"]).lower()
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe product path: {relative}")
    if expected_bytes < 0:
        raise ValueError(f"Invalid byte count for {relative}: {expected_bytes}")
    if len(expected_md5) != 32 or any(c not in "0123456789abcdef" for c in expected_md5):
        raise ValueError(f"Invalid MD5 for {relative}: {expected_md5}")
    return relative, expected_bytes, expected_md5


def download_inventory(manifest_path: Path, destination: Path) -> tuple[int, int]:
    inventory = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_url = str(inventory["base_url"])
    products = inventory["products"]
    expected_total = int(inventory["planned_total_bytes"])
    verified_total = 0

    for product in products:
        relative, expected_bytes, expected_md5 = validate_product(product)
        target = destination.joinpath(*relative.parts)
        valid_existing = (
            target.exists()
            and target.stat().st_size == expected_bytes
            and md5sum(target) == expected_md5
        )
        if not valid_existing:
            fetch(urllib.parse.urljoin(base_url, relative.as_posix()), target)
        actual_bytes = target.stat().st_size
        actual_md5 = md5sum(target)
        if actual_bytes != expected_bytes or actual_md5 != expected_md5:
            raise RuntimeError(
                f"Integrity failure for {relative}: expected {expected_bytes} bytes/"
                f"{expected_md5}, got {actual_bytes} bytes/{actual_md5}"
            )
        verified_total += actual_bytes
        print(f"verified {relative} ({actual_bytes:,} bytes)")

    if verified_total != expected_total:
        raise RuntimeError(
            f"Inventory total mismatch: expected {expected_total}, verified {verified_total}"
        )
    return len(products), verified_total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    count, total = download_inventory(args.manifest, args.destination)
    print(f"verified {count} products totaling {total:,} bytes")


if __name__ == "__main__":
    main()
