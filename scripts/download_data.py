"""Download the original RetailRocket v2 event file; never execute remote code."""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.kaggle.com/api/v1/datasets/download/retailrocket/ecommerce-dataset/events.csv?datasetVersionNumber=2"
SOURCE = "https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset"
HEADER = ["timestamp", "visitorid", "event", "itemid", "transactionid"]


def main():
    raw = ROOT / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    target = raw / "events.csv"
    if not target.exists():
        archive = raw / "events_v2.zip.part"
        request = urllib.request.Request(URL, headers={"User-Agent": "RetailRocket-Local-Study/1.0"})
        print("Downloading the original event data...", flush=True)
        with urllib.request.urlopen(request, timeout=90) as response, archive.open("wb") as f:
            shutil.copyfileobj(response, f)
        if not zipfile.is_zipfile(archive):
            raise ValueError("Download was not a ZIP. Use the source page to download events.csv manually.")
        # Extract only this explicit member; do not extract arbitrary archive paths.
        with zipfile.ZipFile(archive) as z:
            member = z.getinfo("events.csv")
            if member.file_size > 200_000_000:
                raise ValueError("Unexpected event file size; inspect the upstream dataset before proceeding.")
            temporary = raw / "events.csv.part"
            with z.open(member) as src, temporary.open("wb") as dst:
                shutil.copyfileobj(src, dst)
        with temporary.open(newline="", encoding="utf-8-sig") as f:
            if next(csv.reader(f)) != HEADER:
                raise ValueError("Unexpected CSV schema; original file has not been replaced.")
        temporary.replace(target)
        # Keep the downloaded archive as provenance; ignored by Git.
        archive.replace(raw / "events_v2.zip")
    with target.open(newline="", encoding="utf-8-sig") as f:
        if next(csv.reader(f)) != HEADER:
            raise ValueError("Existing events.csv has an unexpected header.")
    with target.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    manifest_path = ROOT / "reports" / "source_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dataset": "Retailrocket recommender system dataset",
        "publisher": "Retailrocket / Roman Zykov (Kaggle listing)",
        "dataset_version": 2,
        "source_page": SOURCE,
        "download_endpoint": URL,
        "license": "CC BY-NC-SA 4.0 (original dataset listing)",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "file": "data/raw/events.csv",
        "bytes": target.stat().st_size,
        "sha256": digest,
        "schema": HEADER,
        "transformation": "Original events.csv extracted unchanged from official version-2 download",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
