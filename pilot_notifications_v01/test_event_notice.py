"""Frozen synthetic validation of AAB-001 event/terminal separation prototype."""
import json
import tempfile
import unittest
from pathlib import Path
from event_notice import accept_event


def ev(n, kind, task="AAB-v01", state=None, evidence="", checked=False, action=False):
    return {"source_comment_id": n, "kind": kind, "task_id": task,
            "final_state": state, "evidence_ref": evidence,
            "review_verified": checked, "owner_action_required": action}


class NoticeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = Path(self.temp.name) / "state.json"

    def test_watch_only_and_duplicate_suppressed(self):
        e = ev(6229005206, "EVENT_OBSERVED")
        self.assertIsNone(accept_event(self.ledger, e)["owner_notice"])
        before = self.ledger.read_bytes()
        self.assertEqual(accept_event(self.ledger, e)["disposition"], "DUPLICATE")
        self.assertEqual(before, self.ledger.read_bytes())

    def test_progress_cannot_create_terminal(self):
        result = accept_event(self.ledger, ev(1, "TASK_PROGRESS"))
        self.assertIsNone(result["owner_notice"])
        self.assertEqual(json.loads(self.ledger.read_text())["terminal"], {})

    def test_independent_review_one_notice(self):
        accept_event(self.ledger, ev(6229049249, "EVENT_OBSERVED"))
        a = accept_event(self.ledger, ev(6229092721, "TASK_TERMINAL", state="COMPLETED", evidence="pilot_mvp/pilot_impl.py#SHA256", checked=True))
        self.assertIn("COMPLETED", a["owner_notice"])
        b = accept_event(self.ledger, ev(6229092722, "TASK_TERMINAL", state="COMPLETED", evidence="pilot_mvp/pilot_impl.py#SHA256", checked=True))
        self.assertIsNone(b["owner_notice"])
        self.assertEqual(len(json.loads(self.ledger.read_text())["notices"]), 1)

    def test_spec_not_authorization(self):
        result = accept_event(self.ledger, ev(6229129210, "EVENT_OBSERVED", task="AAB-v02"))
        self.assertIsNone(result["owner_notice"])
        self.assertNotIn("AAB-v02", json.loads(self.ledger.read_text())["terminal"])

    def test_unverified_completion_rejected_without_mutation(self):
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(5, "TASK_TERMINAL", state="COMPLETED", evidence="worker said pass"))
        self.assertFalse(self.ledger.exists())

    def test_owner_blocker_notification_only_if_verified(self):
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(7, "TASK_TERMINAL", state="BLOCKED", evidence="no auth", action=True))
        notice = accept_event(self.ledger, ev(7, "TASK_TERMINAL", state="BLOCKED", evidence="verified auth gate", checked=True, action=True))["owner_notice"]
        self.assertIn("BLOCKED", notice)
        self.assertIn("owner decision", notice)

    def test_no_done_from_plain_watch(self):
        for n in [10, 11, 12, 13]:
            result = accept_event(self.ledger, ev(n, "EVENT_OBSERVED"))
            self.assertIsNone(result["owner_notice"])

    def test_replay_conflict_fails_closed(self):
        accept_event(self.ledger, ev(1, "EVENT_OBSERVED"))
        before = self.ledger.read_bytes()
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(1, "EVENT_OBSERVED", task="different-task"))
        self.assertEqual(before, self.ledger.read_bytes())

    def test_terminal_conflict_fails_closed(self):
        accept_event(self.ledger, ev(2, "TASK_TERMINAL", state="COMPLETED", evidence="sha:aaa", checked=True))
        before = self.ledger.read_bytes()
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(3, "TASK_TERMINAL", state="FAILED", evidence="sha:bbb", checked=True))
        self.assertEqual(before, self.ledger.read_bytes())

    def test_corrupt_ledger_fails_closed(self):
        self.ledger.write_text("broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(1, "EVENT_OBSERVED"))
        self.assertEqual(self.ledger.read_text(), "broken")

    def test_nonterminal_forged_done_rejected(self):
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(1, "EVENT_OBSERVED", state="COMPLETED", checked=True))
        self.assertFalse(self.ledger.exists())

    def test_replayed_source_id_with_changed_payload_fails_closed(self):
        accept_event(self.ledger, ev(4, "TASK_TERMINAL", state="COMPLETED", evidence="sha:original", checked=True))
        before = self.ledger.read_bytes()
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(4, "TASK_TERMINAL", state="COMPLETED", evidence="sha:replacement", checked=True))
        self.assertEqual(before, self.ledger.read_bytes())

    def test_invalid_event_type_fails_closed(self):
        with self.assertRaises(ValueError):
            accept_event(self.ledger, ev(1, ["EVENT_OBSERVED"]))
        self.assertFalse(self.ledger.exists())


if __name__ == "__main__":
    unittest.main()
