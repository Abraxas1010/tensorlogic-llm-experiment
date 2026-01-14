#!/usr/bin/env bash
# Verification script for TensorLogic LLM Tool-Use Experiment
# Usage: ./scripts/verify_experiment.sh

set -e

echo "=== TensorLogic Experiment Verification ==="
echo ""

# Check we're in the right directory
if [ ! -f "README.md" ]; then
  echo "ERROR: Run from RESEARCHER_BUNDLE directory"
  exit 1
fi

# Check for Lean
if ! command -v lake &> /dev/null; then
  echo "ERROR: lake (Lean 4 build tool) not found"
  echo "Install via: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh"
  exit 1
fi

echo "[1/4] Checking experiment files..."
required_files=(
  "experiments/EXPERIMENT_DESIGN.md"
  "experiments/tasks/A1_graph_reachability.md"
  "experiments/reference_solutions/A1_solution.json"
  "experiments/results/gpt-5.2_2026-01-14/transcript_A1.md"
  "scripts/score.py"
)

for f in "${required_files[@]}"; do
  if [ -f "$f" ]; then
    echo "  OK: $f"
  else
    echo "  MISSING: $f"
    exit 1
  fi
done

echo ""
echo "[2/4] Checking Python scorer..."
if python3 -c "import json, re, sys" 2>/dev/null; then
  echo "  OK: Python 3 with required modules"
else
  echo "  ERROR: Python 3 required"
  exit 1
fi

echo ""
echo "[3/4] Verifying score.py runs..."
if python3 scripts/score.py --help > /dev/null 2>&1 || python3 scripts/score.py 2>&1 | grep -q "usage\|solution\|transcript"; then
  echo "  OK: Scorer script executes"
else
  echo "  WARNING: Scorer script may have issues (non-critical)"
fi

echo ""
echo "[4/4] Checking result artifacts..."
if [ -f "experiments/results/gpt-5.2_2026-01-14/score_A1.json" ]; then
  score=$(python3 -c "import json; print(json.load(open('experiments/results/gpt-5.2_2026-01-14/score_A1.json'))['total'])")
  echo "  Task A1 score: $score/7"
else
  echo "  WARNING: score_A1.json not found"
fi

echo ""
echo "=== Verification Complete ==="
echo ""
echo "To build and run the TensorLogic tool:"
echo "  cd lean && lake update && lake build tensorlogic_tool_runner"
echo "  echo '{...}' | lake exe tensorlogic_tool_runner"
