# Flywheel Cycle 1 — Before / After

This document records the first full pass of Paperclip's improvement loop: a single
**trace → evaluate → fix → re-evaluate** cycle run against the live server-side org. It is
the centerpiece evidence for how Paperclip improves itself, and it is written to be honest
about what moved, what didn't, and what we are carrying forward.

The mechanic is deliberately simple and repeatable:

1. **Trace** — run the org's own classification instrument over every manager to establish
   a ground-truth baseline.
2. **Evaluate** — select a small set of audit findings as the cycle's targets.
3. **Fix** — dispatch a multi-agent orchestration to close those findings.
4. **Re-evaluate** — re-run the *same* instrument and compare, manager by manager, against
   the prior baseline.

The loop is the product. No single business workflow is the point — the point is that the
org grades itself with the same rigor it would grade any other system, and ships the
correction rather than hiding the gap.

---

## The instrument

Before shipping the org, we built the instrument that grades the org. Every manager is
classified into one of four states:

- **VERIFIED** — the manager is doing real domain work, with evidence (artifacts, closures,
  cited sources) to prove it.
- **PARTIAL** — some real output exists, but the manager is incompletely scaffolded or its
  evidence is thin.
- **STUB** — a placeholder: a directory or a single file with no substantive workload.
- **DORMANT** — heartbeats but no domain output. Process theatre.

The honest, uncomfortable reading of the first trace was that most of the org was theatre.
That is the baseline we chose to publish.

---

## Baseline (before)

The first trace classified roughly 30 managers and found:

| Metric | Value |
|---|---|
| Verified (doing real work) | **7** |
| Process-theatre (heartbeats, no domain output) | **23** |
| Verified share | **23%** |

Twenty-three of thirty managers were running — emitting heartbeats, occupying their lanes —
without producing domain output. That is the gap a self-grading org has to be willing to
state out loud.

---

## The cycle (fix)

From the baseline, we selected **6 audit findings** as cycle-1 targets and closed them with
a roughly **36-agent orchestration** — managers plus a worker pool fanned out underneath
them (on the order of six managers each driving a small worker set). The orchestration ran
overnight against the cycle-1 run directory, produced its artifacts, and handed back closures
for re-audit.

Production safety held throughout. Paperclip gates actions on a human-in-the-loop approval
model keyed on **stakes and reversibility**: low-stakes, reversible actions (such as heartbeat
writes) auto-execute, while high-stakes, irreversible actions (external-system writes) require
an explicit approval token. During this cycle, **0 external writes** occurred — the gate held,
and one finding correctly escalated a large reclaim to the operator rather than acting on it
(see carry-forward below).

---

## Re-audit (after)

The same instrument was re-run against the post-cycle state and compared, manager by manager,
to the baseline.

| Metric | Before | After |
|---|---|---|
| Verified | 7 | **11** |
| Process-theatre | 23 | **19** |
| Verified share | 23% | **37%** |

- **+4 managers transitioned** out of theatre into verified or partial work.
- **0 regressions** — none of the original 7 verified managers fell back.
- **5 of 6 findings accepted**; 1 returned **needs-revision** because it surfaced a deeper
  issue rather than a clean close.

A +4 net move with zero regression in one overnight pass is a modest but real gain — and,
more importantly, it is a *measured* gain. The same instrument graded both ends.

### What moved (by lane / codename)

| Lane / manager | Before | After | What changed |
|---|---|---|---|
| coo · network-ports remediation lane | STUB (single file) | **VERIFIED** | An architecture decision record plus a closeout, citing an internal tracking ticket, turned a placeholder into a documented remediation lane. |
| cko · filesystem-organization | DORMANT | **VERIFIED** | A cycle-1 handoff closure, citing real source paths, gave the lane verifiable domain output. |
| cko · cleanup-archival | DORMANT | **VERIFIED** | A reclaim window was opened, worked, and honestly closed, with a heartbeat trail to back it. |
| coo · cycle | DORMANT (no directory) | **PARTIAL** | A shell-only lane now exists with real capacity numbers, but it is not yet fully scaffolded — see needs-revision below. |

### Verdict per finding

- **Sovereignty (two findings):** ACCEPTED — both architecture decision records are
  substantive and cite a real internal tracking ticket.
- **Stale handoffs:** ACCEPTED — the handoff closures cite real source paths.
- **Reclaim window:** ACCEPTED with caveat — the window was closed honestly, and a large
  reclaim was correctly escalated to the operator rather than executed.
- **Weekly report:** ACCEPTED — cites real per-business modified-times and drift.
- **Capacity refresh:** **NEEDS-REVISION** — the capacity numbers are real, but the `coo/cycle`
  lane is still a shell (missing its full role, status, log, and procedures scaffolding).

---

## Honest carry-forward to cycle 2

The re-audit was charitable where it could be and skeptical where it had to be. Four quality
flags carry forward rather than being papered over:

1. **Architecture-record internal-consistency nit** — one decision record has a mismatch
   between its header phrasing and its body. Real content, but it needs to read consistently.
2. **A shell-only lane needs a full scaffold** — the `coo/cycle` lane has real capacity data
   but lacks its complete role / status / log / procedures structure. Numbers without a home
   are not yet a verified manager.
3. **Handoff closures used a most-charitable reading** — the closures are honest, but the
   framing leans on the most generous interpretation of the evidence. That is fine to state;
   it is not fine to hide. The Q&A around it needs prep for cycle 2.
4. **A large reclaim is escalated to the operator** — under the no-delete rule, the reclaim
   was surfaced for operator authorization rather than acted on. It remains pending by design,
   not by oversight.

---

## What this cycle is — and is not

This is one pass of a loop, not a finished org. The honest framing matters:

- **It is:** a measured, instrument-graded improvement (23% → 37% verified) with zero
  regression, produced by the org grading and then correcting itself.
- **It is not yet:** judge calibration (true-positive / true-negative thresholds remain
  unshipped); a fully verified org (19 managers are still process-only, many scaffolded
  with no domain workload yet); or an automated regression check after each manager fix.
  Full distributed tracing is a later phase — today's observability feeds the eval harness,
  it is not the harness itself.

The generalizable result is the loop and the audit-as-eval pattern: trace → evaluate → fix →
re-evaluate, run with the same instrument at both ends, with the result published whether it
flatters the org or not.

