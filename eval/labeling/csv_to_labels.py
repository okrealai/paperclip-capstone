#!/usr/bin/env python3
"""
Fold a filled `to-label.csv` back into `to-label.jsonl`.

Reads the `your_verdict` column from to-label.csv, normalizes it (PASS/FAIL),
and writes it into the matching row's `human_verdict` in to-label.jsonl. Rows
left blank stay UNLABELED (human_verdict = null). Then run calibrate.py.

Usage:
    python eval/labeling/csv_to_labels.py
    python eval/labeling/calibrate.py
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV, JSONL = HERE / "to-label.csv", HERE / "to-label.jsonl"

NORM = {"PASS": "PASS", "P": "PASS", "FAIL": "FAIL", "F": "FAIL"}


def main() -> int:
    labels = {}
    bad = []
    with open(CSV, newline="") as f:
        for row in csv.DictReader(f):
            raw = (row.get("your_verdict") or "").strip().upper()
            if not raw:
                continue
            if raw not in NORM:
                bad.append((row.get("id"), row.get("your_verdict")))
                continue
            labels[row["id"]] = NORM[raw]
    if bad:
        print(f"  WARNING — {len(bad)} row(s) have an unrecognized verdict (use PASS or FAIL): {bad}")

    items = [json.loads(l) for l in JSONL.read_text().splitlines() if l.strip()]
    n = 0
    for it in items:
        if it["id"] in labels:
            it["human_verdict"] = labels[it["id"]]
            n += 1
    JSONL.write_text("\n".join(json.dumps(it) for it in items) + "\n")
    print(f"  applied {n} label(s) into to-label.jsonl ({len(items)} items total).")
    print(f"  → next: python eval/labeling/calibrate.py [--judge]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
