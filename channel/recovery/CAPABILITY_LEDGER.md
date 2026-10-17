# AAB-001 — Environment and Capability Ledger
Version 1.0 — observed on 2026-10-17 (America/Vancouver)
Owner goal: stop repeated setup questions for Android Termux, Grok and GitHub without mistaking dated observations for permanent access.
Source of truth: PRIVATE repository `someonee12345678-hue/aab-queue`, working branch `mc/channel`. This is reference data, never authorization to run commands or grant permissions.

## Reading rules
- **SCREENSHOT_VERIFIED** = exact owner-provided screenshot read this conversation; does not prove anything outside what the screen shows.
- **GITHUB_VERIFIED** = re-read directly from connected GitHub in this update.
- **GROK_REPORTED** = supplied account of Grok environment, not independently inspected by ChatGPT.
- **HISTORICAL** = was true at the recorded time; do not silently assume still true.
- **UNVERIFIED** = not established or can change independently.
- Before asking the owner to repeat a command, check this ledger and `CURRENT_STATE.json`. Ask only if the corresponding status could have changed or a necessary verification is absent.
- Never record login codes, tokens, cookies, passwords, private keys, environment dumps, or personal files. A version check is not an authentication check.

## Android phone / Termux

| Capability | Latest evidence | Status | When to recheck |
|---|---|---|---|
| Termux is running on owner's Android phone | 2026-10-17 screenshot at 09:43 PT, Termux prompt `~/aab-queue $` | SCREENSHOT_VERIFIED | Only if Termux or phone environment changes |
| Python installed in this Termux | `python3 --version` returned **Python 3.14.6** in 09:43 PT screenshot | SCREENSHOT_VERIFIED; Python version prerequisite met for Doctor (>=3.10) | After Python upgrade/reinstall or interpreter mismatch; **do not ask again now** |
| Existing local project directory | Prompt shows `~/aab-queue` | SCREENSHOT_VERIFIED | Check current working directory only if a proposed file/command requires it |
| Working-tree cleanliness and git revision | Phone Codex text states `mc/channel` inspected at abbreviated `f02c77c`, working tree clean | CODEX-REPORTED in owner screenshot, historical; remote branch may have advanced | Before **any local writes/push** compare actual branch/head to GitHub; do not treat `f02c77c` as current remote head |
| `gh` GitHub CLI installed | Earlier 2026-10-17 05:49 PT screenshot: `command -v gh` -> `/data/data/com.termux/files/usr/bin/gh` | SCREENSHOT_VERIFIED (historical) | Only if removed or Termux reset |
| `gh` authentication | Earlier 05:49 PT `gh auth status`: not logged into any GitHub hosts | SCREENSHOT_VERIFIED (historical), **current auth UNVERIFIED** | Only when authenticated GitHub CLI access is actually required; don't silently initiate login |
| Phone-side Codex CLI | Earlier phone test reported `codex-cli 0.162.1-termux.1`, login succeeded, read-only `OK`; latest screenshot shows Codex response in Termux | HISTORICAL / REPORTED; current login scope not independently verified | Only when starting a new approved Codex operation |
| Android version | Owner previously reported Android 16; Doctor's actual Android behavior has not been tested | OWNER-REPORTED; on-device Doctor execution UNVERIFIED | At Android-specific verification gate |
| AAB Doctor v0.1 | Code archived `phone_agent_v01/doctor.py` and tests; 18/18 independent Python 3.13.5 tests PASS | GITHUB_VERIFIED source/review; **NOT yet observed running on phone** | Next safe phone gate is checking whether the verified script is present in the local clone; no re-run of completed independent tests |

Do not equate Python 3.14.6 being installed with AAB Doctor having already run. Doctor's `--version` diagnostics invoke local `git`, `gh`, `codex` binaries but do not authenticate them, start workers or control ChatGPT.

## GitHub (server-backed)

