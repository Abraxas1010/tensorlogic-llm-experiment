# TensorLogic LLM Tool-Use Experiment

<p align="center">
  <strong>Evaluating LLM capabilities in formal logic reasoning via tool use</strong><br/>
  <em>
    A comprehensive evaluation framework for assessing language model performance on Datalog inference,
    semantic understanding, and program debugging tasks using the TensorLogic engine.
  </em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tasks-12-blue" alt="12 Tasks"/>
  <img src="https://img.shields.io/badge/Difficulty_Levels-4-purple" alt="4 Levels"/>
  <img src="https://img.shields.io/badge/GPT--5.2_A1_Score-7%2F7-brightgreen" alt="A1 Score"/>
</p>

---

Part of the broader HeytingLean formal verification project: https://apoth3osis.io

## Executive Summary

This repository contains a complete evaluation framework for assessing LLM tool-use capabilities on formal logic tasks. The framework uses the **TensorLogic Datalog engine** - a certified Lean 4 implementation supporting multiple inference semantics (boolean, F2/XOR, fuzzy, Heyting).

**Key Finding**: The F2 (XOR) solver treats UNSAT as a first-class result, returning a structured `status: "unsat"` response with a witness when no fixed point exists. When given the cyclic rules `q :- p` and `p :- q` with base fact `p=1`, the solver returns UNSAT with a canonical witness because the induced equation `p = 1 XOR p` has no solution in GF(2).

### Evaluation Results (GPT-5.2, 2026-01-14)

| Task | Category | Score | Notes |
|------|----------|-------|-------|
| A1 | Graph Reachability | **7/7** | Perfect precision/recall on derived atoms |
| B2 | XOR Semantics | **Diagnostic** | Correctly identified F2 inconsistency |
| C3 | Program Repair | **Pass** | Diagnosed `own` vs `owns` predicate typo |

## Technical Report

### 1. Motivation

Large language models are increasingly used as tool-calling agents for complex reasoning tasks. However, evaluating their performance on **formal logic** and **program verification** tasks requires:

1. **Deterministic ground truth** - Unlike natural language tasks, logic programs have exact correct answers
2. **Multiple semantics** - Different inference modes (OR, XOR, fuzzy) expose semantic understanding
3. **Debugging capability** - Program repair tasks test diagnostic reasoning

TensorLogic provides an ideal testbed because:
- It produces **hash-stamped outputs** for exact reproducibility
- It supports **multiple inference semantics** under a unified JSON interface
- The engine is **certified in Lean 4** (no sorry/admit), ensuring correctness

### 2. Framework Design

#### 2.1 Task Categories

| Level | Category | Skill Tested |
|-------|----------|--------------|
| A (Basic) | Forward inference | Rule application, fixpoint iteration |
| B (Intermediate) | Semantic comparison | Boolean vs XOR vs fuzzy understanding |
| C (Advanced) | Program debugging | Diagnosis and repair |
| D (Expert) | Cross-semantic analysis | Meta-level reasoning about inference |

#### 2.2 Input Schema

The tool accepts ad-hoc Datalog programs via JSON:

```json
{
  "program": {
    "rules": [
      {
        "head": {"pred": "reach", "args": [{"var": "Y"}]},
        "body": [
          {"pred": "reach", "args": [{"var": "X"}]},
          {"pred": "edge", "args": [{"var": "X"}, {"var": "Y"}]}
        ]
      }
    ]
  },
  "facts": [
    {"atom": {"pred": "start", "args": ["a"]}, "weight": 1.0}
  ],
  "config": {"mode": "boolean", "bot": "monotone"}
}
```

#### 2.3 Output Format

**Success (status: "ok")**
```json
{
  "bundle_hash": "78957183c7774793fb0a62fac81e2a4873177bcf293712433022478e637eeda5",
  "converged": true,
  "facts": [{"atom": {"pred": "reach", "args": ["a"]}, "weight": {...}}],
  "iters": 5,
  "status": "ok"
}
```

