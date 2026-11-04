"""AAB-001 MVP app acceptance. Frozen reviewer contract. Python stdlib only."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from app import GoalStore, make_server


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "goals.json"
        self.store = GoalStore(self.db)

    def test_empty_read_does_not_write(self):
        self.assertEqual(self.store.list_goals(), [])
        self.assertFalse(self.db.exists())

    def test_add_returns_real_ids_and_persists(self):
        a = self.store.add_goal("Build test app")
        b = self.store.add_goal("Review code")
        self.assertEqual(a, {"id": 1, "title": "Build test app", "status": "TODO"})
        self.assertEqual(b["id"], 2)
        self.assertEqual(GoalStore(self.db).list_goals(), [a, b])

    def test_update_persists(self):
        self.store.add_goal("Compile")
        result = self.store.set_status(1, "DOING")
        self.assertEqual(result["status"], "DOING")
        self.assertEqual(GoalStore(self.db).set_status(1, "DONE")["status"], "DONE")

    def test_bad_titles_and_status_are_rejected(self):
        for val in ("", " ", "X" * 121, 10, None):
            with self.subTest(val=val), self.assertRaises((ValueError, TypeError)):
                self.store.add_goal(val)
        self.store.add_goal("Valid")
        initial = self.db.read_bytes()
        for val in ("done", "WAIT", "", None):
            with self.subTest(val=val), self.assertRaises((ValueError, TypeError)):
                self.store.set_status(1, val)
        self.assertEqual(self.db.read_bytes(), initial)

    def test_missing_goal_or_corrupt_store_does_not_overwrite(self):
        with self.assertRaises((ValueError, KeyError)):
            self.store.set_status(99, "DONE")
        self.db.write_text("{broken", encoding="utf-8")
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            self.store.list_goals()
        with self.assertRaises(ValueError):
            self.store.add_goal("Do not overwrite corrupt file")
        self.assertEqual(before, self.db.read_bytes())


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        db = Path(self.temp.name) / "goals.json"
        self.server = make_server(db, port=0)
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def request(self, path, method="GET", obj=None):
        data = None if obj is None else json.dumps(obj).encode("utf-8")
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(
            self.base + path, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, response.headers, response.read()

    def test_web_page_is_served(self):
        status, headers, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get_content_type())
        self.assertIn(b"<html", body.lower())
        self.assertIn(b"/api/goals", body)

    def test_http_create_update_reload_and_export(self):
        status, _, raw = self.request("/api/goals", "POST", {"title": "Phone demo"})
        created = json.loads(raw)
        self.assertEqual(status, 201)
        self.assertEqual(created, {"id": 1, "title": "Phone demo", "status": "TODO"})
        status, _, raw = self.request("/api/goals/1", "PATCH", {"status": "DONE"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["status"], "DONE")
        status, _, raw = self.request("/api/goals")
        self.assertEqual([x["status"] for x in json.loads(raw)], ["DONE"])
        status, _, raw = self.request("/api/export")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["goals"][0]["title"], "Phone demo")

    def test_bad_http_input_rejected_without_new_goal(self):
        for bad in ({"title": ""}, {"title": 42}, {"bad": "key"}):
            with self.subTest(bad=bad), self.assertRaises(urllib.error.HTTPError) as caught:
                self.request("/api/goals", "POST", bad)
            self.assertEqual(caught.exception.code, 400)
        _, _, raw = self.request("/api/goals")
        self.assertEqual(json.loads(raw), [])


if __name__ == "__main__":
    unittest.main()
