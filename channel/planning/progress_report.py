"""AAB-001 read-only progress and completion-time report, standard-library only.

Derives every figure from the goal tracker snapshot (goal_estimates_v01.json)
and the existing calculator estimate.forecast(). Never writes files and never
modifies the snapshot. Planning aid, not a promise.
"""
import argparse
import copy
import json
from pathlib import Path

from estimate import forecast

UNFINISHED = ("TODO", "DOING", "BLOCKED")
METHOD = ("Deterministic sums of each unfinished goal's optimistic/likely/"
          "pessimistic active hours, plus p50/p80 from the existing "
          "estimate.forecast() triangular simulation (seed 20261017, 20,000 "
          "samples). Calendar days = hours / hours per day. Inputs are "
          "subjective, uncalibrated judgments from the snapshot.")


def build_report(snapshot, hours_per_day=8):
    data = copy.deepcopy(snapshot)  # guarantee the caller's data is untouched
    fc = forecast(data, hours_per_day)  # also validates statuses and hours
    completed, unfinished, blockers = [], [], []
    totals = {"optimistic": 0.0, "likely": 0.0, "pessimistic": 0.0}
    for g in data["milestones"]:
        if g["status"] == "DONE":
            completed.append({"id": g["id"], "label": g["label"],
                              "evidence": g["evidence"]})
            continue
        hours = {k: g["active_hours"][k] for k in totals}
        for k in totals:
            totals[k] += hours[k]
        item = {"id": g["id"], "label": g["label"], "status": g["status"],
                "active_hours": hours}
        unfinished.append(item)
        if g["status"] == "BLOCKED":
            blockers.append({"id": g["id"], "label": g["label"],
                             "evidence": g.get("evidence")})
    totals = {k: round(v, 2) for k, v in totals.items()}
    return {
        "project": data["project"],
        "target": data["target"],
        "as_of_utc": data["as_of_utc"],
        "counts": {"completed": len(completed), "unfinished": len(unfinished),
                   "blocked": len(blockers), "total": len(data["milestones"])},
        "completed_goals": completed,
        "recorded_achievements": [dict(m) for m in data.get("completed_milestones", [])],
        "unfinished_goals": unfinished,
        "blockers": blockers,
        "estimate": {
            "hours_per_day": hours_per_day,
            "remaining_hours_sum": totals,
            "remaining_days_sum": {k: round(v / hours_per_day, 1)
                                   for k, v in totals.items()},
            "simulated_hours_p50": fc["estimated_active_hours_p50"],
            "simulated_hours_p80": fc["estimated_active_hours_p80"],
            "simulated_days_p50": fc["estimated_calendar_days_p50"],
            "simulated_days_p80": fc["estimated_calendar_days_p80"],
            "method": METHOD,
            "warning": fc["warning"],
        },
    }


def render_text(r):
    c, e = r["counts"], r["estimate"]
    out = ["AAB progress report: " + r["project"], "Target: " + r["target"],
           "Snapshot as of (UTC): " + r["as_of_utc"],
           "Goals: %d total, %d completed, %d unfinished, %d blocked"
           % (c["total"], c["completed"], c["unfinished"], c["blocked"]), "",
           "COMPLETED GOALS"]
    out += ["- %s: %s [evidence: %s]" % (g["id"], g["label"], g["evidence"])
            for g in r["completed_goals"]] or ["- none"]
    out += ["", "RECORDED ACHIEVEMENTS"]
    out += ["- %s: %s [evidence: %s]" % (g["id"], g["label"], g.get("evidence"))
            for g in r["recorded_achievements"]] or ["- none"]
    out += ["", "UNFINISHED GOALS (optimistic/likely/pessimistic hours)"]
    out += ["- %s [%s]: %s (%s/%s/%s h)" % (
        g["id"], g["status"], g["label"], g["active_hours"]["optimistic"],
        g["active_hours"]["likely"], g["active_hours"]["pessimistic"])
        for g in r["unfinished_goals"]] or ["- none"]
    out += ["", "BLOCKERS"]
    out += ["- %s: %s" % (b["id"], b["label"]) for b in r["blockers"]] \
        or ["- none recorded in snapshot"]
    s, d = e["remaining_hours_sum"], e["remaining_days_sum"]
    out += ["", "UPDATED TIME ESTIMATES (%s focused hours/day)" % e["hours_per_day"],
            "- Summed hours: optimistic %s, likely %s, pessimistic %s"
            % (s["optimistic"], s["likely"], s["pessimistic"]),
            "- Summed days: optimistic %s, likely %s, pessimistic %s"
            % (d["optimistic"], d["likely"], d["pessimistic"]),
            "- Simulated hours: p50 %s, p80 %s" % (e["simulated_hours_p50"], e["simulated_hours_p80"]),
            "- Simulated days: p50 %s, p80 %s" % (e["simulated_days_p50"], e["simulated_days_p80"]),
            "Method: " + e["method"], "Warning: " + e["warning"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only AAB progress report")
    ap.add_argument("snapshot", type=Path)
    ap.add_argument("--hours-per-day", type=float, default=8)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    report = build_report(json.loads(a.snapshot.read_text(encoding="utf-8")),
                          a.hours_per_day)
    print(json.dumps(report, indent=2) if a.json else render_text(report), end="" if not a.json else "\n")


if __name__ == "__main__":
    main()
