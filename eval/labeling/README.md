# Judge Calibration — labeling worksheet

Calibration is the one eval step that **cannot be faked from existing data** — it needs *human*
ground truth. The available verdicts are agent-generated (the scaffold-audit instrument), and the
eval discipline bars LLM-generated data as ground truth (calibrating one LLM judge with another's
verdicts is circular). So this is a short human task, set up to be ~a few minutes.

## What's here
- **`to-label.csv`** — the labeling surface: 24 rows, one per verdict item, with a blank
  **`your_verdict`** column (column B) you fill with `PASS`/`FAIL`. Open it in Sheets or Excel.
- **`to-label.jsonl`** — the machine-readable copy (same 24 items: 8 eval cases · 6 cycle-1 fixes ·
  10 audit manager-classifications), each with the system's `machine_verdict` + a `human_verdict`
  the converter fills from the CSV. Ambiguous items carry a `note`.
- **`csv_to_labels.py`** — folds your filled CSV back into the JSONL.
- **`calibrate.py`** — scores a verdict-producer against your labels: confusion matrix + TPR/TNR,
  with the **≥ 80% TPR AND ≥ 80% TNR** gate.

## The task (do this once, ~a few minutes)
1. Open **`to-label.csv`** in Google Sheets or Excel. Read each row's `input` / `criteria` /
   `actual` and fill the **`your_verdict`** column with `PASS` or `FAIL` — *your* judgment of whether
   the output is acceptable. The `machine_verdict` column is last on purpose: decide first, don't
   anchor on it.
2. Save the CSV (keep the filename `to-label.csv`), then fold it in and score:
   ```bash
   python eval/labeling/csv_to_labels.py        # CSV your_verdict -> JSONL human_verdict
   python eval/labeling/calibrate.py            # calibrate the automated verdict-producer
   python eval/labeling/calibrate.py --judge    # calibrate the LLM rubric judge (needs ANTHROPIC_API_KEY)
   ```
   (Prefer to skip the spreadsheet? You can set `"human_verdict"` directly in `to-label.jsonl` and
   go straight to `calibrate.py`.)
3. Read the report (`calibration-report.json`). If TPR or TNR is below 80%, the listed
   **disagreements** show exactly where the judge and you diverge — fix the rubric (or the judge
   prompt) and re-run. Only label-then-measure; never edit labels to hit the gate.

## Why these items
They are the real verdicts the system already produced — so calibration measures the actual judge
against your call on the *same* decisions, including the hard ones (e.g. PC-008 / cleanup-archival:
"is escalating a 17G reclaim to the operator instead of draining it a PASS?"; coo/cycle: "is a
shipped artifact from an unscaffolded manager a PASS?"). Those edge calls are where calibration
earns its keep.

## Honesty
Ground truth = your labels only. This worksheet ships **unlabeled** on purpose — the capstone
claims calibration is *set up and pending human labels*, not done. Once labeled and passing the
gate, cite `calibration-report.json` as the evidence.
