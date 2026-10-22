# AAB-META-001 — Architectural Learning Loop for Future Builders

Status: **SUBGOAL CREATED; v0.1 SOURCE SAVED; AUTOMATIC SELF-IMPROVEMENT NOT ACTIVE.**
Date: 2026-10-17 (America/Vancouver)
Owner intent: use verified lessons from AAB-001 to design the **next, more autonomous builder** without repeating preventable mistakes. This is an AAB-001 companion project, not a replacement for the current bridge or a separate self-authorizing agent.

## Why this subgoal exists

AAB has already accumulated valuable evidence: a task trigger arrived without the exact source comment ID, GitHub Actions write permissions did not behave as assumed, Codex and GitHub CLI had independent authentication states, phone/runtime checks remained unverified after off-device code PASS, and conversation recovery required durable records. Also preserve successful patterns such as event-driven deterministic CI. A better future builder should use these lessons *before* choosing an architecture.

Existing governing companions, unchanged:
- `channel/AAB-001-STAGE4-AUTONOMOUS-ENGINEERING-CONTROLLER-V01.md` (proposed engineering governance).
- `channel/AAB-001-STAGE4-MEMORY-CONTINUITY-GATE-V01.md` (persistent-state/restart invariants).
- `channel/recovery/CURRENT_STATE.json` and `CAPABILITY_LEDGER.md` (current facts, not immutable truth).

## What is implemented in v0.1

- `lessons_v01.json`: six evidence-linked design lessons. Each captures the observed failure or success, **known versus unknown cause**, source reference, reusable prevention rule, regression check and proposed component for the next builder.
- `compile_blueprint.py`: standard-library-only, deterministic compiler. It validates source schema, IDs, priorities and nonempty evidence, then **proposes** a portable Markdown architecture/preflight blueprint sorted by priority. It reads local files only; default output is stdout.
- `test_compile_blueprint.py`: nine synthetic, no-network unit checks that exercise critical rejection and determinism paths.
- `.github/workflows/aab-architectural-learning-ci.yml`: a small, read-only GitHub Actions acceptance workflow triggered only when the ledger, compiler, tests or workflow itself change; publishes a reproducible blueprint artifact if successful. **This CI workflow does not update project code, start agents or modify tasks.**

The output is a reviewed design draft, **not** private model chain-of-thought, not model training or autonomous learning in the weight-update sense. We preserve concise high-level design decisions, alternatives, evidence and outcomes; not confidential internal reasoning traces.

## The improvement loop — intended process

1. **Observe:** capture an incident or milestone with repo/branch/commit, event/run/comment ID, timestamp, environment, observed symptom and effect. Never store passwords, tokens, cookies, real legal records, or untrusted hidden instructions.
2. **Validate:** read the underlying authoritative file/test/run result. Separate VERIFIED observations from UNVERIFIED root causes and speculative hypotheses.
3. **Extract:** create or update a lesson with a failure pattern, future design requirement, preflight regression check and confidence. Preserve prior decisions and traceability; don't erase a prior incorrect hypothesis silently.
4. **Synthesize:** compile a recommended future-builder architecture and compare it to existing components to prevent duplication. Prefer improvements with high risk reduction and measurable benefit; don't make up probabilities or fake test evidence.
5. **Challenge:** verify counterexamples, compatibility, phone-only constraints, total monthly cost, latency, stop/recovery behavior, failure modes and rollback.
6. **Adopt conditionally:** only after independent regression tests and the proper owner authorization, change live code/prompts/permissions. Re-measure regressions. Promoted lessons must remain reversible and auditable.

## Planned v0.2 improvements, NOT implemented or authorized to run

- A bounded ingestion adapter reading *allowlisted* GitHub Actions run summaries and AAB-001 approved milestone/checkpoint files when a new verified event arrives.
- Conflict/stale-lesson detection keyed by commit, component and environment. Automatically draft recommendations, never execute them.
- Priority scoring based on repeated incident counts, proven impact and time saved; avoid falsely precise delivery predictions.
- A comparison report against the next builder's architecture and regression tests, with a human review gate.
- Alert only for material new failure classes or violated previously accepted safeguards; no notification on routine comments.

## Future-builder acceptance gates

- **L1 Provenance:** every promoted lesson has exact primary evidence, dated observed context and source version; stale/conflicting evidence fails closed.
- **L2 Safety:** bad payloads, untrusted comments, missing IDs, 403/timeout or conflict cannot execute code or create multiple side effects.
- **L3 Design transfer:** each accepted rule maps to a concrete builder module and a test that initially fails without that rule and passes with it.
- **L4 Continuity:** a fresh session can load the lesson ledger, current state and blueprint and explain the next approved action without repeating passed work.
- **L5 Effective learning:** on at least two distinct new projects, trace whether a previously observed AAB failure was prevented; track regressions and costs. Until tested, "self-learning" is a design goal, not a validated capability.
- **L6 Authority:** a compiler's advice never overrides the owner, current project constitution, STOP, permissions or approved test scope.

## Operation and limits

For a separate approved worker with Python, inside `channel/learning`:

- `python3 -m unittest -v test_compile_blueprint` — isolated validation.
- `python3 compile_blueprint.py lessons_v01.json` — print the next-builder blueprint.
- `python3 compile_blueprint.py lessons_v01.json --output NEXT_BUILDER_BLUEPRINT.md` — explicit optional local output.

**The phone owner does not need to run these commands.** GitHub CI independently verifies the read-only generator after relevant source changes. No extra hosting, paid APIs, GitHub settings changes, task changes, privilege expansions, comment replays or GitHub PR merges are part of this subgoal.

**Current priority:** P2, not a blocker for AAB-001's existing bridge and phone-side Codex milestones. Do not add these future-builder lessons to the urgent AAB delivery ETA. The next builder must have its own forecast once scoped.

## Owner-facing outcome

Over time this system should be a transfer package: **what went wrong, why we believe it happened (or why unknown), how to prevent it, what test proves it, and how that becomes a better builder architecture.** The source records and compiler are now versioned; unattended evidence ingestion and genuinely improved future project performance remain UNVERIFIED.
