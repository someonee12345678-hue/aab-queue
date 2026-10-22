# AAB-001 — Phone-side Codex optional capability checkpoint

Date: 2026-10-18 (owner screenshot, Android Termux)
Status: DEFERRED / AVAILABLE FOR FUTURE PLANNING; no new executor activated.

## Owner-directed priority
Phone-side Codex is an optional execution capability for later, NOT the current primary engineering objective. Continue work on reliable GitHub/Grok/ChatGPT event and durable handoff behavior. Do not expand scope tonight or run new deployment/integration tests.

## Screenshot-observed state (not independent runtime audit)
- Termux working directory: ~/aab-queue
- Codex version: codex-cli 0.162.1
- gh auth status: signed in to github.com as repository owner; token visible only redacted in screenshot. No token value stored here.
- gh auth status reports HTTPS Git and scopes gist, read:org, repo, workflow. These are broad privileges; future automation should avoid using this token by default.
- git status --short --branch reports mc/channel aligned with origin/mc/channel, with no modified files shown.
- git ls-remote and local HEAD matched at screenshot time: 7f92522f8bfcb691239150571bb0653768e6daded (may be stale later).
- Local handoff queue record channel/handoffs/6236560957.json listed. This listing alone does not verify contents or outcome.

## Limits and security gates
- This is a capability registration, not owner approval for phone-side Codex to run new repository writes unattended.
- Existing phone login must stay on device. Never copy GitHub tokens or Codex credentials into GitHub comments, files or third-party machines.
- Use least privilege and constrained worktree/sandbox on later activation. Do not run commands from untrusted PR comments automatically.
- Do not touch GitHub default HEAD, draft PR #2, existing processors, live workflows or historical tests as part of this checkpoint.
- Phone Android battery/process restrictions and automatic background execution remain unverified.

## Revisit trigger
After the core GitHub-to-ChatGPT handoff is reliable, design a bounded, approved phone-side Codex task runner, review required permissions, and demonstrate safe STOP/recovery on synthetic data. No action required from owner now.
