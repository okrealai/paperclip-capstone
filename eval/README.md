# Eval Harness

Evaluation is treated as **infrastructure, not a one-shot script**. The harness exists so that each
audit→fix→re-audit cycle starts from named, reusable cases instead of from zero.

## Layout
- **`failure-modes.md`** — the 7 observed failure modes (with severity), each grounded in a real
  observation from the baseline audit.
- **`cases/PC-0NN.json`** — 10 cases mapping to those failure modes. Each declares `input`,
  `expected` behavior, and is scored `actual` / `verdict` at run time. Cases cover routing,
  gated external writes (incl. a malformed-token negative case), dormancy, stale memory recall,
  concurrency dedup, and stale-handoff processing.
- **`judge/rubric.md`** — the 5-component LLM-judge prompt (Role / Accept rubric / Reject rubric /
  few-shot / output format).
- **`results/cycle-1.md`** — the before/after record for the first flywheel cycle (23% → 37%).

## Ground-truth discipline
Every case is driven by an **observed** failure, never synthetic data. Judge calibration
(TPR/TNR thresholds against a human-labeled set) is **not yet shipped** — verdicts are advisory
until then.
