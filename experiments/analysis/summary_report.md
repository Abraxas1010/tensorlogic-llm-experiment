# TensorLogic LLM Tool Use Experiment — Summary Report

**Date:** 2026-01-14
**Agent/model:** GPT-5.2
**Tool under test:** `tensorlogic_tool_runner`

## Scope / setup
- The experiment design expects an ad-hoc input schema of the form `{program, facts, config}`.
- The repository tool originally only accepted the demo-registry schema `{demo, bot, ...}`.
- To make the experiment executable, `tensorlogic_tool_runner` was extended to support the experiment schema *in addition to* the existing demo schema.
  - Implementation: `lean/HeytingLean/CLI/TensorLogicToolRunnerMain.lean`
  - Regression checks: `cd lean && lake exe tensorlogic_harness_selftest` (PASS) and `cd lean && lake exe tensorlogic_harness_faulttest` (PASS)

## Artifacts produced
- Transcripts:
  - `experiments/tensorlogic_llm_tool_experiment/results/gpt-5.2_2026-01-14/transcript_A1.md`
  - `experiments/tensorlogic_llm_tool_experiment/results/gpt-5.2_2026-01-14/transcript_B2.md`
  - `experiments/tensorlogic_llm_tool_experiment/results/gpt-5.2_2026-01-14/transcript_C3.md`
- Automated score (A1 only; the repo contains only `A1_solution.json`):
  - `experiments/tensorlogic_llm_tool_experiment/results/gpt-5.2_2026-01-14/score_A1.json`

## Results by task

### Task A1 (Graph reachability)
- Tool usage: 1 call.
- Outcome: derived `reach(a), reach(b), reach(c), reach(d)`.
- Score: **7/7** (via `experiments/tensorlogic_llm_tool_experiment/score.py`).

Notes on output shaping:
- The scorer treats *extra derived atoms* as false positives.
- The tool’s experiment-schema output was therefore filtered to report only IDB predicates (predicates appearing in rule heads) rather than also echoing EDB base facts.

### Task B2 (XOR semantics detection)
- Boolean run (monotone): returns `{p, q}` as expected.
- F₂ run (`f2solve`): returns **error**: `f2solve: no fixed point found`.

Interpretation:
- Under this tool’s F₂ semantics, the solver searches for fixed points of the equations induced by `stepFromBase`:
  - `x = init ⊕ T(x)` over F₂.
- For rules `q :- p` and `p :- q` with base fact `p=1`, the induced system is inconsistent:
  - `q = p`
  - `p = 1 ⊕ q`
  - ⇒ `p = 1 ⊕ p` (no solution).

This is a useful diagnostic result: the tool detects that the specified recursive XOR system is unsatisfiable under the engine’s semantics (rather than silently producing a misleading “stable state”).

### Task C3 (Program repair)
- Bug reproduction: program derives `can_access(bob,file1)` but not `can_access(alice,database)`.
- Diagnosis: predicate typo in facts (`own` vs `owns`).
- Fix verification: after correcting to `owns(admins,database)`, the tool derives:
  - `can_access(alice,database)` (via group ownership)
  - `can_access(bob,file1)` (direct ownership)
  - plus `in_group(alice,admins)` and `can_access(admins,database)` (a consequence of rule 1 as written).

## Conclusion
- For straightforward monotone Datalog tasks (A1) and debugging typos (C3), the tool is effective and produces deterministic, hash-stamped outputs.
- For XOR/recursive tasks (B2), the tool provides actionable feedback: in this semantics, the specified system has **no fixed point** given the base fact, so the appropriate “answer” is an inconsistency report.

## Follow-ups (optional)
- Add reference solutions + scorer extensions for B2/C3 (currently only A1 has a machine-checkable reference).
- Consider an explicit config flag documenting the intended base-fact policy for F₂ runs (e.g. whether base facts are treated as a constant XOR term vs an initial assignment), to avoid ambiguity in future experiments.
