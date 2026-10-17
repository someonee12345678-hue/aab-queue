# AAB-001 — Full MAIN Recovery Handoff (2026-10-17 15:32 PDT)

**Status:** CONTINUITY SAVED; engineering not reset. This is a bounded recovery record, not authority for a new Grok/Codex task or phone action.

## Why this handoff exists
The owner-provided Android Chrome screenshots show the explicit **"You've reached the maximum length for this conversation"** message. This is a ChatGPT conversation-size boundary, not proof that a GitHub run, bot, browser, phone or repo has frozen. Other apparent stalls remain unverified until identified by exact on-screen symptom and timestamp. Recovery must use GitHub's durable state, not the unavailable continuation of the old chat.

The owner also provided screenshots of a preceding MAIN recovery account that referenced an uploaded `master architecture record.zip` containing 22 historic screenshots. **This update verified the current authoritative repository architecture and selected direction; it has NOT independently inspected or reconciled those 22 images.** Their general ambition (coordinated agents, specialist workers, persistent project memory, master architect) aligns with this project's recorded architecture, but that is not verification that all old conceptual components are implemented.

## Current independently read source identity
- Private GitHub repo: `someonee12345678-hue/aab-queue`.
- Default branch **literally** `HEAD`; working branch `mc/channel`; PR #2 remains **open and draft**.
- PR #2 head SHA observed in current recovery read: `473315a79c96b9d24b31f688b071839a20cf80b8` (a historical observation, likely to advance when this checkpoint is committed). Always refresh before writing/syncing.
- Authoritative active state: `channel/recovery/CURRENT_STATE.json`.
- Capability/phone facts: `channel/recovery/CAPABILITY_LEDGER.md`.
- Governing operating guidance: `channel/recovery/OPERATING_RULES.md` and repo-root `AGENTS.md`.
- Selected owner architecture: `channel/AAB-001-ARCHITECTURE-DECISION-GITHUB-GROK-PHONE-CODEX-2026-10-17.md`.

## Verified achievements — DO NOT replay
- Python Pocket Task Board app: accepted 8/8 independently, GitHub Actions run `39014190117` success.
- Real Grok/Cursor handoff PR #2 `6236560957`; immutable create-only record `channel/handoffs/6236560957.json` on `mc/channel`; GitHub Actions run `39049184153` succeeded.
- The queue record means **receipt at handoff**, and keeps `review_status: NOT_PERFORMED` by design; ChatGPT's **later separate** independent review PR #2 `6236772954` is the accepted review evidence. These are not inconsistent.
- Grok AAB Doctor v0.1 `phone_agent_v01/`: exact four source SHA-256 checks and independent off-device Python 3.13.5 tests 18/18 PASS; **Android runtime of Doctor UNVERIFIED**.
- GitHub Actions assignment controller v0.1: 12/12 PASS in run `39052656248`; **PROPOSAL ONLY**, auto-dispatch false.
- AAB architectural learning source and CI `39067220221` SUCCESS; lesson compiler is a proposal generator, not autonomous self-improvement or agent execution.
- Historical prior v0.3/v0.4 multiworker experiments passed independent functional tests and are preserved.

## Active boundaries / blockers
1. **Android local revision pending.** Phone screenshots previously showed Termux in `~/aab-queue`, Python **3.14.6**, local branch `mc/channel` and missing local `phone_agent_v01/doctor.py`. No full `git rev-parse HEAD` on-phone SHA has been verified. Do not assume local and remote branches match or blindly pull.
2. Current `gh` CLI authentication on phone UNVERIFIED; earlier `gh auth status` showed not logged in. This is separate from Codex login and GitHub Actions token permissions. Do not ask user to authenticate as a prerequisite for the read-only local SHA check.
3. Native **automatic ChatGPT wake → independent review → feedback to Grok** is NOT verified. A durable GitHub receipt is not a wake guarantee, work authorization, or completion.
4. Existing v0.6 and PING processors remain under **OpenAI Support case 17390055**; do not replay historical source comment 6226123463, mutate those tasks, or infer a root cause without execution traces.
5. Grok's VM is not an authorized place to keep the owner's passwords/tokens or real legal data. No paid APIs, browser stealth, session-cookie reuse, or unauthorized phone UI automation.

## Conversation exhaustion mitigation — mandatory on subsequent AAB MAIN work
- Use three **logical** lanes: MAIN architect/decisions; ENGINEERING Grok/CI/scoped phone Codex; RELIABILITY incident evidence and lessons. They do not imply three active autonomous background bots.
- GitHub is the durable source; ChatGPT conversations are ephemeral working surfaces. Minimize giant screenshot/source dumps into MAIN; save source, evidence, decisions, and source IDs in GitHub.
- On **each meaningful verified milestone, changed blocker, user-approved architectural decision or before switching chats**, save or update a concise versioned GitHub handoff with source IDs and the next action; then read it back. At long conversation/screenshot-heavy periods, proactively offer a fresh MAIN and carry the pointer, without promising exact advance warning or an exact remaining context percentage.
- All handoffs must include repo/branch/revision/time, validated tests, VERIFIED vs REPORTED vs UNVERIFIED, protected boundaries, STOP/approval state, and **single next safe action**.
- If a response seems frozen without the explicit length banner, record URL, screenshot, model/effort, timestamp, last verified side effect, and outcome; inspect GitHub before retrying mutation. Do not misdiagnose the cause or repeat one-time comments.
- For **AAB-ERR-CHAT-001**, open a fresh MAIN and load `AGENTS.md`, `CURRENT_STATE.json`, `CAPABILITY_LEDGER.md`, `OPERATING_RULES.md`, this file and latest GitHub runs/PR; skip passed tests.
- Continue with evidence-based refinements in `channel/learning/`; don't duplicate the existing AAB-L004 lesson on chat limits.

## One next owner action — PHONE / TERMUX
Open Termux, confirm the shell is in `~/aab-queue` (as last observed), and **enter exactly this one read-only command**:

```sh
git rev-parse HEAD
```

Send the full 40-character Git SHA or screenshot back to MAIN. ChatGPT compares it against the **fresh live remote** `mc/channel` HEAD, then chooses the smallest safe sync plan to bring the archived Doctor onto the phone. Do **not** run Doctor yet; do not run `git pull`/`git push`, log in to `gh`, reinstall Python, paste the MAIN recovery script into Bash or execute new Codex tasks.

## Copy-ready MAIN resume text
MAIN — Resume AAB-001 from the private GitHub repo `someonee12345678-hue/aab-queue`, work branch `mc/channel`, default `HEAD`, draft PR #2. Read `AGENTS.md`, `channel/recovery/CURRENT_STATE.json`, `channel/recovery/CAPABILITY_LEDGER.md`, `channel/recovery/OPERATING_RULES.md`, and `channel/recovery/AAB-001-FULL-MAIN-HANDOFF-2026-10-17-1532-PT.md`, then compare live branch SHA and new events. Preserve all passing tests, queue receipt 6236560957, separate independent Doctor 18/18 review comment 6236772954, proposal-only controller 12/12 and architecture GitHub+Grok+phone Codex. Chat-length exhaustion AAB-ERR-CHAT-001 was confirmed, not GitHub failure. Do not modify Support-held v0.6/PING, replay comments, repeat passed tests or use browser stealth. Next ONE read-only phone action: `git rev-parse HEAD` inside `~/aab-queue`; reconcile with current remote before sync or Android Doctor execution. Clearly report what is verified versus unverified.

**Do not paste this MAIN recovery text into Termux.**