**UNSAT (status: "unsat")** - F2 solver found no fixed point
```json
{
  "status": "unsat",
  "message": "f2solve: UNSAT (no fixed point)",
  "witness": {
    "atoms": ["p", "q"],
    "atoms_count": 2,
    "init_bits": [1, 0],
    "contribs": [[0, 1], [1, 0]],
    "conflict_explanation": "x = init ⊕ T(x) has no solution in GF(2)"
  }
}
```

**Status codes:**
- `ok` - Fixed point found, derived facts returned
- `unsat` - F2 solver proved no fixed point exists (with witness)
- `unknown` - Iteration capped / maxAtoms limit reached
- `error` - Parse error or other failure

### 3. Inference Semantics

#### 3.1 Boolean (OR) Mode

Standard Datalog semantics with least fixpoint computation:
- Rules fire when all body atoms are satisfied
- Multiple derivations OR together (idempotent)
- **Guaranteed convergence** to unique least fixpoint

#### 3.2 F2 (XOR) Mode

XOR-based inference over GF(2):
- Rules contribute XOR rather than OR
- Base facts act as constant XOR terms: `x = init(x) XOR T(x)`
- **May have no fixed point** for inconsistent systems
- The `f2solve` bot uses Gaussian elimination for exact solutions

**Critical Insight**: For cyclic rules like:
- `q :- p`
- `p :- q`
- with base fact `p = 1`

The induced system is:
- `q = p`
- `p = 1 XOR q`

Substituting: `p = 1 XOR p`, which has **no solution** in GF(2). The solver returns `status: "unsat"` with a canonical witness (atoms, init bits, contribution matrix) rather than producing arbitrary output.

#### 3.3 Fuzzy Mode

Probabilistic inference with weight propagation:
- Weights multiply through rule applications
- `w(head) = w(body1) * w(body2) * ... * w(rule)`
- Convergence when weight changes fall below threshold

### 4. Detailed Task Results

#### Task A1: Graph Reachability

**Goal**: Given a directed graph, derive all reachable nodes from a start node.

**Program**:
```
reach(X) :- start(X).
reach(Y) :- reach(X), edge(X,Y).
```

**Facts**: `start(a)`, `edge(a,b)`, `edge(b,c)`, `edge(c,d)`

**Expected Output**: `reach(a), reach(b), reach(c), reach(d)`

**GPT-5.2 Result**:
- Correctly constructed JSON request
- Derived exactly `{reach(a), reach(b), reach(c), reach(d)}`
- Score: **7/7** (precision 1.0, recall 1.0)

#### Task B2: XOR Semantics Detection

**Goal**: Explain why the same rules produce different results under boolean vs XOR semantics.

**Program**:
```
q :- p.
p :- q.
```

**Base Fact**: `p = 1`

**Boolean Result**: `{p, q}` - Both atoms are true (mutual support converges)

**F2 Result**:
```json
{"status":"unsat","message":"f2solve: UNSAT (no fixed point)","witness":{...}}
```

**GPT-5.2 Analysis**:
- Correctly ran both modes
- Explained that XOR semantics leads to `p = 1 XOR p` (unsatisfiable)
- Identified that boolean OR is idempotent while XOR is not
- The UNSAT witness provides:
  - `atoms` / `atoms_count` - variables in the system
  - `init_bits` - initial values from base facts
  - `contribs` - contribution matrix from rules
  - `conflict_explanation` - human-readable reason for UNSAT

**Assessment**: Demonstrates semantic understanding of non-monotone logics. The first-class UNSAT response with structured witness enables LLMs to reason about *why* no solution exists.

#### Task C3: Program Repair

**Goal**: Diagnose why a program fails to derive expected facts and fix it.

**Buggy Program**: Access control rules with predicate typo (`own` vs `owns`)

**Symptoms**:
- `can_access(bob, file1)` correctly derived
- `can_access(alice, database)` missing (should be derived via group ownership)

**GPT-5.2 Diagnosis**:
1. Reproduced the bug by running the original program
2. Identified predicate mismatch: facts use `own(admins, database)` but rules expect `owns(G, R)`
3. Corrected to `owns(admins, database)`
4. Verified fix: `can_access(alice, database)` now derived

**Assessment**: Successfully combined tool use with diagnostic reasoning.

### 5. Scoring Methodology

The scorer (`score.py`) evaluates:

