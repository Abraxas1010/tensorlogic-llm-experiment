#!/usr/bin/env python3
"""
TensorLogic LLM Tool Use Experiment - Scoring Script

Usage:
  python3 score.py --reference A1_solution.json --agent agent_output.json
  python3 score.py --task A1 --transcript transcript.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

def normalize_atom(atom_str: str) -> str:
    """Normalize atom string for comparison."""
    # Remove whitespace, lowercase
    return re.sub(r'\s+', '', atom_str.lower())

def extract_facts_from_output(output: dict) -> Set[str]:
    """Extract derived facts from tool output."""
    facts = set()
    for f in output.get("facts", []):
        atom = f.get("atom", {})
        pred = atom.get("pred", "")
        args = atom.get("args", [])
        facts.add(f"{pred}({','.join(args)})")
    return facts

def score_result_accuracy(expected: List[str], actual: Set[str]) -> Tuple[float, float, float]:
    """
    Compute precision, recall, F1 for derived facts.
    """
    expected_set = {normalize_atom(a) for a in expected}
    actual_set = {normalize_atom(a) for a in actual}

    if not expected_set:
        return (1.0, 1.0, 1.0) if not actual_set else (0.0, 1.0, 0.0)

    tp = len(expected_set & actual_set)
    fp = len(actual_set - expected_set)
    fn = len(expected_set - actual_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return (precision, recall, f1)

def check_json_validity(json_str: str) -> Tuple[bool, Optional[dict], str]:
    """Check if JSON is valid and return parsed object."""
    try:
        obj = json.loads(json_str)
        return (True, obj, "")
    except json.JSONDecodeError as e:
        return (False, None, str(e))

def extract_json_from_transcript(transcript: str) -> List[str]:
    """Extract JSON blocks from markdown transcript."""
    # Find JSON in code blocks
    pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
    matches = re.findall(pattern, transcript)
    return matches

def score_transcript(transcript_path: Path, reference_path: Path) -> Dict:
    """Score an agent transcript against reference solution."""

    with open(transcript_path) as f:
        transcript = f.read()

    with open(reference_path) as f:
        reference = json.load(f)

    scores = {
        "task_id": reference.get("task_id", "unknown"),
        "valid_json": 0,
        "correct_rules": 0,
        "correct_facts": 0,
        "correct_answer": 0,
        "explanation": 0,
        "total": 0,
        "max_total": reference.get("scoring", {}).get("total", 7),
        "details": {}
    }

    # Extract JSON requests from transcript
    json_blocks = extract_json_from_transcript(transcript)

    if not json_blocks:
        scores["details"]["json_extraction"] = "No JSON blocks found in transcript"
        return scores

    # Check JSON validity
    valid_jsons = []
    for jb in json_blocks:
        is_valid, obj, error = check_json_validity(jb)
        if is_valid:
            valid_jsons.append(obj)

    if valid_jsons:
        scores["valid_json"] = 1
        scores["details"]["json_validity"] = f"Found {len(valid_jsons)} valid JSON block(s)"
    else:
        scores["details"]["json_validity"] = "No valid JSON blocks"
        return scores

    # Find the request JSON (has "program" key)
    request_json = None
    for obj in valid_jsons:
        if "program" in obj:
            request_json = obj
            break

    if not request_json:
        scores["details"]["request_found"] = "No request JSON with 'program' key found"
        return scores

    # Compare rules (simplified - just check count and predicates)
    ref_rules = reference.get("request", {}).get("program", {}).get("rules", [])
    agent_rules = request_json.get("program", {}).get("rules", [])

    if len(agent_rules) == len(ref_rules):
        scores["correct_rules"] = 2
        scores["details"]["rules"] = f"Correct rule count ({len(agent_rules)})"
    else:
        scores["correct_rules"] = 1 if agent_rules else 0
        scores["details"]["rules"] = f"Expected {len(ref_rules)} rules, got {len(agent_rules)}"

    # Compare facts
    ref_facts = reference.get("request", {}).get("facts", [])
    agent_facts = request_json.get("facts", [])

    if len(agent_facts) == len(ref_facts):
        scores["correct_facts"] = 1
        scores["details"]["facts"] = f"Correct fact count ({len(agent_facts)})"
    else:
        scores["details"]["facts"] = f"Expected {len(ref_facts)} facts, got {len(agent_facts)}"

    # Look for derived facts in transcript (from tool output)
    expected_derived = reference.get("expected_derived_facts", [])

    # Try to find output JSON in transcript
    output_json = None
    for obj in valid_jsons:
        if "status" in obj and "facts" in obj:
            output_json = obj
            break

    if output_json:
        actual_facts = extract_facts_from_output(output_json)
        precision, recall, f1 = score_result_accuracy(expected_derived, actual_facts)

        if f1 >= 0.99:
            scores["correct_answer"] = 2
        elif f1 >= 0.5:
            scores["correct_answer"] = 1

        scores["details"]["accuracy"] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "expected": expected_derived,
            "actual": list(actual_facts)
        }
    else:
        scores["details"]["accuracy"] = "Could not find tool output in transcript"

    # Explanation scoring (simple heuristic - check for key terms)
    explanation_terms = ["derived", "rule", "fact", "iteration", "because", "therefore"]
    term_count = sum(1 for term in explanation_terms if term.lower() in transcript.lower())

    if term_count >= 4:
        scores["explanation"] = 1

    scores["details"]["explanation_terms"] = term_count

    # Total
    scores["total"] = (
        scores["valid_json"] +
        scores["correct_rules"] +
        scores["correct_facts"] +
        scores["correct_answer"] +
        scores["explanation"]
    )

    return scores

def main():
    parser = argparse.ArgumentParser(description="Score TensorLogic LLM experiment")
    parser.add_argument("--transcript", type=Path, help="Path to agent transcript")
    parser.add_argument("--reference", type=Path, help="Path to reference solution")
    parser.add_argument("--task", type=str, help="Task ID (e.g., A1)")
    parser.add_argument("--output", type=Path, help="Output scores to file")

    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent

    if args.task and not args.reference:
        args.reference = script_dir / "reference_solutions" / f"{args.task}_solution.json"

    if not args.transcript or not args.reference:
        parser.error("Need --transcript and --reference (or --task)")

    if not args.transcript.exists():
        print(f"Error: Transcript not found: {args.transcript}", file=sys.stderr)
        sys.exit(1)

    if not args.reference.exists():
        print(f"Error: Reference not found: {args.reference}", file=sys.stderr)
        sys.exit(1)

    scores = score_transcript(args.transcript, args.reference)

    # Output
    output_str = json.dumps(scores, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_str)
        print(f"Scores written to {args.output}")
    else:
        print(output_str)

    # Summary
    print(f"\n=== Score Summary ===")
    print(f"Task: {scores['task_id']}")
    print(f"Total: {scores['total']} / {scores['max_total']}")
    print(f"  Valid JSON: {scores['valid_json']}")
    print(f"  Correct Rules: {scores['correct_rules']}")
    print(f"  Correct Facts: {scores['correct_facts']}")
    print(f"  Correct Answer: {scores['correct_answer']}")
    print(f"  Explanation: {scores['explanation']}")

if __name__ == "__main__":
    main()
