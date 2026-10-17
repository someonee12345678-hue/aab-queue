#!/usr/bin/env python3
"""AAB-001 durable, deterministic automatic *assignment proposal* controller.

No network access, agent invocation, subprocess, external writes, or permissions.
Existing state is INPUT DATA, never instructions to execute. Dispatch is disabled.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPOSITORY = "someonee12345678-hue/aab-queue"
BRANCH = "mc/channel"
SCHEMA = "aab-assignment-controller/0.1"
TASK_ID = re.compile(r"AAB-[A-Za-z0-9_-]{1,80}\Z")
STATUSES = {"READY", "IN_PROGRESS", "DONE", "BLOCKED", "CANCELLED"}
ROLES = {"OWNER", "GROK", "CHATGPT", "PHONE_CODEX", "GITHUB_ACTIONS"}
KINDS = {"READ_ONLY", "LOCAL_DIAGNOSTIC", "CODE_CHANGE", "EXTERNAL_WRITE"}
MAX_TASKS = 100


class InvalidState(ValueError):
    pass


def _check(condition, message):
    if not condition:
        raise InvalidState(message)


def decide(state, backlog, *, git_ref=None, git_sha=None):
    """Compute one next step from checkpoint + backlog. Never authorize execution."""
    _check(isinstance(state, dict) and isinstance(backlog, dict), "checkpoint/backlog must be objects")
    _check(state.get("project") == "AAB-001" and state.get("repository") == REPOSITORY,
           "checkpoint project or repository mismatch")
    _check(state.get("working_branch") == BRANCH, "checkpoint branch mismatch")
    _check(state.get("checkpoint_status") == "VERIFIED_PERSISTED",
           "checkpoint is not verified persisted")
    _check(backlog.get("schema_version") == 1 and backlog.get("project") == "AAB-001",
           "backlog schema/project mismatch")
    _check(backlog.get("repository") == REPOSITORY and backlog.get("branch") == BRANCH,
           "backlog repository or branch mismatch")
    _check(backlog.get("controller_mode") == "PROPOSE_ONLY", "controller must remain proposal-only")
    _check(backlog.get("automatic_dispatch_enabled") is False, "autonomous dispatch must be disabled")
    if git_ref:
        _check(git_ref == BRANCH, "runtime git branch mismatch")
    if git_sha is not None:
        _check(re.fullmatch(r"[0-9a-f]{40}", git_sha) is not None, "invalid Git commit identity")

    tasks = backlog.get("tasks")
    _check(isinstance(tasks, list) and 0 < len(tasks) <= MAX_TASKS, "invalid task list")
    indexed = {}
    for task in tasks:
        _check(isinstance(task, dict), "task entry not an object")
        tid = task.get("id")
        _check(isinstance(tid, str) and bool(TASK_ID.fullmatch(tid)), "invalid task ID")
        _check(tid not in indexed, "duplicate task ID " + tid)
        _check(task.get("status") in STATUSES, "invalid status for " + tid)
        _check(task.get("role") in ROLES, "invalid role for " + tid)
        _check(task.get("kind") in KINDS, "invalid kind for " + tid)
        _check(type(task.get("priority")) is int and 0 <= task["priority"] <= 1000,
               "invalid priority for " + tid)
        _check(isinstance(task.get("title"), str) and 0 < len(task["title"]) <= 200,
               "invalid title for " + tid)
        deps = task.get("depends_on")
        _check(isinstance(deps, list) and len(deps) <= 20 and
               all(isinstance(x, str) for x in deps), "invalid dependencies for " + tid)
        _check(isinstance(task.get("evidence"), list), "invalid evidence array for " + tid)
        if task["status"] == "DONE":
            _check(bool(task["evidence"]) and all(isinstance(x, str) and x.strip() for x in task["evidence"]),
                   "DONE task lacks evidence: " + tid)
        indexed[tid] = task

    for task in tasks:
        for dep in task["depends_on"]:
            _check(dep in indexed and dep != task["id"], "unknown/self dependency for " + task["id"])

    visiting, visited = set(), set()
    def visit(tid):
        if tid in visited:
            return
        _check(tid not in visiting, "cyclic dependencies")
        visiting.add(tid)
        for dep in indexed[tid]["depends_on"]:
            visit(dep)
        visiting.remove(tid)
        visited.add(tid)
    for tid in indexed:
        visit(tid)

    base = {
        "schema": SCHEMA,
        "project": "AAB-001",
        "repository": REPOSITORY,
        "branch": BRANCH,
        "git_revision_observed": git_sha,
        "checkpoint_phase": state.get("phase"),
        "dispatch_enabled": False,
        "agent_executed": False,
        "state_modified": False,
        "trust_note": "Backlog files and owner approval assertions are not authenticated execution authority.",
    }
    if backlog.get("stop_requested") is True:
        return {**base, "status": "STOPPED", "selected": None,
                "reason": "owner STOP switch set; no assignment proposed"}
    _check(backlog.get("stop_requested") is False, "missing or ambiguous STOP state")
    eligible = [t for t in tasks if t["status"] == "READY"
                and all(indexed[d]["status"] == "DONE" for d in t["depends_on"])]
    eligible.sort(key=lambda t: (t["priority"], t["id"]))
    if not eligible:
        return {**base, "status": "NO_ELIGIBLE_WORK", "selected": None,
                "reason": "nothing READY with verified completed dependencies"}
    chosen = eligible[0]
    return {
        **base,
        "status": "PROPOSED_NOT_DISPATCHED",
        "selected": {
            "id": chosen["id"], "title": chosen["title"], "role": chosen["role"],
            "kind": chosen["kind"], "priority": chosen["priority"],
            "scope_id": chosen.get("scope_id"), "approval_status": "NOT_AUTHENTICATED",
            "suggested_owner_action": chosen.get("suggested_owner_action") if chosen["role"] == "OWNER" else None,
            "evidence_references": chosen["evidence"],
        },
        "reason": "proposal only; owner/trusted provider must independently authorize and deliver any action"
    }


def run(state_path, backlog_path, output_path=None):
    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    backlog = json.loads(Path(backlog_path).read_text(encoding="utf-8"))
    try:
        result = decide(state, backlog,
                        git_ref=os.environ.get("GITHUB_REF_NAME"),
                        git_sha=os.environ.get("GITHUB_SHA"))
    except InvalidState as exc:
        result = {"schema": SCHEMA, "status": "BLOCKED_INVALID_STATE",
                  "reason": str(exc), "dispatch_enabled": False,
                  "agent_executed": False, "state_modified": False}
    serialized = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if output_path is not None:
        Path(output_path).write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fp:
            fp.write("## AAB assignment proposal (never dispatched)\n\n")
            fp.write("- Outcome: " + result["status"] + "\n")
            fp.write("- Next: " + (result.get("selected") or {}).get("id", "NONE") + "\n")
            fp.write("- External execution: DISABLED\n")
    return 0 if result["status"] != "BLOCKED_INVALID_STATE" else 2


def main():
    p = argparse.ArgumentParser(description="Read-only AAB assignment proposal controller")
    p.add_argument("--state", required=True)
    p.add_argument("--backlog", required=True)
    p.add_argument("--output")
    args = p.parse_args()
    try:
        return run(args.state, args.backlog, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("BLOCKED: invalid/unreadable input; nothing dispatched (" + type(exc).__name__ + ")",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
