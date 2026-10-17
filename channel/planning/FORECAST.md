# AAB-001 — Goal Tracker and Project ETA v0.1

Snapshot: 2026-10-17 00:19 America/Vancouver. **Planning aid, not an always-on watcher.**

## Delivery status

- VERIFIED: v0.3 automatic wake-to-code, v0.4 GitHub checkpoint/second worker handoff, Grok-built Pocket Task Board v0.1 with ChatGPT's independent 8/8 acceptance pass, source and evidence in GitHub PR #2.
- UNVERIFIED: unattended ChatGPT review/return in response to a Grok application handoff, then unattended Grok continuation on that review. Existing ChatGPT event tasks have narrower operations and previously encountered comment identity/routing issues.
- The user has prioritized a useful early-stage prototype over a fully stabilized final product; the first semi-autonomous program-build and manual-review MVP is already demonstrated.

## Measured duration samples

| Stage | Github timestamps (UTC) | Measured elapsed |
|---|---|---|
| v0.3 signal to coding handoff | 05:18:47 → 05:20:34 | 1m47s |
| v0.4 start to second-worker final handoff | 05:32:23 → 05:36:37 | 4m14s |
| Pocket Task Board handoff to independent ChatGPT result | 06:20:48 → 06:31:50 | 11m02s |

These observations cover **bounded execution windows**, not time spent preparing code/test specifications or solving platform integration. The app reviewer was manually prompted. They cannot be used as an end-to-end autonomous-cycle average yet.

## Current forecast for more autonomous two-way engineering

Inputs are in [goal_estimates_v01.json](./goal_estimates_v01.json), calculated by [estimate.py](./estimate.py). Seven open milestones: free Actions billing safeguards; one minimal CI workflow; reliable event identity; automated review/return; Grok feedback continuation; single full demonstration; optional Android browser smoke test.

A reproducible 20,000-sample triangular-scenario calculation, using subjective optimistic/likely/pessimistic engineering-hour estimates, yields:

| Focused engineering capacity | Midpoint scenario | 80th-percentile scenario |
|---|---:|---:|
| 4 hours/calendar day | 5.8 days | 6.5 days |
| 8 hours/calendar day | 2.9 days | 3.3 days |
| 12 hours/calendar day | 1.9 days | 2.2 days |

Approximate remaining active engineering work under these assumptions: 23.0 hours midpoint and 26.1 hours at the 80th-percentile scenario. These percentile labels are **mathematical outputs of uncalibrated estimates**, not actual success probabilities. Do not treat the table as a promise or a deadline. Platform failures, authorization or billing delays, task retries and scope change can materially increase elapsed time.

**Practical initial planning range for the unattended review-and-feedback loop: approximately 3–5 days.** A bounded semi-autonomous product-development MVP is already achieved. A 24–48h full unattended loop is plausible only if trigger integration cooperates and high focused-worker availability is real.

## Maintenance and operating rules

- GitHub on branch `mc/channel` is the durable server-backed record, not a paid dashboard. Reading and editing the snapshot does not incur Actions minutes.
- Each milestone records status and engineering-hour range. Only change status to `DONE` when accompanied by verifiable source/comment/test evidence. Do not mark a task complete just because an AI reported success.
- Calculator command for Grok/ChatGPT environments: `python3 estimate.py goal_estimates_v01.json --hours-per-day 8` (run inside this directory). The owner should not have to use a terminal.
- Re-run the forecast after each material verified milestone or changed constraint. The estimate should shrink or expand based on actual evidence, not due to optimistic time assumptions.
- **No automatic scheduler, GitHub Actions workflow, task, notification or server has been created for the tracker.** To watch and refresh goals automatically later, reuse a GitHub event-triggered workflow after $0 cost controls and scope authorization are verified.
- No new paid API, GitHub plan, Copilot plan, repository branch change, PR merge or existing automation modification was made.
