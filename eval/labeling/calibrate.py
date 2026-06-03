#!/usr/bin/env python3
"""
Judge calibration — measure verdict-producer agreement against HUMAN labels.

Ground truth = the `human_verdict` you fill into ``to-label.jsonl`` (PASS/FAIL).
This script computes the confusion matrix and TPR/TNR of a verdict-producer
against those human labels, and applies the >= 80% gate.

Two modes:
  default   : calibrate the *automated* verdict already on each item
              (``machine_verdict`` — the deterministic scorer / audit instrument).
  --judge   : calibrate the *LLM rubric judge* (eval/judge/rubric.md) — it runs
              the judge on each labeled item and scores ITS verdicts vs human.
              Requires ANTHROPIC_API_KEY (falls back with a clear message).

A judge is calibration-ready only when BOTH TPR >= 0.80 AND TNR >= 0.80
(true-positive rate on human-PASS items, true-negative rate on human-FAIL items).

Usage:
    # 1) open to-label.jsonl, set "human_verdict" to "PASS" or "FAIL" on each row
    python eval/labeling/calibrate.py            # automated verdict vs your labels
    python eval/labeling/calibrate.py --judge    # LLM rubric judge vs your labels
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent
WORKSHEET = HERE / "to-label.jsonl"
sys.path.insert(0, str(EVAL))  # import judge_case from eval/run.py


def load_items() -> list[dict]:
    return [json.loads(l) for l in WORKSHEET.read_text().splitlines() if l.strip()]


def confusion(pairs: list[tuple[str, str]]) -> dict:
    """pairs = (human, predicted). PASS is the positive class."""
    tp = sum(1 for h, p in pairs if h == "PASS" and p == "PASS")
    fn = sum(1 for h, p in pairs if h == "PASS" and p == "FAIL")
    tn = sum(1 for h, p in pairs if h == "FAIL" and p == "FAIL")
    fp = sum(1 for h, p in pairs if h == "FAIL" and p == "PASS")
    tpr = tp / (tp + fn) if (tp + fn) else None
    tnr = tn / (tn + fp) if (tn + fp) else None
    acc = (tp + tn) / len(pairs) if pairs else None
    return {"tp": tp, "fn": fn, "tn": tn, "fp": fp, "tpr": tpr, "tnr": tnr,
            "accuracy": acc, "n": len(pairs)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Judge calibration vs human labels")
    ap.add_argument("--judge", action="store_true", help="calibrate the LLM rubric judge (needs API key)")
    ap.add_argument("--out", default=str(HERE / "calibration-report.json"))
    args = ap.parse_args()

    items = load_items()
    labeled = [it for it in items if it.get("human_verdict") in ("PASS", "FAIL")]
    if not labeled:
        print(f"  0 / {len(items)} items labeled.")
        print(f"  → Open {WORKSHEET} and set \"human_verdict\" to \"PASS\" or \"FAIL\" on each row,")
        print(f"     then re-run. (~24 items, a few minutes.)")
        return 0

    predicted_by = "machine_verdict"
    judge_unavailable = False
    if args.judge:
        try:
            from run import judge_case  # eval/run.py
        except Exception as e:
            print(f"  cannot import judge_case from eval/run.py: {e}")
            return 2
        rubric = (EVAL / "judge" / "rubric.md").read_text()
        for it in labeled:
            verdict = judge_case({"input": it["input"], "expected": it["criteria"]},
                                 {"observed": it["actual"]}, rubric)
            if verdict is None:
                judge_unavailable = True
                break
            it["_judge_verdict"] = verdict["verdict"]
        if judge_unavailable:
            print("  --judge requested but the LLM judge is unavailable "
                  "(no anthropic SDK or no ANTHROPIC_API_KEY). Showing automated-verdict calibration instead.\n")
        else:
            predicted_by = "_judge_verdict"

    pairs = [(it["human_verdict"], it[predicted_by]) for it in labeled]
    cm = confusion(pairs)
    gate = (cm["tpr"] is not None and cm["tpr"] >= 0.80 and
            cm["tnr"] is not None and cm["tnr"] >= 0.80)

    disagreements = [{"id": it["id"], "human": it["human_verdict"],
                      "predicted": it[predicted_by], "note": it.get("note", "")}
                     for it in labeled if it["human_verdict"] != it[predicted_by]]

    report = {"calibrated": gate, "predicted_by": predicted_by,
              "labeled": len(labeled), "total": len(items),
              "metrics": cm, "disagreements": disagreements}
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")

    print(f"  calibrating: {predicted_by}  ({len(labeled)}/{len(items)} labeled)")
    print(f"  confusion: TP={cm['tp']} FN={cm['fn']} TN={cm['tn']} FP={cm['fp']}")
    fmt = lambda v: "n/a" if v is None else f"{v:.0%}"
    print(f"  TPR={fmt(cm['tpr'])}  TNR={fmt(cm['tnr'])}  accuracy={fmt(cm['accuracy'])}")
    print(f"  gate (TPR>=80% AND TNR>=80%): {'PASS — calibration-ready' if gate else 'FAIL — not yet calibrated'}")
    if disagreements:
        print(f"  {len(disagreements)} disagreement(s): " +
              ", ".join(f"{d['id']}(you={d['human']},sys={d['predicted']})" for d in disagreements))
    print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
