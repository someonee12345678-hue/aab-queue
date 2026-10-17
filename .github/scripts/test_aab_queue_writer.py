"""Synthetic, no-network acceptance tests for the GitHub create-only handoff queue."""
import base64
import hashlib
import json
import unittest

from aab_queue_writer import API, ApiError, QueueBlocked, build_record, process

ID = 6239990001
TASK = "AAB-NEW-TEST-001"
BODY = "ARTIFACT_HANDOFF — " + TASK + "\nsynthetic fake test"
CREATED = "2026-10-17T09:05:00Z"
COMMENT = {
    "id": ID, "issue_url": f"{API}/issues/2", "html_url": f"https://github.com/someonee12345678-hue/aab-queue/pull/2#issuecomment-{ID}",
    "created_at": CREATED, "body": BODY,
    "user": {"login": "someonee12345678-hue", "id": 341747055},
    "performed_via_github_app": {"slug": "cursor", "id": 1055},
}
REPORT = {
    "status": "IDENTIFIED_PENDING_INDEPENDENT_REVIEW", "source_comment_id": ID,
    "task_id": TASK, "event_created_at": CREATED,
    "comment_html_url": COMMENT["html_url"], "comment_author_id": 341747055,
    "posting_app_id": 1055, "body_sha256": hashlib.sha256(BODY.encode()).hexdigest(),
    "workflow_run_id": 39999999999,
}


class QueueTests(unittest.TestCase):
    def test_happy_path_creates_only_verified_metadata(self):
        written = []
        def read(url):
            if url.endswith(f"/issues/comments/{ID}"):
                return COMMENT
            raise ApiError(404)
        def create(url, body):
            written.append((url, body))
            return {"commit": {"sha": "a" * 40}}
        outcome = process(REPORT, read, create)
        self.assertEqual(outcome["outcome"], "QUEUED")
        self.assertEqual(len(written), 1)
        self.assertEqual(written[0][1]["branch"], "mc/channel")
        saved = json.loads(base64.b64decode(written[0][1]["content"]))
        self.assertEqual(saved["source_comment_id"], ID)
        self.assertEqual(saved["review_status"], "NOT_PERFORMED")
        self.assertNotIn("body", saved)

    def test_ordinary_comment_no_write_and_no_read(self):
        reads = []
        self.assertEqual(process({"status": "IGNORED_NOT_HANDOFF"},
                                 lambda url: reads.append(url), lambda a, b: self.fail("write"))["outcome"], "IGNORED")
        self.assertFalse(reads)

    def test_wrong_author_or_app_blocks(self):
        for field, value in (("user", {"login": "stranger", "id": 341747055}),
                             ("performed_via_github_app", {"slug": "chatgpt-codex-connector", "id": 1055})):
            comment = {**COMMENT, field: value}
            with self.assertRaises(QueueBlocked):
                build_record(REPORT, comment)

    def test_modified_content_or_identity_blocks(self):
        for key, value in (("body", BODY + " evil"), ("created_at", "2026-10-17T09:05:01Z"),
                           ("issue_url", f"{API}/issues/3"), ("id", ID + 1)):
            with self.assertRaises(QueueBlocked):
                build_record(REPORT, {**COMMENT, key: value})

    def test_old_event_is_not_backfilled(self):
        report = {**REPORT, "event_created_at": "2026-10-17T08:50:00Z"}
        with self.assertRaises(QueueBlocked):
            build_record(report, {**COMMENT, "created_at": "2026-10-17T08:50:00Z"})

    def test_existing_matching_record_is_not_overwritten(self):
        saved = build_record(REPORT, COMMENT)
        def read(url):
            if url.endswith(f"/issues/comments/{ID}"):
                return COMMENT
            return {"content": base64.b64encode(json.dumps(saved).encode()).decode()}
        out = process(REPORT, read, lambda a, b: self.fail("overwrite"))
        self.assertEqual(out["outcome"], "ALREADY_QUEUED")

    def test_conflicting_existing_record_blocks(self):
        saved = {**build_record(REPORT, COMMENT), "task_id": "AAB-CONFLICT"}
        def read(url):
            if url.endswith(f"/issues/comments/{ID}"):
                return COMMENT
            return {"content": base64.b64encode(json.dumps(saved).encode()).decode()}
        with self.assertRaises(QueueBlocked):
            process(REPORT, read, lambda a, b: self.fail("write"))

    def test_api_error_or_uncertain_create_blocks_without_retry(self):
        def read(url):
            if url.endswith(f"/issues/comments/{ID}"):
                return COMMENT
            raise ApiError(404)
        calls = []
        def create(url, body):
            calls.append(url)
            raise ApiError(409)
        with self.assertRaises(QueueBlocked):
            process(REPORT, read, create)
        self.assertEqual(len(calls), 1)

    def test_missing_run_identity_blocks(self):
        report = {**REPORT, "workflow_run_id": None}
        with self.assertRaises(QueueBlocked):
            build_record(report, COMMENT)

    def test_forbidden_comment_fetch_stops_before_write(self):
        def read(url):
            self.assertTrue(url.endswith(f"/issues/comments/{ID}"))
            raise ApiError(403, "Forbidden", "GET", f"/repos/someonee12345678-hue/aab-queue/issues/comments/{ID}")
        with self.assertRaises(ApiError) as caught:
            process(REPORT, read, lambda a, b: self.fail("write"))
        self.assertIn(f"GET /repos/someonee12345678-hue/aab-queue/issues/comments/{ID}", str(caught.exception))
        self.assertNotIn("Bearer", str(caught.exception))

    def test_non_object_existing_entry_fails_closed(self):
        def read(url):
            if url.endswith(f"/issues/comments/{ID}"):
                return COMMENT
            return {"content": base64.b64encode(b"[]").decode()}
        with self.assertRaisesRegex(QueueBlocked, "must be a JSON object"):
            process(REPORT, read, lambda a, b: self.fail("write"))


if __name__ == "__main__":
    unittest.main()
