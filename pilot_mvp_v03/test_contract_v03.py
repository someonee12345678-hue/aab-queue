"""AAB-001 v0.3: frozen synthetic two-task coding contract, Python stdlib only."""
import unittest

from build_summary import parse_result, summarize_results


class ParseResultTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_result("compile:PASS"), ("compile", "PASS"))
        self.assertEqual(parse_result("  smoke_test : FAIL "), ("smoke_test", "FAIL"))
        self.assertEqual(parse_result("build-2:PASS"), ("build-2", "PASS"))

    def test_format_rejected(self):
        for raw in ("", "compile", "compile:WARN", "compile:pass", ":PASS",
                    "0start:PASS", "bad name:PASS", "compile:PASS:extra"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_result(raw)

    def test_type_rejected(self):
        for raw in (None, 12, ["compile:PASS"]):
            with self.subTest(raw=raw), self.assertRaises(TypeError):
                parse_result(raw)


class SummarizeResultsTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize_results([]), {
            "passed": 0, "failed": 0, "total": 0, "overall": "EMPTY"})

    def test_all_pass(self):
        self.assertEqual(summarize_results(["compile:PASS", "smoke:PASS"]), {
            "passed": 2, "failed": 0, "total": 2, "overall": "PASS"})

    def test_mixed(self):
        self.assertEqual(summarize_results(["compile:PASS", "smoke:FAIL", "package:PASS"]), {
            "passed": 2, "failed": 1, "total": 3, "overall": "FAIL"})

    def test_invalid_container(self):
        for raw in (None, "compile:PASS", ("compile:PASS",), 3):
            with self.subTest(raw=raw), self.assertRaises(TypeError):
                summarize_results(raw)

    def test_invalid_item(self):
        for raw in (["compile:PASS", "bad:UNKNOWN"], ["compile:PASS", None]):
            with self.subTest(raw=raw), self.assertRaises((ValueError, TypeError)):
                summarize_results(raw)


if __name__ == "__main__":
    unittest.main()
