# TensorLogic LLM Tool Use Experiment

**Version:** 1.0
**Date:** 2026-01-14
**Purpose:** Evaluate LLM agent capability to use the TensorLogic tool suite for reasoning tasks

---

## 1. Experiment Overview

### 1.1 Hypothesis

An LLM agent can effectively use the `tensorlogic_tool_runner` to:
1. Formulate Datalog programs from natural language specifications
2. Select appropriate inference modes for different problem types
3. Interpret results and explain reasoning
4. Detect and handle edge cases (F₂ divergence, non-monotone programs)

### 1.2 Tool Interface

The agent interacts via JSON requests to `tensorlogic_tool_runner`:

```bash
echo '{"program": {...}, "facts": [...], "config": {...}}' | lake exe tensorlogic_tool_runner
```

**Input Schema:**
```json
{
  "program": {
    "rules": [
      {"head": {"pred": "P", "args": [...]}, "body": [...], "weight": 1.0}
    ]
  },
  "facts": [
    {"atom": {"pred": "Q", "args": [...]}, "weight": 1.0}
  ],
  "config": {
    "mode": "boolean|f2|fuzzy|heyting",
    "bot": "monotone|f2solve|fuzzy|f2linear",
    "max_iter": 50,
    "eps": 1e-6
  }
}
```

**Output Schema:**
```json
{
  "status": "ok|error",
  "facts": [...],
  "iters": N,
  "converged": true|false,
  "bundle_hash": "..."
}
```

---

## 2. Task Categories

### 2.1 Category A: Basic Formulation (Easy)

**Task A1: Graph Reachability**
```
Natural language: "Given edges a→b, b→c, c→d, which nodes are reachable from a?"

Expected program:
- Rule: reach(X) :- start(X)
- Rule: reach(Y) :- reach(X), edge(X,Y)
- Facts: start(a), edge(a,b), edge(b,c), edge(c,d)

Success criteria: Agent produces correct Datalog, runs tool, reports {reach(a), reach(b), reach(c), reach(d)}
```

**Task A2: Transitive Closure**
```
Natural language: "Person A knows B, B knows C. Who does A transitively know?"

Expected: Agent models knows/2 relation and transitive closure rule.
```

**Task A3: Simple Classification**
```
Natural language: "Items with weight > 10 are heavy. Items that are heavy and fragile need special handling."

Expected: Agent models predicates and derives which items need special handling.
```

### 2.2 Category B: Mode Selection (Medium)

**Task B1: Weighted Inference**
```
Natural language: "Edge a→b has reliability 0.9, b→c has 0.8. What's the reliability of reaching c from a?"

Expected: Agent selects mode=fuzzy, interprets product t-norm result (~0.72)
```

**Task B2: XOR Semantics Detection**
```
Natural language: "A light switch toggles: if on, turn off; if off, turn on. Starting on, what's the final state after rules fire?"

Expected: Agent recognizes mutual recursion, selects mode=f2, explains XOR semantics
```

**Task B3: Monotone vs Non-Monotone**
```
Natural language: "Given p↔q (mutual implication), compute the fixpoint under boolean vs F₂ semantics."

Expected: Agent runs both modes, explains why boolean gives {p,q} but f2 may give {} or {p} depending on solver
```

### 2.3 Category C: Debugging & Analysis (Hard)

**Task C1: Non-Convergence Diagnosis**
```
Input: A program that oscillates under naive iteration
Challenge: Agent must detect non-convergence, suggest f2solve, explain why

Example:
  p :- not_p
  not_p :- p
  Fact: p (initial)
```

**Task C2: Result Interpretation**
```
Given: A complex policy program with 20+ rules
Challenge: Agent must trace why a specific atom was/wasn't derived

Success: Agent uses explain bot or manually traces derivation
```

**Task C3: Program Repair**
```
Given: A program with a bug (e.g., typo in predicate name)
Challenge: Agent must identify the bug from unexpected results and fix it
```

### 2.4 Category D: Multi-Step Reasoning (Expert)

**Task D1: Comparative Analysis**
```
Challenge: Run same program under all 4 modes, explain semantic differences
Expected: Table comparing results, explanation of why they differ
```

