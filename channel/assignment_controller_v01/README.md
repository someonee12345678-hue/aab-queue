# AAB-001 — Automatic Assignment Controller v0.1

**Status: proposal engine, not an autonomous executor.** Source of truth is the private GitHub repository `someonee12345678-hue/aab-queue`, branch `mc/channel`. Prepared 2026-10-17 after owner requested preservation and an automatic assignment controller.

## Why this component exists

The system must continue safely after ChatGPT conversation exhaustion, Termux file drift, Grok VM reset, missed event, or a processor receiving incomplete metadata. The controller reads a durable checkpoint and a bounded backlog; it deterministically chooses the next eligible proposed task and records evidence. It does not mistake GitHub comments for authorization, infer completed work from AI text, or replay historical events.

## Inputs and outputs

- Inputs: `channel/recovery/CURRENT_STATE.json` (previously verified project checkpoint) and `channel/assignment_controller_v01/BACKLOG.json` (status, priority, dependencies, STOP).
- Output: `assignment-controller-report.json` plus a GitHub Actions job summary and seven-day downloadable artifact. Every result includes project identity, observed Git SHA, selected task, evidence references and the explicit flag `dispatch_enabled: false`.
- GitHub Actions: `.github/workflows/aab-assignment-controller.yml`, activated only by a trusted push to `mc/channel` changing this controller/backlog or the workflow. Read-only `contents: read`, one short job; no scheduled polling, no writes to GitHub, no comment posting, no GROK/Codex invocation.
- STOP: set `stop_requested: true` in the backlog through a separately approved change; the next run reports STOPPED. No persistent worker or task exists to stop in this v0.1 component.

## Guardrails

A task marked DONE must include verifiable evidence, but the controller **does not independently authenticate** the listed evidence or an approval claim; it reads these strings as data. It only proposes a next action. The future dispatcher, if authorized, must independently authenticate owner approval, source revision, safety boundaries and durable claim/lease state. Do not automatically execute `suggested_owner_action` as a shell command: it is owner guidance, not computer instructions.

Valid roles: OWNER, GROK, CHATGPT, PHONE_CODEX, GITHUB_ACTIONS. Tasks involving changing code, a remote write, permissions or credentials must have a separate explicit authorization, not a backlog flag. The existing v0.6/PING/PR-watch ChatGPT tasks remain untouched. Repository `HEAD` is literally the default branch and must not be silently replaced with `main`. Keep PR #2 draft, and all personal/legal records out of the experimental project.

## Initial actual state

- GitHub recovery checkpoint, capability ledger, AAB Doctor source and 18/18 independent reviewer tests exist; the Doctor was **not** verified running on Android.
- 2026-10-17 10:02 PT screenshots: Termux Python 3.14.6 PASS, shell in `~/aab-queue`, working branch `mc/channel`, local `phone_agent_v01/doctor.py` missing. Pasting `MAIN — Resume ...` into the shell caused harmless `command not found` errors; that text belongs in a new ChatGPT chat, not the Linux command line.
- First proposed task is a single **read-only local revision check** using `git rev-parse HEAD`. The user can send the result to MAIN so the assistant can compare it with live GitHub HEAD before authorizing a safe sync. Do not blindly pull while the local revision is unknown.
- GitHub previously recorded successful create-only queue receipt `channel/handoffs/6236560957.json` and independent Doctor review. Immutable queue receipt still reads `NOT_PERFORMED`, while separate review comment `6236772954` establishes a later review stage; these are distinct facts.
- AAB Doctor source exists in the remote repo but is not auto-mounted in local Termux. `gh auth status` was previously not logged in; GitHub CLI authentication is separate from Codex login and not necessary for a read-only local SHA check.

## Engineering/testing

The controller uses Python standard library and has no import of HTTP/network, git subprocess, Codex APIs or external executing hooks. It fails closed on wrong repo/branch, stale/unverified checkpoint, invalid task records, circular/missing dependencies, unsupported mode, ambiguous STOP and attempted automatic-dispatch settings.

From this directory on an approved Python host:

```sh
python3 -m unittest -v test_controller
python3 controller.py --state ../recovery/CURRENT_STATE.json --backlog BACKLOG.json --output assignment-controller-report.json
```

Those commands are for maintainers / GitHub Actions, **not a request for the owner to paste documentation into Termux**. Controller output is a proposed assignment, not evidence that a task was executed, a GitHub event delivered or the phone received a notification.

## Next deployment boundary

Once the read-only controller itself passes CI, a later **separately approved** phase could consume signed/verified owner-authorized jobs on the phone, use an explicit STOP and retry limits, and send authenticated completion receipts. No automatic Grok/phone/ChatGPT dispatch has been implemented or authorized by this v0.1 controller.