# Data Model (Phase 1) — Advanced Solver Modes

This document defines in-memory entities and relationships for solver modes v1–v3.

## Core Domain (existing)
- Position(row:int, col:int)
- Cell(pos:Position, value:int|None, given:bool)
- Grid(cells:2D[Cell], neighbors_of(pos):list[Position])
- Constraints(min_value:int, max_value:int, adjacency:"4"|"8")
- Puzzle(grid:Grid, constraints:Constraints)

## Solver Entities (new/extended)

### CandidateModel
- value_to_positions: dict[int, set[Position]]
- pos_to_values: dict[Position, set[int]]
- Methods:
  - init_from(puzzle)
  - remove_value_from_pos(value, pos)
  - assign(value, pos) → updates both maps
  - candidates_for_value(value) → set[Position]
  - candidates_for_pos(pos) → set[int]

### PropagationFrontier (v1)
- anchor_value: int
- direction: int  # +1 or -1
- candidates: set[Position]

### SequenceGap (v2)
- start_value: int
- end_value: int
- length: int  # end-start-1

### EmptyRegion (v2)
- id: int
- cells: set[Position]
- size: int
- boundary_values: set[int]
- adjacency: Literal[4,8]

### CorridorMap (v2)
- key: tuple[int,int]  # (start_value, end_value)
- cells_on_any_corridor: set[Position]

### DegreeIndex (v2)
- degree: dict[Position, int]  # count of legal neighbors under current state

### SearchNode (v3)
- depth: int
- chosen_pos: Position|None
- chosen_value: int|None
- remaining_values: set[int]
- hash: int

### SearchStats (v3)
- nodes_explored: int
- max_depth_reached: int
- pruned_nodes: int
- guesses_made: int
- elapsed_ms: int

## Validation Rules
- Values unique in grid.
- Adjacency: consecutive numbers must be adjacent as per constraints.adjacency.
- CandidateModel consistency invariants across maps.
- DegreeIndex: endpoint values may have degree==1; middle values require degree>=2.

## State Transitions
- assign(value,pos): updates puzzle copy, CandidateModel, DegreeIndex, regions cache, corridormap as needed; push step to trace.
- backtrack(node): revert last assignment(s), restore candidate diffs, stats updated.
