"""Standard-library tests for progress_report.py (AAB-MVP-APP-002)."""
import copy
import hashlib
import io
import json
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import estimate
import progress_report as pr

HERE = Path(__file__).resolve().parent
SNAP = HERE / "goal_estimates_v01.json"


def load():
    return json.loads(SNAP.read_text(encoding="utf-8"))


def goal(gid, status, lo=1, mode=2, hi=3, evidence=None):
    return {"id": gid, "label": gid + " label", "status": status,
            "active_hours": {"optimistic": lo, "likely": mode, "pessimistic": hi},
            "evidence": evidence}


def snap(*goals):
    return {"project": "P", "target": "T", "as_of_utc": "2026-01-01T00:00:00Z",
            "milestones": list(goals)}


class RealSnapshot(unittest.TestCase):
    def test_counts_and_sections(self):
        r = pr.build_report(load())
        self.assertEqual(r["counts"], {"completed": 2, "unfinished": 6,
                                       "blocked": 0, "total": 8})
        self.assertEqual([g["id"] for g in r["completed_goals"]],
                         ["CI", "GITHUB_EVENT_GATE"])
        self.assertEqual([g["id"] for g in r["unfinished_goals"]],
                         ["BUDGET", "EVENT_ID", "REVIEW_RETURN", "FEEDBACK",
                          "DEMO", "ANDROID"])
        self.assertEqual(r["blockers"], [])
        self.assertEqual(
            [item["id"] for item in r["recorded_achievements"]],
            ["MVP_APP", "CROSS_WAKE", "GITHUB_EVENT_GATE", "AAB_MVP_APP_002"])

    def test_estimates_derived_from_data(self):
        e = pr.build_report(load())["estimate"]
        self.assertEqual(e["remaining_hours_sum"],
                         {"optimistic": 6.0, "likely": 16.25, "pessimistic": 41.0})
        self.assertEqual(e["remaining_days_sum"]["likely"], 2.0)
        self.assertEqual((e["simulated_hours_p50"], e["simulated_hours_p80"]), (21.0, 23.9))
        self.assertEqual((e["simulated_days_p50"], e["simulated_days_p80"]), (2.6, 3.0))

    def test_existing_calculator_unchanged(self):
        out = estimate.forecast(load(), 8)
        self.assertEqual((out["completed"], out["remaining"], out["blocked"]), (2, 6, []))
        self.assertEqual((out["estimated_active_hours_p50"],
                          out["estimated_active_hours_p80"]), (21.0, 23.9))

    def test_text_output(self):
        t = pr.render_text(pr.build_report(load()))
        for s in ("COMPLETED GOALS", "UNFINISHED GOALS", "BLOCKERS",
                  "none recorded in snapshot", "UPDATED TIME ESTIMATES",
                  "p50 21.0, p80 23.9", "Method:"):
            self.assertIn(s, t)


class Behaviour(unittest.TestCase):
    def test_blocked_goal_listed_and_counted(self):
        r = pr.build_report(snap(goal("A", "BLOCKED"), goal("B", "TODO")))
        self.assertEqual([b["id"] for b in r["blockers"]], ["A"])
        self.assertEqual(r["counts"]["unfinished"], 2)
        self.assertEqual(r["estimate"]["remaining_hours_sum"]["likely"], 4.0)

    def test_hours_per_day(self):
        r = pr.build_report(snap(goal("A", "TODO", 4, 4, 4)), hours_per_day=4)
        self.assertEqual(r["estimate"]["remaining_days_sum"]["likely"], 1.0)

    def test_all_done(self):
        r = pr.build_report(snap(goal("A", "DONE", evidence="c1")))
        self.assertEqual(r["counts"]["unfinished"], 0)
        self.assertEqual(r["estimate"]["simulated_hours_p50"], 0)

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            pr.build_report(snap(goal("A", "DONE")))  # DONE without evidence
        with self.assertRaises(ValueError):
            pr.build_report(snap(goal("A", "WAITING")))
        with self.assertRaises(ValueError):
            pr.build_report(snap(goal("A", "TODO", 3, 2, 1)))

    def test_read_only(self):
        data = load()
        before = copy.deepcopy(data)
        file_hash = hashlib.sha256(SNAP.read_bytes()).hexdigest()
        files = sorted(os.listdir(HERE))
        buf = io.StringIO()
        with redirect_stdout(buf):
            pr.main([str(SNAP), "--json"])
        pr.build_report(data)
        self.assertEqual(data, before)
        self.assertEqual(hashlib.sha256(SNAP.read_bytes()).hexdigest(), file_hash)
        self.assertEqual(sorted(os.listdir(HERE)), files)
        self.assertEqual(json.loads(buf.getvalue())["counts"]["total"], 8)


if __name__ == "__main__":
    unittest.main()
