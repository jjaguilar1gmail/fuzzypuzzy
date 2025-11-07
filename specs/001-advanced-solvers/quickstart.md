# Quickstart — Advanced Solver Modes

This guide shows how to use the new solver modes v1–v3 from the CLI/REPL and tests.

## Prerequisites
- Python 3.11+
- Windows PowerShell (or any shell)

## Run tests

```powershell
# From repo root
pytest
```

## Lint

```powershell
ruff check .
```

## Try the REPL and new modes

```powershell
# Start the demo/REPL
python .\hidato.py --demo
# In the REPL, use
#   solve --mode logic_v1
#   solve --mode logic_v2
#   solve --mode logic_v3
#   hint --mode logic_v2
```

## Configuration knobs and Modes

### Logic v1 (Enhanced Pure Logic)
- `max_logic_passes`: Maximum iterations before giving up (default: 50)
- `tie_break`: Deterministic tie-breaker for equal candidates (default: "row_col")
- Features: Two-ended propagation, global uniqueness checks, early contradictions
- No guessing; purely deterministic

### Logic v2 (Shape/Region Aware Logic)  
- `enable_island_elim`: Prune candidates that split empties into disconnected regions (default: true)
- `enable_segment_bridging`: Use corridor feasibility between placed numbers (default: true)
- `enable_degree_prune`: Eliminate cells with insufficient neighbors for path continuity (default: true)
- Inherits all v1 features plus spatial reasoning
- No guessing; purely deterministic

### Logic v3 (Hybrid Logic + Bounded Search)
- Search budgets:
  - `max_nodes`: Maximum search nodes before termination (default: 20000)
  - `max_depth`: Maximum search depth (default: 50)
  - `timeout_ms`: Time limit in milliseconds (default: 500)
- `ordering`: Search strategy (default: "mrv_lcv_frontier" = Min-Remaining-Values + Least-Constraining-Value + frontier bias)
- Runs all v2 logic to fixpoint before and after guesses
- Emits telemetry: nodes explored, max depth, elapsed time

## REPL Examples

```powershell
# Generate a medium puzzle
generate --rows 10 --cols 10 --seed 12345

# Try different solver modes
solve --mode logic_v0    # Basic consecutive logic (existing)
solve --mode logic_v1    # + two-ended propagation
solve --mode logic_v2    # + region/corridor reasoning  
solve --mode logic_v3    # + bounded backtracking

# Get hints using advanced logic
hint --mode logic_v1     # Next logical step using v1
hint --mode logic_v2     # Next step with region awareness

# Show current state
show

# Time a solve
solve --mode logic_v2
# (Timing shown in result message)
```

## Expected Performance (Reference: Win11 i7-12700H Python 3.11.9)
- v1/v2 median solve time: ≤300ms on 15x15 medium puzzles
- v3 hint latency: ≤150ms median
- v3 search typically explores <40% nodes vs naive brute-force

See `specs/001-advanced-solvers/spec.md` for complete success criteria and test corpus details.
