"""Classify AAB handoff GitHub event metadata, without executing untrusted content."""
import json
import os
import re
import sys
from pathlib import Path

REPOSITORY = "someonee12345678-hue/aab-queue"
ISSUE_NUMBER = 2
HANDOFF_HEADER = re.compile(r"^#?\s*ARTIFACT_HANDOFF\s+[—-]\s+(AAB-[A-Za-z0-9_-]{1,76})\s*$")
MAX_COMMENT_BYTES = 100_000


def inspect(event):
    """Only GitHub event envelope establishes transport identity, not authority."""
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
    if len(body.encode("utf-8")) > MAX_COMMENT_BYTES:
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
        "body_bytes": len(body.encode("utf-8")),
        "event_created_at": comment.get("created_at"),
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
