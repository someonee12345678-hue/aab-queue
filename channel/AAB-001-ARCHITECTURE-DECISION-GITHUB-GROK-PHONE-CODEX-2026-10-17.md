# AAB-001 — Architecture Decision: GitHub + Grok + Phone-Side Codex
Date: 2026-10-17 (America/Vancouver)
Status: OWNER-SELECTED DIRECTION, RECORDED; integration only partly proven.
Authority: Owner's explicit selection in the MAIN conversation on 2026-10-17. No new permission granted to run arbitrary code or change external systems.

## Selected architecture
- **GitHub** (existing private repository `someonee12345678-hue/aab-queue`): durable transport, checkpoints, scoped handoff queue, independent GitHub Actions evidence, and project goals/forecast. Existing working branch `mc/channel`, default branch literally `HEAD`, draft PR #2 must not be merged.
- **Grok**: authorized project programmer/coordinator, with a separately approved task scope. Use existing Cursor/GitHub posting mechanism only; never infer new work authorization from a GitHub comment.
- **Codex on owner's Android phone via Termux**: optional local, owner-controlled agent/executor for strictly approved engineering tasks, holding its own credentials on the phone. It is NOT a replacement for OpenAI's event-triggered ChatGPT Tasks or an unsupported way to force ChatGPT to wake. The phone agent must not have broad background or filesystem access before appropriate boundaries are checked.
- **ChatGPT**: architect, issue decomposer, independent evidence reviewer, decision-maker and owner-facing checkpoint. Can use connected GitHub tools when available. Do not claim to run persistently on the phone or across sessions without an actual mechanism.

## Efficiency decision and failure-handling contract
1. Prefer existing event-driven GitHub Actions to repeatable manual test/reporting; use only a narrow least-privilege workflow with a verified budget boundary.
2. Execute tests where they are cheapest and most deterministic: Grok's approved local task environment for rapid iteration, GitHub Actions for repeatable independent acceptance. Codex on the phone only when its use materially removes owner work.
3. Separate message identity (GitHub comment ID), receipt, work authorization, execution, review, and terminal notification. A queue receipt is not completion or ChatGPT review.
4. Treat any failed/missing/uncertain event as BLOCKED or UNVERIFIED, never auto-replay or claim success. Use durable SHA/branch/time evidence. Preserve owner STOP, no blind retries or duplicate tasks.
5. Use owner-authenticated CLI login on the phone, not unattended UI/browser-stealth automation; do not export cookies, device codes, passwords, tokens or local auth state into third-party servers or GitHub comments.
6. Operate with fictional/non-sensitive inputs during prototypes; keep personal/legal records and credentials out of Grok's shared VM.
7. Do not purchase APIs, services, GitHub/Copilot upgrades, or alter default branch/PR/task configurations without a scope-specific approval. No invasive phone UI automation.

## Verified / unverified checkpoints
- VERIFIED: GitHub Actions accepted the Pocket Task Board frozen tests (8/8); independent Grok-v0.4 checkpoint pilots; GitHub event gate can capture exact PR comment IDs; 17 synthetic queue safety tests passed.
- VERIFIED: owner-provided screenshot shows Termux `gh` installed and `gh auth status` reports **not logged in**; earlier phone Codex CLI sign-in and `OK` canary were reported successful, but current login has not been rechecked.
- VERIFIED: real Cursor-posted handoff PR #2 comment 6233858121 reached GitHub Actions 39032500246; queue writer returned HTTP 403. Exact failing API request and underlying token policy UNVERIFIED. No live queue file verified.
- UNVERIFIED: phone-side `gh` auth, phone Codex execution with the repo, live queue write, unattended ChatGPT review/return, correct first-live feedback delivery, Android browser smoke test.
- CRITICAL: GitHub CLI authentication on Android is **independent** of both Codex's ChatGPT login and GitHub Actions `GITHUB_TOKEN`. Signing in with `gh` will NOT by itself repair the Actions queue HTTP 403.

## Next work / staged validation
A. Read-only diagnose the existing Actions HTTP 403 at exact request boundary; retain the current synthetic PASS and blocked-receipt evidence, do not replay history.
B. If owner wants local GitHub read/write by phone-side Codex, authenticate `gh` interactively in Termux, privately on the owner's phone; verify only with `gh auth status`. Do not share authentication codes or tokens in chat.
C. Validate minimum read-only phone path before any new phone write, installation or background execution.
D. Only after queue identity and safe grants are verified, connect approved work processing and independent reviewer feedback. Full unattended operation remains unproven until actual evidence.

This is a **project-specific durable architecture decision**, not a model-wide permanent instruction or proof of completed implementation. Review this file on project restart alongside the MAIN resume and latest verified state.
