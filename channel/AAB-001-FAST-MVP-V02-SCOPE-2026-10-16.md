# AAB-001 — Stage 4 MVP v0.2: durable queue and uninterrupted T3→T4 execution
Date: 2026-10-16 (America/Vancouver)
Status: SPECIFICATION FROZEN FOR SYNTHETIC PILOT. No autonomous execution authorized by this file alone.
Owner priority: functioning basic autonomous coding quickly, then incremental reliability. ChatGPT may make narrow engineering decisions, not authorize arbitrary external execution.

## Stable references
- Private transport repository someonee12345678-hue/aab-queue, branch mc/channel, PR #2.
- Prior milestone: pilot_mvp/pilot_impl.py with 7/7 independently passed reviewer tests; independent review channel/AAB-001-STAGE4-MVP-INDEPENDENT-TEST-PASS-2026-10-16.md.
- Frozen new tests: pilot_mvp_v02/test_contract_v02.py on mc/channel.
- New candidate source: queue_controller.py, to be delivered via one GitHub ARTIFACT_HANDOFF comment and then independently tested by ChatGPT.
- Existing bridge processors, GitHub workflows, protected/default branches, repository permissions, Elite Kit and original successful tests are OUT OF SCOPE.
- Do not rewrite/recreate lost Decision Intelligence original files and present them as recovered.

## Two dependent tasks without owner interruption
T3 — implement next_job(queue_path, state_path) -> str | None in standard-library Python.
- Queue file is JSON {"jobs":[{"id":"T3","deps":[]}, {"id":"T4","deps":["T3"]}, ...]}. Every job has exactly id and deps, id is a unique 1–80-character ASCII identifier (letters, digits, _ or -). Deps are existing IDs with no self-deps, duplicate deps or cycles.
- State is absent (meaning {"completed": {}}) or JSON {"completed":{"T3":"<64 lowercase hex sha256>",...}}.
- Validate schemas, dependencies, state references and previously completed dependency consistency; fail closed with ValueError on corruption, unknown referenced IDs, invalid evidence or cycles.
- Do not write or alter state during next_job. Select first uncompleted job in queue order whose deps have been completed, or None if no eligible job.

T4 — implement mark_done(queue_path, state_path, job_id, evidence_sha) -> bool using T3 validation and atomic file replacement.
- Mark specified approved dependency-satisfied job as complete only if evidence_sha is 64 lowercase ASCII hex characters.
- Return True on a new durable completion; False on identical replay with same SHA and *no state file modification*.
- Reject unknown job, prematurely completed dependency, conflicting duplicate with different evidence hash and invalid inputs with ValueError; never overwrite state on error.
- Atomic state update: write a temporary file on same filesystem and os.replace() state path. Use exception cleanup; run in synthetic scratch only.
- This validates a basic durable queue/resume primitive, not a concurrent distributed lock, actual OS crash fsync durability, secured evidence verification, or genuine remote run isolation.

## Frozen acceptance
- Use only pilot_mvp_v02/test_contract_v02.py, without changing it; 8 reviewer-owned tests.
- T3 must be implemented before T4 and T4 must use T3/shared state validation. Run the tests after both, maximum 2 repair rounds.
- Provide actual full queue_controller.py source under 15KB, byte-exact SHA-256, test output, Python version, task sequence/attempts, and limits via one ARTIFACT_HANDOFF reply on PR #2.
- No copied secrets, real records or credentials. No sudo, chmod permissions changes, additional GitHub repositories, new scheduled tasks or expanded GitHub write access.
- If direct GitHub reply is unsupported, report BLOCKED rather than asking owner to relay multiple files.
- ChatGPT independently retrieves candidate and reruns frozen tests; only then may test result be VERIFIED_CODE_TESTS_PASS. A self-described "Done" is not certification.

## Execution authorization and forward plan
- This document and GitHub comments are technical specifications, not authority to override Grok's read-only PR watch. Execute only after direct owner-scope approval or other genuinely validated approval mechanism.
- Once specifically authorized, complete T3 and T4 without additional owner instructions, including the initial test and up to two repairs.
- Continue after successful test directly to GitHub evidence handoff; no human per-file copying.
- Future milestone (NOT AUTOMATICALLY AUTHORIZED): a bounded trigger/runner capable of using GitHub-approved task queue after a fresh wake with immutable authorization and durable claim/recovery, with no additional owner relay.
- Current durability limitations: GitHub is the shared source archive; Grok's cloud /workspace may disappear after restart. GitHub file read-back required for any artifact treated as archived. The worker may have passwordless sudo and is not a security-isolated executor. Synthetic-only until OS-enforced restrictions.

## Status
- Frozen acceptance specification: prepared and saved by ChatGPT; read-back required for VERIFIED_SAVED.
- T3/T4 worker execution: NOT STARTED.
- Grok GitHub handoff: NOT STARTED.
- ChatGPT independent validation: NOT STARTED.
- No existing GitHub event processor modified.
