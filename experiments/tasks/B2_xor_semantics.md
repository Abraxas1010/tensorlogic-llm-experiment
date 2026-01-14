# Task B2: XOR Semantics Detection

**Category:** Mode Selection
**Difficulty:** Medium
**Expected Time:** 10 minutes

---

## Specification

Consider the following logical rules:
- If p is true, then q becomes true
- If q is true, then p becomes true

Initial fact: **p is true**

**Question:** What is the stable state under:
1. Standard boolean (OR) semantics?
2. F₂ (XOR) semantics?

Explain why the results differ.

---

## Background

In standard Datalog, disjunction (OR) is used:
- `p OR q` = true if either is true

In F₂ semantics, XOR replaces OR:
- `p XOR q` = true if exactly one is true
- This models "toggle" or "parity" behavior

---

## Instructions

1. Formulate the mutual implication program
2. Run it with `mode: "boolean"` and observe the result
3. Run it with `mode: "f2"` and `bot: "f2solve"` and observe the result
4. Explain the semantic difference

---

## Expected Analysis Points

- Under boolean: both p and q should be derived (mutual support)
- Under F₂: the mutual recursion may "cancel out" due to XOR
- The f2solve bot finds the lexicographically minimal fixpoint

---

## Evaluation Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Boolean run correct | 2 | Shows {p, q} derived |
| F₂ run correct | 2 | Shows different result |
| Mode selection | 2 | Uses f2solve for F₂ |
| Semantic explanation | 3 | Explains XOR cancellation |
| **Total** | **9** | |

---

## Key Insight

This task tests whether the agent understands that:
1. The same logical rules can have different semantics
2. Mutual recursion under XOR can lead to "cancellation"
3. The choice of solver (bot) affects the result for non-monotone programs