**Task D2: Evidence Bundle Verification**
```
Given: A pre-generated evidence bundle JSON
Challenge: Agent must verify the bundle_hash matches, explain canonicalization
```

**Task D3: Incremental Refinement**
```
Challenge: Start with incomplete specification, iteratively refine program based on test cases
Expected: Agent demonstrates hypothesis-test-refine loop
```

---

## 3. Evaluation Metrics

### 3.1 Correctness Metrics

| Metric | Definition | Scoring |
|--------|------------|---------|
| **Program Validity** | Does the JSON parse and run without error? | Binary (0/1) |
| **Semantic Correctness** | Does the program model the specification? | 0-1 scale |
| **Result Accuracy** | Are the derived facts correct? | Precision/Recall |
| **Mode Appropriateness** | Did the agent select the right mode? | Binary |

### 3.2 Process Metrics

| Metric | Definition | Scoring |
|--------|------------|---------|
| **Tool Invocations** | Number of tool calls to reach answer | Lower is better |
| **Error Recovery** | Did agent recover from tool errors? | Binary |
| **Explanation Quality** | Can agent explain the results? | 0-3 scale |

### 3.3 Scoring Rubric

**Explanation Quality:**
- 0: No explanation or incorrect
- 1: Partial/superficial explanation
- 2: Correct but incomplete
- 3: Complete, accurate, insightful

---

## 4. Experiment Protocol

### 4.1 Setup

```bash
# Ensure tools are built
cd /path/to/heyting-surreal/lean
lake build tensorlogic_tool_runner

# Verify tool works
echo '{"program":{"rules":[]},"facts":[],"config":{"mode":"boolean"}}' | lake exe tensorlogic_tool_runner
```

### 4.2 Agent Instructions (System Prompt)

```
You have access to a Datalog inference tool via bash. To use it:

echo '<JSON_REQUEST>' | lake exe tensorlogic_tool_runner

The tool accepts:
- program.rules: list of {head, body, weight} rules
- facts: list of {atom, weight} base facts
- config: {mode, bot, max_iter, eps}

Modes: boolean (standard), f2 (XOR disjunction), fuzzy (weighted), heyting (intuitionistic)
Bots: monotone (Kleene), f2solve (exact XOR), fuzzy (t-norm), f2linear (linear algebra)

Respond with your reasoning, tool invocations, and final answer.
```

### 4.3 Task Presentation

Each task is presented as:
```
## Task [ID]: [Title]

**Specification:** [Natural language description]

**Provided facts:** [If any specific facts are given]

**Question:** [What the agent should determine]

Please:
1. Formulate the Datalog program
2. Select the appropriate mode
3. Run the tool
4. Interpret and explain the results
```

### 4.4 Data Collection

For each task, record:
1. Agent's raw response (full transcript)
2. All tool invocations (JSON in/out)
3. Time to completion
4. Final answer
5. Evaluator scores

---

## 5. Test Cases

### 5.1 Task A1: Graph Reachability (Reference Implementation)

**Input Specification:**
```
Edges: a→b, b→c, c→d
Starting node: a
Question: Which nodes are reachable from a?
```

**Expected Tool Request:**
```json
{
  "program": {
    "rules": [
      {
        "head": {"pred": "reach", "args": [{"var": "X"}]},
        "body": [{"pred": "start", "args": [{"var": "X"}]}],
        "weight": 1.0
      },
      {
        "head": {"pred": "reach", "args": [{"var": "Y"}]},
        "body": [
          {"pred": "reach", "args": [{"var": "X"}]},
          {"pred": "edge", "args": [{"var": "X"}, {"var": "Y"}]}
        ],
        "weight": 1.0
      }
    ]
  },
  "facts": [
    {"atom": {"pred": "start", "args": ["a"]}, "weight": 1.0},
    {"atom": {"pred": "edge", "args": ["a", "b"]}, "weight": 1.0},
    {"atom": {"pred": "edge", "args": ["b", "c"]}, "weight": 1.0},
    {"atom": {"pred": "edge", "args": ["c", "d"]}, "weight": 1.0}
  ],
  "config": {
    "mode": "boolean",
    "bot": "monotone"
  }
}
```

