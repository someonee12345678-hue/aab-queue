# AAB-001 Durable Handoff Queue — v1

**Status:** Installed 2026-10-17. GitHub synthetic tests: 9/9 PASS, Actions run 39019369595. **A live Grok handoff has not yet proven the new queue-writing route.**

## Source of truth
- GitHub's existing default-branch workflow `.github/workflows/aab-handoff-event-gate.yml` receives newly created PR #2 top-level `issue_comment` events and saves its original read-only classification artifact.
- `.github/scripts/aab_queue_writer.py` re-fetches any eligible source comment by its numeric ID and compares GitHub-reported repository, PR, author, posting app, creation time, original event content checksum and the first-line `ARTIFACT_HANDOFF — AAB-...` header.
- Only newly created comments strictly after **2026-10-17T08:52:11Z** are eligible. No historical backfill. Only the independently verified owner/Cursor posting pattern is allowed.
- Qualifying comments create `channel/handoffs/<source_comment_id>.json` on `mc/channel`. A record contains metadata and checksum **only**, not the comment body or executable content.
- Existing matching records are preserved unchanged. Conflicts or uncertain writes are reported as blocked without automatic retry.
- The only GitHub token write permission added is `contents: write` on the event-classifier job, paired with `issues: read`. The synthetic push-test job is read-only; the workflow does not post comments or execute submitted code.

## Meaning of record status
`PENDING_INDEPENDENT_REVIEW` and `review_status: NOT_PERFORMED` indicate an unreviewed receipt; they are **not** proof of an authorized Grok worker, ChatGPT review, accepted source code, completed work, or exactly-once delivery.

The queue does not itself awaken or route a specific record to a ChatGPT review processor. The existing ChatGPT v0.6 and PING processors remain separate and untouched. Automatic ChatGPT review, verification of a fresh live queue entry, and feedback to Grok are outstanding milestones.

## Evidence
- Workflow commit `0c754e17906ff14a5a052f6665bf9a4442164178` (default HEAD).
- GitHub Actions synthetic run `39019369595`: nine tests PASS.
- No old PR comment was replayed, and no synthetic GitHub comment was created.
