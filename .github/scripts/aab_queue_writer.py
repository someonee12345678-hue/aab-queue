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
    def __init__(self, code, explanation="", method=None, api_path=None):
        # Log only method/path, never bearer token or comment body.
        target = f" during {method} {api_path}" if method and api_path else ""
        super().__init__(f"GitHub API HTTP {code}{target}: {explanation[:180]}")
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
        if not isinstance(previous, dict):
            raise QueueBlocked("existing queue entry must be a JSON object")
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
        raise ApiError(exc.code, exc.reason, method, urllib.parse.urlsplit(url).path) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise QueueBlocked(f"GitHub connection failure during {method} {urllib.parse.urlsplit(url).path}") from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise QueueBlocked(f"GitHub returned invalid response during {method} {urllib.parse.urlsplit(url).path}") from exc


def execute_with_receipt(report, read_json, create_json, receipt_path,
                         summary_path=None):
    """One attempt; persist a small secret-free outcome even when the attempt blocks.

    Never performs a retry and never treats an outcome receipt as a queue record.
    The report/transport are untrusted, so archive codes rather than exception bodies.
    """
    cid = report.get("source_comment_id") if isinstance(report, dict) else None
    task = report.get("task_id") if isinstance(report, dict) else None
    receipt = {
        "protocol": "AAB-001/queue-attempt-v1",
        "outcome": "BLOCKED",
        "reason_code": "NOT_STARTED",
        "source_comment_id": cid if type(cid) is int and cid > 0 else None,
        "task_id": task if isinstance(task, str) and TASK_PATTERN.fullmatch(task) else None,
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "note": "Metadata-only attempt receipt; not a successful handoff or code review.",
    }
    try:
        if not isinstance(report, dict) or not isinstance(report.get("status"), str):
            raise QueueBlocked("classification report missing or invalid")
        result = process(report, read_json, create_json)
        receipt["outcome"] = result["outcome"]
        receipt["reason_code"] = "NONE"
        if result.get("path"):
            receipt["queue_path"] = result["path"]
        if result.get("commit_sha"):
            receipt["commit_sha"] = result["commit_sha"]
    except QueueBlocked as exc:
        message = str(exc)
        if "queue create was not confirmed" in message or "queue create outcome unconfirmed" in message:
            receipt["reason_code"] = "WRITE_UNCONFIRMED"
        elif "connection failure" in message:
            receipt["reason_code"] = "NETWORK_FAILURE"
        elif "invalid response" in message:
            receipt["reason_code"] = "INVALID_API_RESPONSE"
        else:
            receipt["reason_code"] = "VALIDATION_OR_CONFLICT"
    except ApiError as exc:
        receipt["reason_code"] = "API_HTTP_" + str(exc.code)
    except Exception:
        # Fail closed without leaking exception messages from untrusted responses.
        receipt["reason_code"] = "UNEXPECTED_FAILURE"
    Path(receipt_path).write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n",
                                  encoding="utf-8")
    line = receipt["outcome"] + ":" + receipt["reason_code"]
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## AAB queue attempt (not a review)\n\n")
            handle.write("- Outcome: " + line + "\n")
            handle.write("- Source comment ID: " + str(receipt["source_comment_id"]) + "\n")
            handle.write("- This receipt does not confirm delivery to ChatGPT or Grok.\n")
    if receipt["outcome"] == "BLOCKED":
        print("BLOCKED:" + receipt["reason_code"] + "; no retry or backfill", file=sys.stderr)
        return False
    print(json.dumps(receipt, sort_keys=True))
    return True


def main():
    receipt_path = Path("aab-handoff-queue-outcome.json")
    try:
        if len(sys.argv) != 2:
            raise ValueError("missing report path")
        report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("report must be an object")
    except (OSError, ValueError):
        report = {}
    token = os.environ.get("AAB_GITHUB_TOKEN", "")
    if token:
        read_json = lambda url: github_request(url, token)
        create_json = lambda url, body: github_request(url, token, body)
    else:
        def no_token(*args):
            raise QueueBlocked("missing GitHub token")
        read_json = no_token
        create_json = no_token
    success = execute_with_receipt(
        report, read_json, create_json, receipt_path, os.environ.get("GITHUB_STEP_SUMMARY"))
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
