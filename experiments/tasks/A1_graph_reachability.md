# Task A1: Graph Reachability

**Category:** Basic Formulation
**Difficulty:** Easy
**Expected Time:** 5 minutes

---

## Specification

You are given a directed graph with the following edges:
- a → b
- b → c
- c → d

The starting node is **a**.

**Question:** Which nodes are reachable from the starting node?

---

## Instructions

1. Formulate a Datalog program that computes reachability
2. Use the `tensorlogic_tool_runner` to execute the program
3. Report which nodes are reachable
4. Briefly explain how the rules derive each reachable node

---

## Tool Usage

Run your program with:
```bash
echo '<your_json_request>' | lake exe tensorlogic_tool_runner
```

---

## Hints

- You'll need a base case rule: nodes that are starting points are reachable
- You'll need a recursive rule: if X is reachable and there's an edge X→Y, then Y is reachable
- Use `mode: "boolean"` for standard Datalog semantics

---

## Expected Output Format

Your response should include:
1. The Datalog rules in natural language
2. The JSON request you sent to the tool
3. The tool's response
4. Your interpretation: "Nodes reachable from a: {list}"

---

## Evaluation Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Valid JSON | 1 | Request parses without error |
| Correct rules | 2 | Rules model reachability correctly |
| Correct facts | 1 | All edges and start encoded |
| Correct answer | 2 | Reports {a, b, c, d} as reachable |
| Explanation | 1 | Traces derivation path |
| **Total** | **7** | |
