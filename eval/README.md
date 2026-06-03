# Eval Harness

Evaluation is treated as **infrastructure, not a one-shot script**. The harness exists so that each
audit→fix→re-audit cycle starts from named, reusable cases instead of from zero.

## Layout
- **`run.py`** — the runner/scorer. Loads the cases, scores each against its `expected` block
  (deterministic code checks first; optional `--judge` LLM pass for subjective cases), and writes
  `results/latest.json`. Stdlib-only by default — no secrets, runs offline.
- **`fixtures.json`** — illustrative *recorded* `actual` outputs keyed by `case_id`, so the runner is
  demonstrably functional without touching the live system.
- **`failure-modes.md`** — the 7 failure modes (with severity), grounded in the baseline audit.
- **`cases/PC-0NN.json`** — 10 cases mapping to those failure modes. Each declares `input`,
  `expected` behavior, and `actual` / `verdict` (scored by `run.py`). Cases cover routing,
  gated external writes (incl. a malformed-token negative case), dormancy, stale memory recall,
  concurrency dedup, and stale-handoff processing.
- **`judge/rubric.md`** — the 5-component LLM-judge prompt (Role / Accept rubric / Reject rubric /
  few-shot / output format).
- **`results/latest.json`** — last runner output. **`results/cycle-1.md`** — the before/after record
  for the first flywheel cycle (23% → 37%).

## Running it
```bash
python eval/run.py                              # score; unscored where no recorded output
python eval/run.py --fixtures eval/fixtures.json # score against recorded outputs
python eval/run.py --fixtures eval/fixtures.json --judge   # + LLM judge (needs ANTHROPIC_API_KEY)
```
With the shipped fixtures this currently yields **7 PASS / 1 FAIL / 2 UNSCORED** (pass rate 88% of
scored). PC-008 and PC-010 score from **real flywheel-cycle-1 outcomes** (a reclaim window closed with a
sha256 manifest; a stale handoff processed to an operator-confirmed closure). The one FAIL is PC-009 —
the documented stale-memory gap (the memory layer does not yet flag age), reported failing honestly. The
2 remaining UNSCORED (PC-004 Notion-refresh, PC-006 ambiguous-directive) have **no recorded run** — they
stay unscored rather than being faked.

## Provenance & status
The headline **23% → 37%** improvement was measured by the org's **scaffold-audit instrument** (the same
classifier described in the repo README), **not** by executing the JSON cases below. The `cases/PC-0NN.json`
files **define** the harness; they ship as **unscored templates** (`actual` / `verdict` = `null`), and
`run.py` scores them against recorded outputs (see `fixtures.json`). PC-008 / PC-010 now carry **real
recorded outcomes** from flywheel cycle 1, so the runner scores them PASS in agreement with
`results/cycle-1.md`. Cases with no recorded run (PC-004, PC-006) stay `UNSCORED` — that is the honest
state, not a gap to paper over.

**Calibration (still open):** judge calibration (TPR/TNR ≥ 80%) is **not done and cannot be faked from
what exists.** The available verdicts are agent-generated (the scaffold-audit instrument) — and the eval
discipline forbids LLM-generated data as ground truth (calibrating one LLM judge with another's verdicts is
circular). A real calibration set requires a human to hand-label a batch of (output → PASS/FAIL) judgments.

## Ground-truth discipline
Cases are grounded in **observed** failures where possible (dormancy, stale handoffs, mis-routing). Some are
**preventive / negative tests** (malformed approval token, ambiguous directive, external-write gate) and are
labeled as such rather than claimed as observed. **Coverage gap:** failure-mode **7** (alert routed to an
archived destination) is *defined* but not yet *cased*. Judge calibration (TPR/TNR thresholds against a
human-labeled set) is **not yet shipped** — verdicts are advisory until then.
