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

## Provenance & status
The headline **23% → 37%** improvement was measured by the org's **scaffold-audit instrument** (the same
classifier described in the repo README), **not** by executing the JSON cases below. The `cases/PC-0NN.json`
files **define** the harness; most ship as **unscored templates** (`actual` / `verdict` = `null`) — there is
**no runner/scorer committed yet** (a roadmap item, see the repo "What is NOT built yet"). Where
`results/cycle-1.md` cites PC-008 / PC-010 as FAIL → PASS, those verdicts were **observed via the audit
instrument**, not produced by scoring the JSON.

## Ground-truth discipline
Cases are grounded in **observed** failures where possible (dormancy, stale handoffs, mis-routing). Some are
**preventive / negative tests** (malformed approval token, ambiguous directive, external-write gate) and are
labeled as such rather than claimed as observed. **Coverage gap:** failure-mode **7** (alert routed to an
archived destination) is *defined* but not yet *cased*. Judge calibration (TPR/TNR thresholds against a
human-labeled set) is **not yet shipped** — verdicts are advisory until then.
