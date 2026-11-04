# AAB-001 — Event Notification v0.1 Synthetic Prototype Milestone
Date: 2026-10-16, America/Vancouver
Status: PROTOTYPE_TESTS_PASS, NOT LIVE / NOT DEPLOYED
Architectural authority: channel/AAB-001-EVENT-COMPLETION-CONTRACT-V01.md.

## Persisted immutable-for-review source
- pilot_notifications_v01/event_notice.py — SHA-256 dccbba2f1522f1178543e4fe8901aae610b8a0214e45b0863d8c9ed49380d6f1 ; Git blob 4992732da6280b3e1ff4b35aff9ba74c18f11edc.
- pilot_notifications_v01/test_event_notice.py — SHA-256 22faf7aa1f4a76adacf9368125ef51ab1dba050d33e723d8d564e16f988f841d ; Git blob 1100a77a0952483d77f9b8883e3a371dbd22d8f2.
- Both files created in private someonee12345678-hue/aab-queue branch mc/channel, fetched back and verified to match submitted source; local git hash-object exactly matched returned GitHub blobs.

## Local synthetic test evidence
Command: python -m unittest -q, working directory containing exactly the above module and tests.
Observed: Ran 13 tests in 0.018s; OK; exit code 0.
Tests: corrupt ledger rejection, first/duplicate event suppress, terminal proof prerequisite, event-vs-progress separation, repeated review only one owner notice, specification not authorization, verified blocker notice, four ordinary watch events silent, contradictory source-ID replay fail-closed, conflicting terminal result fail-closed, nonterminal false completion rejected, payload-changed replay rejected, malformed event type rejected.
No older bridge or real-build tests repeated.

## Design notes and limits
- Event records identified by numeric GitHub comment id with SHA-256 digest over canonical event payload; changed replay is a conflict.
- One terminal notice per task ID, only for trusted reviewer-verified completion or verified blocker explicitly requiring owner action.
- Atomic on-filesystem JSON replacement with fsync on file; process is single-writer only. No distributed lock, durable multi-agent claim, concurrent multi-writer protection, fsync on directory, independent tamper resistance, secret verification, actual GitHub event adapter, or evidence authentication.
- Trusted structured inputs: review_verified and owner_action_required MUST come from a separately trusted verifier, NEVER from an AI/GitHub comment body. Prototype does not itself verify evidence or authenticate agents; plugging in untrusted fields defeats its claimed protection.
- This is a prototype and is NOT integrated with Grok PR #2 read-only watcher or ChatGPT processors. No changes made to live bridge, workflows, credentials, PR status or repository permissions.
- v0.1 independently verified programming code still preserved; Stage 4 v0.2 T3/T4 remains prepared but NOT STARTED, requiring separately validated Grok scope authorization.

## Next engineering decision
Integrate a trusted adapter into Grok's *owner-notification path* in an isolated environment only after verifying it can run without breaking the existing read-only event watch, and that it obtains external verification fields from an actual trusted provenance source. Until then, avoid claiming the repeated Done messages are fixed in production.
