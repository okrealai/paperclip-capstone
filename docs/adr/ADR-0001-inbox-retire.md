---
id: ADR-0001
title: Retire an orphaned routing inbox after a role rename
status: accepted
date: 2026-06-02
decided_by: James Smith
---

# ADR-0001 — Retire an orphaned routing inbox after a role rename

## Context

A platform-engineering role in the server org was renamed. The role's prior tree was quarantined to a dated archive directory, and canonical ownership of platform-engineering responsibilities moved to the newly named role's directory.

Despite that migration, the retired role's inbox remained live and kept accumulating a sizable backlog of stale alerts spanning several weeks (various platform-health categories). No consumer polled that inbox after the role was archived — the platform sweepers had been redirected to write to the new role's inbox, so detection responsibility had moved while the old routing target was left in place.

The orphan was surfaced by an internal audit finding during a scheduled security-lane activation sweep. The same review flagged the retired inbox as filing drift: alerts continued landing in a retired role's inbox while detection sovereignty had moved to the new role.

## Decision

1. **Declare the retired role's inbox retired** — it is no longer an active routing target for the org.
2. **Move-only archive** all existing files from the retired inbox into a dated archive directory. The archive step performs a move only (defaulting to a dry-run, with an explicit apply step), generates a checksummed (sha256) manifest, and performs no deletion.
3. **Canonical alert destination** for platform sweepers is the new role's inbox. No sweeper or scheduled job may recreate writes to the retired path.
4. After a successful apply and manifest verification, leave the retired inbox absent or empty; do not repurpose the path without a new ADR.

## Consequences

**Positive:** Eliminates dual-inbox confusion; aligns filesystem routing with the renamed role; preserves historical alerts in a dated archive for audit replay; satisfies the audit finding's hygiene requirement without deleting evidence.

**Negative / trade-offs:** Operators searching the old inbox path must use the archive path instead; any undocumented external script still targeting the retired inbox will fail until patched (a guard check on the retired path name in the relevant role's manager tree catches recurrence).

**Dependencies:** The remediation of the underlying port-binding drift surfaced by the same audit finding is owned by a separate role (operations) and is tracked separately from this ADR; this ADR covers only the inbox-retirement and archival hygiene.

## Alternatives considered

| Option | Verdict |
|--------|---------|
| **Keep the retired inbox as a dead-letter target** | Rejected — an orphan path invites missed alerts and contradicts the archived role definition. |
| **Route alerts to the operations role's inbox** | Rejected — the audit finding assigns operations the *remediation* of drift, not the *detection* inbox triage. |
| **Route to the security role's inbox** | Rejected — the security role finds, gates, and routes; platform sweep alerts belong to the platform-engineering role's inbox. |

## Rollback path

If a legitimate consumer still requires the retired inbox: (1) restore files from the dated archive directory's checksummed manifest via an inverse move (verify sha256); (2) supersede this ADR; (3) document the consumer in the platform-engineering role's manager registry. Reversal cost is low while the archive is intact; cost rises if new alerts in the active inbox are later conflated with a restored copy of the retired tree.

