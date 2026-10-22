"""AAB-001 v0.4 frozen reviewer-owned cross-wake coding contract (synthetic)."""
import unittest

from ticket_queue import parse_ticket, pick_ticket


class TicketTests(unittest.TestCase):
    def test_parse_valid(self):
        self.assertEqual(parse_ticket("JOB42|HIGH"), ("JOB42", "HIGH"))
        self.assertEqual(parse_ticket("  BUILD_2 | LOW "), ("BUILD_2", "LOW"))
        self.assertEqual(parse_ticket("A|MEDIUM"), ("A", "MEDIUM"))

    def test_parse_rejects_bad_format(self):
        for raw in ("", "JOB42", "JOB42|", "|HIGH", "JOB42|high",
                    "JOB42|URGENT", "job42|HIGH", "1JOB|HIGH",
                    "BAD JOB|LOW", "JOB42|HIGH|EXTRA", "Å|HIGH",
                    "A" * 25 + "|LOW"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_ticket(raw)

    def test_parse_rejects_bad_types(self):
        for raw in (None, 1, ["A|HIGH"]):
            with self.subTest(raw=raw), self.assertRaises(TypeError):
                parse_ticket(raw)

    def test_pick_priority_over_order(self):
        self.assertEqual(pick_ticket(["LOW_JOB|LOW", "MED_JOB|MEDIUM", "TOP_JOB|HIGH"]), "TOP_JOB")
        self.assertEqual(pick_ticket(["LOW_JOB|LOW", "MED_JOB|MEDIUM"]), "MED_JOB")

    def test_pick_stable_ties(self):
        self.assertEqual(pick_ticket(["A|HIGH", "B|HIGH", "C|LOW"]), "A")
        self.assertEqual(pick_ticket(["A|LOW", "B|LOW"]), "A")

    def test_pick_empty(self):
        self.assertIsNone(pick_ticket([]))

    def test_pick_requires_list(self):
        for raw in (None, "A|HIGH", ("A|HIGH",), 1):
            with self.subTest(raw=raw), self.assertRaises(TypeError):
                pick_ticket(raw)

    def test_pick_rejects_invalid_member(self):
        for raw in (["A|HIGH", "B|urgent"], ["A|HIGH", None]):
            with self.subTest(raw=raw), self.assertRaises((TypeError, ValueError)):
                pick_ticket(raw)


if __name__ == "__main__":
    unittest.main()
