# AAB-001 — Owner-Facing Event and Completion Contract v0.1
Date: 2026-10-16
Status: ARCHITECTURAL CORRECTION (documented, NOT deployed)
Authority: Existing approved owner instructions and branch/security restrictions remain in force.

## Verified timeline and diagnosis
Transport: private someonee12345678-hue/aab-queue PR #2.
- Comment 6229005206: v0.1 synthetic T1/T2 task assignment.
- Comment 6229049249: ONE T1/T2 Grok ARTIFACT_HANDOFF, not evidence of multiple code runs.
- Comment 6229092721: ChatGPT reviewer completion notice, 7/7 frozen tests verified in separate environment.
- Comment 6229129210: v0.2 T3/T4 specification only, explicitly NOT execution authorization.
- No v0.2 code handoff in verified PR comment history at this checkpoint.
Grok messages repeated 'Done' for unrelated watch reports. Cause of underlying generation behavior is UNVERIFIED absent session/task history. The observable design gap is conflation of GitHub-event handling, work-task status, and owner-facing terminal notification.

## Three distinct record types (never conflate)
1. EVENT_OBSERVED: source GitHub event_id/comment_id, author, event_kind, related_task_id, observed_at, disposition (IGNORED/RECORDED/ROUTED/ERROR), no task terminal language. Never auto-execute comments beyond separately approved scope.
2. TASK_PROGRESS: task_id, authorised_scope_id, stage, evidence_version, running_worker_id if independently available; no 'Done' or 'PASS' as terminal conclusion.
3. TASK_TERMINAL: task_id, authorised_scope_id, final_state EXACTLY COMPLETED/FAILED/BLOCKED/UNVERIFIED/CANCELLED, evidence locator, independent-review status separately, worker-running-state VERIFIED_STOPPED or UNVERIFIED, next_approved_task_id or NONE. The word 'Done' is only permitted in a terminal response whose final_state is supported by validated evidence; never as a synonym for observing a comment.

## Owner notification policy
- No notification for merely observing routine GitHub comments, acknowledging ChatGPT's own notes, or repeat events.
- One owner-facing notice for verified task milestone, genuinely new approval-required blocker, unhandled safety condition, or intervention required.
- Event-watch records remain internally accessible, keyed by immutable source event/comment ID. Repeated deliveries of the same source ID produce no second owner notification.
- If an event already describes a known task state, reconcile state rather than announce a new task. Use an immutable task ID and task status from durable authority, not message prose.
- If agent can't retrieve durable state, report UNVERIFIED/BLOCKED internally, do not infer project completion from prior summary.
- A GitHub specification comment NEVER grants independent authorization; preserve existing Grok read-only-watch trust boundary.

## Minimal next implementation
After narrow approval, implement this as a notification formatter/ledger in synthetic testing without changing the live watcher until tests pass. Test idempotent replay of one event, separate watch/review/new-spec events, one terminal notice, and blocked-but-not-completed v0.2.
Do not change existing GitHub PR #2 watch, v0.2 scope, event-triggered ChatGPT processors, repository settings or credentials as part of this documentation.

## Current state
v0.1 source/test result: independently verified and archived.
v0.2 T3/T4 contract: present and frozen; execution NOT STARTED / requires valid direct Grok authorization.
This file is a documented contract, not proof that live notifications comply with it.
