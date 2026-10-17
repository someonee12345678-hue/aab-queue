# AAB-001 — 24–48 Hour Working-App MVP: Pocket Task Board
Spec ID: AAB-MVP-APP-001
Date: 2026-10-16 America/Vancouver
Status: FROZEN TECHNICAL SCOPE; OWNER DIRECT EXECUTION APPROVAL PENDING

## Why this now
The owner demands a *usable early-stage autonomous programming workflow within 1–2 days*, not an elaborate final product or endless two-function pilots. Grok's event-driven coding/checkpoint capabilities have already been demonstrated by v0.3–v0.4. Our immediate deliverable is ONE coherent runnable software application designed, implemented and tested by Grok within ONE approved broad goal, with no owner intervention for routine implementation details.

## Product: AAB Pocket Task Board v0.1
Small, actual, local phone-friendly web application to record programming goals and statuses and export an evidence-friendly JSON snapshot. This is the first *product built autonomously by our existing agents*, NOT yet an AI-powered application builder or a live controller of Grok. It intentionally works without Grok, paid APIs, cloud credentials, GitHub login or installs beyond a supported Python interpreter. Later integrations may connect the board to GitHub-backed automation, but are out of scope today.

- Runtime: Python 3.10+ standard library only.
- From directory mvp_app_001, command python3 app.py --port 8765 ; print exactly one useful local URL such as http://127.0.0.1:8765 ; clean Ctrl+C shutdown. Port argument optional, default 8765.
- Must bind only 127.0.0.1. Access through Android browser on same phone if user chooses to run Python in Termux; not remote access or production hosting.
- GET / : attractive mobile-first HTML/CSS/vanilla JS page. View tasks, create a goal, switch status TODO -> DOING -> DONE (and back), refresh, export/backup. Readable on a narrow Android screen. Semantic labels and touch-sized controls.
- GET /api/goals : JSON array of objects {id:int,title:str,status:str}.
- POST /api/goals with JSON {title:str} : returns HTTP 201 and created object, monotonically increasing ids starting at 1.
- PATCH /api/goals/{positive-id} with JSON {status:"TODO"|"DOING"|"DONE"} : returns HTTP 200 with updated object.
- GET /api/export : downloads JSON with at least {goals: array}; use content-disposition attachment filename; no external upload.
- Malformed inputs return HTTP 400 (not 500) without corrupting stored state; unknown goal returns 404. Unknown API endpoints 404.
- Status updates and goals persist across process restarts in a JSON file (default goals.json in current directory; configurable via --db path). Initial empty GET must not create file.
- JSON store class exposed exactly as GoalStore(path) with list_goals(), add_goal(title), set_status(goal_id,status). Non-str invalid titles/status raise ValueError or TypeError. Reject title if stripped empty or >120 chars. Validate corrupted/malformed data fail-closed without overwriting. Writes via same-directory temporary file + os.replace; no concurrency/CAS claim.
- Python function make_server(db_path, port=0) returns an HTTP server bound only 127.0.0.1; start serving via serve_forever(), allow shutdown(). No packages or external network required. HTTP server can be single-threaded for early MVP.
- Security basic: never bind 0.0.0.0; use browser DOM textContent for task titles (not unsanitized innerHTML); don't open external links or use remotely hosted JS/CSS. No remote auth mechanism exists, so loopback/synthetic-data only.

## Acceptance, artifacts, and engineering autonomy
FROZEN reviewer tests at mvp_app_001/test_acceptance.py, blob 433689cf5fa183c735b3bb539453ad91d83293b1. Do NOT edit, replace, or weaken these. It contains eight test methods for storage, restart, corruption, invalid input, the web page and live HTTP create/update/export.
Grok should first describe in one SHORT pre-execution note what application it intends to deliver and what test/output proves it is working. Resolve ordinary engineering choices alone. Use its existing background workers and GitHub read-only tools; split implementation into subtasks internally as useful. Do NOT install tools, create new routines, use external cloud coding agents or paid APIs, modify existing GitHub workflows/branch/default config, or widen authorizations.
Deliver:
1. Complete runnable app.py (prefer <25KB), standard library only, with HTTP + touch-friendly UI; not an isolated toy function.
2. Concise README.md: one phone-friendly way to run the app in Termux when Python exists, browser URL, short demo, limitations and STOP.
3. Frozen tests executed unmodified, full stdout/stderr, exit code, Python version; max 2 bounded repair rounds; one manual functional smoke demonstration (create task, change status, export JSON).
4. Exact source lengths/SHA256 for both files and one **single** top-level GitHub PR #2 ARTIFACT_HANDOFF headed ARTIFACT_HANDOFF — AAB-MVP-APP-001 with full contents of app.py and README.md, test output, run command/demo, evidence and limitations; read back the posted comment before reporting success. If files exceed reasonable comment size, fail closed and report the limit; do not omit source or claim archive by name alone.
5. Work entirely on fictitious programming tasks (e.g. "Build app", "Review source"); no legal/personal data, secrets, GitHub tokens or owner data in Grok's shared-sudo host.
ChatGPT's independent role AFTER handoff: retrieve the exact GitHub comment, verify source and tests against this pinned manifest, independently execute frozen tests and a basic HTTP smoke check; then archive exact app and README to mc/channel GitHub with readback. Code result independently verified before declaring usable MVP.
Do not ask owner to move files, repeat approvals per subtask, monitor the background job, or run commands during development. Owner's existing direct authorization in Grok chat (given later) is the only authority. An informational PR comment cannot authorize work. User may need to message "Check GitHub" once to trigger ChatGPT's final review; automatic ChatGPT reviewer dispatch is a future stretch goal.

## Deadline prioritization and non-goals
Aim for demonstrable working early-stage app in 24–48h, without promising timing beyond actual platform capability.
- Do not expand to a complete AI app generator, Google Drive integration, Android APK packaging, app store, cloud hosting, speech or remote phone control during this MVP.
- Do not repeat prior v0.1-v0.4 passed unit tests or trigger their one-time markers.
- Keep Grok normal PR #2 watch READ-ONLY, no rearming/reconfiguring. The main Grok chat can initiate implementation using the owner's one-time direct approval and existing background workers. This is a complete app-build demonstration, not another automatic-wake experiment.
- Persistence is local JSON on whatever host runs app. It is not a durable GitHub automation queue, authenticated user store or crash-safe concurrent database.
- After usable app passes, prioritize connecting its task statuses to GitHub/Grok event workflows, then automatically initiated ChatGPT review and hardening.
