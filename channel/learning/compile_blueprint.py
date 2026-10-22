"""AAB-META-001: compile verified architectural lessons into a future-builder blueprint.

Deterministic, offline, standard-library only. Does not run lessons as instructions.
No background process, GitHub API calls, model calls or operational changes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

VALID_STATUSES = {"VERIFIED_OBSERVATION", "UNVERIFIED_OBSERVATION"}
VALID_IMPACTS = {"HIGH", "MEDIUM", "LOW"}
ID_PATTERN = re.compile(r"AAB-L[0-9]{3}\Z")
COMPONENT_PATTERN = re.compile(r"[a-z][a-z0-9_]{1,79}\Z")


def validate(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("invalid ledger schema version")
    if data.get("project") != "AAB-001" or data.get("subgoal") != "AAB-META-001":
        raise ValueError("ledger identity mismatch")
    entries = data.get("lessons")
    if not isinstance(entries, list) or not entries:
        raise ValueError("ledger must have lessons")
    seen = set()
    for l in entries:
        if not isinstance(l, dict):
            raise ValueError("invalid lesson")
        lid = l.get("id")
        if not isinstance(lid, str) or not ID_PATTERN.fullmatch(lid) or lid in seen:
            raise ValueError("missing, malformed or duplicate lesson ID")
        seen.add(lid)
        if l.get("status") not in VALID_STATUSES:
            raise ValueError(f"{lid}: invalid evidence status")
        if l.get("impact") not in VALID_IMPACTS:
            raise ValueError(f"{lid}: invalid impact")
        if type(l.get("priority")) is not int or not 1 <= l["priority"] <= 5:
            raise ValueError(f"{lid}: invalid priority")
        comp = l.get("transfer_component")
        if not isinstance(comp, str) or not COMPONENT_PATTERN.fullmatch(comp):
            raise ValueError(f"{lid}: invalid future component ID")
        for f in ("observation", "failure_pattern", "future_builder_rule", "preflight_test", "root_cause"):
            if not isinstance(l.get(f), str) or not l[f].strip():
                raise ValueError(f"{lid}: missing {f}")
        evidence = l.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(
                isinstance(x, str) and x.strip() for x in evidence):
            raise ValueError(f"{lid}: missing cited evidence")
    return sorted(entries, key=lambda x: (x["priority"], x["id"]))


def build(data):
    items = validate(data)
    lines = [
        "# Future Builder — Evidence-Based Architecture Blueprint",
        "",
        "Generated from AAB-META-001's versioned lessons. Every recommendation is a",
        "**review proposal**, not executable instructions or owner authorization.",
        "",
        f"Origin project: AAB-001. Lessons: **{len(items)}**.",
        "Success in an off-device test is not proof of device readiness or unattended behavior.",
        "",
        "## High-priority preflight architecture",
        "",
    ]
    for l in items:
        lines.extend([
            f"### {l['id']} — {l['transfer_component']} (priority {l['priority']}, {l['impact']})",
            "",
            f"- **Observed:** {l['observation']}",
            f"- **Failure risk:** {l['failure_pattern']}",
            f"- **Proposed design rule:** {l['future_builder_rule']}",
            f"- **Required regression check:** {l['preflight_test']}",
            f"- **Cause:** {l['root_cause']}; source status: {l['status']}",
            f"- **Evidence pointers:** {'; '.join(l['evidence'])}",
            "",
        ])
    lines += [
        "## Review gate for adapting future systems",
        "",
        "1. Retrieve current repository, project rules and newest verified evidence.",
        "2. Compare each design rule with current capabilities and counterexamples.",
        "3. Draft an architectural change request with expected benefit and regressions.",
        "4. Execute a scoped synthetic test only after authorization; keep results auditable.",
        "5. Seek owner approval before altering live permissions, code, prompts, agents or budgets.",
        "6. Adopt accepted lessons in the next builder, preserving original evidence.",
        "",
        "## Not implemented here",
        "",
        "- No model-weight training, autonomous policy self-editing or hidden reasoning capture.",
        "- No GitHub comment execution, browser steering or external machine control.",
        "- No automatic triggers, notifications, task creation or approvals.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline evidence-to-blueprint compiler")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", type=Path, help="optional explicit output path; otherwise stdout")
    args = parser.parse_args(argv)
    data = json.loads(args.ledger.read_text(encoding="utf-8"))
    result = build(data)
    if args.output:
        args.output.write_text(result, encoding="utf-8")
        print("Wrote reviewed-design draft:", args.output)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
