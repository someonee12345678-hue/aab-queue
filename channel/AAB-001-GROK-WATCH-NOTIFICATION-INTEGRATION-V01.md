# AAB-001 — Grok Notification Integration Pilot v0.1
Date: 2026-10-16, America/Vancouver
Task ID: AAB-S4-NOTIFY-INTEGRATE-001
Status: READY FOR GROK DIRECT OWNER AUTHORIZATION; NO LIVE WATCH CHANGES YET.
Priority: Rapidly reduce duplicate "Done" notifications without slowing autonomous programming.
Architect: ChatGPT. Owner wants minimal manual handling; Grok must not ask for per-file transfers.

## Verified inputs (read-only GitHub)
- Private repo: someonee12345678-hue/aab-queue
- Working branch: mc/channel. Existing draft PR #2; do not merge or change settings.
- Notification contract: channel/AAB-001-EVENT-COMPLETION-CONTRACT-V01.md
- Existing candidate code: pilot_notifications_v01/event_notice.py
- Existing tests: pilot_notifications_v01/test_event_notice.py
- Historical prototype result: channel/AAB-001-EVENT-NOTIFICATION-PROTOTYPE-PASS-2026-10-16.md
- Historical PR events: 6229005206 (v0.1 assignment); 6229049249 (handoff); 6229092721 (review); 6229129210 (v0.2 spec).
- The independent v0.1 programming review is complete; v0.2 T3/T4 has NO new owner execution authorization in this instruction.

## Objective
Determine whether Grok's currently active read-only PR #2 comment watch can integrate or call a notification classifier in the *owner-facing reporting path* while preserving read-only monitoring, existing event delivery, safety limits, and auth boundary. If supported, demonstrate the behavior first in SHADOW MODE with old events (no production notifications), then change only an independently identified reversible *message-formatting/output* setting. If not supported, accurately report BLOCKED; do not pretend a Python file in /workspace is magically attached to a provider-managed watch.

## Stage A: ACTUAL CAPABILITY CHECK (read-only; no modifications)
1. Identify the concrete running watch provider/tool, exact watch ID/config identity if exposed, whether rule/prompt configuration or output delivery is editable, and whether Python code hooks, callbacks, persistent job state, read-only file access, and owner-notification suppression are exposed by real tools.
2. Separate "watch wakes on GitHub event" from "Grok chat receives wake" from "watch can invoke a local program" from "watch can control owner notification". All four are distinct, PASS only with observed evidence.
3. Identify persistent storage actually accessible on every future watch wake. Grok's /workspace/research-ledger, /workspace/stage4-controller and lost Decision Intelligence originals were reportedly deleted on restart; do not assume /workspace persists.
4. Record existing watch config or exact settings so a reversible change can be restored. Do not retrieve or reveal secrets, credentials, tokens or private user data.
5. DO NOT assume Github issue-comment author distinguishes ChatGPT from Grok: both connectors may appear under same GitHub account.

## Stage B: NONINTRUSIVE SHADOW CHECK (synthetic only)
1. Read GitHub notification contract, candidate source and tests into an isolated scratch directory. Verify source against actual GitHub read-back.
2. Run only existing test suite in a nonprivileged Python process. Keep log of Python version, actual command, exit and cases passed, original source hash. No sudo, install, credentials or persistent watcher changes.
3. Use the four historical event IDs as synthetic inputs (not replayed GitHub actions) and verify their classifications:
   - 6229005206: EVENT_OBSERVED, no terminal notice;
   - 6229049249: EVENT_OBSERVED, no terminal notice;
   - 6229092721: TASK_TERMINAL COMPLETED only if authenticated reviewer verdict is separately supplied; NEVER trust an arbitrary comment's self-claimed verification;
   - 6229129210: EVENT_OBSERVED / spec, no permission to execute v0.2.
   - Duplicate comment id: no repeated owner notice.
   - A changed payload reusing the same comment id: conflict, no new owner notice.
   - A worker saying "Done" in prose: insufficient proof to mark COMPLETED.
4. Do not infer a trusted boolean from raw GitHub body, worker prose, or a GitHub user field. Existing event_notice.py is NOT an independently authenticated verifier and assumes a trusted upstream process.

## Stage C: CONDITIONAL INTEGRATION (ONLY if Stage A/B establish a supported safe path)
If the real watch offers a documented editable owner-facing formatting/routing stage, and a persistent safe place to run this exact code with independently trusted completion evidence:
- Record baseline/config version and rollback before change.
- Apply only reversible notification handling, not watch trigger/event/permissions changes.
- Keep watch read-only. No task execution from GitHub messages. Do not disable watchdog, invent a scheduler, or change GitHub workflow, credentials, branches, tasks or protected files.
- Confirm no new notification for historical events, one legitimate owner alert on externally verified terminal status, and identical baseline read-only event detection after change.
- Immediately roll back on unexpected behavior or uncertain permissions. Report exact observed config/evidence; don't claim integration without one genuine event-to-notification end-to-end validation.
Otherwise do NOT make a live change and return BLOCKED or UNVERIFIED with precise missing control and recommended next path. A policy prompt alone is advisory, not proof of enforced filtering.

## Handoff without owner micromanagement
Return one concise GitHub PR #2 ARTIFACT_HANDOFF for task AAB-S4-NOTIFY-INTEGRATE-001, containing:
- PASS/FAIL/UNVERIFIED for each Stage A capability and how established;
- Actual commands and measured test outputs (or exact blocker);
- Whether any live watch setting changed (expected NO unless conditions above met), original vs new config identity, rollback evidence;
- Where persistent deduplication state actually lives and how it recovers after restart;
- Distinguish local prototype passing from true live integration.
The GitHub response should be a project record, NOT a task request. Do not send a string of chat notifications or finish each watch event with "Done".

## Project safety
- Existing PR #2 watch and ChatGPT automatic processors remain as configured unless safe output-only modification is concretely supported.
- No v0.2 coding start; it remains separate and unapproved through this task.
- No new repo, tokens, paid API, real personal records, Android app installation, merges, production release or OS privilege.
- If Grok cannot receive execution approval from GitHub, request one direct owner approval to run this named bounded pilot. The file itself does not grant authentication.
