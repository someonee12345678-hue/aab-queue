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

class InvalidGoal(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise InvalidGoal(reason)

def evaluate(goal, *, observed_branch=None, observed_commit=None, completed_keys=(), verified_evidence=()):
    """Return a non-executable proposal. Strings in goal are untrusted data."""
    try:
        require(type(goal) is dict, "goal must be object")
        require(type(goal.get("schema_version")) is int and goal["schema_version"] == 1, "schema")
        require(goal.get("project") == "AAB-001" and goal.get("repo") == REPO and goal.get("branch") == BRANCH, "identity")
        require(type(goal.get("goal_id")) is str and ID.fullmatch(goal["goal_id"]), "goal_id")
        require(type(goal.get("base_commit")) is str and SHA.fullmatch(goal["base_commit"]), "base_commit")
        require(goal.get("goal_status") in GOALS, "goal_status")
        require(type(goal.get("stop")) is bool, "stop flag")
        require(type(goal.get("owner_scope_ref")) is str and bool(goal["owner_scope_ref"].strip()), "owner scope reference")
        require(type(goal.get("last_verified_utc")) is str, "timestamp")
        dt = datetime.fromisoformat(goal["last_verified_utc"].replace("Z", "+00:00"))
        require(dt.tzinfo is not None and dt.utcoffset() == timezone.utc.utcoffset(dt), "timestamp timezone")
        require(type(goal.get("evidence_checkpoint")) is str and bool(goal["evidence_checkpoint"].strip()), "checkpoint")
        require(observed_branch == BRANCH, "missing or stale observed branch")
        require(type(observed_commit) is str and SHA.fullmatch(observed_commit) and observed_commit == goal["base_commit"], "missing or stale observed commit")
        require(type(verified_evidence) in (tuple, list, set, frozenset) and all(type(e) is str for e in verified_evidence), "verified evidence registry")
        steps = goal.get("steps")
        require(type(steps) is list and 0 < len(steps) <= 100, "steps")
        indexed, keys = {}, set()
        for s in steps:
            require(type(s) is dict, "step object")
            sid, key = s.get("step_id"), s.get("idempotency_key")
            require(type(sid) is str and ID.fullmatch(sid) and sid not in indexed, "step id")
            require(type(key) is str and ID.fullmatch(key) and key not in keys, "idempotency key")
            require(s.get("assigned_role") in ROLES and s.get("status") in STATES, "role/status")
            require(type(s.get("prerequisite_step_ids")) is list and all(type(d) is str for d in s["prerequisite_step_ids"]), "dependencies")
            require(type(s.get("evidence_refs")) is list and all(type(e) is str and bool(e.strip()) for e in s["evidence_refs"]), "evidence")
            require(s["status"] != "VERIFIED" or (bool(s["evidence_refs"]) and all(e in verified_evidence for e in s["evidence_refs"])), "verified without independently checked evidence")
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
            require(type(action.get("description")) is str and type(action.get("approval_ref")) is str, "action fields")
        require(goal["goal_status"] != "VERIFIED_COMPLETE" or all(s["status"] == "VERIFIED" for s in steps), "inconsistent completed goal")
        if goal["stop"] or goal["goal_status"] in ("STOPPED", "BLOCKED"):
            return {"status": "STOPPED", "next_step_id": None, "execution_authorized": False}
        require(type(completed_keys) in (tuple, list, set, frozenset), "completed keys")
        require(all(type(k) is str for k in completed_keys), "completed key type")
        eligible = [s for s in steps if s["status"] in ("PENDING", "READY")
                    and all(indexed[d]["status"] == "VERIFIED" for d in s["prerequisite_step_ids"])
                    and s["idempotency_key"] not in completed_keys]
        return {"status": "PROPOSED_NOT_DISPATCHED" if eligible else "NO_ELIGIBLE_STEP",
                "next_step_id": eligible[0]["step_id"] if eligible else None,
                "execution_authorized": False}
    except (InvalidGoal, ValueError, TypeError, KeyError, OverflowError) as exc:
        return {"status": "BLOCKED_INVALID_STATE", "next_step_id": None,
                "execution_authorized": False, "reason": str(exc)}
