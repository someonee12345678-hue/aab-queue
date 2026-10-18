# AAB-EXEC-001 — Goal-State Schema and Synthetic Acceptance Specification
Status: DESIGN SPECIFICATION ONLY; no executor, live schema or tests installed.
Date: 2026-10-18. Project: AAB-001. Branch: mc/channel.
Companion: channel/recovery/AAB-EXEC-001-PERSISTENT-GOAL-DESIGN-2026-10-18.md

## Proposed GOAL_STATE.json v0.1 shape
Required fields:
- schema_version: integer 1
- project: constant AAB-001
- goal_id: stable nonempty ID
- owner_scope_ref: explicit approved-scope reference; absence means no execution
- repo, branch, base_commit: full identity and 40-character commit SHA
- goal_status: PROPOSED | APPROVED | IN_PROGRESS | BLOCKED | VERIFIED_COMPLETE | STOPPED
- stop: boolean, fail-closed
- steps: ordered array of unique step_id, prerequisite_step_ids, assigned_role, status (PENDING | READY | RUNNING | REPORTED | VERIFIED | BLOCKED), evidence_refs, idempotency_key
- next_authorized_action: nullable description and required approval reference
- last_verified_utc: ISO 8601 UTC; not an authorization token
- evidence_checkpoint: reference to immutable GitHub evidence; never inline secrets.

## Validation invariants
1. Reject unknown schema versions, duplicate step IDs or idempotency keys, missing repo identity, invalid SHA or cyclic prerequisites.
2. VERIFIED steps must have exact evidence references; REPORTED does not satisfy a prerequisite requiring VERIFIED.
3. Next step must have all prerequisites VERIFIED; STOP, expired scope or conflicting branch/head blocks all side effects.
4. Never promote a step from REPORTED to VERIFIED based solely on agent self-report.
5. Any ambiguous remote write requires readback and reconciliation, never blind retry.
6. GOAL_STATE is a proposal until approved; PR comments and controller suggestions cannot supply approval.
7. No concurrent writers to one state file without compare-and-swap / current blob SHA; conflict must return BLOCKED.
8. NEXT_ACTION is derived from validated state and is never a second source of authority.
9. Append-only execution log references observed evidence and commits; no historical receipt edits.
10. Preserve v0.6/PING Support hold, STOP and existing phone revision gate.

## Six proposed synthetic tests (not executed)
- T1 interrupted after VERIFIED step 1: next session selects step 2, no repeat of step 1.
- T2 stale base SHA or contradictory state: BLOCKED, zero writes.
- T3 duplicate event/idempotency key: at most one effect, ambiguous result requires reconciliation.
- T4 STOP true or missing owner scope: zero executions.
- T5 fresh context reconstructs repo/branch, evidence and one next action with no chat history.
- T6 measure resume latency and repeated completed steps against current manual recovery; no speed claim without observations.

## Engineering sequencing
A. Read and compare the existing assignment-controller schema and recovery state contracts.
B. Implement a pure read-only validator with standard-library-only synthetic fixtures, subject to separate implementation approval.
C. Run deterministic CI only for changed sources after authorization.
D. Demonstrate a bounded interruption/recovery test before considering an executor.
E. Separately authorize any real dispatch or Android operation.

This document grants no agent runtime, background scheduling, GitHub workflow changes or phone commands.