| Criterion | Points | Description |
|-----------|--------|-------------|
| `valid_json` | 1 | Well-formed JSON in request |
| `correct_rules` | 2 | Rule count matches expected |
| `correct_facts` | 1 | Fact count matches expected |
| `correct_answer` | 2 | Precision/recall on derived atoms |
| `explanation` | 1 | Sufficient explanation terms |

**Total**: 7 points per task

### 6. Reproducibility

All results are reproducible via:

```bash
# Build the tool
cd lean && lake build tensorlogic_tool_runner

# Run self-tests
lake exe tensorlogic_harness_selftest  # Should PASS
lake exe tensorlogic_harness_faulttest # Should PASS

# Replay task A1
cat experiments/tasks/A1_reachability.json | lake exe tensorlogic_tool_runner

# Score against reference
python3 experiments/score.py \
  experiments/tasks/A1_solution.json \
  experiments/results/gpt-5.2_2026-01-14/transcript_A1.md
```

### 7. Conclusions

1. **Tool-use competence**: GPT-5.2 demonstrated effective use of the TensorLogic JSON interface, correctly constructing requests and interpreting responses.

2. **Semantic understanding**: The model correctly distinguished boolean and XOR semantics, explaining why the same program produces different results.

3. **Diagnostic capability**: The model successfully diagnosed a predicate typo bug and verified its fix.

4. **F2 solver correctness**: The solver's "no fixed point" error for inconsistent XOR systems is **correct behavior**, not a bug. This demonstrates that the tool provides actionable feedback rather than misleading results.

### 8. Future Work

1. **Extended task suite**: Add tasks for fuzzy inference, Heyting semantics, and multi-round debugging
2. **Automated scoring for all tasks**: Currently only A1 has machine-checkable reference
3. **Config flag documentation**: Clarify base-fact policy for F2 runs (constant XOR term vs initial assignment)
4. **Cross-model comparison**: Evaluate Claude, Gemini, and other models on the same tasks

## Quick Start

```bash
# Clone this repository
git clone https://github.com/Abraxas1010/tensorlogic-experiment.git
cd tensorlogic-experiment

# Build the tool
cd lean && lake update && lake build tensorlogic_tool_runner

# Run the experiment framework
python3 experiments/score.py --help

# View results
cat experiments/results/gpt-5.2_2026-01-14/transcript_A1.md
```

## Directory Structure

```
RESEARCHER_BUNDLE/
├── README.md                    # This technical report
├── experiments/
│   ├── EXPERIMENT_DESIGN.md     # Full experiment protocol
│   ├── tasks/
│   │   ├── A1_reachability.json # Task A1 input
│   │   ├── A1_solution.json     # Task A1 reference solution
│   │   ├── B2_xor_semantics.json
│   │   └── C3_program_repair.json
│   ├── results/
│   │   └── gpt-5.2_2026-01-14/
│   │       ├── transcript_A1.md
│   │       ├── transcript_B2.md
│   │       ├── transcript_C3.md
│   │       └── score_A1.json
│   └── analysis/
│       └── summary_report.md
├── scripts/
│   └── score.py                 # Automated scorer
├── lean/                        # Lean 4 source (subset)
│   └── HeytingLean/
│       └── CLI/
│           └── TensorLogicToolRunnerMain.lean
└── artifacts/
    └── experiment_diagram.svg   # Visual overview
```

## Dependencies

- **Lean 4**: `leanprover/lean4:v4.16.0`
- **Python 3**: For scoring script
- **Mathlib**: For HeytingLean library

## License

**Copyright (c) 2022-2026 Equation Capital LLC. All rights reserved.**

This software is available under a **dual licensing model**:
- **AGPL-3.0** for open source, academic, and personal use
- **Commercial License** available for proprietary use

Contact: rgoodman@apoth3osis.io

## Citation

If you use this evaluation framework in your research, please cite:

```bibtex
@software{tensorlogic_experiment,
  title = {TensorLogic LLM Tool-Use Experiment},
  year = {2026},
  note = {Evaluating LLM capabilities in formal logic reasoning via tool use}
}
```

---

<p align="center">
  <em>Part of the <a href="https://apoth3osis.io">HeytingLean</a> formal verification project</em>
</p>
