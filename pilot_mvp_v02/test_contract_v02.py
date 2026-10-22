"""AAB-001 v0.2: frozen tests for durable synthetic job queue. Reviewer-owned."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from queue_controller import next_job, mark_done


class QueueControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.queue = self.folder / "queue.json"
        self.state = self.folder / "state.json"
        self.jobs = [
            {"id": "T3", "deps": []},
            {"id": "T4", "deps": ["T3"]},
            {"id": "T5", "deps": ["T4"]},
        ]
        self.set_queue(self.jobs)

    def set_queue(self, jobs):
        self.queue.write_text(json.dumps({"jobs": jobs}), encoding="utf-8")

    def test_first_and_dependencies(self):
        self.assertEqual(next_job(self.queue, self.state), "T3")
        self.assertFalse(self.state.exists())  # reading does not mutate state
        self.assertTrue(mark_done(self.queue, self.state, "T3", "a" * 64))
        self.assertEqual(next_job(self.queue, self.state), "T4")
        self.assertTrue(mark_done(self.queue, self.state, "T4", "b" * 64))
        self.assertEqual(next_job(self.queue, self.state), "T5")
        self.assertTrue(mark_done(self.queue, self.state, "T5", "c" * 64))
        self.assertIsNone(next_job(self.queue, self.state))

    def test_completion_persists_after_reload(self):
        mark_done(self.queue, self.state, "T3", "a" * 64)
        saved = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(saved, {"completed": {"T3": "a" * 64}})
        self.assertEqual(next_job(self.queue, self.state), "T4")

    def test_duplicate_completion_is_no_op(self):
        mark_done(self.queue, self.state, "T3", "a" * 64)
        before = self.state.read_bytes()
        self.assertFalse(mark_done(self.queue, self.state, "T3", "a" * 64))
        self.assertEqual(self.state.read_bytes(), before)
        with self.assertRaises(ValueError):
            mark_done(self.queue, self.state, "T3", "b" * 64)
        self.assertEqual(self.state.read_bytes(), before)

    def test_out_of_order_and_unknown_blocked(self):
        with self.assertRaises(ValueError):
            mark_done(self.queue, self.state, "T4", "a" * 64)
        with self.assertRaises(ValueError):
            mark_done(self.queue, self.state, "UNKNOWN", "a" * 64)
        self.assertFalse(self.state.exists())

    def test_bad_evidence_blocked(self):
        with self.assertRaises(ValueError):
            mark_done(self.queue, self.state, "T3", "not-a-sha")
        with self.assertRaises(ValueError):
            mark_done(self.queue, self.state, "T3", "A" * 64)
        self.assertFalse(self.state.exists())

    def test_corrupted_state_fails_closed(self):
        self.state.write_text("{bad", encoding="utf-8")
        with self.assertRaises(ValueError):
            next_job(self.queue, self.state)
        with self.assertRaises(ValueError):
            mark_done(self.queue, self.state, "T3", "a" * 64)
        self.assertEqual(self.state.read_text(encoding="utf-8"), "{bad")

    def test_invalid_queue_fails_closed(self):
        for jobs in (
            [{"id": "T3", "deps": []}, {"id": "T3", "deps": []}],
            [{"id": "T3", "deps": ["MISSING"]}],
            [{"id": "T3", "deps": ["T4"]}, {"id": "T4", "deps": ["T3"]}],
        ):
            with self.subTest(jobs=jobs):
                self.set_queue(jobs)
                with self.assertRaises(ValueError):
                    next_job(self.queue, self.state)

    def test_state_with_unknown_completed_job_fails(self):
        self.state.write_text(json.dumps({"completed": {"UNKNOWN": "a" * 64}}), encoding="utf-8")
        with self.assertRaises(ValueError):
            next_job(self.queue, self.state)


if __name__ == "__main__":
    unittest.main()
