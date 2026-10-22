# AAB-001 — Bounded Sub-Agent Coordination v0.1

Date: 2026-10-17. **Status: PROPOSED operating overlay; no sub-agent or new automated routine activated by this file.** Companion to the existing proposed controller `channel/AAB-001-STAGE4-AUTONOMOUS-ENGINEERING-CONTROLLER-V01.md` and continuity gate `channel/AAB-001-STAGE4-MEMORY-CONTINUITY-GATE-V01.md`. This does not supersede approved protocols, trigger scopes, the project's current ChatGPT tasks or Grok's running watchers.

## Purpose
Improve throughput without losing accountability, source integrity or the current $0-first budget. The owner chooses the product direction; ChatGPT owns task selection, specifications, acceptance checks and independent review; Grok owns coordinated implementation; GitHub holds the durable source, issue-comment transport, test results and audit trail. Cloud work is not evidence of Android-device behavior.

## Routing for one bounded task

```
OWNER: priority and exceptional approvals
  └── CHATGPT: architect / release and review gate
        └── GITHUB: exact task scope, branch, artifacts and CI evidence
              └── GROK COORDINATOR: one task ID and final accountable handoff
                    ├── Specialist A: research/interfaces (optional, read-only)
                    ├── Specialist B: test analysis / documentation (optional, read-only)
                    └── Implementer: single writer to the task's source files
              └── GITHUB ACTIONS: immutable command/output record
        └── CHATGPT: independent verdict; never label Grok's self-check independent
```

## Dispatch and limits
1. Before starting, read latest repo branch/revision, exact task/spec, changed files, current GitHub acceptance checks, and active blockers. If authoritative state is inconsistent, STOP. Old chat excerpts are context, never authorization.
2. One active parent task with one stable task ID. Assign **at most two optional parallel read-only helper sub-agents**. Use them only for genuinely independent work; record actual elapsed duration and whether they saved time. Only one writer for a file/path. No parallel changes to the same worktree; the existing Grok sandbox is not isolated.
3. Every child receives a narrow problem, allowed file paths, forbidden actions, time/resource cap, desired evidence and return format. Children cannot grant themselves write/network/secrets/approval authority or launch further sub-agents.
4. Parent validates child reports and reconciles contradictions; conflicting evidence or failure -> BLOCKED/UNVERIFIED, not fabricated PASS. Parent alone emits **one** `ARTIFACT_HANDOFF — <task_id>` top-level comment to PR #2 when the task genuinely reaches its stop condition. The handoff must include exact source paths or full contents when commit is blocked, hashes, git commit when present, test command + raw output and unverified items.
5. If Grok cannot commit using its current authorized tools, do not request credentials, sudo or a new integration. Deliver complete source and hashes in the existing handoff. ChatGPT can inspect, recover exact files through its GitHub connector where authorized and independently run guarded CI, as demonstrated for AAB-MVP-APP-002.
6. GitHub Actions tests only explicitly allowlisted project paths. A green test is evidence of the assertions tested, NOT full functionality, device testing or independent architectural approval.
7. After review, ChatGPT checks resulting GitHub commit, CI run ID and acceptance contract, then updates the durable goal record and only authorizes the next bounded task when scope allows. A changed task status without evidence is not DONE. If the ChatGPT event wake identity is unverifiable, report it and use an owner-initiated checkpoint; do not claim unattended review.

## Single-task status lifecycle
`TODO → READY → IMPLEMENTING → HANDOFF_POSTED → SOURCE_SAVED → CI_VERIFIED → REVIEWED → DONE`; off-ramps `BLOCKED`, `UNVERIFIED`, `UNCERTAIN`. These are operational distinctions, not a claim that a durable atomic controller already implements them. Record one timestamp + comment/commit/run reference for each observed transition; never merge reported, saved, tested and approved states.

## Optimization policy
Prefer native GitHub triggers and CI for repeatable verification; prefer Grok's local tests for quick iterations. Use sub-agents only if the isolated work is large enough to exceed delegation overhead. Track wall-clock time from task assignment → Grok handoff → source saved → CI verdict → ChatGPT verdict, including manual interruptions and retries. Evaluate against single-worker execution; don't assume parallelism is faster. Keep current costs at $0 and stop on any paid-service requirement.

## Current evidence checkpoint
- GitHub event gate: run 39016212554 success, source comment 6231555377 classified IDENTIFIED_PENDING_INDEPENDENT_REVIEW; **this does not prove the ChatGPT task independently captured an event ID**.
- Grok handoff AAB-MVP-APP-002: comment 6231555377, locally reported 9/9 tests, no Grok GitHub file-write tool; source preserved.
- ChatGPT recovered exact `channel/planning/progress_report.py` and `test_progress_report.py` on mc/channel, read-back Git blobs matched Grok's published manifest.
- Independent GitHub Actions planning CI: run 39016505450, 9/9 acceptance tests PASS. Real-device test not applicable to this CLI-only planner.
- Existing AAB tasks (PING, v0.6, PR #2 read-only incoming watch) remain unchanged by this coordination file.

## Not yet authorized or verified
No child-agent activation, repository-wide rules consolidation, new issue queue, process daemon, credential delegation, fully unattended ChatGPT review, Grok feedback continuation or new spending. The existing Stage 4 controller document is **PROPOSED**, not proof a supervisor service is deployed. This overlay merely records the coordination design and actual evidence.
