"""AAB controller v0.1: synthetic, no-network, no-execution safety tests."""
import copy
import unittest

from controller import InvalidState, decide

STATE = {"project": "AAB-001", "repository": "someonee12345678-hue/aab-queue",
         "working_branch": "mc/channel", "checkpoint_status": "VERIFIED_PERSISTED",
         "phase": "ANDROID_DOCTOR_LOCAL_FILE_CHECK_PENDING"}
TASK_A = {"id": "AAB-PHONE-CHECK-001", "title": "Read-only phone revision check",
          "scope_id": "AAB-PHONE-AGENT-001", "role": "OWNER", "kind": "READ_ONLY",
          "status": "READY", "priority": 10, "depends_on": [],
          "evidence": ["2026-10-17 screenshot"], "suggested_owner_action": "git rev-parse HEAD"}
TASK_B = {"id": "AAB-PHONE-DOCTOR-002", "title": "Read-only phone Doctor",
          "scope_id": "AAB-PHONE-AGENT-001", "role": "PHONE_CODEX", "kind": "LOCAL_DIAGNOSTIC",
          "status": "READY", "priority": 5, "depends_on": ["AAB-PHONE-CHECK-001"],
          "evidence": []}
BACKLOG = {"schema_version": 1, "project": "AAB-001",
           "repository": "someonee12345678-hue/aab-queue", "branch": "mc/channel",
           "controller_mode": "PROPOSE_ONLY", "automatic_dispatch_enabled": False,
           "stop_requested": False, "tasks": [TASK_A, TASK_B]}


def fixture():
    return copy.deepcopy(STATE), copy.deepcopy(BACKLOG)


class ControllerTests(unittest.TestCase):
    def test_only_ready_unblocked_task_is_proposed(self):
        s, b = fixture()
        r = decide(s, b, git_ref="mc/channel", git_sha="f" * 40)
        self.assertEqual(r["status"], "PROPOSED_NOT_DISPATCHED")
        self.assertEqual(r["selected"]["id"], "AAB-PHONE-CHECK-001")
        self.assertEqual(r["selected"]["suggested_owner_action"], "git rev-parse HEAD")
        self.assertFalse(r["dispatch_enabled"])
        self.assertFalse(r["agent_executed"])

    def test_completed_dependency_lets_second_task_be_proposed(self):
        s, b = fixture()
        b["tasks"][0]["status"] = "DONE"
        b["tasks"][0]["evidence"] = ["verified phone SHA"]
        r = decide(s, b)
        self.assertEqual(r["selected"]["id"], "AAB-PHONE-DOCTOR-002")
        self.assertIsNone(r["selected"]["suggested_owner_action"])

    def test_done_requires_evidence(self):
        s, b = fixture()
        b["tasks"][0]["status"] = "DONE"
        b["tasks"][0]["evidence"] = []
        with self.assertRaisesRegex(InvalidState, "lacks evidence"):
            decide(s, b)

    def test_stop_switch_overrides_ready_tasks(self):
        s, b = fixture()
        b["stop_requested"] = True
        r = decide(s, b)
        self.assertEqual(r["status"], "STOPPED")
        self.assertIsNone(r["selected"])

    def test_dispatch_cannot_be_switched_on(self):
        s, b = fixture()
        b["automatic_dispatch_enabled"] = True
        with self.assertRaisesRegex(InvalidState, "dispatch"):
            decide(s, b)

    def test_wrong_repository_or_branch_fails_closed(self):
        for key, bad in (("repository", "someone-else/aab-queue"), ("working_branch", "HEAD")):
            s, b = fixture()
            s[key] = bad
            with self.assertRaises(InvalidState):
                decide(s, b)
        s, b = fixture()
        with self.assertRaisesRegex(InvalidState, "runtime git branch"):
            decide(s, b, git_ref="HEAD")

    def test_duplicates_or_unknown_deps_fail_closed(self):
        s, b = fixture()
        b["tasks"].append(copy.deepcopy(b["tasks"][0]))
        with self.assertRaisesRegex(InvalidState, "duplicate"):
            decide(s, b)
        s, b = fixture()
        b["tasks"][1]["depends_on"] = ["AAB-NOT-FOUND"]
        with self.assertRaisesRegex(InvalidState, "unknown"):
            decide(s, b)

    def test_dependency_cycle_fails_closed(self):
        s, b = fixture()
        b["tasks"][0]["depends_on"] = ["AAB-PHONE-DOCTOR-002"]
        with self.assertRaisesRegex(InvalidState, "cyclic"):
            decide(s, b)

    def test_no_eligible_work_is_not_mistaken_for_completion(self):
        s, b = fixture()
        b["tasks"][0]["status"] = "BLOCKED"
        b["tasks"][1]["status"] = "BLOCKED"
        r = decide(s, b)
        self.assertEqual(r["status"], "NO_ELIGIBLE_WORK")
        self.assertIsNone(r["selected"])

    def test_priority_tie_is_stable_by_task_id(self):
        s, b = fixture()
        b["tasks"][1]["depends_on"] = []
        b["tasks"][1]["priority"] = 10
        self.assertEqual(decide(s, b)["selected"]["id"], "AAB-PHONE-CHECK-001")

    def test_invalid_commit_ref_fails_closed(self):
        s, b = fixture()
        with self.assertRaisesRegex(InvalidState, "commit"):
            decide(s, b, git_sha="BAD")

    def test_unverified_checkpoint_is_rejected(self):
        s, b = fixture()
        s["checkpoint_status"] = "UNVERIFIED"
        with self.assertRaisesRegex(InvalidState, "verified"):
            decide(s, b)


if __name__ == "__main__":
    unittest.main()
