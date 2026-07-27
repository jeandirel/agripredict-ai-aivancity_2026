#!/usr/bin/env python3
"""Download public Kaggle datasets declared in configs/data/datasets.json.

The script does not commit downloaded data. It records download/extraction status,
checksums and file sizes in data/manifests/datasets_download_status.json.
Optional KAGGLE_USERNAME/KAGGLE_KEY environment variables are supported.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DownloadResult:
    dataset_id: str
    slug: str
    status: str
    source_url: str
    api_url: str
    output_dir: str
    archive_path: str | None = None
    archive_sha256: str | None = None
    archive_size_bytes: int | None = None
    extracted_files: int = 0
    extracted_size_bytes: int = 0
    error: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def request_headers() -> dict[str, str]:
    headers = {"User-Agent": "AgriPredictAI/1.0 (+aivancity-clinique-ia)"}
    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")
    if username and key:
        token = base64.b64encode(f"{username}:{key}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    return headers


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    destination = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if destination not in target.parents and target != destination:
            raise ValueError(f"Unsafe ZIP entry: {member.filename}")
    archive.extractall(destination)


def download_one(dataset: dict[str, Any], output_root: Path, retries: int) -> DownloadResult:
    dataset_id = dataset["id"]
    slug = dataset["slug"]
    target_dir = output_root / dataset["layer"] / dataset_id
    archive_dir = output_root / "_archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{dataset_id}.zip"
    api_url = f"https://www.kaggle.com/api/v1/datasets/download/{slug}"

    result = DownloadResult(
        dataset_id=dataset_id,
        slug=slug,
        status="started",
        source_url=dataset["url"],
        api_url=api_url,
        output_dir=str(target_dir),
        archive_path=str(archive_path),
        started_at=utc_now(),
    )

    request = urllib.request.Request(api_url, headers=request_headers())
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=180) as response, archive_path.open("wb") as out:
                shutil.copyfileobj(response, out)
            last_error = None
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 20))

    if last_error is not None:
        result.status = "failed"
        result.error = f"{type(last_error).__name__}: {last_error}"
        result.finished_at = utc_now()
        return result

    try:
        result.archive_size_bytes = archive_path.stat().st_size
        result.archive_sha256 = sha256_file(archive_path)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            safe_extract(archive, target_dir)
        files = [p for p in target_dir.rglob("*") if p.is_file()]
        result.extracted_files = len(files)
        result.extracted_size_bytes = sum(p.stat().st_size for p in files)
        result.status = "downloaded"
    except Exception as exc:  # noqa: BLE001
        result.status = "failed"
        result.error = f"{type(exc).__name__}: {exc}"
    result.finished_at = utc_now()
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="configs/data/datasets.json")
    parser.add_argument("--output", default="data/external")
    parser.add_argument("--status", default="data/manifests/datasets_download_status.json")
    parser.add_argument("--ids", nargs="*", help="Download only selected dataset IDs")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--keep-archives", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_root = Path(args.output)
    status_path = Path(args.status)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    datasets = manifest["datasets"]
    if args.ids:
        wanted = set(args.ids)
        datasets = [item for item in datasets if item["id"] in wanted]
        missing = wanted - {item["id"] for item in datasets}
        if missing:
            raise SystemExit(f"Unknown dataset IDs: {sorted(missing)}")

    results: list[DownloadResult] = []
    for dataset in datasets:
        print(f"[download] {dataset['id']} <- {dataset['slug']}", flush=True)
        result = download_one(dataset, output_root, args.retries)
        results.append(result)
        print(f"[status] {dataset['id']}: {result.status}", flush=True)
        if result.status == "failed" and not args.continue_on_error:
            break

    if not args.keep_archives:
        shutil.rmtree(output_root / "_archives", ignore_errors=True)

    payload = {
        "generated_at": utc_now(),
        "manifest": str(manifest_path),
        "download_root": str(output_root),
        "authentication": "kaggle_credentials" if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY") else "public_api",
        "summary": {
            "requested": len(datasets),
            "downloaded": sum(r.status == "downloaded" for r in results),
            "failed": sum(r.status == "failed" for r in results),
        },
        "results": [asdict(result) for result in results],
    }
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Download status written to {status_path}")

    failed = payload["summary"]["failed"]
    if failed and not args.continue_on_error:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
