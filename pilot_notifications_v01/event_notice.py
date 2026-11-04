"""AAB-001 standalone event-notice prototype (NOT connected to the live watcher).

A trusted supervisor provides typed, independently assessed events. Never feed raw
GitHub comment text into review_verified or owner_action_required fields.
The single-writer local ledger is for simulation only, not a distributed lock.
"""
from __future__ import annotations

import json
import hashlib
import os
import re
import tempfile
from pathlib import Path

VALID_KINDS = frozenset({"EVENT_OBSERVED", "TASK_PROGRESS", "TASK_TERMINAL"})
TERMINAL_STATES = frozenset({"COMPLETED", "FAILED", "BLOCKED", "UNVERIFIED", "CANCELLED"})
TOKEN = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")


def _fresh():
    return {"v": 1, "events": {}, "terminal": {}, "notices": {}}


def _read(path):
    if not path.exists():
        return _fresh()
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("invalid notification ledger") from exc
    if (not isinstance(obj, dict) or set(obj) != {"v", "events", "terminal", "notices"}
            or obj["v"] != 1 or any(not isinstance(obj[k], dict) for k in ("events", "terminal", "notices"))):
        raise ValueError("invalid notification ledger schema")
    # Do not infer validity from a file that merely looks plausible.
    for k, v in obj["events"].items():
        if not k.isdigit() or not isinstance(v, dict) or set(v) != {"kind", "task_id", "digest"}:
            raise ValueError("invalid recorded event")
        if (v["kind"] not in VALID_KINDS or not _token(v["task_id"]) or
                type(v["digest"]) is not str or re.fullmatch(r"[0-9a-f]{64}", v["digest"]) is None):
            raise ValueError("invalid recorded event")
    for k, v in obj["terminal"].items():
        if not _token(k) or not isinstance(v, dict) or set(v) != {"state", "evidence"} or v["state"] not in TERMINAL_STATES or not isinstance(v["evidence"], str):
            raise ValueError("invalid terminal record")
    for k, v in obj["notices"].items():
        if not _token(k) or not isinstance(v, str):
            raise ValueError("invalid notice record")
    return obj


def _token(s):
    return type(s) is str and TOKEN.fullmatch(s) is not None


def _commit(path, ledger):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=str(path.parent), prefix=".notice-", delete=False) as f:
            temp = Path(f.name)
            json.dump(ledger, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def accept_event(ledger_path: str | Path, event: dict) -> dict:
    """Process a trusted, structured event; return a possible owner notice.

    Returns one of {"disposition": "RECORDED|DUPLICATE", "owner_notice": str|None}.
    TERMINAL "COMPLETED" requires reviewer attestation supplied separately from
    worker prose; no backend verification of that attestation exists in v0.1.
    """
    if not isinstance(event, dict):
        raise ValueError("event must be an object")
    expected = {"source_comment_id", "kind", "task_id", "final_state", "evidence_ref", "review_verified", "owner_action_required"}
    if set(event) != expected:
        raise ValueError("invalid event keys")
    source_id = event["source_comment_id"]
    kind = event["kind"]
    task_id = event["task_id"]
    final = event["final_state"]
    evidence = event["evidence_ref"]
    verified = event["review_verified"]
    owner_action = event["owner_action_required"]
    if type(source_id) is not int or source_id <= 0 or type(kind) is not str or kind not in VALID_KINDS or not _token(task_id):
        raise ValueError("invalid event identity")
    if type(verified) is not bool or type(owner_action) is not bool:
        raise ValueError("invalid review fields")
    if not isinstance(evidence, str) or len(evidence) > 1024:
        raise ValueError("invalid evidence field")
    if kind != "TASK_TERMINAL":
        if final is not None or verified or owner_action or evidence:
            raise ValueError("nonterminal event cannot claim completion or require action")
    elif type(final) is not str or final not in TERMINAL_STATES:
        raise ValueError("invalid final state")
    if kind == "TASK_TERMINAL" and final == "COMPLETED" and (not verified or not evidence):
        raise ValueError("completed task requires external verification and evidence")
    if kind == "TASK_TERMINAL" and owner_action and (final not in {"BLOCKED", "FAILED"} or not verified or not evidence):
        raise ValueError("owner action requires verified blocker or failure and evidence")

    path = Path(ledger_path)
    data = _read(path)
    key = str(source_id)
    event_digest = hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
    identity = {"kind": kind, "task_id": task_id, "digest": event_digest}
    if key in data["events"]:
        if data["events"][key] != identity:
            raise ValueError("conflicting replay of source comment ID")
        return {"disposition": "DUPLICATE", "owner_notice": None}

    notice = None
    if kind == "TASK_TERMINAL":
        prior = data["terminal"].get(task_id)
        current = {"state": final, "evidence": evidence}
        if prior is not None and prior != current:
            raise ValueError("conflicting terminal result for task")
        if prior is None:
            data["terminal"][task_id] = current
            if final == "COMPLETED" and verified:
                notice = f"Task {task_id}: COMPLETED — independently checked evidence: {evidence}"
            elif owner_action:
                notice = f"Task {task_id}: {final} — owner decision required; evidence: {evidence}"
            if notice is not None:
                data["notices"][task_id] = notice
    data["events"][key] = identity
    _commit(path, data)
    return {"disposition": "RECORDED", "owner_notice": notice}
