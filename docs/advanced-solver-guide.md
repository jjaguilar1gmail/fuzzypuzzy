# Advanced Solver Architecture - Complete Documentation

## Overview

This document provides comprehensive documentation for the advanced Hidato solver system implemented in the fuzzypuzzy project. The solver features four progressive modes with increasing sophistication.

## Solver Modes

### logic_v0 (Baseline)
- **Purpose**: Basic logical deduction
- **Techniques**: Single candidate detection
- **Use Case**: Simple puzzles with obvious logical moves
- **Performance**: Fast, minimal memory usage
- **Limitations**: Gets stuck on moderately complex puzzles

### logic_v1 (Enhanced Logic)
- **Purpose**: Stronger logical reasoning with no guessing
- **Techniques**: 
  - Two-ended propagation
  - Enhanced candidate tracking
  - Single position/value detection
  - Bidirectional constraint analysis
- **Use Case**: Medium complexity puzzles solvable through pure logic
- **Performance**: Fast with moderate memory usage
- **Infrastructure**: CandidateModel for bidirectional value/position mappings

### logic_v2 (Region-Aware)
- **Purpose**: Board shape aware pruning with no guessing
- **Techniques**:
  - All logic_v1 techniques
  - Island elimination
  - Corridor bridging
  - Degree-based pruning
  - Empty region analysis
- **Use Case**: Complex puzzles requiring spatial reasoning
- **Performance**: Moderate speed, higher memory usage
- **Infrastructure**: RegionCache, CorridorMap, DegreeIndex

### logic_v3 (Bounded Search)
- **Purpose**: Hybrid approach combining v2 logic with controlled backtracking
- **Techniques**:
  - All logic_v2 techniques
  - Bounded depth-first search
  - MRV (Minimum Remaining Values) heuristic
  - LCV (Least Constraining Value) heuristic
  - Intelligent variable/value ordering
- **Use Case**: Very complex puzzles requiring search
- **Performance**: Variable (fast for solvable, bounded for impossible)
- **Bounds**: Configurable node limits, depth limits, timeouts

## Architecture Components

### CandidateModel
```python
# Bidirectional value/position mapping for efficient operations
value_to_positions: Dict[int, Set[Position]]  # Value -> possible positions
pos_to_values: Dict[Position, Set[int]]       # Position -> possible values
```

**Key Methods**:
- `init_from(puzzle)`: Initialize from puzzle state
- `single_candidate_values()`: Find positions with only one possible value
- `single_candidate_positions()`: Find values with only one possible position
- `assign(value, pos)`: Update all mappings after placement
- `remove_candidate(value, pos)`: Eliminate invalid candidates

### RegionCache
```python
# Empty region analysis for spatial reasoning
regions: List[EmptyRegion]           # Contiguous empty areas
pos_to_region: Dict[Position, int]   # Position -> region mapping
```

**Key Methods**:
- `build_regions(puzzle)`: Identify contiguous empty regions via flood fill
- `get_empty_regions()`: Return all empty regions
- `can_fit_sequence_length(region, length)`: Check if region can hold sequence

### CorridorMap
```python
# Corridor feasibility analysis between placed values
corridor_cache: Dict[Tuple[int, int], Set[Position]]  # Cached corridor paths
```

**Key Methods**:
- `corridors_between(puzzle, start_value, end_value)`: Find valid paths
- `get_all_sequence_gaps(puzzle)`: Identify gaps needing bridging
- `prune_candidates_by_corridors()`: Eliminate unreachable positions

### DegreeIndex
```python
# Neighbor connectivity analysis for constraint checking
degree: Dict[Position, int]  # Position -> neighbor count
```

**Key Methods**:
- `build_degree_index(puzzle)`: Count legal neighbors for each position
- Supports degree constraints (endpoints need ≥1, middle values need ≥2)

## Configuration & Usage

### Basic Usage
```python
from solve.solver import Solver

# Simple solving
result = Solver.solve(puzzle, mode="logic_v1")

# Advanced solving with configuration
result = Solver.solve(puzzle, mode="logic_v3", 
                     max_nodes=5000,
                     max_depth=20, 
                     timeout_ms=10000,
                     ordering="mrv_lcv_frontier")
```

### Mode Selection Guidelines

