# Data Model: Fix v2/v3 solvers for 5x5 deterministic

Created: 2025-11-07 | Branch: 001-fix-v2-v3-solvers

## Entities

### Puzzle (existing)
- Fields: grid (rows, cols, cells), constraints (min_value, max_value, adjacency='8'|'4'), givens
- Invariants: givens immutable; values unique 1..N; adjacency for consecutive numbers

### CandidateModel (existing concept)
- value_to_positions: dict[int, set[Position]]
- pos_to_values: dict[Position, set[int]]
- Invariants: mirror consistency; prune operations keep both maps in sync

### CorridorMap (updated)
- cache: dict[(start:int,end:int), set[Position]]
- _cache_dirty: bool (set False after compute; True when placements change)
- Methods: compute_corridor(start,end,state) using dual BFS; invalidate_on_change()

### DegreeIndex (updated)
- degree_by_pos: dict[Position, int]  # count of empty neighbors only
- Methods: recompute(state); get_degree(pos)

### RegionCache (updated minimal)
- components: list[set[Position]]  # connected components of empty cells
- Methods: recompute(state); min_capacity_intersecting(corridor:set[Position]) -> int

### TranspositionTable (new, optional)
- table: dict[Tuple[int,...], Any]  # key by value→pos tuple of length N (row*W+col, or -1)
- capacity: int (e.g., 10k)
- Methods: make_key(state) -> tuple; get(key); put(key, value) (LRU or simple FIFO if needed)

### SearchConfig (existing/updated)
- max_nodes: int; max_depth: int; time_budget_ms: int; use_transposition: bool

## Relationships
- CorridorMap and RegionCache depend on current empty cell mask from Puzzle
- DegreeIndex depends on Puzzle grid occupancy
- CandidateModel feeds MRV/LCV value selection and pruning mechanics
- TranspositionTable consumes a canonicalized state signature

## Validation Rules
- Solver must validate final solution: path 1..N contiguous per adjacency; givens preserved
- Pre-branch: ensure logic fixpoint reached; if candidates exhausted → unsat

## State Transitions
- Placement: update grid cell; update CandidateModel and caches (invalidate corridor/region; update degree for neighbors)
- Elimination: update CandidateModel; possibly trigger singleton placements
