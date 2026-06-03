# Judge Calibration — labeling worksheet

Calibration is the one eval step that **cannot be faked from existing data** — it needs *human*
ground truth. The available verdicts are agent-generated (the scaffold-audit instrument), and the
eval discipline bars LLM-generated data as ground truth (calibrating one LLM judge with another's
verdicts is circular). So this is a short human task, set up to be ~a few minutes.

## What's here
- **`to-label.jsonl`** — 24 real, sanitized verdict items (8 eval cases · 6 cycle-1 fixes ·
  10 audit manager-classifications), each with the system's `machine_verdict` and a blank
  `human_verdict`. Items the system found genuinely ambiguous carry a `note`.
- **`calibrate.py`** — scores a verdict-producer against your labels: confusion matrix + TPR/TNR,
  with the **≥ 80% TPR AND ≥ 80% TNR** gate.

## The task (do this once)
1. Open `to-label.jsonl`. For each row, read `input` / `criteria` / `actual` and set
   `"human_verdict"` to `"PASS"` or `"FAIL"` — *your* judgment of whether the output is acceptable.
   Ignore the `machine_verdict` while you decide (don't anchor on it).
2. Run the calibration:
   ```bash
   python eval/labeling/calibrate.py            # calibrate the automated verdict-producer
   python eval/labeling/calibrate.py --judge    # calibrate the LLM rubric judge (needs ANTHROPIC_API_KEY)
   ```
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
