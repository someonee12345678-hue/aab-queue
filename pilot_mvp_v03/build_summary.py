"""AAB-001 v0.3 synthetic build summary (T5 parse_result, T6 summarize_results). Stdlib only."""
import re

_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}", re.ASCII)
_STATUSES = ("PASS", "FAIL")


def parse_result(line):
    """T5: parse 'name:STATUS' into (name, status). TypeError for non-str, ValueError if malformed."""
    if not isinstance(line, str):
        raise TypeError("line must be a str")
    if line.count(":") != 1:
        raise ValueError("line must contain exactly one ':'")
    raw_name, raw_status = line.split(":")
    name, status = raw_name.strip(), raw_status.strip()
    if not name.isascii() or _NAME_RE.fullmatch(name) is None:
        raise ValueError(f"invalid name: {name!r}")
    if status not in _STATUSES:
        raise ValueError(f"invalid status: {status!r}")
    return name, status


def summarize_results(lines):
    """T6: count PASS/FAIL using parse_result; any bad member invalidates the whole input."""
    if not isinstance(lines, list):
        raise TypeError("lines must be a list")
    parsed = [parse_result(item) for item in lines]  # reuse T5; raises before any counting
    passed = sum(1 for _, status in parsed if status == "PASS")
    failed = sum(1 for _, status in parsed if status == "FAIL")
    total = len(parsed)
    if total == 0:
        overall = "EMPTY"
    elif failed:
        overall = "FAIL"
    else:
        overall = "PASS"
    return {"passed": passed, "failed": failed, "total": total, "overall": overall}
