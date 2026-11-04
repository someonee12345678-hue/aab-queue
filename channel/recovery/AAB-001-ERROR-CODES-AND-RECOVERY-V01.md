# AAB-001 — Failure Codes and Context Recovery Protocol v0.1
Date: 2026-10-17 (America/Vancouver)
Status: DOCUMENTED / VERIFIED SAVED ON GITHUB; automatic UI detection and failover NOT IMPLEMENTED.
Applies to: MAIN ChatGPT conversation, GitHub durable transport, Grok workflows, phone-side Termux/Codex.
Authority: Owner-approved project scopes and existing safety gates. This protocol is not an authorization to execute new code or alter processors.

## Failure vocabulary
Codes are operational diagnoses, **not** product/platform-generated error identifiers. Use a code only when its detection evidence is recorded. Do not invent a native ChatGPT error code.

| Code | Meaning / detection evidence | Safe recovery | Never do |
|---|---|---|---|
| AAB-ERR-CHAT-001 | **Conversation reached maximum length.** UI explicitly says maximum length; older chat cannot accept messages. | Start a **new MAIN** conversation; read latest `channel/recovery/CURRENT_STATE.json` and this protocol from `mc/channel`, verify live evidence, continue only the next incomplete operation. | Claim cloud worker crashed, reset progress or rerun successful tests. |
| AAB-ERR-CHAT-002 | **App appears stalled.** No response/visible change after a reasonable wait; without UI trace, actual worker state is UNVERIFIED. | Capture screenshot + approximate local timestamp, inspect task run/GitHub evidence read-only, create new chat if UI cannot recover; treat external write outcome as uncertain. | Infer failure merely from grey buttons; press Run now or resubmit a possibly writing job. |
| AAB-ERR-STATE-003 | **Stale/conflicting record.** Repo/branch/revision/test result conflicts with latest independently verified GitHub record. | Stop writes, retrieve exact current repo, branch and file hashes and reconcile with independent evidence; label disputed fields UNVERIFIED. | Override owner scope with memory or stale screenshots. |
| AAB-ERR-STATE-004 | **Checkpoint missing/unreadable.** GitHub/connector cannot fetch required governing/current state. | Fail closed; use pinned original PR comment and reviewer report if accessible, or owner supplies existing checkpoint; no task advancement. | Recreate facts, approvals, histories or test results from a guess. |
| AAB-ERR-EVENT-005 | **GitHub trigger source event ID missing in ChatGPT task.** `UNVERIFIED_EVENT_ID` recorded. | Use GitHub's independently recorded comment IDs and durable queue as *data*, reconcile read-only; await an authorized supported ChatGPT wake/dispatch route. | Select the newest comment by assumption or edit Support-held v0.6/PING tasks. |
| AAB-ERR-QUEUE-006 | **GitHub queue write blocked/uncertain**, e.g. HTTP 403/409/timeout. | Inspect exact Actions run, outcome artifact and queue path before any new operation; preserve original event and previous attempts. | Replay a historical event, duplicate the queue file, widen token permissions without approval. |
| AAB-ERR-REVIEW-007 | **Review status mismatched across durable records.** Immutable queue may still say NOT_PERFORMED despite later independent review. | Preserve original queue receipt; link to separately verified reviewer verdict/comment and note that each document records a different stage. | Mutate or reinterpret queue receipt as an approval. |
| AAB-ERR-PHONE-008 | **On-device readiness unverified**, or a tool/permission is unavailable on Android. | Do one read-only capability check in Termux and capture the result; preserve login credentials locally only. | Assume separate Linux-host tests proved Android behavior or install an unapproved controller. |
| AAB-ERR-AUTH-009 | **Authentication/permission problem.** Actual `gh` or Codex status reports unavailable/blocked. | Report precise tool and scope, keep GitHub/ChatGPT/Codex auth distinct, require supported sign-in on user's own phone if needed. | Post secrets into chat/GitHub or bypass bot/anti-automation controls. |

## Deterministic restart gate — new MAIN chat
1. Confirm project is AAB-001, repository `someonee12345678-hue/aab-queue` (PRIVATE), branch `mc/channel`; default branch literally `HEAD`; draft PR #2 stays unchanged.
2. Open `channel/recovery/CURRENT_STATE.json` and this file. Compare record timestamps and pinned proof references to live GitHub source, reviews, queue file, Actions, and branch revisions; if stale, warn before acting.
3. Load the latest source-of-truth review for the active task, not just the oldest MAIN resume document. Separate PASSED reviewer tests, verified saves, phone runtime tests, and unauthorized/unattempted work.
4. Determine the **single smallest unfinished authorized operation**. Do not replay a committed operation if its outcome is uncertain; inspect the exact operation ID, event ID, task ID, and artifact first.
5. If tools cannot access GitHub, report BLOCKED and use a user-provided existing checkpoint as a manual fallback; never invent GitHub results.
6. Tell the owner exactly which chat they are in (**MAIN** or **BURNER**), one phone-friendly step, and when to switch tabs. Avoid requesting screenshots when not needed.

## Recommended per-operation checkpoint fields
`project`, `repository`, `branch`, `scope_id`, `current_phase`, `last_verified_evidence`, `test_result`, `external_write_identity`, `unverified`, `blockers`, `next_single_action`, `error_code`, `state_updated_utc`.

Save a durable checkpoint at a significant PASS/FAIL/BLOCKED result and before planned long/multi-step changes. If a write is uncertain, record UNCERTAIN and check whether it committed before retry. The absence of chat output does not authorize repeating writes. Separate reviewed, saved, verified and owner-approved states.

## Limitation
No ChatGPT tool here can reliably monitor an arbitrary browser tab for imminent context exhaustion, intercept the maximum-length banner, seamlessly transfer a running hidden computation to another chat, or guarantee background recovery. Our mitigation is **loss-limited persistence and evidence-driven continuation**, not a false promise of preventing a product limit.

## Phone-friendly recovery request
In a NEW MAIN chat, paste:
`MAIN — Resume AAB-001 using someonee12345678-hue/aab-queue branch mc/channel, channel/recovery/CURRENT_STATE.json and AAB-001-ERROR-CODES-AND-RECOVERY-V01.md. Verify latest GitHub evidence, report error code and one next action. No replays or changes to existing processors.`
