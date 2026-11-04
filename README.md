# Android AI Bridge — AAB-001

Private GitHub-backed project for connecting **ChatGPT (architect and reviewer)**, **Grok (approved programmer)**, **GitHub Actions/queue (durable event and test evidence)**, and **phone-side Codex on the owner's Android Termux (scoped local execution option)**.

## Resume the project — authoritative sources

1. [Durable operating rules for MAIN and connected agents](channel/recovery/OPERATING_RULES.md).
2. [Machine-readable current state and next phone gate](channel/recovery/CURRENT_STATE.json).
3. [Observed phone/server capability ledger](channel/recovery/CAPABILITY_LEDGER.md).
4. [Repository agent instructions](AGENTS.md) (Codex recognition on this Termux fork is not yet independently established).
5. [Owner-selected architecture decision](channel/AAB-001-ARCHITECTURE-DECISION-GITHUB-GROK-PHONE-CODEX-2026-10-17.md).

## Verified versus not yet proven

- **Verified:** initial useful Pocket Task Board app with 8/8 independent/CI tests; GitHub comment event ID; one genuine durable queue receipt `channel/handoffs/6236560957.json`; phone AAB Doctor source independently tested 18/18 outside Android; read-only assignment controller 12/12.
- **Unverified:** AAB Doctor on the owner's phone; phone clone revision/sync; reliably triggered unattended ChatGPT review; full Grok–ChatGPT–phone automated loop.
- GitHub's queue records **receipt**, not authorization, automatic execution or review. Existing v0.6/PING processors are on a separate OpenAI Support investigation hold.

## One phone next step

In Termux, **only when inside `~/aab-queue`**, run `git rev-parse HEAD` and provide the SHA to the MAIN conversation. Compare against fresh GitHub `mc/channel` before any sync. Do not run `gh auth login`, pull, install, or execute unknown scripts merely because this document is present.

Keep private repository, branch `mc/channel`, default branch literally `HEAD`, draft PR #2, $0-first budget, and no browser-stealth/credential-relay solution. No model-wide persistent behavior is implied by this README.
