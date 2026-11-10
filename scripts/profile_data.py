"""Read-only raw-data audit, using Python standard library only."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / "data" / "raw" / "events.csv"
    if not source.exists():
        raise SystemExit("Run scripts/download_data.py first, or manually place original events.csv in data/raw/.")
    events, missing = Counter(), Counter()
    visitors, items, transactions = set(), set(), set()
    lo, hi, rows, invalid, purchase_missing_transaction = None, None, 0, 0, 0
    with source.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            for key, value in row.items():
                if not value:
                    missing[key] += 1
            try:
                ts = int(row["timestamp"])
                uid, iid = int(row["visitorid"]), int(row["itemid"])
                event = row["event"]
                if event not in {"view", "addtocart", "transaction"}:
                    raise ValueError("unknown event")
            except (ValueError, TypeError, KeyError):
                invalid += 1
                continue
            events[event] += 1
            visitors.add(uid)
            items.add(iid)
            if row["transactionid"]:
                transactions.add(row["transactionid"])
            elif event == "transaction":
                purchase_missing_transaction += 1
            lo = ts if lo is None else min(lo, ts)
            hi = ts if hi is None else max(hi, ts)
    result = {
        "raw_rows": rows,
        "event_counts": dict(events),
        "unique_visitors": len(visitors),
        "unique_items": len(items),
        "distinct_nonempty_transaction_ids": len(transactions),
        "min_timestamp_ms": lo,
        "max_timestamp_ms": hi,
        "min_time_utc": datetime.fromtimestamp(lo / 1000, timezone.utc).isoformat() if lo is not None else None,
        "max_time_utc": datetime.fromtimestamp(hi / 1000, timezone.utc).isoformat() if hi is not None else None,
        "missing_by_column": dict(missing),
        "invalid_required_fields_or_event": invalid,
        "purchase_rows_missing_transaction_id": purchase_missing_transaction,
        "checks": {
            "event_counts_reconcile": sum(events.values()) + invalid == rows,
            "matches_original_v2_raw_count": rows == 2_756_101,
            "matches_original_v2_event_counts": events == Counter(view=2_664_312, addtocart=69_332, transaction=22_457),
        },
        "limits": [
            "This profile is before deduplication; duplicate sensitivity is a later project task.",
            "NULL transactionid on view/addtocart is valid, not a reason to delete events.",
            "Transaction rows are item-level events; distinct transaction IDs are a different metric.",
            "First seen in this log does not establish the visitor's registration date.",
        ],
    }
    output = ROOT / "reports" / "raw_profile.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if invalid or not all(result["checks"].values()):
        raise SystemExit("Data audit needs investigation; inspect reports/raw_profile.json.")


if __name__ == "__main__":
    main()