**Expected Output Contains:**
```json
{
  "status": "ok",
  "facts": [
    {"atom": {"pred": "reach", "args": ["a"]}, ...},
    {"atom": {"pred": "reach", "args": ["b"]}, ...},
    {"atom": {"pred": "reach", "args": ["c"]}, ...},
    {"atom": {"pred": "reach", "args": ["d"]}, ...}
  ]
}
```

**Scoring:**
- Program Validity: 1 if runs without error
- Semantic Correctness: 1 if models reachability correctly
- Result Accuracy: 1 if all 4 reach facts derived
- Mode Appropriateness: 1 if boolean/monotone selected

### 5.2 Task B2: XOR Semantics (Reference)

**Input Specification:**
```
Rules:
  - p implies q
  - q implies p
Facts: p is true
Question: Under F₂ (XOR) semantics, what is the fixpoint?
```

**Expected Analysis:**
- Boolean mode: {p, q} (both derived)
- F₂ mode: depends on solver
  - f2solve: {} or {p} (XOR cancellation)
  - f2linear: may differ based on matrix solution

**Key Insight Agent Should Discover:**
Under XOR semantics, p→q and q→p create a cycle where:
- If p=1, then q=1 (from rule 1)
- But if q=1, then p gets XOR'd again, potentially flipping

---

## 6. Baseline Comparisons

### 6.1 Human Expert Baseline

A human Datalog expert completes all tasks. Record:
- Time per task
- Tool invocations
- Accuracy

### 6.2 No-Tool Baseline

LLM attempts tasks without tool access (pure reasoning).
Compare accuracy to tool-assisted performance.

### 6.3 Model Comparisons

Test across multiple LLMs:
- Claude (Opus, Sonnet, Haiku)
- GPT-4
- Open models (Llama, Mistral)

---

## 7. Expected Outcomes

### 7.1 Capability Levels

| Level | Description | Expected Tasks |
|-------|-------------|----------------|
| **Basic** | Can formulate simple programs, run tool | A1-A3 |
| **Intermediate** | Selects appropriate modes, interprets results | B1-B3 |
| **Advanced** | Debugs issues, explains complex semantics | C1-C3 |
| **Expert** | Multi-step refinement, verification | D1-D3 |

### 7.2 Failure Modes to Observe

1. **JSON Syntax Errors** - Agent produces invalid JSON
2. **Schema Violations** - Valid JSON but wrong structure
3. **Semantic Errors** - Valid program but wrong modeling
4. **Mode Confusion** - Selects inappropriate inference mode
5. **Result Misinterpretation** - Correct tool use but wrong conclusion

---

## 8. Files in This Experiment

```
experiments/tensorlogic_llm_tool_experiment/
├── EXPERIMENT_DESIGN.md          # This document
├── tasks/
│   ├── A1_graph_reachability.md
│   ├── A2_transitive_closure.md
│   ├── A3_simple_classification.md
│   ├── B1_weighted_inference.md
│   ├── B2_xor_semantics.md
│   ├── B3_monotone_comparison.md
│   ├── C1_non_convergence.md
│   ├── C2_result_interpretation.md
│   ├── C3_program_repair.md
│   ├── D1_comparative_analysis.md
│   ├── D2_evidence_verification.md
│   └── D3_incremental_refinement.md
├── reference_solutions/
│   └── [task_id]_solution.json
├── results/
│   └── [model]_[date]/
│       ├── transcript_[task_id].md
│       └── scores.json
└── analysis/
    └── summary_report.md
```

---

## 9. Running the Experiment

### 9.1 Quick Start

```bash
# 1. Build tools
cd /path/to/heyting-surreal/lean
lake build tensorlogic_tool_runner

# 2. Test tool works
echo '{"program":{"rules":[]},"facts":[],"config":{"mode":"boolean"}}' | lake exe tensorlogic_tool_runner

# 3. Present task A1 to agent and record results
```

### 9.2 Automated Scoring

```bash
# Compare agent output to reference
python3 experiments/tensorlogic_llm_tool_experiment/score.py \
  --reference reference_solutions/A1_solution.json \
  --agent results/claude_2026-01-14/A1_output.json
```

---

## 10. Next Steps

1. Create individual task files with detailed specifications
2. Generate reference solutions for all tasks
3. Build automated scoring script
4. Run experiment with target LLM
5. Analyze results and write report
