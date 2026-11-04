"""AAB-001 no-cost milestone forecast, standard-library only.

Reads a GitHub-stored JSON snapshot. This is a planning aid, not a promise or
an automatic server-side job. Use evidence to change task status/estimates.
"""
import argparse
import json
import random
from pathlib import Path


def forecast(snapshot, daily_hours=8, iterations=20000, seed=20261017):
    if not 0 < daily_hours <= 24:
        raise ValueError("daily_hours must be between 0 and 24")
    milestones = snapshot["milestones"]
    valid = {"TODO", "DOING", "DONE", "BLOCKED"}
    remaining = []
    for goal in milestones:
        status = goal["status"]
        if status not in valid:
            raise ValueError("unknown status: " + str(status))
        if status == "DONE":
            if not goal.get("evidence"):
                raise ValueError("DONE requires verified evidence: " + goal["id"])
            continue
        estimate = goal["active_hours"]
        lo, mode, hi = (estimate[k] for k in ("optimistic", "likely", "pessimistic"))
        if not (0 <= lo <= mode <= hi):
            raise ValueError("invalid hours for " + goal["id"])
        remaining.append((goal["id"], lo, mode, hi))
    rand = random.Random(seed)
    samples = sorted(sum(rand.triangular(lo, hi, mode)
                         for _, lo, mode, hi in remaining)
                     for _ in range(iterations))
    def percentile(p):
        return round(samples[int((iterations - 1) * p)], 1)
    p50 = percentile(.5)
    p80 = percentile(.8)
    return {
        "project": snapshot["project"],
        "goal": snapshot["target"],
        "as_of": snapshot["as_of_utc"],
        "completed": sum(g["status"] == "DONE" for g in milestones),
        "remaining": len(remaining),
        "blocked": [g["id"] for g in milestones if g["status"] == "BLOCKED"],
        "estimated_active_hours_p50": p50,
        "estimated_active_hours_p80": p80,
        "capacity_hours_per_calendar_day": daily_hours,
        "estimated_calendar_days_p50": round(p50 / daily_hours, 1),
        "estimated_calendar_days_p80": round(p80 / daily_hours, 1),
        "warning": "Judgment-based time estimates, not calibrated probabilities. Assumes continuous access, no new blockers, and no overlapping work; excludes approvals and outages."
    }


def main():
    ap = argparse.ArgumentParser(description="Estimate AAB project remaining duration")
    ap.add_argument("snapshot", type=Path)
    ap.add_argument("--hours-per-day", type=float, default=8)
    args = ap.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    print(json.dumps(forecast(snapshot, args.hours_per_day), indent=2))


if __name__ == "__main__":
    main()
