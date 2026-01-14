# Task C3: Program Repair

**Category:** Debugging & Analysis
**Difficulty:** Hard
**Expected Time:** 15 minutes

---

## Specification

A junior developer wrote the following Datalog program to compute whether a person can access a resource:

**Rules (as described):**
1. A user can access a resource if they own it
2. A user can access a resource if they are in a group that owns it
3. A user is in a group if they are a member of that group

**Facts:**
- alice is a member of admins
- admins owns database
- bob owns file1

**Expected results:**
- alice can access database (via group)
- bob can access file1 (via ownership)

**Actual JSON submitted:**
```json
{
  "program": {
    "rules": [
      {
        "head": {"pred": "can_access", "args": [{"var": "U"}, {"var": "R"}]},
        "body": [{"pred": "owns", "args": [{"var": "U"}, {"var": "R"}]}]
      },
      {
        "head": {"pred": "can_access", "args": [{"var": "U"}, {"var": "R"}]},
        "body": [
          {"pred": "in_group", "args": [{"var": "U"}, {"var": "G"}]},
          {"pred": "owns", "args": [{"var": "G"}, {"var": "R"}]}
        ]
      },
      {
        "head": {"pred": "in_group", "args": [{"var": "U"}, {"var": "G"}]},
        "body": [{"pred": "member", "args": [{"var": "U"}, {"var": "G"}]}]
      }
    ]
  },
  "facts": [
    {"atom": {"pred": "member", "args": ["alice", "admins"]}, "weight": 1.0},
    {"atom": {"pred": "own", "args": ["admins", "database"]}, "weight": 1.0},
    {"atom": {"pred": "owns", "args": ["bob", "file1"]}, "weight": 1.0}
  ],
  "config": {"mode": "boolean", "bot": "monotone"}
}
```

**Observed result:** Only `can_access(bob, file1)` is derived. Alice cannot access database.

---

## Task

1. Run the provided program and confirm the bug
2. Identify what is wrong
3. Fix the program
4. Verify the fix produces correct results

---

## Hints

- Look carefully at predicate names in facts vs rules
- Typos are a common source of bugs
- The tool treats `own` and `owns` as different predicates

---

## Evaluation Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Reproduces bug | 1 | Runs original, sees missing result |
| Identifies cause | 3 | Finds the typo (own vs owns) |
| Fixes correctly | 2 | Changes `own` to `owns` in facts |
| Verifies fix | 2 | Shows both access facts derived |
| Explanation | 2 | Explains why the bug caused the issue |
| **Total** | **10** | |

---

## Learning Objective

This task tests:
1. Careful reading of program structure
2. Hypothesis formation ("why might this fail?")
3. Systematic debugging approach
4. Tool use for verification
