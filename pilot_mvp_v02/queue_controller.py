"""AAB-001 v0.2 synthetic durable job queue (T3 next_job, T4 mark_done). Stdlib only."""
import json
import os
import re
import tempfile
from pathlib import Path

_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,80}")
_SHA_RE = re.compile(r"[0-9a-f]{64}")


def _is_id(value):
    return isinstance(value, str) and value.isascii() and _ID_RE.fullmatch(value) is not None


def _is_sha(value):
    return isinstance(value, str) and value.isascii() and _SHA_RE.fullmatch(value) is not None


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable or corrupt JSON: {path}") from exc


def _load_queue(queue_path):
    data = _read_json(queue_path)
    if not isinstance(data, dict) or set(data) != {"jobs"} or not isinstance(data["jobs"], list):
        raise ValueError("queue must be {'jobs': [...]}")
    order, deps = [], {}
    for job in data["jobs"]:
        if not isinstance(job, dict) or set(job) != {"id", "deps"}:
            raise ValueError("each job must have exactly 'id' and 'deps'")
        jid, jdeps = job["id"], job["deps"]
        if not _is_id(jid):
            raise ValueError(f"invalid job id: {jid!r}")
        if jid in deps:
            raise ValueError(f"duplicate job id: {jid}")
        if not isinstance(jdeps, list) or not all(_is_id(d) for d in jdeps):
            raise ValueError(f"invalid deps for {jid}")
        if len(set(jdeps)) != len(jdeps):
            raise ValueError(f"duplicate dep in {jid}")
        if jid in jdeps:
            raise ValueError(f"self dependency in {jid}")
        order.append(jid)
        deps[jid] = list(jdeps)
    for jid in order:
        for d in deps[jid]:
            if d not in deps:
                raise ValueError(f"{jid} depends on unknown job {d}")
    # cycle detection (iterative DFS, colours: 0 new, 1 active, 2 done)
    colour = {j: 0 for j in order}
    for start in order:
        if colour[start]:
            continue
        stack = [(start, iter(deps[start]))]
        colour[start] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                colour[node] = 2
                stack.pop()
            elif colour[nxt] == 1:
                raise ValueError(f"dependency cycle via {nxt}")
            elif colour[nxt] == 0:
                colour[nxt] = 1
                stack.append((nxt, iter(deps[nxt])))
    return order, deps


def _load_state(state_path, deps):
    if not os.path.exists(state_path):
        return {}
    data = _read_json(state_path)
    if not isinstance(data, dict) or set(data) != {"completed"} or not isinstance(data["completed"], dict):
        raise ValueError("state must be {'completed': {...}}")
    completed = data["completed"]
    for jid, sha in completed.items():
        if jid not in deps:
            raise ValueError(f"state references unknown job {jid}")
        if not _is_sha(sha):
            raise ValueError(f"invalid evidence for {jid}")
    for jid in completed:
        for d in deps[jid]:
            if d not in completed:
                raise ValueError(f"{jid} completed before dependency {d}")
    return dict(completed)


def _load(queue_path, state_path):
    order, deps = _load_queue(queue_path)
    completed = _load_state(state_path, deps)
    return order, deps, completed


def next_job(queue_path, state_path):
    """T3: first uncompleted job (queue order) whose deps are all completed; None if none. Read-only."""
    order, deps, completed = _load(queue_path, state_path)
    for jid in order:
        if jid not in completed and all(d in completed for d in deps[jid]):
            return jid
    return None


def _atomic_write(state_path, payload):
    directory = os.path.dirname(os.path.abspath(state_path))
    fd, tmp = tempfile.mkstemp(prefix=".state-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, state_path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def mark_done(queue_path, state_path, job_id, evidence_sha):
    """T4: durably mark job complete. True on new completion, False on identical replay."""
    if not _is_id(job_id):
        raise ValueError(f"invalid job id: {job_id!r}")
    if not _is_sha(evidence_sha):
        raise ValueError("evidence_sha must be 64 lowercase hex characters")
    order, deps, completed = _load(queue_path, state_path)  # shared T3 validation
    if job_id not in deps:
        raise ValueError(f"unknown job: {job_id}")
    if job_id in completed:
        if completed[job_id] == evidence_sha:
            return False
        raise ValueError(f"conflicting evidence for completed job {job_id}")
    missing = [d for d in deps[job_id] if d not in completed]
    if missing:
        raise ValueError(f"{job_id} has incomplete dependencies: {missing}")
    completed[job_id] = evidence_sha
    _atomic_write(state_path, {"completed": completed})
    return True
