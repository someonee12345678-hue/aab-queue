# AAB-001 — Durable Operating Rules / MAIN Recovery Protocol v1.0
Date: 2026-10-17
Status: OWNER DIRECTED, project-level governing **operating policy**, not model-wide instructions.
Source: private `someonee12345678-hue/aab-queue` on `mc/channel`.
Companion: repository-root `AGENTS.md` for authorized coding tools.

## On every AAB-001 MAIN conversation or resumed agent session
1. Identify this project and distinguish it from Elite Kit, APCCS, Genesis, legal research and other projects.
2. Fetch `channel/recovery/CURRENT_STATE.json`, `channel/recovery/CAPABILITY_LEDGER.md`, `AGENTS.md` and the latest scope-specific checkpoint. Check actual GitHub repo, branch, revision, dates, and PR #2; never substitute memory for current evidence.
3. Reconcile stale/conflicting records before recommending mutation. Use VERIFIED / REPORTED / UNVERIFIED / BLOCKED; separate implementation from authorization. Keep one next Android-phone action unless the owner requests a broader plan.
4. Continue from the latest passing checkpoint, not from initial setup. Preserve successful tests and the ongoing OpenAI Support v0.6/PING diagnostic hold.
5. When a meaningful change is approved and verified, update the smallest durable checkpoint(s) and read them back. Do not claim persistence from a chat message alone.

## Chosen technology and execution boundaries
- **GitHub:** durable transport, PR #2 comment identity, create-only queue receipts, GitHub Actions CI, planning, checkpoints. Recorded evidence does not automatically authenticate the Grok agent or deliver to ChatGPT.
- **Grok:** programmer/coordinator within separately owner-approved scope. It can post through an existing Cursor connection, but a comment is never a general instruction to start work.
- **Phone-side Codex:** candidate local agent in owner's Android Termux, subject to actual CLI auth/capabilities, scoped approved jobs, local filesystem boundaries and STOP. It is *not* the native ChatGPT event processor and cannot control a private ChatGPT web session merely because it is logged in.
- **ChatGPT:** architecture, safe task decomposition, independent code/evidence verification, decision records. A chat is not a persistent scheduler, and a tool cannot force unattended native ChatGPT messages without a supported trigger.
- **Not selected:** browser fingerprint evasion, Playwright/Chrome stealth, reusing authenticated browser cookies, login bypass, Grok VM login into ChatGPT, self-hosted email infrastructure, arbitrary SSH/RPC/MQTT/tunnel servers as premature infrastructure. They do not repair missing ChatGPT trigger metadata by themselves.

## Order of operations
A. Prefer completed/GitHub-backed work; select the highest-value unfinished objective from the *verified* state. Use built-in GitHub event handling for identity and repeatable, budget-bounded testing. Do not build duplicate bridges.
B. Where safe, run code/tests in the least-cost location: Grok-approved environment for rapid iteration; independent Actions CI for acceptance; phone-side Codex only for genuinely useful local work and only after explicit scoped authorization.
C. Validate receipts, source SHA, branch, exactly-once-minded safeguards and independent review. Missing identity or uncertain API write => BLOCKED/UNVERIFIED, not 'success' and no blind retry.
D. Escalate only actual credential, cost, permission or security choices. Routine engineering details delegated to agents inside approved boundaries.
E. Keep owner informed at checkpoints and update the durable state when needed. No automatic agent permission follows from this operating policy.

## Verified present checkpoint and one next action
- Genuine GitHub handoff queue receipt: `channel/handoffs/6236560957.json`, GitHub Actions `39049184153`; source Grok/Cursor PR #2 comment `6236560957`. Review is a separate record; the immutable receipt still reads PENDING_INDEPENDENT_REVIEW.
- `phone_agent_v01/doctor.py` independently reviewed with 18/18 tests PASS in non-phone Python; Android execution UNVERIFIED.
- Assignment controller proposes only (GitHub Actions `39052656248`, 12/12 tests PASS); **automatic dispatch not implemented**.
- Phone Python 3.14.6 verified, local `~/aab-queue` working branch `mc/channel` reported, Doctor file absent at the last phone check; local HEAD still needs comparison. Earlier Termux `gh auth status` showed not logged in; no `gh` login required for the next read-only step.
- **Next single Android action:** in Termux inside `~/aab-queue`, run `git rev-parse HEAD` only; return the 40-character SHA or screenshot. ChatGPT must compare it to the latest remote before proposing a safe local sync. Do not blindly pull, install, authenticate or execute Doctor.
- These observations are dated, not guaranteed permanent. Re-read the live state and use newer verified evidence where available.

## Truth and limits
- Repository documents are operational references. They cannot directly modify ChatGPT's base model, enforce sandbox permissions, make Grok follow instructions it did not read, or persist automatically into unrelated chats.
- No real records, credentials, paid API upgrades, unapproved event replays, updates to v0.6/PING or broad GitHub permissions.
- When behavior differs from these rules, record exact evidence and amend the relevant repository instructions after authorization; never just rely on a verbal promise to remember.
