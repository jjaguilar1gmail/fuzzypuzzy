# Quickstart: Solver-Driven Pruning

## Overview

The solver-driven pruning system uses binary search interval reduction and frequency-based repair to minimize clue counts while maintaining puzzle uniqueness. It replaces the legacy linear removal approach with a more efficient algorithm.

## Basic Usage

### Generate a hard 9x9 with pruning (Python API)

```python
from generate.generator import Generator

result = Generator.generate_puzzle(
    size=9,
    difficulty="hard",
    seed=12345,
    allow_diagonal=True,
    path_mode="serpentine"
)

print(f"Clue Count: {result.clue_count}")
print(f"Difficulty: {result.difficulty_label}")
print(f"Status: {result.uniqueness_verified}")
```

### CLI Usage (if available)

```bash
python hidato.py --generate --size 9 --difficulty hard --path-mode serpentine --seed 12345 --verbose
```

## Expected Output

- **Anchor Policy**: adaptive_v1 or endpoints-only for hard mode
- **Anchor Count**: 2 (endpoints only for hard/extreme)
- **Final Clue Density**: ~24–32% (hard mode target)
- **Status**: `success`, `success_with_repairs`, `aborted_max_repairs`, or `aborted_timeout`
- **Metrics**: 
  - `pruning_iterations`: Number of interval reduction steps
  - `uniqueness_failures`: Failed uniqueness checks (triggers repair)
  - `repairs_used`: Clues added to restore uniqueness
  - `interval_contractions`: Binary search contractions
  - `timeout_occurred`: Whether timeout was hit
  - `time_ms`: Total pruning time

## Configuration Knobs

All settings in `GenerationConfig`:

### Core Settings
- `pruning_enabled`: `bool = True` - Enable/disable pruning (feature flag)
- `pruning_max_repairs`: `int = 2` - Cap on repair cycles per generation
- `pruning_linear_fallback_k`: `int = 6` - Switch to linear when ≤K clues remain

### Density Targets
- `pruning_target_density_hard_min`: `float = 0.24` - Hard mode minimum (24%)
- `pruning_target_density_hard_max`: `float = 0.32` - Hard mode maximum (32%)

### Repair Settings
- `pruning_alternates_count`: `int = 5` - Number of alternate solutions to sample
- `pruning_repair_topn`: `int = 5` - Top-N repair candidates to consider

## Tuning Tips

### For Faster Generation
- Increase `pruning_linear_fallback_k` (e.g., 10) to exit interval reduction earlier
- Reduce `pruning_alternates_count` (e.g., 3) to speed up repair sampling
- Decrease `pruning_max_repairs` (e.g., 1) to fail faster on hard-to-repair puzzles

### For Minimal Clue Counts
- Decrease `pruning_target_density_hard_min` (e.g., 0.20)
- Increase `pruning_max_repairs` (e.g., 3) to allow more repair attempts
- Use `path_mode="random_walk"` for more structure-diverse paths

### For Deterministic Results
- Always set a fixed `seed` value
- Use the same configuration parameters
- Verify with `compute_pruning_hash()` across runs

## Reproducibility

To verify deterministic behavior:

```python
from generate.generator import Generator
from generate.pruning import compute_pruning_hash

seed = 42
results = []

for run in range(5):
    result = Generator.generate_puzzle(
        size=7,
        difficulty="medium",
        seed=seed,
        allow_diagonal=True
    )
    
    # Compute hash (requires accessing internal puzzle structure)
    # hash_val = compute_pruning_hash(puzzle, path, "medium")
    results.append(result.clue_count)

# All runs should produce identical clue counts
assert len(set(results)) == 1, "Non-deterministic behavior detected!"
print(f"✓ Deterministic: {results[0]} clues across {len(results)} runs")
```

## Interpreting Metrics

### Status Values
- **SUCCESS**: Pruning completed without issues
- **SUCCESS_WITH_REPAIRS**: Uniqueness restored via repair clues (1-2 repairs)
- **ABORTED_MAX_REPAIRS**: Hit repair cap, returned best-so-far state
- **ABORTED_TIMEOUT**: Exceeded time limit, returned last valid state

### Performance Indicators
- **Low iterations** (<10): Efficient pruning, reached target quickly
- **High uniqueness failures** (>5): Puzzle structure makes uniqueness challenging
- **Repairs used** (1-2): Common; indicates ambiguity was resolved
- **Timeout occurred**: Increase timeout_ms or reduce grid size

## Benchmarking

Run the benchmark script:

```bash
cd benchmarks
python benchmark_pruning.py 20 7 medium
# Args: <num_seeds> <size> <difficulty>
```

Expected performance (Success Criteria):
- **Hard 9x9**: ≤6.0s median per puzzle
- **Iteration Reduction**: ≥40% fewer iterations vs legacy
- **Clue Density**: Within target band (24-32% for hard)

## Troubleshooting

### High Clue Counts
- Check if `pruning_enabled=True`
- Verify difficulty band targets are set correctly
- Try different `seed` values (some paths are harder to minimize)

### Timeout Issues
- Increase `timeout_ms` in config
- Reduce `pruning_alternates_count` to speed up repair
- Use smaller grid sizes for testing

### Non-Unique Puzzles After Max Repairs
- This is expected behavior (status=`ABORTED_MAX_REPAIRS`)
- Puzzle structure may not support lower clue counts
- Try different `path_mode` or `seed`

## Advanced: Custom Pruning Config

```python
from generate.models import GenerationConfig

config = GenerationConfig(
    size=9,
    difficulty="hard",
    seed=12345,
    pruning_enabled=True,
    pruning_max_repairs=3,  # Allow more repairs
    pruning_target_density_hard_min=0.20,  # More aggressive
    pruning_linear_fallback_k=8,  # Exit interval reduction earlier
    pruning_alternates_count=4,  # Faster sampling
    pruning_repair_topn=3  # Fewer repair candidates
)

# Use config in generator (requires code modification to accept config directly)
```

## References

- Specification: `specs/001-solver-driven-pruning/spec.md`
- Research Decisions: `specs/001-solver-driven-pruning/research.md`
- Task Breakdown: `specs/001-solver-driven-pruning/tasks.md`
- Data Model: `specs/001-solver-driven-pruning/data-model.md`
