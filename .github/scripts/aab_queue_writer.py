"""Create one data-only, verified, GitHub handoff queue record per new comment.

Never executes GitHub comment content, changes existing records, or retries uncertain writes.
"""
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "someonee12345678-hue/aab-queue"
TARGET_BRANCH = "mc/channel"
QUEUE_PREFIX = "channel/handoffs"
PR = 2
# No backfill of earlier GitHub events, even when a run is reattempted.
START_AFTER = "2026-10-17T08:52:11Z"
OWNER = "someonee12345678-hue"
AUTHORIZED_POSTING_APP = "cursor"  # Previous independently checked Grok handoffs.
TASK_PATTERN = re.compile(r"AAB-[A-Za-z0-9_-]{1,76}\Z")
API = f"https://api.github.com/repos/{REPO}"


class QueueBlocked(Exception):
    """An incomplete, ambiguous or unexpected event is not safe to queue."""


class ApiError(Exception):
    def __init__(self, code, explanation=""):
        super().__init__(f"GitHub API HTTP {code}: {explanation[:180]}")
        self.code = code


def _iso(s):
    if not isinstance(s, str) or not s.endswith("Z"):
        raise QueueBlocked("invalid creation timestamp")
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QueueBlocked("invalid creation timestamp") from exc


def build_record(report, comment):
    if report.get("status") != "IDENTIFIED_PENDING_INDEPENDENT_REVIEW":
        return None
    cid = report.get("source_comment_id")
    task = report.get("task_id")
    if type(cid) is not int or cid < 1 or not isinstance(task, str) or not TASK_PATTERN.fullmatch(task):
        raise QueueBlocked("invalid reported comment/task identity")
    if _iso(report.get("event_created_at")) <= _iso(START_AFTER):
        raise QueueBlocked("historical events cannot be backfilled")
    if comment.get("id") != cid or (type(comment.get("id")) is not int):
        raise QueueBlocked("comment id mismatch")
    if comment.get("issue_url") != f"{API}/issues/{PR}":
        raise QueueBlocked("comment is not on PR #2")
    if comment.get("created_at") != report.get("event_created_at"):
        raise QueueBlocked("creation timestamp mismatch")
    if comment.get("html_url") != report.get("comment_html_url"):
        raise QueueBlocked("comment url mismatch")
    owner = comment.get("user") or {}
    app = comment.get("performed_via_github_app") or {}
    if owner.get("login") != OWNER or app.get("slug") != AUTHORIZED_POSTING_APP:
        raise QueueBlocked("comment author or posting app not allowlisted")
    if owner.get("id") != report.get("comment_author_id") or app.get("id") != report.get("posting_app_id"):
        raise QueueBlocked("source author/app identifier mismatch")
    body = comment.get("body")
    if not isinstance(body, str) or len(body.encode("utf-8")) > 100000:
        raise QueueBlocked("comment body unavailable or oversize")
    body_digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if body_digest != report.get("body_sha256"):
        raise QueueBlocked("event body checksum mismatch")
    first = body.lstrip("\ufeff\n\r ").splitlines()[0].strip() if body.strip() else ""
    if not re.fullmatch(r"#?\s*ARTIFACT_HANDOFF\s+[—-]\s+" + re.escape(task), first):
        raise QueueBlocked("handoff header mismatch")
    if report.get("workflow_run_id") is None or type(report.get("workflow_run_id")) is not int:
        raise QueueBlocked("missing workflow run ID")
    return {
        "protocol": "AAB-001/durable-handoff-v1",
        "status": "PENDING_INDEPENDENT_REVIEW",
        "review_status": "NOT_PERFORMED",
        "origin_authenticity": "UNVERIFIED_AGENT_IDENTITY",
        "source_repository": REPO,
        "source_pull_request_number": PR,
        "source_comment_id": cid,
        "source_comment_url": comment["html_url"],
        "source_comment_created_at": comment["created_at"],
        "task_id": task,
        "source_body_sha256": body_digest,
        "source_comment_author_login": owner["login"],
        "source_posting_app_slug": app["slug"],
        "verified_comment_via_github_get": True,
        "event_workflow_run_id": report["workflow_run_id"],
        "disclaimer": "Metadata-only queue receipt; no code execution, review or Grok authorization.",
    }


def process(report, read_json, create_json):
    if report.get("status") != "IDENTIFIED_PENDING_INDEPENDENT_REVIEW":
        return {"outcome": "IGNORED", "reason": "not an accepted handoff classification"}
    cid = report.get("source_comment_id")
    if type(cid) is not int or cid < 1:
        raise QueueBlocked("missing numeric source comment ID")
    comment = read_json(f"{API}/issues/comments/{cid}")
    record = build_record(report, comment)
    path = f"{QUEUE_PREFIX}/{cid}.json"
    url = f"{API}/contents/{path}?ref={urllib.parse.quote(TARGET_BRANCH, safe='')}"
    try:
        existing = read_json(url)
    except ApiError as exc:
        if exc.code != 404:
            raise
    else:
        if not isinstance(existing, dict) or not isinstance(existing.get("content"), str):
            raise QueueBlocked("existing queue entry cannot be inspected")
        try:
            previous = json.loads(base64.b64decode(existing["content"]).decode("utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise QueueBlocked("existing queue entry cannot be decoded") from exc
        if (previous.get("source_comment_id"), previous.get("task_id"), previous.get("source_body_sha256")) != (cid, record["task_id"], record["source_body_sha256"]):
            raise QueueBlocked("conflicting pre-existing queue entry")
        return {"outcome": "ALREADY_QUEUED", "source_comment_id": cid, "path": path}
    serialized = json.dumps(record, indent=2, sort_keys=True) + "\n"
    payload = {"message": f"AAB: queue verified comment {cid} for independent review", "branch": TARGET_BRANCH,
               "content": base64.b64encode(serialized.encode("utf-8")).decode("ascii")}
    try:
        result = create_json(f"{API}/contents/{path}", payload)
    except ApiError as exc:
        # Fail closed after any uncertain write, including 409/422. Never retry here.
        raise QueueBlocked(f"queue create was not confirmed (HTTP {exc.code}); do not retry") from exc
    if not isinstance(result, dict) or not (result.get("commit") or {}).get("sha"):
        raise QueueBlocked("queue create outcome unconfirmed; do not retry")
    return {"outcome": "QUEUED", "source_comment_id": cid, "path": path,
            "commit_sha": result["commit"]["sha"]}


def github_request(url, token, body=None):
    method = "PUT" if body is not None else "GET"
    req = urllib.request.Request(url, method=method,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "AAB-Durable-Queue/1", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, exc.reason) from exc


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 aab_queue_writer.py CLASSIFICATION_REPORT.json")
    token = os.environ.get("AAB_GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("BLOCKED: no scoped GitHub token; nothing queued")
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    try:
        outcome = process(report, lambda url: github_request(url, token),
                          lambda url, body: github_request(url, token, body))
        print(json.dumps(outcome, sort_keys=True))
    except (QueueBlocked, ApiError) as exc:
        print(f"BLOCKED: {exc}; no retry or backfill", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
