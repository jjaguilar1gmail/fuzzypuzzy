# Quickstart: Staged Uniqueness Validation

## Goal
Run the staged uniqueness checker against a generated 7x7 puzzle and interpret metrics.

## Configuration Options

### Default Budgets (FR-014)
- **Easy**: 600ms total
- **Medium**: 500ms total  
- **Hard**: 400ms total
- **Small boards (≤5x5)**: 100ms enumeration

### Stage Budget Split (default)
- **early_exit**: 40% of total budget
- **probes**: 40% of total budget
- **sat**: 20% of total budget (disabled by default)

### Strategy Flags
- **early_exit**: Enable bounded backtracking with diverse heuristics (default: `True`)
- **probes**: Enable randomized solver probes (default: `True`)
- **sat**: Enable optional SAT/CP verification (default: `False` per FR-012)

## Quick Start

### Option 1: Using Helper Function (Recommended)
```python
from generate.uniqueness_staged import create_request, check_uniqueness

# Create request with defaults
request = create_request(
    puzzle=my_puzzle,
    size=7,
    difficulty='medium',
    seed=42
)

# Run check
result = check_uniqueness(request)
print(f"Decision: {result.decision.value}")
print(f"Decided by: {result.stage_decided}")
print(f"Time: {result.elapsed_ms}ms")
print(f"Per-stage: {result.per_stage_ms}")
```

### Option 2: Full Control
```python
from generate.uniqueness_staged import UniquenessCheckRequest, check_uniqueness

req = UniquenessCheckRequest(
    puzzle=my_puzzle,
    size=7,
    adjacency=8,
    difficulty='medium',
    total_budget_ms=500,
    stage_budget_split={'early_exit': 0.4, 'probes': 0.4, 'sat': 0.2},
    seed=42,
    strategy_flags={'early_exit': True, 'probes': True, 'sat': False}
)

result = check_uniqueness(req)
```

## Programmatic API

### Enable/Disable Stages
```python
from generate.uniqueness_staged import create_request, enable_stage, disable_stage

request = create_request(puzzle=my_puzzle, size=7)

# Disable probes, enable SAT
disable_stage(request, 'probes')
enable_stage(request, 'sat')

result = check_uniqueness(request)
```

### Using Configuration Class
```python
from generate.uniqueness_staged import UniquenessConfig

# Create config with defaults for difficulty
config = UniquenessConfig.from_difficulty(size=7, difficulty='hard', seed=123)

# Validate budget allocation
config.validate_budget_allocation()

# Get specific stage budget
early_exit_budget = config.get_stage_budget('early_exit')
```

## Interpreting Results

### Decision Values
- **UNIQUE**: Exactly one solution (high confidence)
- **NON_UNIQUE**: Multiple solutions detected
- **INCONCLUSIVE**: Could not determine within budget

### Tri-State Handling (FR-008)
```python
from generate.uniqueness_staged import UniquenessDecision

if result.decision == UniquenessDecision.UNIQUE:
    print("Verified unique!")
elif result.decision == UniquenessDecision.NON_UNIQUE:
    print("Non-unique, add another clue")
else:  # INCONCLUSIVE
    print(f"Inconclusive: {result.notes}")
    # Conservative: treat as non-unique or increase budget
```

### Metrics Analysis
```python
# Per-stage timing
print(f"Early-exit: {result.per_stage_ms.get('early_exit', 0)}ms")
print(f"Probes: {result.per_stage_ms.get('probes', 0)}ms")

# Search statistics
print(f"Nodes explored: {result.nodes_explored}")
print(f"Probes run: {result.probes_run}")

# Which stage decided?
print(f"Decided by: {result.stage_decided}")
```

## Integration with Pruning

The staged checker can be integrated into `generate/pruning.py`:

```python
# In check_puzzle_uniqueness():
from generate.uniqueness_staged import create_request, check_uniqueness, UniquenessDecision

request = create_request(
    puzzle=puzzle,
    size=puzzle.grid.size,
    adjacency=puzzle.grid.adj,
    difficulty='medium',
    enable_early_exit=True,
    enable_probes=True,
    enable_sat=False
)

result = check_uniqueness(request)

if result.decision == UniquenessDecision.UNIQUE:
    return True
elif result.decision == UniquenessDecision.NON_UNIQUE:
    return False
else:  # INCONCLUSIVE - conservative approach
    return False  # Trigger another clue/pruning pass
```

## SAT/CP Hook (Optional)

To use external SAT/CP solvers:

```python
from generate.uniqueness_staged import sat_hook

# Define solver implementation
class MySATSolver(sat_hook.SolverInterface):
    def find_solution(self, puzzle, timeout_ms):
        # Convert to SAT, solve
        return solution_or_none
    
    def find_second_solution(self, puzzle, first_solution, timeout_ms):
        # Add blocking clause, solve again
        return second_solution_or_none

# Register solver
sat_hook.register_sat_solver(MySATSolver())

# Enable SAT stage in request
request = create_request(puzzle=my_puzzle, size=7, enable_sat=True)
result = check_uniqueness(request)
```

## Notes
- **Deterministic**: same seed + config → identical outcomes (FR-013)
- **Budget enforcement**: All stages respect time limits (FR-014)
- **Early returns**: Non-Unique detected immediately on second solution (FR-006)
- **No mutation**: Puzzle objects are never modified (FR-010)

## User Story 1 (US1) Acceptance Test

**Scenario**: Verify fast bounded uniqueness checks detect non-unique puzzles within budget.

**Setup**:
1. Generate a 7x7 puzzle with medium difficulty (500ms total budget)
2. Create request with early_exit stage enabled
3. Optionally: generate a puzzle known to be non-unique by providing 2+ solutions

**Expected Outcomes**:
- ✅ If puzzle has 2+ solutions: decision == `NON_UNIQUE`, stage_decided == `early_exit`
- ✅ Elapsed time ≤ total_budget_ms (500ms for medium)
- ✅ Early return when second solution found (no unnecessary continuation)
- ✅ Metrics recorded: per_stage_ms shows time spent in early_exit
- ✅ If inconclusive: notes field explains why (e.g., "All heuristics exhausted without finding 2 solutions")

**Test Command**:
```powershell
$env:PYTHONPATH="$pwd"; python test_staged_smoke.py
```

**Validation**:
- Check `result.decision` is one of: UNIQUE, NON_UNIQUE, INCONCLUSIVE
- Check `result.elapsed_ms <= request.total_budget_ms`
- Check `result.stage_decided` is not empty when decision != INCONCLUSIVE
- Check `result.notes` contains explanation if INCONCLUSIVE

**Notes**:
- Early-exit stage uses 4 default heuristic profiles: row_major, center_out, mrv, degree_biased
- Each profile gets equal share of early_exit budget allocation
- Solver pass reuse (corridors, degree, islands) applied before branching
- Solution cap enforced at 2 solutions maximum

