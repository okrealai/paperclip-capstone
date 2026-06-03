---
id: ADR-0002
title: Detection vs. Remediation Sovereignty — splitting drift detection from drift correction across two operating lanes
status: accepted
date: 2026-06-02
decided_date: 2026-06-02
decided_by: James Smith
supersedes: none
superseded_by: none
decision-makers: James Smith
consulted: Conduit (CIO lane), Cycle (COO lane), Bulwark (CISO lane)
informed: server-org leadership lanes
---

# ADR-0002 — Detection vs. Remediation Sovereignty

## Context

A transport-substrate configuration drift was detected by the platform's automated monitor. The
drift surfaced a real ownership ambiguity: two operating lanes each had a plausible claim over the
response.

- One lane (the **detection / information lane**) operates the monitor, maintains the declared
  source-of-truth registry that records the expected substrate state, and produces the periodic
  drift reports that bucket findings by category.
- Another lane (the **operations / remediation lane**) owns the live services whose behavior
  produces substrate side-effects, and had already demonstrated a precedent: correcting a single
  registry entry while attaching durable evidence that the corrected state was intended.

A security-lane finding (recorded in an internal tracking ticket) framed the detected drift as a
set of standing security findings and asserted that the operations lane — not the detection lane —
owns *remediation or registry correction*. That assertion collided with the detection lane's
declared ownership of the registry and the substrate inventory.

The conflict is fundamentally a governance question, not a technical one: **when a system-state
drift is detected, who is allowed to fix it, and who is allowed to amend the record of what
"correct" means?**

## Decision

Adopt a **split between detection and remediation/registry-correction.** Detection and the
source-of-truth registry stay with the information lane; remediation of service-induced
side-effects, and the narrow authority to correct a registry row, move to the operations lane.

## Ownership

**Detection lane (information):**
- Operates the monitor and produces the drift reports, bucketing findings by category.
- Performs the live inventory of the current substrate state.
- Owns the declared source-of-truth registry — its schema, its baseline snapshots, and the
  read / audit / generate path against it.
- Surfaces unknown-owner items and security-framed findings.
- Performs **no live mutations and no registry corrections.** Its output is observation and
  classification, not change.

**Operations lane (remediation):**
- Owns the service-induced side-effects of the substrate (the running services whose configuration
  produces the observed bindings), via its service-health responsibility.
- Is authorized to **execute remediation** and to **correct a registry row** when a drift must be
  resolved.
- Produces the evidence that closes a security finding — the durable proof that a given state is
  intended and non-exposing.

## Sovereignty rule

- The detection lane proposes classification and raises flags through its reports and inventory.
- The operations lane may correct a registry row **only when accompanied by durable evidence**
  (a written proof artifact plus a timestamp) and must record the action.
- Classification or ownership disputes about a specific item escalate to the server-org leadership
  lane.
- **James Smith is the final decider** on boundary disputes and on any policy change to this split
  (for example, introducing a dual-sign-off requirement for registry writes).

The security lane retains **independent security-finding ownership** and continues to route
remediation instructions to the operations lane regardless of the detection path. Splitting
detection from remediation does not subordinate the security lane to either of the other two.

## Rationale

The split honors the security-lane assignment of remediation and registry-correction authority to
the operations lane, while preserving the detection lane's charter over the observation surface and
the source-of-truth registry. The earlier single-row correction is treated as the **canonical
precedent**, not an exception: it modeled exactly the pattern this ADR formalizes — operations
fixes a side-effect, attaches durable evidence, and the registry is updated to reflect intended
state.

The rejected alternative — consolidating both detection and remediation under the detection lane —
was declined for two reasons: it would contradict the security-lane finding, and it would duplicate
a concern (service-induced side-effects) that already belongs to the operations lane's
service-health responsibility. Concentrating "detect" and "fix" in one lane also removes the
healthy separation that makes the detection lane's reports trustworthy: a lane that both grades and
repairs has an incentive to grade leniently.

## Consequences

- The source-of-truth registry physically stays with the detection lane as the single record of
  expected state, but it is now **mutably authoritative**: documented operations-lane corrections
  are first-class writes, not edits to be reverted.
- The monitor, the drift reports, and their schedule are unchanged and remain with the detection
  lane.
- Future operations-lane remediation artifacts are stored in the operations lane with cross-links
  back to the detection lane's reports, so the audit trail spans both lanes.
- No artifacts were archived or removed as a result of this decision; the operations-lane
  responsibility that previously existed only as a stub is formalized as the remediation lane.

## Status note

This is the **governance** decision. The specific drift that prompted it — its category, counts,
mechanism, and the substrate involved — is intentionally out of scope for this public record;
those operational details live in the private operating environment. What is durable here is the
ownership model: **detection observes and owns the record; remediation fixes and may amend the
record with evidence; security findings stay independent; disputes escalate; the operator decides.**

