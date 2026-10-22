"""Synthetic, offline-only tests for AAB-EXEC-001."""
import copy
import unittest
from validator_v01 import evaluate as _evaluate


def evaluate(goal, **kwargs):
    options = {"observed_branch": "mc/channel", "observed_commit": "a" * 40,
               "verified_evidence": ("synthetic:proof1",)}
    options.update(kwargs)
    return _evaluate(goal, **options)


def fixture():
    return {
        "schema_version": 1, "project": "AAB-001", "repo": "someonee12345678-hue/aab-queue",
        "branch": "mc/channel", "base_commit": "a" * 40, "goal_id": "AAB-EXEC-001",
        "owner_scope_ref": "OWNER-APPROVED-VALIDATOR-ONLY", "goal_status": "IN_PROGRESS",
        "stop": False, "last_verified_utc": "2026-10-18T12:00:00Z",
        "evidence_checkpoint": "synthetic:fixture",
        "next_authorized_action": None,
        "steps": [
            {"step_id": "step1", "idempotency_key": "key1", "assigned_role": "CHATGPT",
             "status": "VERIFIED", "prerequisite_step_ids": [], "evidence_refs": ["synthetic:proof1"]},
            {"step_id": "step2", "idempotency_key": "key2", "assigned_role": "GROK",
             "status": "READY", "prerequisite_step_ids": ["step1"], "evidence_refs": []}
        ]
    }


class ValidatorTests(unittest.TestCase):
    # Existing 20 test cases retained from the verified baseline.
    def test_resume(self):
        self.assertEqual(evaluate(fixture())["next_step_id"], "step2")

    def test_stale_commit(self):
        self.assertEqual(evaluate(fixture(), observed_commit="b" * 40)["status"], "BLOCKED_INVALID_STATE")

    def test_stale_branch(self):
        self.assertEqual(evaluate(fixture(), observed_branch="main")["status"], "BLOCKED_INVALID_STATE")

    def test_duplicate_key(self):
        x = fixture(); x["steps"][1]["idempotency_key"] = "key1"
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_completed_key(self):
        self.assertIsNone(evaluate(fixture(), completed_keys=["key2"])["next_step_id"])

    def test_stop(self):
        x = fixture(); x["stop"] = True
        self.assertEqual(evaluate(x)["status"], "STOPPED")

    def test_missing_scope(self):
        x = fixture(); x["owner_scope_ref"] = ""
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_unverified_dependency(self):
        x = fixture(); x["steps"][0]["status"] = "REPORTED"
        self.assertIsNone(evaluate(x)["next_step_id"])

    def test_cycle(self):
        x = fixture(); x["steps"][0]["prerequisite_step_ids"] = ["step2"]
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_missing_verified_evidence(self):
        x = fixture(); x["steps"][0]["evidence_refs"] = []
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_no_execution(self):
        self.assertFalse(evaluate(fixture())["execution_authorized"])

    def test_bad_timestamp(self):
        x = fixture(); x["last_verified_utc"] = "2026-10-18"
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_missing_observed_commit(self):
        self.assertEqual(_evaluate(fixture(), observed_branch="mc/channel",
                                   verified_evidence=("synthetic:proof1",))["status"], "BLOCKED_INVALID_STATE")

    def test_missing_observed_branch(self):
        self.assertEqual(_evaluate(fixture(), observed_commit="a" * 40,
                                   verified_evidence=("synthetic:proof1",))["status"], "BLOCKED_INVALID_STATE")

    def test_unverified_evidence(self):
        self.assertEqual(evaluate(fixture(), verified_evidence=())["status"], "BLOCKED_INVALID_STATE")

    def test_partial_evidence_registry(self):
        x = fixture(); x["steps"][0]["evidence_refs"].append("synthetic:missing")
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_inconsistent_completed_goal(self):
        x = fixture(); x["goal_status"] = "VERIFIED_COMPLETE"
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_valid_completed_goal(self):
        x = fixture(); x["goal_status"] = "VERIFIED_COMPLETE"
        x["steps"][1]["status"] = "VERIFIED"; x["steps"][1]["evidence_refs"] = ["synthetic:proof2"]
        self.assertEqual(evaluate(x, verified_evidence=("synthetic:proof1", "synthetic:proof2"))["status"], "NO_ELIGIBLE_STEP")

    def test_fake_scope_not_authority(self):
        x = fixture(); x["owner_scope_ref"] = "FAKE-APPROVAL"
        self.assertFalse(evaluate(x)["execution_authorized"])

    def test_malformed_evidence_registry(self):
        self.assertEqual(evaluate(fixture(), verified_evidence="synthetic:proof1")["status"], "BLOCKED_INVALID_STATE")

    # New malformed-input and resource-bound regression cases.
    def test_too_many_steps(self):
        x = fixture(); x["steps"] *= 51
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_too_many_dependencies(self):
        x = fixture(); x["steps"][1]["prerequisite_step_ids"] = ["step1"] * 101
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_duplicate_dependencies(self):
        x = fixture(); x["steps"][1]["prerequisite_step_ids"] = ["step1", "step1"]
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_too_many_evidence_refs(self):
        x = fixture(); x["steps"][0]["evidence_refs"] = ["synthetic:proof1"] * 101
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_oversized_evidence_reference(self):
        x = fixture(); x["steps"][0]["evidence_refs"] = ["x" * 513]
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_oversized_scope_reference(self):
        x = fixture(); x["owner_scope_ref"] = "x" * 513
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_oversized_evidence_registry(self):
        self.assertEqual(evaluate(fixture(), verified_evidence=["x"] * 10001)["status"], "BLOCKED_INVALID_STATE")

    def test_oversized_completed_key_registry(self):
        self.assertEqual(evaluate(fixture(), completed_keys=["k"] * 10001)["status"], "BLOCKED_INVALID_STATE")

    def test_unknown_top_level_field(self):
        x = fixture(); x["unexpected"] = "value"
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_unknown_step_field(self):
        x = fixture(); x["steps"][0]["unexpected"] = "value"
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_malformed_action_fields(self):
        x = fixture(); x["next_authorized_action"] = {"description": " ", "approval_ref": "x"}
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")

    def test_oversized_action_description(self):
        x = fixture(); x["next_authorized_action"] = {"description": "x" * 1025, "approval_ref": "ref"}
        self.assertEqual(evaluate(x)["status"], "BLOCKED_INVALID_STATE")


if __name__ == "__main__":
    unittest.main()