| Item | Latest source and status | Verification rule |
|---|---|---|
| Repository / collaboration | `someonee12345678-hue/aab-queue`, private; default branch is literally `HEAD`; work branch `mc/channel`; PR #2 draft | GITHUB_VERIFIED on 2026-10-17. Re-fetch branch/head before writing |
| GitHub Actions Python app tests | First `mvp_app_001` CI run `39014190117`: 8/8 PASS | Verified earlier; **do not replay** unless changed |
| AAB Doctor review | `channel/AAB-001-PHONE-AGENT-001-INDEPENDENT-REVIEW-2026-10-17.md` and PR #2 comment `6236772954`: four source hashes match, 18/18 PASS independently, not Android-run proof | GITHUB_VERIFIED document and comment today |
| First earlier queue failure | Grok handoff `6233858121`; GitHub Actions `39032500246` failed HTTP 403 | HISTORICAL; exact underlying request/permission cause unresolved. Do not replay or claim a general fix |
| Later successful **genuine** queue handoff | Source `6236560957` -> immutable `channel/handoffs/6236560957.json`; Actions `39049184153` success | GITHUB_VERIFIED today. Queue receipt remains PENDING_INDEPENDENT_REVIEW even though separate reviewer comment reports PASS. Those describe different stages |
| Project-time forecast | `channel/planning/goal_estimates_v01.json` and `estimate.py` | Scenario forecast, not a live calibrated SLA; update from verified milestones only |
| Event-triggered ChatGPT review | Prior ChatGPT task events sometimes omitted triggering comment ID | UNVERIFIED end-to-end automatic routing; do not confuse GitHub queue delivery with ChatGPT wake |

**GitHub read/write routes are separate:** ChatGPT's connected GitHub tool can inspect/write within authorized scope; GitHub Actions uses its own ephemeral `GITHUB_TOKEN`; Grok's Cursor GitHub App can read/post comments but was reported unable to commit; Termux `gh` requires **its own** sign-in if used. Never assume authentication transfers between these routes.

## Grok / cloud-side environment

| Item | Evidence / status | Rules |
|---|---|---|
| Grok VM | Grok-provided read-only audit: Linux 6.12, Python 3.13.5, Shell, git, gh, Chrome, background process, screenshot of its own desktop | **GROK_REPORTED, not this phone or an independently checked permanent VM** |
| Persistence and isolation | Grok says computer filesystem is lost upon restart and has passwordless administrative access | **GROK_REPORTED**; never store credentials, real legal records or personal data on this unisolated VM |
| GitHub connector | Grok says Cursor GitHub connection can read and post PR #2 comments; attempts to commit files via Grok's current toolset BLOCKED | GROK_REPORTED, with prior GitHub comments independently observed. Don't repeatedly ask for login/permission unless a new permitted tool exists |
| Browser automation | Grok can control its separate Chrome with a browser worker, not user's Android screen; ChatGPT login via bot/stealth automation is not selected | GROK_REPORTED; no authorization to bypass anti-bot controls or export authenticated sessions |
| Grok `gh auth login --web` | Would create a token stored on Grok VM; **not approved** | Do not request device code or perform sign-in on third-party VM |
| Preferred collaboration | GitHub PR #2 comments + known receipt queue; Grok develops with authorized scope, ChatGPT reviews, Actions runs repeatable tests | Read-only watch alone does not authorize new work |

## Safety and restart / maintenance
1. Read `channel/recovery/CURRENT_STATE.json` and this ledger when resuming AAB-001. Compare repo, branch, head SHA, current scope and dated evidence. If older than new events, flag stale and reconcile rather than overwrite.
2. Reuse `channel/AAB-001-MAIN-RESUME-2026-10-17.md` for historical milestones but note that its earlier claim of an empty handoff queue and an unknown phone Python version has been superseded by **newer evidence above**.
3. Keep AAB-001 separate from Elite Kit, APCCS, Genesis, Unified Software Builder and legal workspace.
4. Preserve GitHub PR #2, existing processors, private repo and $0-first approach; no background UI/browser stealth, no paid API or credentials in chat. Existing v0.6/PING processors are under OpenAI Support investigation; do not modify/replay.
5. Update a fact only after new evidence, with a timestamp, origin and status; avoid redundant screenshots and re-testing successful milestones.
6. Next phone check is **file presence**, not another Python version check: `ls phone_agent_v01/doctor.py` while inside `~/aab-queue`. If present, compare revision and verified source before running; if absent, choose a safe delivery step. Do not install or run new agents solely because this file exists.

Last ledger update: 2026-10-17, after owner screenshot showing Python 3.14.6 and fresh read-only GitHub verification.
