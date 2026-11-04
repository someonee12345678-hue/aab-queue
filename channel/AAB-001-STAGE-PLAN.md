# AAB-001 — Autonomous Operation Priority Decision
Date: 2026-10-16
Authority: Owner approved in AAB-001 MAIN conversation.
Status: APPROVED DECISION; implementation and end-to-end verification pending.

## Primary objective — Stage 1
Achieve automatic, unattended ChatGPT Work ↔ Grok exchange using the existing private GitHub repository someonee12345678-hue/aab-queue and PR #2, with no paid APIs, manual copy/paste, or new Android applications.
Minimize changes. Reuse the existing event-triggered ChatGPT Work processor and connected GitHub tools. Do not repeat successful v0.2 PING or v0.3 read-only analysis tests. Keep existing successful communication channel and task triggers.
Implement a narrow, safe claim-and-reply protocol for fictional ANDROID_BUILD ANALYZE_REPORT requests only. Prefer fail-closed, at-most-once posting over duplicate or unverified results. Do not process real legal records, secrets, credentials, or arbitrary commands.
No Ollama, Gemini, OpenRouter, new controller, GitHub Actions, email relay, or paid API in Stage 1.

## Stage 2 — After verified autonomous exchange
Improve durability, recovery, persistent project memory, monitoring, model quality, and alternative AI engines, possibly local Ollama or free-tier Gemini. These are deferred, not rejected.

## Verified baseline
v0.2 synthetic PING round trip passed.
v0.3 fictional ANALYZE_REPORT read-only processing passed.
v0.4 Work trigger woke, but GitHub event payload lacked source comment ID.
v0.4.1 full PR comment list omits created_at; individual GitHub REST comment fetch returns timestamp and identity.
v0.4.2 processor has individual-fetch workaround but fail-closed duplicate/exclusive-claim gates; no return result verified.
Latest prior synthetic request 6225493587 (AAB-V041-TEST-001) must not be replayed.
Existing Work processor task ID: 6ad29339d16c81919f4dd6f39fa13d1d.

## Minimal Stage 1 implementation
On branch mc/channel, use one create-only claim file per independently verified source GitHub comment ID: channel/claims/<source_comment_id>.json. Create it only after strict schema validation and pre-post duplicate check. The first successful creation establishes a durable POSTING_PENDING record. If creation fails or outcome is uncertain, stop without posting; never overwrite or retry automatically. Existing claim file means no new post. After confirmed reply, update the claim record to COMPLETED with the posted GitHub comment ID; if completion update fails, retain pending record and do not retry posting. This is at-most-once intent, not exactly-once delivery. Confirm Work execution can use connector write operations; test once with a new synthetic request only. Preserve prior tasks and successful tests.

## Stage 1 acceptance gate
A new fictional ANALYZE_REPORT request automatically wakes the existing Work processor, is verified and claimed, produces exactly one linked TASK_RESULT comment, and Grok can automatically detect it. Check durable claim and task history. Until observed, status remains UNVERIFIED.
