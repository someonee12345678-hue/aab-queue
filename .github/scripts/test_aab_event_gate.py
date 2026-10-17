"""AAB-GATE-IDENTITY-001: focused classifier identity and safety regression tests."""
import hashlib
import unittest

from aab_event_gate import inspect


RUNTIME = {"GITHUB_RUN_ID": "39017026536", "GITHUB_RUN_ATTEMPT": "1",
           "GITHUB_SHA": "3b0daebdbe99143ec250bb3f7ea776eb51dac658"}


def event(body="ARTIFACT_HANDOFF — AAB-TEST-001\nsource", number=2, action="created"):
    return {
        "action": action,
        "repository": {"full_name": "someonee12345678-hue/aab-queue"},
        "issue": {"number": number, "pull_request": {"url": "https://example.test/2"}},
        "comment": {
            "id": 6231674058, "node_id": "IC_test", "body": body,
            "user": {"login": "test-user", "id": 123},
            "performed_via_github_app": {"slug": "cursor", "id": 456},
            "author_association": "OWNER", "created_at": "2026-10-17T08:20:49Z",
            "updated_at": "2026-10-17T08:20:49Z",
            "html_url": "https://github.com/example/pr/2#issuecomment-6231674058",
        },
    }


class IdentityGateTests(unittest.TestCase):
    def test_handoff_includes_exact_identity_and_byte_checksum(self):
        e = event("ARTIFACT_HANDOFF — AAB-IDENTITY-001\n☃")
        actual = inspect(e, RUNTIME)
        self.assertEqual(actual["status"], "IDENTIFIED_PENDING_INDEPENDENT_REVIEW")
        self.assertEqual(actual["task_id"], "AAB-IDENTITY-001")
        self.assertEqual(actual["source_comment_id"], 6231674058)
        self.assertEqual(actual["source_comment_node_id"], "IC_test")
        self.assertEqual((actual["comment_author_login"], actual["comment_author_id"]),
                         ("test-user", 123))
        self.assertEqual((actual["posting_app_slug"], actual["posting_app_id"]),
                         ("cursor", 456))
        self.assertEqual(actual["author_association"], "OWNER")
        self.assertEqual(actual["event_created_at"], e["comment"]["created_at"])
        self.assertEqual(actual["event_updated_at"], e["comment"]["updated_at"])
        self.assertEqual(actual["comment_html_url"], e["comment"]["html_url"])
        self.assertEqual(actual["body_bytes"], len(e["comment"]["body"].encode("utf-8")))
        self.assertEqual(actual["body_sha256"], hashlib.sha256(e["comment"]["body"].encode("utf-8")).hexdigest())
        self.assertEqual(actual["workflow_run_id"], 39017026536)
        self.assertEqual(actual["workflow_run_attempt"], 1)
        self.assertEqual(actual["event_commit_sha"], RUNTIME["GITHUB_SHA"])
        self.assertFalse(actual["verified_review"])

    def test_nonhandoff_preserves_id_and_checksum_without_review(self):
        e = event("Ordinary comment: ☃")
        actual = inspect(e, RUNTIME)
        self.assertEqual(actual["status"], "IGNORED_NOT_HANDOFF")
        self.assertNotIn("task_id", actual)
        self.assertEqual(actual["source_comment_id"], 6231674058)
        self.assertEqual(actual["body_sha256"], hashlib.sha256(e["comment"]["body"].encode("utf-8")).hexdigest())

    def test_wrong_scope_and_edit_ignored(self):
        for e in (event(number=4), event(action="edited"), event()):
            if e["action"] == "created" and e["issue"]["number"] == 2:
                e["repository"]["full_name"] = "someone-else/different"
            self.assertEqual(inspect(e, RUNTIME), {
                "protocol": "AAB-001/handoff-event-v1", "status": "IGNORED", "verified_review": False})

    def test_bad_id_is_fail_closed(self):
        for value in (True, 0, None, "6231674058"):
            e = event()
            e["comment"]["id"] = value
            self.assertEqual(inspect(e, RUNTIME)["status"], "UNVERIFIED_BAD_COMMENT_ID")

    def test_missing_body_is_fail_closed(self):
        e = event()
        del e["comment"]["body"]
        self.assertEqual(inspect(e, RUNTIME)["status"], "UNVERIFIED_BAD_BODY")

    def test_unknown_optional_metadata_is_null_not_fabricated(self):
        e = event()
        del e["comment"]["user"]
        del e["comment"]["performed_via_github_app"]
        r = inspect(e, {})
        self.assertIsNone(r["comment_author_login"])
        self.assertIsNone(r["posting_app_slug"])
        self.assertIsNone(r["workflow_run_id"])
        self.assertIsNone(r["event_commit_sha"])
        self.assertEqual(r["status"], "IDENTIFIED_PENDING_INDEPENDENT_REVIEW")

    def test_oversize_not_accepted_as_handoff(self):
        e = event("ARTIFACT_HANDOFF — AAB-LARGE-001\n" + "a" * 100_000)
        r = inspect(e, RUNTIME)
        self.assertEqual(r["status"], "UNVERIFIED_OVERSIZE")
        self.assertNotIn("task_id", r)
        self.assertEqual(r["body_bytes"], len(e["comment"]["body"].encode("utf-8")))


if __name__ == "__main__":
    unittest.main()
