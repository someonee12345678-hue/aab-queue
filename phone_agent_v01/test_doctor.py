"""Frozen simulated tests for AAB Doctor v0.1. All data fictional."""
import io
import json
import os
import socket
import subprocess
import tempfile
import unittest
from unittest import mock

import doctor

FAKE_BIN = {"git": "/fake/bin/git", "gh": "/fake/bin/gh", "codex": "/fake/bin/codex"}
GOOD = {"git": "git version 2.47.0", "gh": "gh version 2.60.1 (2026-01-01)", "codex": "codex-cli 0.40.0"}


def make_env(present=FAKE_BIN, outputs=GOOD, timeout=(), version=(3, 12, 1),
             termux=True, path="/fake/bin", calls=None):
    def which(name, path=None):
        return present.get(name)

    def run(argv, t):
        if calls is not None:
            calls.append(list(argv))
        name = os.path.basename(argv[0])
        if name in timeout:
            raise subprocess.TimeoutExpired(argv, t)
        return 0, outputs[name], ""
    return doctor.Env(which=which, run=run, version_info=version, system=lambda: "Linux",
                      isdir=lambda p: termux, path_value=path, has_termux_var=False)


def by_id(rep):
    return {c["id"]: c for c in rep["checks"]}


class DoctorTests(unittest.TestCase):
    def test_all_present_pass(self):
        r = doctor.build_report(make_env())
        self.assertEqual(by_id(r)["tool:gh"]["status"], "PASS")
        self.assertEqual(r["overall"], "UNVERIFIED")  # android_settings is always UNVERIFIED

    def test_missing_gh_and_codex(self):
        r = by_id(doctor.build_report(make_env(present={"git": "/fake/bin/git"})))
        self.assertEqual(r["tool:gh"]["status"], "UNVERIFIED")
        self.assertEqual(r["tool:codex"]["status"], "UNVERIFIED")
        self.assertIn("not found", r["tool:codex"]["detail"])

    def test_missing_required_git_fails(self):
        r = doctor.build_report(make_env(present={}))
        self.assertEqual(by_id(r)["tool:git"]["status"], "FAIL")
        self.assertEqual(r["overall"], "FAIL")

    def test_timeout(self):
        r = by_id(doctor.build_report(make_env(timeout=("codex",))))
        self.assertEqual(r["tool:codex"]["status"], "UNVERIFIED")
        self.assertIn("timed out", r["tool:codex"]["detail"])

    def test_malformed_output(self):
        out = dict(GOOD, gh="\x1b[31m!!garbage\x00\nsecond line")
        c = by_id(doctor.build_report(make_env(outputs=out)))["tool:gh"]
        self.assertEqual(c["status"], "UNVERIFIED")
        self.assertNotIn("\x1b", c["detail"])
        self.assertNotIn("second line", c["detail"])

    def test_unsafe_output_secret_and_path_redacted(self):
        out = dict(GOOD, gh="gh 2.0 token ghp_FAKEFAKEFAKEFAKE1234 at /data/data/com.termux/files/home/x")
        c = by_id(doctor.build_report(make_env(outputs=out)))["tool:gh"]
        self.assertEqual(c["status"], "UNVERIFIED")
        self.assertNotIn("ghp_", c["detail"])
        self.assertNotIn("/data/data", c["detail"])

    def test_output_length_capped(self):
        out = dict(GOOD, git="git version 2.1 " + "x " * 5000)
        c = by_id(doctor.build_report(make_env(outputs=out)))["tool:git"]
        self.assertLessEqual(len(c["detail"]), doctor.MAX_OUT)

    def test_unusual_path_empty(self):
        r = by_id(doctor.build_report(make_env(path="")))
        self.assertEqual(r["tool:git"]["status"], "FAIL")

    def test_unusual_path_odd_chars(self):
        r = by_id(doctor.build_report(make_env(path="/odd dir:;rm -rf /:$(x)")))
        self.assertEqual(r["tool:git"]["status"], "PASS")  # PATH is only passed to which()

    def test_impossible_prerequisite_old_python(self):
        r = doctor.build_report(make_env(version=(3, 8, 0)))
        self.assertEqual(by_id(r)["python"]["status"], "FAIL")
        self.assertEqual(r["overall"], "FAIL")

    def test_allowlist_and_shell_false(self):
        calls = []
        doctor.build_report(make_env(calls=calls))
        for argv in calls:
            self.assertEqual(argv[1:], ["--version"])
        with self.assertRaises(ValueError):
            doctor.check_tool(make_env(), "rm")
        with mock.patch("subprocess.run") as m:
            m.return_value = subprocess.CompletedProcess([], 0, "v 1.2", "")
            doctor.Env._run(["/fake/bin/git", "--version"], 5)
            self.assertIs(m.call_args.kwargs["shell"], False)
            self.assertEqual(m.call_args.kwargs["timeout"], 5)

    def test_android_settings_never_confirmed(self):
        c = by_id(doctor.build_report(make_env()))["android_settings"]
        self.assertEqual(c["status"], "UNVERIFIED")

    def test_not_termux(self):
        c = by_id(doctor.build_report(make_env(termux=False)))["platform"]
        self.assertEqual(c["status"], "UNVERIFIED")

    def test_json_format_and_exit_zero(self):
        buf = io.StringIO()
        rc = doctor.main(["--json"], env=make_env(present={}), out=buf)
        self.assertEqual(rc, 0)
        d = json.loads(buf.getvalue())
        self.assertEqual(d["schema"], "aab-doctor/0.1")
        for c in d["checks"]:
            self.assertIn(c["status"], ("PASS", "FAIL", "UNVERIFIED"))
        self.assertTrue(d["limitations"])

    def test_human_output_has_stop(self):
        buf = io.StringIO()
        self.assertEqual(doctor.main([], env=make_env(), out=buf), 0)
        self.assertIn("STOP", buf.getvalue())

    def test_tool_error_nonzero(self):
        buf = io.StringIO()
        self.assertEqual(doctor.main(["--bogus"], env=make_env(), out=buf), 2)
        env = make_env()
        env.system = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        buf = io.StringIO()
        self.assertEqual(doctor.main(["--json"], env=env, out=buf), 2)
        self.assertIn("error", json.loads(buf.getvalue()))

    def test_no_secret_or_env_disclosure(self):
        fake = {"GH_TOKEN": "ghp_FICTIONAL0000000000", "OPENAI_API_KEY": "sk-FICTIONAL0000000000"}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, fake):
            doctor.main(["--json"], env=make_env(), out=buf)
        text = buf.getvalue()
        for v in list(fake) + list(fake.values()):
            self.assertNotIn(v, text)
        self.assertNotIn("/fake/bin", text)

    def test_no_network_no_writes(self):
        def deny(*a, **k):
            raise AssertionError("network attempted")
        real_open = open

        def guarded_open(f, mode="r", *a, **k):
            if any(ch in mode for ch in "wax+"):
                raise AssertionError("write attempted")
            return real_open(f, mode, *a, **k)
        with tempfile.TemporaryDirectory() as d:
            before = os.listdir(d)
            cwd = os.getcwd()
            os.chdir(d)
            try:
                with mock.patch.object(socket, "socket", deny), \
                     mock.patch.object(socket, "create_connection", deny), \
                     mock.patch("builtins.open", guarded_open):
                    rc = doctor.main(["--json"], env=make_env(), out=io.StringIO())
            finally:
                os.chdir(cwd)
            self.assertEqual(rc, 0)
            self.assertEqual(os.listdir(d), before)


if __name__ == "__main__":
    unittest.main()
