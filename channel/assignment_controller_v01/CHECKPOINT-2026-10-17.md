# AAB-001 — Assignment Controller v0.1 Verified Checkpoint

Recorded: 2026-10-17 10:11 PT / 17:11 UTC. Project: AAB-001. Private repo: `someonee12345678-hue/aab-queue`. Working branch: `mc/channel`; default branch literally `HEAD`. Existing draft PR #2, v0.6/PING/watch processors and queue receipts were not modified for this scope.

## SAVED / VERIFIED

1. `channel/assignment_controller_v01/controller.py` — deterministic standard-library decision engine. GitHub blob `bec8899ef62ad9142342b50f5dd79d20b24625ab`.
2. `channel/assignment_controller_v01/test_controller.py` — twelve isolated acceptance checks, GitHub blob `5c5d5c64490585023eb388b40bc7c9cec567ae6c`.
3. `channel/assignment_controller_v01/BACKLOG.json` — evidence-bearing explicit goal order; current top is one phone read-only revision check; GitHub blob `54f9a667279c9ec3b2bae314993894ace0121da3`.
4. `channel/assignment_controller_v01/README.md` — architecture and safe phone recovery.
5. `.github/workflows/aab-assignment-controller.yml` — push-event-driven proposal workflow on `mc/channel`, read-only token; initial workflow commit `fd9d1a661876418fe8709f1febc93be9241d8d20`.
6. **GitHub Actions run [39052656248](https://github.com/someonee12345678-hue/aab-queue/actions/runs/39052656248): SUCCESS**, job `117454201344`. Independent GitHub logs: **Ran 12 tests ... OK**. Proposal report: `PROPOSED_NOT_DISPATCHED`, selected `AAB-PHONE-REV-001`, `dispatch_enabled: false`, `agent_executed: false`.
7. GitHub Actions output artifact **12107944083**: `aab-assignment-proposal-39052656248` (7-day retention); after artifact expires the durable source/backlog/checkpoint and test run metadata remain on GitHub. The artifact is not the authoritative project record.

## RECOVERED CONTEXT — IMPORTANT

Owner Termux screenshots 2026-10-17 10:02 PT:
- Python `3.14.6` runs in Termux; do not recheck a passed prerequisite.
- `~/aab-queue` shell is on local `mc/channel` (`git status -sb`), with no visible changed files.
- `ls phone_agent_v01/doctor.py` returned NO SUCH FILE LOCALLY, even though that source is saved and independently reviewed on remote `mc/channel`. This is **phone-local source availability unknown/stale**, not project data loss. No `git pull` or `git fetch` has been approved or run during this checkpoint.
- Owner pasted the **chat prompt** `MAIN — Resume AAB-001 ...` into Termux Bash and got `MAIN: command not found`, etc. This does not damage GitHub. Recovery prompts belong inside a NEW ChatGPT chat, **not** Termux terminal.
- Next single phone-safe action: `git rev-parse HEAD` entered **alone** in Termux. Reply with its 40-character output in MAIN. ChatGPT then compares the local commit to the current GitHub branch before permitting any pull or source execution. No credentials or internet needed for this read-only local check.
- The AAB Doctor's remote source plus 18/18 reviewer tests remain a **separate verified checkpoint**. Android runtime Doctor not yet confirmed.

## CONTROLLER SAFETY/OPERATION CONTRACT

- Trigger: trusted GitHub push on controller/backlog/workflow paths; no timers, no personal browser automation.
- Behavior: verify repo/branch and recovery state; reject duplicate IDs, bad evidence for DONE, unknown/cyclic dependencies, invalid STOP, wrong runtime revision/branch and any attempt to enable automatic dispatch; choose one eligible item by priority.
- Output is a *proposal only*, not a Grok or phone Codex command, not owner-authenticated work authorization. No GitHub comments, status updates, external writes, arbitrary code execution, token exposure, device access or changes to existing event processors.
- Actual automatic dispatch + trusted owner approval, phone isolation/battery constraints, durable claims and idempotent completion still require independent engineering and separate scope authorization. `BACKLOG.json` cannot certify its own authorization.

## Error classification

`AAB-ERR-PHONE-008`: Android on-device source readiness UNVERIFIED because the local Doctor file is missing. No evidence of losing remote source. `AAB-ERR-STATE-003` must not be asserted until a real revision conflict is verified.

## Resume instruction for a new MAIN chat

Read `channel/recovery/CURRENT_STATE.json`, `channel/recovery/CAPABILITY_LEDGER.md`, and this checkpoint on `mc/channel`; compare the current GitHub head and known reviewer evidence. Do not repeat passing tests or recreate successful GitHub files. Continue from the single read-only Termux revision command, then make one evidence-driven decision about local source sync.

**Stop conditions:** any mismatch in branch/revision or approvals, uncertain external write, altered protected tasks, or lack of supported device isolation. Owner STOP always supersedes assignment proposals.