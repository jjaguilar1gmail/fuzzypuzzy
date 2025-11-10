# Data Model: Solver-Driven Pruning

## Entities

### Puzzle
- size: (rows, cols)
- clue_positions: set[Position]
- path_signature: hash
- difficulty_band: enum{easy, medium, hard, extreme}
- uniqueness_status: enum{unique, non_unique, unknown}

### RemovalBatch
- batch_size: int
- candidate_positions: list[Position]
- attempt_index: int

### IntervalState
- low_index: int
- high_index: int
- contraction_reason: enum{unique_fail, density_goal, timeout}

### PruningSession
- iteration_count: int
- uniqueness_failures: int
- repairs_used: int
- history: list[IntervalState]

### AmbiguityProfile
- entries: list[{position: Position, frequency_score: float, segment_index: int}]
- computed_from_alternates: int

### RepairCandidate
- position: Position
- rationale: enum{high_divergence, branching_reduction}
- score: float

### MetricsReport
- final_density: float
- time_ms: float
- status: enum{success, success_with_repairs, aborted_max_repairs, aborted_timeout}
- pruning_iterations: int
- interval_contractions: int
- uniqueness_failures: int
- repairs_used: int

## Relationships
- PruningSession uses multiple RemovalBatches and maintains IntervalState history.
- AmbiguityProfile generated when uniqueness fails; RepairCandidate selected from profile.
- MetricsReport summarises PruningSession and final Puzzle state.

## Validation Rules
- Endpoints must remain in clue_positions (never removed).
- repairs_used ≤ configured cap (default 2).
- batch_size ≥ 1; interval indices within bounds.
- status must align with counts (e.g., success_with_repairs iff repairs_used ≥ 1 and uniqueness restored).
