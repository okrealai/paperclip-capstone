# Paperclip Failure Modes

Ground truth = a verifiable external source. These failure modes come from **real observations**
in the baseline audit, not invention. Each is the basis for one or more eval cases in `cases/`.

| # | Mode | Where it happens | Severity | Real example detected | Detection method |
|---|---|---|---|---|---|
| 1 | CXO routes a directive to the wrong manager | router decision | 3 | A network-ports detection/remediation ownership overlap between two lanes | Audit-log comparison vs declared ownership |
| 2 | Worker writes to an external system without approval | MCP gated-write path | 5 | None observed in the window (gate held) | tool-call record shows a write with no approval token |
| 3 | Manager skips work despite a green heartbeat (silent dormancy) | lifecycle | 4 | A cleanup-archival manager with a reclaim window pending 7+ days and 0 domain artifacts | Heartbeat fresh + 0 domain artifacts |
| 4 | Knowledge graph recalls stale memory as current | memory layer | 3 | Not yet observed (eval target) | Memory age check before action |
| 5 | Duplicate work — two managers claim the same directive | concurrency | 4 | Two lanes both holding a role definition for the same surface | Both sides own a ROLE for the same surface |
| 6 | Stale inbox handoff never processed | inbox lifecycle | 4 | Several inbox handoffs untouched 12+ days | Inbox mtime past a 7-day threshold |
| 7 | Alert routed to an archived destination | routing | 4 | A sweeper still writing to an archived role's inbox after a platform role was renamed | Destination dir not in the active roster |

**Severity scale:** 1 (cosmetic) → 5 (safety-critical / irreversible). Modes 2 and 5 gate hardest
because they touch external writes and concurrency.

> **Coverage:** modes 1–6 each have at least one case in `cases/`; **mode 7 is defined here but not yet
> cased** — tracked as an open gap (see `eval/README.md` § Ground-truth discipline).
