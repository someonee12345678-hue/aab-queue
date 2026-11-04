# AAB-001 — Conversation Limits, Reliability Investigation and Three-Lane Recovery

Date: 2026-10-17 (America/Vancouver). Owner-authorized investigation and documentation.
Status: VERIFIED symptom; underlying causes of unrelated freezes UNVERIFIED; operating plan PROPOSED.

## Reproducible observation and limits

- User Android Chrome screenshot `Screenshot_20261017-140747.png` displays: **"You've reached the maximum length for this conversation, but you can keep talking by starting a new chat."** A prior message shows "Worked for 2m 34s."
- CONFIRMED: the affected chat can no longer continue in the same thread. No evidence that the server crashed, that a compute-time limit was reached at 2m34s, or that OpenAI throttled the account.
- A prior AAB event processor separately recorded `UNVERIFIED_EVENT_ID` from missing event comment metadata. That is a distinct functional failure, not evidence for the conversation-length banner.
- The owner reports other apparent freezes and frequent context loss; cause, error rate, exact input size, and correlation with model/thinking effort are unverified until systematically captured.
- OpenAI status at inspection (2026-10-17): public `https://status.openai.com/` shows fully operational; this does not rule out an isolated incident. Status history records previously resolved ChatGPT Work degradation on October 14 and widespread degradation October 15; timestamps and product scopes must be compared to any individual event before attributing cause.
- Official references: `https://help.openai.com/en/articles/9047779-why-is-my-chatgpt-taking-so-long-to-respond` and `https://help.openai.com/en/articles/10169521-projects-in-chatgpt`.

## Distinguish failures before acting

| Code | Observable evidence | Hypothesis/impact | First safe action |
|---|---|---|---|
| AAB-ERR-CHAT-001 | Explicit maximum-length banner | Hard thread-size ceiling | Open a new MAIN thread using GitHub recovery gate; do not attempt to resume same chat |
| AAB-ERR-CHAT-002 | Thinking indicator persists; no terminal banner | Streaming/network/browser/model/service; UNKNOWN root cause | Capture local time, conversation URL, model, elapsed duration, latest successful action; compare fresh short chat without modifying live tasks |
| AAB-ERR-CHAT-003 | Response stops mid-artifact or request reports error | Completion and write side effects UNCERTAIN | Read back repository/artifact state and exact commit; do not repeat mutation blindly |
| AAB-ERR-CHAT-004 | GitHub/connector/tool unavailable | Auth, permission, transient tool or service error; UNKNOWN | Record exact safe error/status and single tool; no credentials, no broadened permission |
| AAB-ERR-CHAT-005 | New thread cannot reconstruct current progress | Stale/absent checkpoint vs memory mismatch | Read GitHub CURRENT_STATE, CAPABILITY_LEDGER, active scope/review; compare live branch revision |
| AAB-ERR-CHAT-006 | Distinct short chats fail under same local conditions | Possible client, network, quota or service issue | Compare another browser/network/model if available; consult status and Support |

## One controlled non-destructive diagnostic comparison

1. A: short, fresh conversation on the user's Android browser, one small read-only question. Record response time and result **only when it naturally occurs**; don't induce excessive tests.
2. B: an existing long but not capped conversation with the same simple question **only if already being used for work**, not to force a freeze. Compare error type and elapsed time; treat model and tool workload as confounders.
3. C: if symptom repeats in multiple short threads, read current `status.openai.com`, check browser/tab reload, available network, device memory pressure, and any visible plan/usage message. Capture actual error and timestamp with zone.
4. For Support if reproducible: provide affected URL (with redaction if sensitive), exact time and timezone, screenshot, model/thinking mode, approximate tabs/memory/network state, which operations ran, and any available request/run IDs. HAR/console logs are optional only if obtainable safely; never send cookies/tokens/passwords or device secrets.

No exact model token ceilings, timeouts, remaining context percentages or throttling thresholds have been established. Do not claim one.

## Three-lane architecture: small bounded work, one durable truth

