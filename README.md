# Paperclip

**An AI executive team for a solo multi-business operator.**

Paperclip is a server-side AI organization that absorbs the manager-tier work a solo founder would otherwise do four times over. It routes directives to codenamed CXO agents, dispatches a worker pool, reads and writes a shared memory layer through a gated tool interface, and — the part this repository is really about — grades its own honesty before it ships anything.

This repository is the public artifact for an applied-AI program capstone. It presents Paperclip on its own merits, and it is precise about what is built versus what is still ahead.

---

## The problem

One operator runs four businesses: a commercial real-estate brokerage (BoisCRE), an AI transaction-coordinator SaaS (Keyflo), a media brand (OK Real Estate Media / Closing Daily), and a real-estate investment vehicle (WinWin). One person cannot be CEO, operator, and CTO of four things at once. The bottleneck is not tooling — it is the operator. Every business needs the same manager-tier work (knowledge ops, infra hygiene, security review, document standards, strategy), and a solo operator either does that work four times or does not do it at all.

Paperclip is the dispatch layer that absorbs that manager-tier work so it gets done once, consistently, across all of them.

---

## Architecture

Paperclip runs in three lanes. The full diagram is in [`docs/architecture.mmd`](docs/architecture.mmd) with a written walkthrough in [`docs/architecture.md`](docs/architecture.md).

**① INPUT — directive intake.** A directive enters from one of three sources: an operator prompt, a scheduled cron tick, or an external webhook.

**② PROCESSING — the Paperclip org.** A router decides which CXO lane owns the directive, then that lane's manager dispatches to a worker pool. The managers carry codenames:

- **apex** — CEO / strategy
- **lattice** — CKO / knowledge ops (with sub-lanes for cross-business consistency, cleanup-archival, filesystem organization, and document standards)
- **conduit** — CIO / infrastructure ops (including network-port hygiene and a set of sweepers)
- **bulwark** — CISO / security
- **steward** — HR / self-heal
- **veritas** — audit probes

Plus a COO lane for operational cycles and scheduled health/backup work. Managers hand off to a worker pool (forge, anchor, and steward worker chains), which reaches the rest of the system through an **MCP layer that is read-mostly with gated writes**. Behind that layer sits the **memory + reasoning core**: a knowledge graph (~31k memories / ~55k entities), a source-of-truth vector store, and append-only audit logs.

**③ OUTPUT — artifacts and side effects.** Workers produce markdown artifacts, GitHub commits, HEARTBEAT logs, and audit closures. External systems (a CRM, a workflow engine, a notes workspace, and a chat platform) are wired in but gated — and during the cycle documented below, they received zero writes.

---

## The honest audit (the centerpiece)

Before shipping the org, the operator built the instrument that grades the org.

That instrument classifies every manager into one of four states:

- **VERIFIED** — heartbeat plus an audit pass proving real domain output
- **PARTIAL** — scaffolded, but no telemetry yet
- **STUB** — a placeholder file with no workload
- **DORMANT** — heartbeat green, but the actual work has stopped

Running it produced an honest, uncomfortable baseline. Of roughly 30 managers, **only 7 were verified to be doing real work — 23%.** The other 23 were process theatre: green heartbeats, no domain output. Rather than hide that, the capstone ships the fix.

One **flywheel cycle** — audit → select findings → fix via a multi-agent orchestration (a ~36-agent run of managers plus workers) → re-audit — moved the system in a single overnight pass:

| | Verified | Process-only | Verified % |
|---|---|---|---|
| Baseline | 7 | 23 | 23% |
| After cycle 1 | 11 | 19 | **37%** |

**+4 managers transitioned to verified, 0 of the original 7 regressed, and 5 of 6 audit findings were accepted** (the sixth was marked needs-revision because the fix was shell-only and surfaced a deeper scaffolding gap — kept visible rather than papered over).

The trace → evaluate → fix → re-evaluate loop, plus the audit-as-eval pattern that drives it, is the generalizable contribution. Full cycle detail is in [`docs/flywheel-cycle-1.md`](docs/flywheel-cycle-1.md).

---

## Evaluation harness

The audit is backed by a real evaluation harness, not vibes. See [`eval/`](eval/):

- **Failure modes** — the specific ways a manager can look alive while doing nothing
- **10 cases** — a labeled set covering the four classification states and the boundaries between them
- **Judge rubric** — the criteria a manager must meet to score VERIFIED, applied identically at baseline and re-audit so the before/after comparison is honest

---

## Production safety

Every agent action is classified by **stakes × reversibility**, and the system gates accordingly:

- **Low-stakes + reversible** (e.g. writing a heartbeat log) → auto-execute
- **High-stakes + irreversible** (e.g. any write to an external system) → require a human-in-the-loop approval token

During the documented flywheel cycle, **0 external writes occurred — the gate held.** The reasoning behind the gating model is recorded as architecture decision records in [`docs/adr/`](docs/adr/).

---

## What is NOT built yet

Being precise about gaps is part of the point:

- **Judge calibration** — formal true-positive / true-negative rate thresholds for the audit judge are not yet shipped.
- **The 19 remaining process-only managers** — many are scaffolded with no domain workload yet; cycle 1 moved four of them, the rest are queued.
- **WinWin has zero managers by design** — it is a holding company, not an operating business, so it intentionally carries no manager fleet.
- **Distributed tracing is a later phase** — today's observability feeds the eval harness; it is not yet full distributed tracing.
- **No automated regression check after each manager fix yet** — regression is currently confirmed by re-running the whole audit, not by a per-fix gate.

---

## Who it's for / the IP

Paperclip is built for solo founders and operators running 3+ verticals — people who use many tools and have no executive team to delegate manager-tier work to.

The intellectual property is **not** any single business workflow. It is two reusable patterns:

1. **The orchestration topology** — a router → codenamed CXO managers → worker pool → gated memory layer structure that scales manager-tier work across unrelated verticals.
2. **The audit-as-eval pattern** — building the instrument that grades the org before shipping the org, then closing the loop with a multi-agent fix cycle and re-audit.

---

## Repo layout

```
README.md                    This file
LICENSE                      CC BY-NC-ND 4.0
docs/
  architecture.md            Written walkthrough of the 3-lane design
  architecture.mmd           Mermaid source for the architecture diagram
  adr/
    ADR-0001-inbox-retire.md                       Retire an orphaned routing inbox after a role rename
    ADR-0002-detection-vs-remediation-sovereignty.md   Split drift detection from drift correction
  flywheel-cycle-1.md        The 23% → 37% audit-fix-reaudit cycle in full
eval/
  README.md                  Harness overview
  failure-modes.md           7 observed failure modes with severity
  cases/PC-0NN.json          10 graded cases
  judge/rubric.md            5-component LLM-judge prompt
  results/cycle-1.md         Before/after eval-run record
```

---

## Status

**Complete:** a verified executive core (11/30 managers), one measured flywheel cycle (23% → 37%), the eval
harness (failure modes + 10 cases + judge rubric), two ADRs, and the architecture diagram. **Carries forward:**
judge calibration, an eval runner/scorer, coverage of failure-mode 7, and the 19 remaining process-only
managers. The next cycle starts from those items, not from zero — see `docs/flywheel-cycle-1.md`.

---

## License

[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) — Attribution, NonCommercial, NoDerivatives.

