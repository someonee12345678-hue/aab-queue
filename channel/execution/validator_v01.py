"""AAB-EXEC-001 pure validator: no I/O, network, subprocess or dispatch."""
import re
from datetime import datetime, timezone

REPO = "someonee12345678-hue/aab-queue"
BRANCH = "mc/channel"
SHA = re.compile(r"[0-9a-f]{40}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")
ROLES = {"OWNER", "CHATGPT", "GROK", "PHONE_CODEX", "GITHUB_ACTIONS"}
STATES = {"PENDING", "READY", "RUNNING", "REPORTED", "VERIFIED", "BLOCKED"}
GOALS = {"PROPOSED", "APPROVED", "IN_PROGRESS", "BLOCKED", "VERIFIED_COMPLETE", "STOPPED"}

# Keep the pure validator's work bounded even when the input came from an
# untrusted or malformed checkpoint. Parsing-layer byte limits are still
# needed by any future caller before it constructs these Python objects.
MAX_STEPS = 100
MAX_REFS_PER_STEP = 100
MAX_COMPLETED_KEYS = 10_000
MAX_VERIFIED_EVIDENCE = 10_000
MAX_REFERENCE_LENGTH = 512
MAX_ACTION_DESCRIPTION_LENGTH = 1_024
MAX_TIMESTAMP_LENGTH = 64

GOAL_FIELDS = {
    "schema_version", "project", "repo", "branch", "base_commit", "goal_id",
    "owner_scope_ref", "goal_status", "stop", "last_verified_utc",
    "evidence_checkpoint", "next_authorized_action", "steps",
}
STEP_FIELDS = {
    "step_id", "idempotency_key", "assigned_role", "status",
    "prerequisite_step_ids", "evidence_refs",
}
ACTION_FIELDS = {"description", "approval_ref"}


class InvalidGoal(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise InvalidGoal(reason)


def _bounded_nonempty_text(value, limit):
    return type(value) is str and 0 < len(value) <= limit and bool(value.strip())


def evaluate(goal, *, observed_branch=None, observed_commit=None, completed_keys=(), verified_evidence=()):
    """Return a non-executable proposal. Strings in goal are untrusted data."""
    try:
        require(type(goal) is dict, "goal must be object")
        require(set(goal).issubset(GOAL_FIELDS), "unknown goal field")
        require(type(goal.get("schema_version")) is int and goal["schema_version"] == 1, "schema")
        require(goal.get("project") == "AAB-001" and goal.get("repo") == REPO and goal.get("branch") == BRANCH, "identity")
        require(type(goal.get("goal_id")) is str and ID.fullmatch(goal["goal_id"]), "goal_id")
        require(type(goal.get("base_commit")) is str and SHA.fullmatch(goal["base_commit"]), "base_commit")
        require(goal.get("goal_status") in GOALS, "goal_status")
        require(type(goal.get("stop")) is bool, "stop flag")
        require(_bounded_nonempty_text(goal.get("owner_scope_ref"), MAX_REFERENCE_LENGTH), "owner scope reference")
        timestamp = goal.get("last_verified_utc")
        require(type(timestamp) is str and 0 < len(timestamp) <= MAX_TIMESTAMP_LENGTH, "timestamp length")
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        require(dt.tzinfo is not None and dt.utcoffset() == timezone.utc.utcoffset(dt), "timestamp timezone")
        require(_bounded_nonempty_text(goal.get("evidence_checkpoint"), MAX_REFERENCE_LENGTH), "checkpoint")
        require(observed_branch == BRANCH, "missing or stale observed branch")
        require(type(observed_commit) is str and SHA.fullmatch(observed_commit) and observed_commit == goal["base_commit"], "missing or stale observed commit")
        require(type(verified_evidence) in (tuple, list, set, frozenset)
                and len(verified_evidence) <= MAX_VERIFIED_EVIDENCE
                and all(_bounded_nonempty_text(e, MAX_REFERENCE_LENGTH) for e in verified_evidence),
                "verified evidence registry")
        steps = goal.get("steps")
        require(type(steps) is list and 0 < len(steps) <= MAX_STEPS, "steps")
        indexed, keys = {}, set()
        for s in steps:
            require(type(s) is dict, "step object")
            require(set(s).issubset(STEP_FIELDS), "unknown step field")
            sid, key = s.get("step_id"), s.get("idempotency_key")
            require(type(sid) is str and ID.fullmatch(sid) and sid not in indexed, "step id")
            require(type(key) is str and ID.fullmatch(key) and key not in keys, "idempotency key")
            require(s.get("assigned_role") in ROLES and s.get("status") in STATES, "role/status")
            deps = s.get("prerequisite_step_ids")
            require(type(deps) is list and len(deps) <= MAX_STEPS
                    and all(type(d) is str and ID.fullmatch(d) for d in deps)
                    and len(set(deps)) == len(deps), "dependencies")
            refs = s.get("evidence_refs")
            require(type(refs) is list and len(refs) <= MAX_REFS_PER_STEP
                    and all(_bounded_nonempty_text(e, MAX_REFERENCE_LENGTH) for e in refs), "evidence")
            require(s["status"] != "VERIFIED" or (bool(refs) and all(e in verified_evidence for e in refs)), "verified without independently checked evidence")
            indexed[sid] = s
            keys.add(key)
        visiting, visited = set(), set()

        def visit(sid):
            require(sid in indexed, "unknown dependency")
            require(sid not in visiting, "cyclic dependency")
            if sid in visited:
                return
            visiting.add(sid)
            for dep in indexed[sid]["prerequisite_step_ids"]:
                visit(dep)
            visiting.remove(sid)
            visited.add(sid)

        for sid in indexed:
            visit(sid)
        require(type(goal.get("next_authorized_action")) in (dict, type(None)), "next action")
        if goal["next_authorized_action"] is not None:
            action = goal["next_authorized_action"]
            require(set(action).issubset(ACTION_FIELDS), "unknown action field")
            description, approval_ref = action.get("description"), action.get("approval_ref")
            require(type(description) is str and 0 < len(description) <= MAX_ACTION_DESCRIPTION_LENGTH
                    and bool(description.strip())
                    and _bounded_nonempty_text(approval_ref, MAX_REFERENCE_LENGTH), "action fields")
        require(goal["goal_status"] != "VERIFIED_COMPLETE" or all(s["status"] == "VERIFIED" for s in steps), "inconsistent completed goal")
        if goal["stop"] or goal["goal_status"] in ("STOPPED", "BLOCKED"):
            return {"status": "STOPPED", "next_step_id": None, "execution_authorized": False}
        require(type(completed_keys) in (tuple, list, set, frozenset)
                and len(completed_keys) <= MAX_COMPLETED_KEYS
                and all(type(k) is str and ID.fullmatch(k) for k in completed_keys), "completed keys")
        eligible = [s for s in steps if s["status"] in ("PENDING", "READY")
                    and all(indexed[d]["status"] == "VERIFIED" for d in s["prerequisite_step_ids"])
                    and s["idempotency_key"] not in completed_keys]
        return {"status": "PROPOSED_NOT_DISPATCHED" if eligible else "NO_ELIGIBLE_STEP",
                "next_step_id": eligible[0]["step_id"] if eligible else None,
                "execution_authorized": False}
    except (InvalidGoal, ValueError, TypeError, KeyError, OverflowError) as exc:
        return {"status": "BLOCKED_INVALID_STATE", "next_step_id": None,
                "execution_authorized": False, "reason": str(exc)}
