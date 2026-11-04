# AAB-001 — MAIN Recovery Checkpoint (2026-10-17, 15:47 PDT)

Status: RECOVERED FROM GITHUB; conversation length-limit interruption confirmed by owner screenshots. Other reported stalls/crashes remain UNVERIFIED and should not be assigned a cause without error evidence.

## Identity and verified durable state

- Project: AAB-001 only. Private repository: `someonee12345678-hue/aab-queue`. Default branch literally `HEAD`. Working branch `mc/channel`. Draft PR #2 open; do not merge.
- Latest remote `mc/channel` SHA observed via PR #2 at this check: `a2ed0ceea78a96858ebd802cbeeb171875bdb5c3`. This is a *pre-checkpoint-write observation*; re-fetch the current SHA at next read before any phone sync.
- Verified real Grok/Cursor handoff #6236560957 preserved in immutable queue `channel/handoffs/6236560957.json`; Actions run 39049184153 PASS. Receipt status is PENDING_INDEPENDENT_REVIEW by design at creation time.
- Later independent ChatGPT review #6236772954: AAB Doctor v0.1 four files saved under `phone_agent_v01/` with matching hashes; 18/18 off-device tests PASS. This does NOT verify Doctor execution on Android.
- Pocket Task Board 8/8 PASS. Assignment controller v0.1 12/12 PASS, PROPOSAL ONLY, no automatic dispatch. Architectural learning Actions run 39067220221 SUCCESS.
- Prior v0.6/PING ChatGPT processors remain on Support hold, case 17390055. No replay or modification. End-to-end unattended ChatGPT↔Grok review loop UNVERIFIED.

## Incident and stability

- Owner screenshot includes explicit maximum conversation length banner in former MAIN. This is AAB-ERR-CHAT-001 (thread exhausted), not evidence of a broken GitHub repo or disabled agent.
- Owner also reports apparent early crashes/stalls. Their specific causes, recurrence rate and whether a new tab changes them are UNVERIFIED.
- Use three logical work lanes: MAIN for short decisions and owner guidance; ENGINEERING for GitHub/Grok/CI/scoped phone Codex; RELIABILITY for error evidence and documented lessons. No new bots are implied.
- Before further work, read `AGENTS.md`, `channel/recovery/CURRENT_STATE.json`, `CAPABILITY_LEDGER.md`, `OPERATING_RULES.md` and the latest review. Short scoped operations, save checkpoints at meaningful changes, read back writes, never repeat tests known to pass.

## Phone context and next ONE action

- Previously verified Android Termux shell in `~/aab-queue` on branch `mc/channel`, Python 3.14.6. The local `phone_agent_v01/doctor.py` was absent at last observed check. The local full git commit SHA is not yet observed. Historical `gh auth status` was not logged in; gh is NOT needed for this check.
- **NEXT:** In Termux, when at `~/aab-queue`, enter ONLY `git rev-parse HEAD` and send the complete 40-character SHA (or screenshot) to MAIN.
- The assistant then compares that local SHA against a fresh current GitHub `mc/channel` SHA and chooses the narrowest safe sync plan. No blind `git pull`, no auth, no Doctor run, no new Codex job yet.
- Paste recovery text into ChatGPT, **not Termux Bash**.

## Boundaries

No secrets, unapproved GitHub changes, paid APIs, browser stealth/ChatGPT bot-detection bypass, actual legal data in prototype, task replays or changes to v0.6/PING/PR #2. The owner-selected stack is GitHub + Grok + authorized phone-side Codex + ChatGPT independent review.

Recorded as a small durability checkpoint because owner reported chats reaching their limits and requested earlier, more granular state preservation.
