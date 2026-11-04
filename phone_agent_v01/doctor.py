#!/usr/bin/env python3
"""AAB Doctor v0.1 - read-only Termux/Android setup diagnostic (AAB-PHONE-AGENT-001).

Usage: python3 doctor.py --json   (or without --json for a human summary)
Read-only: no installs, no network, no file writes, no logins, no env dumps.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys

SCHEMA_VERSION = "aab-doctor/0.1"
MIN_PYTHON = (3, 10)
TIMEOUT_S = 5
MAX_OUT = 200  # characters kept from any command output
# Strict allowlist: tool name -> fixed argv tail. Nothing else is ever run.
ALLOWLIST = {
    "git": ("--version",),
    "gh": ("--version",),
    "codex": ("--version",),
}
REQUIRED = ("git",)
TERMUX_PREFIX = "/data/data/com.termux/files/usr"
VERSION_RE = re.compile(r"\d+\.\d+")
SECRET_RE = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|sk-[A-Za-z0-9_-]{10,}"
    r"|[A-Za-z0-9+/=_-]{32,})")
PATH_RE = re.compile(r"(/data/data/[^\s]*|/home/[^\s]*|/root[^\s]*|/storage/[^\s]*|/sdcard[^\s]*|/Users/[^\s]*)")


def redact(text):
    """Cap length, drop control characters, mask paths and secret-like strings."""
    text = (text or "")[: MAX_OUT * 4]
    text = text.splitlines()[0] if text.strip() else ""
    text = "".join(ch for ch in text if ch.isprintable())
    text = SECRET_RE.sub("[REDACTED]", text)
    text = PATH_RE.sub("[PATH]", text)
    return text[:MAX_OUT]


class Env:
    """Injectable view of the system (tests replace these with fakes)."""

    def __init__(self, which=None, run=None, version_info=None, system=None,
                 isdir=None, path_value=None, has_termux_var=None):
        self.which = which or shutil.which
        self.run = run or self._run
        self.version_info = tuple(version_info or sys.version_info[:3])
        self.system = system or (lambda: platform.system())
        self.isdir = isdir or os.path.isdir
        self.path_value = path_value if path_value is not None else os.environ.get("PATH", "")
        self.has_termux_var = (has_termux_var if has_termux_var is not None
                               else "TERMUX_VERSION" in os.environ)

    @staticmethod
    def _run(argv, timeout):
        p = subprocess.run(argv, shell=False, capture_output=True, text=True,
                           timeout=timeout, stdin=subprocess.DEVNULL,
                           errors="replace")
        return p.returncode, p.stdout, p.stderr


def check(cid, status, detail, action=None):
    return {"id": cid, "status": status, "detail": detail, "action": action}


def check_python(env):
    v = env.version_info
    s = ".".join(str(x) for x in v)
    if v[:2] >= MIN_PYTHON:
        return check("python", "PASS", "Python " + s)
    return check("python", "FAIL", "Python %s is older than 3.10" % s,
                 "Upgrade Python in Termux (pkg upgrade python) - separate owner action")


def check_tool(env, name):
    if name not in ALLOWLIST:
        raise ValueError("not allowlisted: " + name)
    cid = "tool:" + name
    path = env.which(name, path=env.path_value) if env.path_value else None
    if not path:
        st = "FAIL" if name in REQUIRED else "UNVERIFIED"
        return check(cid, st, name + " not found on PATH",
                     "Install %s in Termux - separate owner action" % name)
    try:
        rc, out, err = env.run([path] + list(ALLOWLIST[name]), TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return check(cid, "UNVERIFIED", name + " found but --version timed out",
                     "Re-run later; if it repeats, report to reviewer")
    except OSError as e:
        return check(cid, "UNVERIFIED", "%s found but could not run (%s)" % (name, type(e).__name__),
                     "Check the install of " + name)
    line = redact(out or err)
    if rc != 0 or not VERSION_RE.search(line) or "[REDACTED]" in line:
        return check(cid, "UNVERIFIED", "%s output not a recognisable version: %r" % (name, line),
                     "Report to reviewer; do not paste raw output")
    return check(cid, "PASS", line)


def check_platform(env):
    sysname = redact(env.system())
    termux = env.isdir(TERMUX_PREFIX) or env.has_termux_var
    if termux:
        return check("platform", "PASS", "%s; Termux indicator present" % sysname)
    return check("platform", "UNVERIFIED", "%s; no Termux indicator (not Android/Termux?)" % sysname,
                 "Run this inside the Termux app on the phone")


def check_android_settings(env):
    return check("android_settings", "UNVERIFIED",
                 "Battery optimisation and Android settings cannot be read by this tool",
                 "Check manually only if a reviewer asks")


LIMITATIONS = [
    "Android settings and battery optimisation are never confirmed (no read-only API used).",
    "Only git/gh/codex --version are run; login state and network are not checked.",
    "Paths and secret-like strings are redacted; output is capped at %d characters." % MAX_OUT,
    "A PASS means the version command answered, not that the tool works end to end.",
]


def build_report(env):
    checks = [check_platform(env), check_python(env)]
    checks += [check_tool(env, n) for n in ALLOWLIST]
    checks.append(check_android_settings(env))
    statuses = [c["status"] for c in checks]
    overall = "FAIL" if "FAIL" in statuses else ("UNVERIFIED" if "UNVERIFIED" in statuses else "PASS")
    nxt = next((c["action"] for c in checks if c["status"] == "FAIL" and c["action"]), None)
    if nxt is None:
        nxt = next((c["action"] for c in checks if c["status"] == "UNVERIFIED" and c["action"]
                    and c["id"] != "android_settings"), "No action needed. STOP.")
    return {"schema": SCHEMA_VERSION, "overall": overall, "checks": checks,
            "next_action": nxt, "limitations": LIMITATIONS}


def human(report):
    lines = ["AAB Doctor (%s) overall: %s" % (report["schema"], report["overall"])]
    for c in report["checks"]:
        lines.append("  [%s] %s - %s" % (c["status"], c["id"], c["detail"]))
    lines.append("Next: " + report["next_action"])
    lines.append("STOP. Do not run anything else.")
    return "\n".join(lines)


def main(argv=None, env=None, out=None):
    out = out or sys.stdout
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv not in ([], ["--json"]):
            raise ValueError("usage: python3 doctor.py [--json]")
        report = build_report(env or Env())
        out.write((json.dumps(report, indent=2, sort_keys=True) if argv else human(report)) + "\n")
        return 0
    except Exception as e:  # tool-level error -> nonzero, no traceback/secret leak
        out.write(json.dumps({"schema": SCHEMA_VERSION, "error": redact(str(e)) or type(e).__name__}) + "\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
