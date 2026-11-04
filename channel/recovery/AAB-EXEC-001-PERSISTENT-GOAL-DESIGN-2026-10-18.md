# AAB-EXEC-001 — Persistent Goal Execution Design
Date: 2026-10-18
Status: OWNER-APPROVED DESIGN; IMPLEMENTATION NOT STARTED
Repository: someonee12345678-hue/aab-queue
Branch: mc/channel
Scope: Documentation-only; no live processor or task changes.

## Decision
Use GitHub as the durable authoritative notepad for bounded, resumable goal delivery. Extend existing AAB-001 three-lane MAIN / ENGINEERING / RELIABILITY architecture. ChatGPT plans and independently reviews; Grok works only within separately approved scope; Android phone-side Codex remains a separately authorized local executor. No new background runner, webhook, paid API, credential access or implicit agent activation.

## Proposed minimal records (NOT YET CREATED)
1. channel/execution/GOAL_STATE.json — schema_version, project, goal_id, approved_scope_reference, branch, base_commit, current_step_id, steps with stable IDs and prerequisites, role, status, evidence references, STOP, next_authorized_action, verified_utc.
2. channel/execution/EXECUTION_LOG.md — append-only concise checkpoints, source identity, branch/commit, observation timestamp, status and evidence. Never credentials or hidden reasoning.
3. channel/execution/NEXT_ACTION.md — derived resume card, not independent authorization or competing source of truth.

Do not duplicate channel/recovery/CURRENT_STATE.json, channel/recovery/CAPABILITY_LEDGER.md, channel/learning/lessons_v01.json, or immutable channel/handoffs receipts.

## Execution contract
READ -> RECONCILE -> PLAN -> AUTHORIZATION CHECK -> EXECUTE (only separately authorized) -> VERIFY -> CHECKPOINT -> RESUME.
Read-before-write, optimistic branch SHA check, readback. A mismatch or ambiguous outcome blocks side effects. Stable step IDs and idempotency keys prevent blind replay. PASS requires primary evidence. Preserve VERIFIED, REPORTED, BLOCKED, UNVERIFIED. Comments, proposals, queued receipts and this document are not task authorization. Respect STOP, expiration and least privilege. Each run is bounded; persistence does not enlarge model context or ensure an always-on ChatGPT runtime.

## Synthetic acceptance specification (DESIGN ONLY; NOT EXECUTED)
T1: Interrupt at step 2; fresh session resumes first unverified step without repeating verified step 1.
T2: Stale commit and conflicting checkpoint produce BLOCKED, no write.
T3: Duplicate event identity cannot duplicate side effects.
T4: STOP or absent approved scope prevents execution.
T5: New session reconstructs current state, evidence and one next authorized action.
T6: Compare measured recovery time and repeated-work count against existing recovery; performance improvement remains UNVERIFIED until measured.

## Integration and constraints
Reuse existing assignment-controller PROPOSE_ONLY behavior and AAB-META-001 continuity lesson AAB-L004; do not add duplicate lessons. Preserve current Android revision reconciliation gate. Do not modify live code, workflows, permissions, chat-trigger processors, immutable queue receipts, PR #2, phone credentials or other projects. OpenAI Support case 17390055 hold on v0.6/PING remains in force. No tests replayed, agents started or money spent.

## Next bounded milestone
Draft a reviewable schema and deterministic synthetic test plan, without enabling execution. Implementation and automation require separate scope and approval.
