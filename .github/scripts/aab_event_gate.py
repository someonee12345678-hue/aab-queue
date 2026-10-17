"""Classify AAB handoff GitHub event metadata, without executing untrusted content."""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

REPOSITORY = "someonee12345678-hue/aab-queue"
ISSUE_NUMBER = 2
HANDOFF_HEADER = re.compile(r"^#?\s*ARTIFACT_HANDOFF\s+[—-]\s+(AAB-[A-Za-z0-9_-]{1,76})\s*$")
MAX_COMMENT_BYTES = 100_000


def inspect(event, runtime=None):
    """Report event identity as untrusted metadata, never proof of sender authority."""
    result = {"protocol": "AAB-001/handoff-event-v1", "status": "IGNORED", "verified_review": False}
    if event.get("action") != "created":
        return result
    if (event.get("repository") or {}).get("full_name") != REPOSITORY:
        return result
    issue = event.get("issue") or {}
    if issue.get("number") != ISSUE_NUMBER or not issue.get("pull_request"):
        return result
    comment = event.get("comment") or {}
    cid = comment.get("id")
    if type(cid) is not int or cid < 1:
        result["status"] = "UNVERIFIED_BAD_COMMENT_ID"
        return result
    result["source_comment_id"] = cid
    body = comment.get("body")
    if not isinstance(body, str):
        result["status"] = "UNVERIFIED_BAD_BODY"
        return result
    body_bytes = body.encode("utf-8")
    author = comment.get("user") or {}
    app = comment.get("performed_via_github_app") or {}
    runtime = os.environ if runtime is None else runtime
    run_id = runtime.get("GITHUB_RUN_ID")
    attempt = runtime.get("GITHUB_RUN_ATTEMPT")
    result.update({
        "source_comment_node_id": comment.get("node_id"),
        "comment_author_login": author.get("login"),
        "comment_author_id": author.get("id"),
        "author_association": comment.get("author_association"),
        "posting_app_slug": app.get("slug"),
        "posting_app_id": app.get("id"),
        "event_created_at": comment.get("created_at"),
        "event_updated_at": comment.get("updated_at"),
        "comment_html_url": comment.get("html_url"),
        "body_bytes": len(body_bytes),
        "body_sha256": hashlib.sha256(body_bytes).hexdigest(),
        "workflow_run_id": int(run_id) if run_id and run_id.isdecimal() else None,
        "workflow_run_attempt": int(attempt) if attempt and attempt.isdecimal() else None,
        "event_commit_sha": runtime.get("GITHUB_SHA"),
        "identity_note": "Event metadata is not independent author authentication; re-fetch the comment ID and compare before any downstream review.",
    })
    if len(body_bytes) > MAX_COMMENT_BYTES:
        result["status"] = "UNVERIFIED_OVERSIZE"
        return result
    first = body.lstrip("\ufeff\n\r ").splitlines()[0].strip() if body.strip() else ""
    match = HANDOFF_HEADER.fullmatch(first)
    if not match:
        result["status"] = "IGNORED_NOT_HANDOFF"
        return result
    result.update({
        "status": "IDENTIFIED_PENDING_INDEPENDENT_REVIEW",
        "task_id": match.group(1),
        "transport_scope_verified": True,
        "note": "Not authenticated as Grok or owner; source checksums/tests not reviewed."
    })
    return result


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 aab_event_gate.py EVENT_PATH")
    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = inspect(event)
    Path("aab-handoff-event-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## AAB incoming PR comment classification\n\n")
            handle.write("- Outcome: %s\n" % report["status"])
            if "source_comment_id" in report:
                handle.write("- Comment ID: %d\n" % report["source_comment_id"])
            if "task_id" in report:
                handle.write("- Task: %s\n" % report["task_id"])
            handle.write("- This gate does not execute code or authorize new work.\n")


if __name__ == "__main__":
    main()