**Lane A: MAIN — architect/decider.** Only priority selection, owner authority, review verdicts and the next step. Aim for one bounded decision/outcome per fresh chat. A new MAIN conversation begins with `channel/recovery/CURRENT_STATE.json`, `CAPABILITY_LEDGER.md`, `AGENTS.md`, active scope and latest GitHub evidence. Chat memory is advisory only.

**Lane B: ENGINEERING — Grok, GitHub CI, narrowly approved phone-side Codex.** One task ID, one file writer, optional read-only helper agents. Do not paste long source files repeatedly into MAIN; post one GitHub source/checkpoint/handoff and independent CI logs/commit SHA. No implicit work authorization from GitHub comments. Stop at approved scope, don't alter Support-held v0.6/PING.

**Lane C: RELIABILITY/LEARNING — AAB-META-001.** Log incidents and exact failure evidence, update `channel/learning/lessons_v01.json` only after checking source and deduplication, synthesize reusable architecture rules, preserve recovery/incident notes. Existing lesson AAB-L004 covers conversation context exhaustion; this record adds a diagnostic procedure, not a second competing lesson. Keep user-approved scope, no credentials/private chain-of-thought stored.

### Cross-lane handoff contract
Each meaningful handoff is one compact record: project=AAB-001, lane, unique task_id, owner-approved scope, repository/branch/latest commit, observed time UTC, verified artifact/test IDs, outcome (PASS/FAIL/BLOCKED/UNVERIFIED/UNCERTAIN), pending action, next authority, and STOP status. Never confuse an archived file with automatically loaded memory. Large payloads reside only in GitHub.

### Practical context discipline
- Prefer new clean thread for each substantial implementation/audit; MAIN is the coordination thread, not a dump of every screenshot or program log.
- Keep messages and tool runs bounded; avoid screenshots except as evidence of UI-only facts. Upload long source once to GitHub and reference path/commit.
- Write a meaningful checkpoint after milestones, new blockers and before deliberate context switches. Only one authoritative current-state pointer on GitHub.
- Avoid duplicate watches, repeated successful tests, background pollers that merely duplicate GitHub's existing event gate, and unrelated project changes.
- Check evidence freshness by repo, branch, commit, record date and actual environment; stale/conflicting observations do not permit writes.

## Autonomy and subgoal limitations

Current `channel/learning/` implements an evidence-linked lesson ledger, blueprint compiler and tested read-only GitHub CI, **not** continuous self-improvement or always-on auto-documentation. Existing GitHub Actions watches changes to relevant files, but cannot infer conversation-side incidents without a deposited record. Scheduled tasks can inspect the repo periodically, subject to account capability and quota; they cannot guarantee a permanently running ChatGPT browser session or automatic recovery from hidden interrupted reasoning. Prefer event-driven capture plus bounded periodic reconciliation.

## Operational priorities and current project gate

- Preserve proven independent AAB Doctor 18/18 off-device and controller proposal 12/12, and true Grok queue receipt `channel/handoffs/6236560957.json` with Actions `39049184153`. No need to repeat tests.
- Android Doctor runtime has NOT been verified. Latest known phone Python 3.14.6 and Termux `~/aab-queue` are verified; local git SHA not yet reconciled with live remote.
- Do not alter ChatGPT v0.6/PING while Support case 17390055 is under investigation.
- **The original next narrow Android action remains `git rev-parse HEAD` in `~/aab-queue`** to compare with live remote `mc/channel` before sync, but reliability/documentation work can proceed independently.
- The proposed lane split is organizational and does not itself create or run separate AI agents.

## Success criteria for reliability iteration

- A new MAIN chat can reload GitHub state with no need to restate passed AAB milestones.
- At least one future capped conversation resumes safely with no side-effect replay and with a verified repo/branch/test gate.
- A new symptom is recorded with exact timestamp, message, model and context versus guessed root cause.
- AAB-META-001 converts each genuinely new verified failure class into a deduplicated lesson and regression preflight, subject to owner authorization for implementation.
