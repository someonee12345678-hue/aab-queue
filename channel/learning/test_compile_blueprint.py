"""AAB-META-001: no-network synthetic acceptance tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from compile_blueprint import build, main, validate

HERE = Path(__file__).resolve().parent


class BlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((HERE / "lessons_v01.json").read_text(encoding="utf-8"))

    def test_ledger_is_valid_and_contains_six_lessons(self):
        self.assertEqual(len(validate(self.data)), 6)

    def test_priority_is_stable(self):
        items = validate(self.data)
        self.assertEqual([x["priority"] for x in items], sorted(x["priority"] for x in items))

    def test_duplicate_id_is_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["lessons"][1]["id"] = bad["lessons"][0]["id"]
        with self.assertRaises(ValueError):
            validate(bad)

    def test_missing_evidence_is_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["lessons"][0]["evidence"] = []
        with self.assertRaises(ValueError):
            validate(bad)

    def test_invalid_identity_and_status_are_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["project"] = "different-project"
        with self.assertRaises(ValueError):
            validate(bad)
        bad = copy.deepcopy(self.data)
        bad["lessons"][0]["status"] = "OWNER_APPROVED"
        with self.assertRaises(ValueError):
            validate(bad)

    def test_future_rules_preserve_uncertainty(self):
        output = build(self.data)
        self.assertIn("UNVERIFIED", output)
        self.assertIn("GitHub Actions run 39049184153", output)
        self.assertIn("No model-weight training", output)

    def test_output_deterministic_without_mutating_input(self):
        original = copy.deepcopy(self.data)
        first = build(self.data)
        self.assertEqual(first, build(self.data))
        self.assertEqual(original, self.data)
        self.assertEqual(first.count("Required regression check"), 6)

    def test_draft_does_not_claim_approval_or_deployment(self):
        result = build(self.data)
        self.assertIn("review proposal", result)
        self.assertIn("owner approval before", result)
        self.assertIn("No automatic triggers", result)

    def test_explicit_output_is_only_optional_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suggestions.md"
            main([str(HERE / "lessons_v01.json"), "--output", str(path)])
            self.assertEqual(path.read_text(encoding="utf-8"), build(self.data))
            self.assertEqual(len(list(Path(tmp).iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
