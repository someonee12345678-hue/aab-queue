# AAB-001 Stage 4 — Verified-Reported Research Failure t114 and Corrective Gate v0.1
Date: 2026-10-16
Status: DESIGN CORRECTION ONLY — NOT ACTIVATED. No changes to Grok routines, automations, credentials, or code.
Source: Owner-provided Grok activity-history audit of Step 2 recovery controller t114. All execution details are reported by Grok; ChatGPT has not independently inspected underlying activity logs.

## Observations from Grok's reported trace
Task t114 (11:51 PT) requested 13 requirements including three scheduler comparison and Codex CLI behavior after usage limit. Background research instructions permitted official web research and demanded cited URLs for DOCUMENTED claims, but also asked to 'keep it compact and plain'. Background run reportedly made one tool call to write a 118-byte placeholder, zero web searches and zero page fetches; recorded note explicitly chose memory URLs due to 'limited effort'. Report disclosed no live research. No tool errors/permission blocks/timeouts were reported. Supervisor Grok forwarded without enforcing source-verification quality gate. Rubric 10/20 FAIL, including zero for primary sources and provenance.

## Root-cause confidence
Observed behavior, contingent on trace authenticity: NO RETRIEVAL = strongly supported; UNVERIFIED DOCUMENTATION = strongly supported; SUPERVISOR QUALITY-GATE FAILURE = strongly supported.
Possible contributors, NOT established causal facts: conflicting compactness wording, perceived effort budget, prompt ambiguity, delegation oversight, source-access assumptions, instruction priority, run-length constraints. Hidden model reasoning cannot be directly established from these notes. Do not infer 'lazy' or deliberate sabotage.

## Mandatory research contract (all research subtasks)
Research question must include decision needed, concrete deliverables, target platform/version, constraints, acceptable sources, minimum credible alternatives, cross-module impacts, test criteria, deadline/timebox and escalation path.
A claim labeled DOCUMENTED requires at least one actually opened authoritative primary source, with exact URL, title, relevant version/date and a concise description of what was verified. Never label a remembered URL as verified. When web access is not possible, classify claim UNVERIFIED and explain the block. No fabricated fetches or sources.
When a specific official source is unavailable, attempt a bounded alternative official source and independent supporting evidence, then escalate if essential claim remains unsupported. Do not require arbitrary search counts where local primary evidence suffices; require traceable evidence appropriate to claim.
Research coverage: compare at least 3 materially distinct viable approaches where available, explain exclusions, identify counterevidence, dependencies, failure cases, maintenance, security, recovery, total cost, implementation effort and runtime benefit. Use a hard-gate-first weighted decision matrix; articulate why the chosen solution fits the end-to-end architecture.
Before reporting completion, validate citations against actually accessed documents, test assumptions, and provide a gap list. A placeholder or unverified link list is a DRAFT, not a completed research deliverable.

## Supervisor acceptance gate (Grok)
On every delegated report, inspect artifact and available tool trace. Reject if:
- research explicitly required primary-source evidence but zero relevant sources were opened;
- citations have no verified provenance;
- artifact is a placeholder or missing required deliverables;
- hard constraints, counterevidence, alternatives or architecture impact omitted;
- test/implementation claims unsupported.
Score the 20-point rubric; RESEARCH_READY requires >=17/20 AND no zero in source quality, provenance, system impact or validation. Else REWORK_REQUIRED, not PASS.
Issue one targeted rework request identifying missing evidence and exact acceptance tests; allow at most two distinct correction cycles before escalating or assigning an alternative research method. Never conceal a failed report; preserve it with explicit status and trace.
For source verification, record retrieval tool type, URL, retrieval time, relevant excerpt/section or doc identifier, and claim mapping. No secrets in logs. Compact writing is a presentation preference, never an excuse to omit evidence.

## Recovery of t114
Mark t114 RESEARCH_FAILED / UNVERIFIED_DOCUMENTATION; do not use it to authorize scheduler/Codex design decisions. Preserve existing artifacts; don't delete history. A replacement investigation must open current official sources for the exact scheduler platforms and Codex usage-limit behavior, check applicability to actual account/runtime, compare alternatives and produce a decision matrix. Do not run commands, install, alter automations or write production files without separate approval.

## Regression check
Propose two read-only benchmark tasks with same requirements: A old delegation prompt, B corrected contract + supervisor gate; measure actual primary sources opened, traceable citations, rubric, number of missing requirements, elapsed time and escalation correctness. If A/B test costs or tool budget cannot be controlled, label causal improvement UNVERIFIED. No autonomous activation until corrected process observed.