**Use logic_v0 when**:
- Puzzle has many given values
- Quick hint generation needed
- Resource constrained environment

**Use logic_v1 when**:
- Moderate puzzle complexity
- Want pure logical solution
- Performance is important

**Use logic_v2 when**:
- Complex spatial layout
- Many empty regions
- logic_v1 gets stuck but no search desired

**Use logic_v3 when**:
- Maximum solving power needed
- Willing to accept search overhead
- Puzzle may require limited guessing

### Performance Characteristics

| Mode | Speed | Memory | Success Rate | Use Case |
|------|--------|---------|--------------|----------|
| v0 | Fastest | Minimal | Basic | Simple puzzles |
| v1 | Fast | Low | Good | Medium puzzles |
| v2 | Medium | Medium | Better | Complex spatial |
| v3 | Variable | High | Highest | Maximum power |

## Advanced Configuration

### Search Parameters (logic_v3)
```python
# Node limits
max_nodes=20000        # Maximum search nodes before termination

# Depth limits  
max_depth=50          # Maximum search depth

# Time limits
timeout_ms=30000      # Timeout in milliseconds

# Search ordering
ordering="mrv_lcv_frontier"  # Variable/value ordering strategy
```

### Ordering Strategies
- `"mrv"`: Minimum Remaining Values (choose most constrained variable)
- `"lcv"`: Least Constraining Value (choose least constraining value)
- `"frontier"`: Prefer positions adjacent to placed values
- `"mrv_lcv_frontier"`: Combined strategy (recommended)
- `"row_col"`: Simple row-column ordering

### Region Analysis Parameters (logic_v2)
```python
# Enable/disable specific techniques
enable_island_elim=True      # Island elimination
enable_segment_bridging=True # Corridor bridging
enable_degree_prune=True     # Degree-based pruning
```

## Integration

### REPL Integration
```bash
# Command line usage
python hidato.py --mode logic_v3 --max-nodes 1000
```

### API Integration
```python
# Programmatic usage with full configuration
config = {
    'max_logic_passes': 20,
    'tie_break': 'row_col', 
    'max_nodes': 10000,
    'timeout_ms': 15000,
    'ordering': 'mrv_lcv_frontier'
}

result = Solver.solve(puzzle, mode="logic_v3", **config)
```

## Troubleshooting

### Common Issues

**"Stuck after N iterations"**
- Try higher solver mode (v0→v1→v2→v3)
- Increase iteration limits
- Check puzzle validity

**"Exhausted search space"**
- Increase node/depth limits
- Increase timeout
- Puzzle may be impossible

**"Timeout" errors**
- Reduce search limits
- Use lower solver mode for hints
- Consider puzzle difficulty

**Poor performance**
- Use appropriate mode for puzzle complexity
- Reduce search parameters for faster results
- Consider incremental solving (get hints, apply, repeat)

### Validation Issues

The solver includes comprehensive validation:
- All required values must be placed
- Consecutive values must be adjacent
- No duplicate values allowed
- Valid Hidato path must exist

## Testing & Quality Assurance

### Test Coverage
- Unit tests for each component
- Integration tests across all modes
- Edge case testing (impossible puzzles, boundary conditions)
- Performance regression testing

### Known Limitations
- logic_v2 region techniques need refinement for optimal performance
- Very large puzzles may exceed practical search limits in logic_v3
- Memory usage scales with puzzle complexity in advanced modes

## Future Enhancements

### Potential Improvements
1. **Enhanced Region Analysis**: More sophisticated region connectivity analysis
2. **Parallel Search**: Multi-threaded search in logic_v3
3. **Machine Learning**: Value ordering heuristics based on puzzle patterns
4. **Incremental Solving**: Resume from partial solutions
5. **Puzzle Generation**: Reverse-engineering for puzzle creation

### Architecture Extensions
1. **Plugin System**: Pluggable solving techniques
2. **Solver Composition**: Custom solver pipelines
3. **Adaptive Parameters**: Self-tuning based on puzzle characteristics
4. **Solution Caching**: Memoization of partial solutions

## Conclusion

The advanced solver system provides a comprehensive, production-ready solution for Hidato puzzles with clear upgrade paths from basic logic to sophisticated search techniques. The modular architecture allows for targeted application of computational resources based on puzzle requirements.