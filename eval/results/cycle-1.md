# Eval Results — Flywheel Cycle 1

**Goal:** Lift the dormancy + stale-inbox failure modes from the baseline pass rate, and raise the
overall "verified-doing-work" ratio across managers.

## Before (baseline audit)
| Case | Mode | Verdict | Why |
|---|---|---|---|
| PC-008 | 3 (dormancy) | FAIL | cleanup-archival: 0 domain artifacts in the window; reclaim window pending 7+ days |
| PC-010 | 6 (stale handoff) | FAIL | an inbox handoff untouched 12+ days |
| — | — | — | Overall verified-doing-work ratio: **7 / 30 = 23%** |

## Method
A single audit-driven flywheel cycle: **trace → evaluate → fix → re-evaluate.** Six audit
findings were selected as targets and closed by a roughly **36-agent orchestration**
(managers + workers running in parallel). Constraints: internal org-tree edits only, **no external
system writes**, and every case driven by an observed failure — no synthetic data.

> **How these verdicts were obtained:** the case verdicts here were **observed via the org scaffold-audit
> instrument**, not produced by running `eval/cases/*.json` through a scorer (no runner is committed yet —
> see `eval/README.md` § Provenance). Ratios are rounded: 7/30 = 23.3%, 11/30 = 36.7%.

## After (re-audit)
| Case | Mode | Verdict | Why |
|---|---|---|---|
| PC-008 | 3 (dormancy) | **PASS** | reclaim window closed honestly + domain artifact produced |
| PC-010 | 6 (stale handoff) | **PASS** | handoffs processed with outcome artifacts citing real sources |
| — | — | — | Overall verified-doing-work ratio: **11 / 30 = 37%** |

**Delta:** +4 managers transitioned to verified; **0 regressions** on the original 7 verified
workers; 5 of 6 findings accepted, 1 returned NEEDS-REVISION (a lane that is still shell-only).

## Regression check
After each fix, the original verified workers (the CKO/CIO/HR/CISO/CEO core + the audit and
cross-business-consistency lanes) were re-checked — no regressions observed.

## Honest carry-forward (cycle 2 backlog)
1. One ADR has an internal-consistency nit between its header phrasing and body.
2. A still-shell-only lane needs a full role scaffold before it can count as verified.
3. Some handoff closures rely on a "most-charitable reading" — honest, but needs framing.
4. A large storage-reclaim is held pending operator authorization under a no-delete rule.

> This is one cycle, not a finished system. The point of the harness is that the *next* cycle
> starts from these flagged items, not from zero.
