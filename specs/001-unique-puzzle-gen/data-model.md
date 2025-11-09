# Data Model: Uniqueness-Preserving Puzzle Generator

## Entities

### GeneratedPuzzle
- size: int
- allow_diagonal: bool
- blocked_cells: list[(row:int, col:int)]
- givens: list[(row:int, col:int, value:int)]  # final clue set
- solution: list[(row:int, col:int, value:int)] # full solution grid values
- difficulty_label: str (easy|medium|hard|extreme)
- difficulty_score: float (0..1 or band-specific index)
- clue_count: int
- uniqueness_verified: bool
- attempts_used: int
- seed: int
- path_mode: str ("serpentine"|"random_walk")
- clue_mode: str ("anchor_removal_v1")
- symmetry: str|None ("rotational"|"horizontal"|None)
- timings_ms: dict { total:int, solve:int, uniqueness:int }
- solver_metrics: dict { nodes:int, depth:int, steps:int, logic_ratio:float, strategy_hits:dict }
- version: str

### GenerationConfig
- size: int (≤ 9)
- allow_diagonal: bool
- blocked: list[(r,c)]|None
- difficulty: str|None
- percent_fill: float|None (0..1)
- seed: int|None
- path_mode: str
- clue_mode: str
- symmetry: str|None
- turn_anchors: bool (default True)
- timeout_ms: int (overall cap)
- max_attempts: int
- uniqueness_node_cap: int
- uniqueness_timeout_ms: int

### UniquenessCheckResult
- is_unique: bool
- solutions_found: int (1 or 2)
- nodes: int
- depth: int
- elapsed_ms: int

### DifficultyProfile
- name: str
- clue_density_min: float
- clue_density_max: float
- max_search_depth: int
- expected_max_nodes: int
- metrics_thresholds: dict

## Relationships
- GeneratedPuzzle produced by generator using GenerationConfig
- DifficultyProfile selected by difficulty label; used to evaluate solver_metrics

## Validation Rules
- size in [2..9]
- values within [1..N] where N = size*size - len(blocked)
- givens must include value 1 and N
- all given positions unique and not blocked; solution includes every non-blocked cell
- uniqueness_verified must only be true if UniquenessCheckResult.solutions_found == 1 under configured caps

## State Transitions
1. Start: Build solved path
2. Seed anchors (givens)
3. Removal loop (mutating candidate givens set)
4. Verify solvable & uniqueness after each removal/batch
5. Finalize metadata and return
