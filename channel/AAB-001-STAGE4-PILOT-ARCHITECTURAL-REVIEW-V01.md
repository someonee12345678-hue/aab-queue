# AAB-001 — Stage 4 Pilot Architectural Review and Corrections v0.1
Date: 2026-10-16
Status: PROPOSED — READ-ONLY DESIGN. NO PILOT ACTIVATION OR WRITE AUTHORIZATION.
Companions: STAGE4-AUTONOMOUS-ENGINEERING-CONTROLLER-V01, STAGE4-MEMORY-CONTINUITY-GATE-V01, STAGE4-RESEARCH-ROOT-CAUSE-AUDIT-V01. This is an amendment, not a replacement; higher-authority policy remains in force.

## New evidence from Grok
Grok reports no repository-scoped write credential, no verified file write/push path, and STOP/retry enforcement dependent on agent instructions. No isolated pilot repository. These are blockers, not implicit approval to install apps, mint tokens, create a repo, or start a schedule. The Linux runtime and persistence are reported but unattended multi-step operation remains UNVERIFIED.

## Reviewed corrections
1. Least privilege: require an independently verified credential restricted to pilot repository and only needed operations, stored only in Grok-controlled secure environment; do not place tokens in GitHub repo, comments, Termux, reports or logs. A selected-repository GitHub App installation may be viable but must verify actual permission scope and token handling. Fine-grained PAT requires explicit owner approval; never ask owner to paste it into chat.
2. Code+checkpoint in one Git commit is good when both live in the same branch and are committed together. However claim must precede side effects; reserve task with a separate compare-and-swap claim, then implement, then atomically commit code+status. Crash between push and acknowledgment requires reconciliation by exact commit and operation ID.
3. CAS push must be tested with the actual git hosting permissions, branch configuration and concurrency model. Read HEAD, create claim based on expected HEAD, push non-force; if rejected, re-read to determine if another run claimed or an unrelated update happened; do not blindly retry. Git push non-fast-forward behavior alone is not a general exclusive lease or crash-proof lock. Avoid overlapping runs; use a single active run or externally enforced lock/lease if supported.
4. Each wake must read pinned policy version/hash, current approved backlog and checkpoint from authoritative repo, verify their schema and authority, STOP, run count, permissions, dependency graph and live remote SHA. Fresh clone is useful but not sufficient for consistency; compare remote state before each write. If missing, corrupt, stale or conflicting, stop affected operation.
5. Policy pinning must not let an agent self-approve a new policy version. Changes to authority, constraints, acceptance tests or write scope require explicit owner approval and recorded provenance.
6. R2 must inject a true interruption or equivalent controlled failure exactly after a remote write but before local acknowledgment/checkpoint; verify by remote query that restart finds existing operation and does not duplicate. A SIMULATED_CRASH marker alone is insufficient.
7. Six-run cap must be durable and enforceable. Count each wake/attempt including blocked runs. Require no overlapping runs. Verify schedule cadence supported; do not assume 15 minutes. If only agent-side counter/STOP, classify hard-limit enforcement UNVERIFIED and avoid unattended writes.
8. STOP file is cooperative only; authoritative stop is an externally controllable pause/disable/revoke permission. Confirm controller can observe stop before each side effect. A routine's ability to self-delete is UNVERIFIED until demonstrated; don't depend on it.
9. Stage A read-only tests: R1 cold start, R4 missing/corrupt state, R7 stop response, R8 forbidden scope. Stage B only after verified scope and explicit approval: T1 and T2 with injected bug, R2 actual interruption boundary, R3 stale state, R5 conflicting instructions, R6 retry persistence. No Android SDK, builds, GitHub Actions, secrets, merges, deployments or existing AAB-001 processor modifications.

## Dependency-ordered gates
G0 Approved pilot scope, explicit permission matrix, objective, evidence criteria, cost=0, no impact to existing repo or tasks.
G1 Verify available server-side run scheduling, overlap prevention, durable state, independent hard stop, credential scope, file-write path; record PASS/FAIL/UNVERIFIED with evidence.
G2 Verify policy reload and read-only failure behavior from cold start without relying on conversation memory.
G3 Isolated write authorization and narrow CAS claim proof; only in pilot repo.
G4 T1/T2 unattended chaining, actual interrupted-write reconciliation, synthetic failure and architectural checks.
G5 T3 escalation and full negative-scope audit; independent review and owner sign-off.
No stage skipped. Existing v0.5.1 PASS and v0.6 UNVERIFIED status unchanged.

## Research/architecture obligations
Before selecting a pilot implementation, compare three viable mechanisms when available (GitHub App selected-repo, fine-grained PAT, or other supported delegated auth); evaluate operational overhead, revocation, blast radius, lifecycle, permissions and failure recovery. No credentials until explicit owner approval. Grok must submit a bounded decision brief with evidence, recommended least-privilege path, fallback, and test. ChatGPT independently checks system-wide coupling, trust boundaries, portability and recovery. No broad rewrites for a five-second performance improvement.

## Next single action
Grok to perform READ-ONLY feasibility of G1: provide observed evidence for available git push/write tool, actual token/app repo scope, external pause/disable and schedule overlap behavior, and a safe alternative when any is unsupported. No implementation or credential changes.
