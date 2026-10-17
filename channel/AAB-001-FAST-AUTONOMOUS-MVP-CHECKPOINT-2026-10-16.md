# AAB-001 — Fast Autonomous Programming MVP / Durable Recovery Checkpoint
Date: 2026-10-16
Status: ACTIVE ENGINEERING CHECKPOINT — NOT A CLAIM THAT AUTONOMOUS CODING HAS PASSED
Owner direction: Prioritize the fastest working basic autonomous programmer, then build on it. Use engineering judgment for bounded, reversible, zero-cost, synthetic-only changes. Do not require manual multi-file transfers or repeated owner micro-approvals.
Authority: Owner's current direction > existing approved safeguards > this checkpoint. New scope does not approve credentials, production code changes, paid APIs, merges, workflow edits, or removal of safeguards.

## Stable identifiers
- Transport: private GitHub repository someonee12345678-hue/aab-queue, draft PR #2.
- Repository default branch reported by live GitHub metadata: HEAD. Working/development branch: mc/channel.
- Existing ChatGPT PR event processors must remain unchanged; no replay of historical test comments.
- Exact pilot tests: pilot_mvp/test_contract_v01.py on mc/channel. This file is a frozen contract; never change it to satisfy generated code.
- Pilot code file to be produced: pilot_impl.py (candidate, not yet published or approved).

## Preserved versus lost / provenance
- The existing channel/AAB-001-STAGE4-*.md design and audit files on mc/channel are PRESENT in GitHub, but design status does not mean implementation or testing.
- The previously reported Grok files /workspace/aab-decision-v01/ (evaluate.py, DR-1..DR-4, eval.log) are REPORTED MISSING after Grok runtime restart; no exact original recovered or published. DO NOT reconstruct and call originals.
- Grok also reports local /workspace/research-ledger/ and /workspace/stage4-controller/ missing after restart. Their prior conclusions/checks are HISTORICAL USER-SUPPLIED REPORTS, not current active controller guarantees.
- Reported external research-chain anchor: position 3, fc06e34cbc404dad3c5d69c50d0bf7dd47af232139a74b80f6a7819570ad59af. Historical reference only, unverified against lost files.
- Reported prior controller checkpoint hash: ad5093c8bb952a5c38b327e5b3bf211ce5e1a23520b6d5448d6ba22de96b7c79. Historical reference only, controller no longer locally present per Grok.
- No local Grok work is authoritative until source, tests and task state are durably saved and read back by a second party.

## Why we are doing the next pilot
We need a REAL, bounded two-task autonomous programming chain, not another architecture-only audit:
1. T1: Implement normalize_label(text: str) -> str in Python, using ASCII a-z and 0-9 after .lower(), replacing every consecutive run of other characters with '-', trimming '-' from ends, returning 'item' if empty. Non-string input raises TypeError.
2. T2: Without waiting for a new owner instruction, implement unique_labels(values: list[str]) -> list[str] calling T1. Preserve input order, avoid collisions by choosing original normalized label if free, otherwise lowest available suffix '-2', '-3', etc. Reject non-list input or non-string items with TypeError. Do not mutate input.
3. Run frozen tests (7 cases) in pilot_mvp/test_contract_v01.py against a new pilot_impl.py. Only standard-library Python allowed. If tests fail, fix candidate code with at most two repair attempts; preserve failures and final trace.
4. Deliver the exact COMPLETE candidate source text, its SHA-256, test output, environment, worker action evidence and status via one ARTIFACT_HANDOFF comment to PR #2, clearly non-TASK_REQUEST; do not attach multiple separate owner-facing files. If publication fails, declare BLOCKED with evidence and preserve remaining work for later recovery.
5. Reviewer independently checks the GitHub comment, source integrity, and runs the frozen tests against exact supplied code. Pilot PASS only after that independent verification. Grok's own PASS is a claim, not final certification.

## Risk tradeoff and strict scope
- Grok Linux workers reportedly share an account with passwordless sudo. THIS IS NOT A SECURITY-ISOLATED ENVIRONMENT. Do not call it isolated, and do not use any personal or confidential data. This MVP is limited to synthetic source and scratch work, under cooperative restrictions, to measure feasibility of two-task automated coding now. No production, repo settings, secrets, protected branches, workflow or deployment actions permitted by this pilot.
- The external/OS-enforced restricted executor remains a later prerequisite for broad unsupervised real-project write access. This pilot does not satisfy that gate.
- No new token, new integration, new repository or extra owner copy/paste required.
- Abort if pilot would require privileged operations or encounter unresolvable material instruction ambiguity.
- Minimize repeated research. Keep source code and verification evidence as the primary deliverable, not narrative.

## Reporting and recovery
- RUNNING is not COMPLETED. Any background execution state not independently observable is UNVERIFIED.
- Report TASK_ID, exact stage, source hash, frozen test result, exceptions, next action, and GitHub comment ID. Never use 'Done' as proof.
- After worker restart, reload this checkpoint + frozen tests by exact GitHub path. If result artifact is absent, mark work LOST/UNVERIFIED and do not claim prior tests; do not replay uncertain side effects.
- A comment-only source bundle may be durable evidence but is not yet a reviewed GitHub source file; reviewer can publish approved code later.
- Owner should only need to say 'Check GitHub' if automatic reply review isn't configured.

## Status at checkpoint creation
- FROZEN TEST CONTRACT: created by ChatGPT and locally sanity-checked against a private reference implementation; GitHub read-back verification pending.
- G R O K AUTOMATED T1 -> T2 CODING: NOT STARTED.
- EVIDENCE HANDOFF: NOT STARTED.
- CHATGPT INDEPENDENT PILOT VALIDATION: NOT STARTED.
- Existing v0.2 / v0.5.1 communication checkpoints: previously verified; v0.6 real-build return still UNVERIFIED and out of scope.
