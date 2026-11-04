# AAB-001 — Goal Tracker and Project ETA v0.1

Updated: 2026-10-17 00:46 America/Vancouver. **Planning aid, not an always-on forecast watcher.**

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

Inputs are in [goal_estimates_v01.json](./goal_estimates_v01.json), calculated by [estimate.py](./estimate.py). Completed: GitHub CI and the native GitHub comment-event identity gate. Remaining: free Actions billing/allowance verification, **ChatGPT reviewer** event identity/dispatch, automatic review/return, Grok feedback continuation, single full demonstration, and optional Android browser smoke test. GitHub comment event identity does NOT prove ChatGPT's own event processing.

A reproducible 20,000-sample triangular-scenario calculation, using subjective optimistic/likely/pessimistic engineering-hour estimates, yields:

| Focused engineering capacity | Midpoint scenario | 80th-percentile scenario |
|---|---:|---:|
| 4 hours/calendar day | 5.3 days | 6.0 days |
| 8 hours/calendar day | 2.6 days | 3.0 days |
| 12 hours/calendar day | 1.8 days | 2.0 days |

Approximate remaining active engineering work under these assumptions: 21.0 hours midpoint and 23.9 hours at the 80th-percentile scenario. Verified GitHub CI and the event gate are marked DONE in the input snapshot. These percentile labels are **mathematical outputs of uncalibrated estimates**, not actual success probabilities. Do not treat the table as a promise or a deadline. Platform failures, authorization or billing delays, task retries and scope change can materially increase elapsed time.

**Practical initial planning range for the unattended review-and-feedback loop: approximately 3–5 days.** A bounded semi-autonomous product-development MVP is already achieved. A 24–48h full unattended loop is plausible only if trigger integration cooperates and high focused-worker availability is real.

## Maintenance and operating rules

- GitHub on branch `mc/channel` is the durable server-backed record, not a paid dashboard. Reading and editing the snapshot does not incur Actions minutes.
- Each milestone records status and engineering-hour range. Only change status to `DONE` when accompanied by verifiable source/comment/test evidence. Do not mark a task complete just because an AI reported success.
- Calculator command for Grok/ChatGPT environments: `python3 estimate.py goal_estimates_v01.json --hours-per-day 8` (run inside this directory). The owner should not have to use a terminal.
- Re-run the forecast after each material verified milestone or changed constraint. The estimate should shrink or expand based on actual evidence, not due to optimistic time assumptions.
- **The forecast tracker does not yet update itself.** Two separate GitHub Actions workflows now exist: CI on mc/channel and read-only issue-comment event identification on default HEAD. Their verified outcomes can inform tracker updates; neither currently writes to tracker status fields. A future update must require verifiable outcome evidence and fail closed on concurrent/dubious writes.
- No new paid API, GitHub plan or Copilot plan was purchased. The default branch remains named HEAD, PR #2 remains draft and the existing AAB ChatGPT/Grok processors were not modified. The new read-only GitHub issue-comment workflow and its default-branch script are additional, not replacements.
