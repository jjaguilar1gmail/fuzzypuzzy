# Phase 1: Data Model — Hidato Terminal MVP

Created: 2025-11-04

## Entities

### Position
- Fields: row:int, col:int
- Equality/hash: value-based

### Cell
- Fields: pos:Position, value:Optional[int], blocked:bool, given:bool
- Derived: is_empty(), is_filled()

### Grid
- Fields: rows:int, cols:int, cells:List[List[Cell]], adjacency:Adjacency
- Ops: get_cell, iter_cells, neighbors_of(Position)
- No rendering in core

### Adjacency
- Fields: allow_diagonal:bool
- Ops: get_neighbors(Position) -> List[tuple[int,int]]

### Constraints
- Fields: min_value:int, max_value:int, allow_diagonal:bool, must_be_connected:bool,
          blocked_allowed:bool, value_set:Optional[set[int]]
- Ops: in_bounds, valid_value, valid_transition(a:Position,b:Position), neighbors()

### Puzzle
- Fields: grid:Grid, constraints:Constraints, difficulty:str
- Ops: givens(), to_dict(), from_dict(), occupied_positions(), empty_positions(),
      value_positions(), is_complete(), is_valid_partial(), verify_path_contiguity(),
      clone(replacements), clear_non_givens(), summary()

### Move (play interaction)
- Fields: pos:Position, value:int
- Rules: valid if value in range and consecutive-adjacent to neighbors as per constraints; cannot overwrite given/blocked

### GeneratorConfig
- Fields: seed:int, path_mode:str ("serpentine"), clue_mode:str ("even"), size:(rows,cols)

### SolverConfig
- Fields: mode:str ("logic_v0"), max_time_s:float (soft), explain:bool (record steps)

### RendererConfig
- Fields: ascii_theme:str (simple), show_givens:bool, show_blocked:bool

## Relationships
- Puzzle has Grid & Constraints
- Grid has Cells; Cells have Position
- Generator produces (Puzzle, metadata)
- Solver consumes Puzzle and returns (Solution, trace) without mutating input

## Validation Rules
- Position in_bounds on access; Grid.get_cell raises on OOB
- Constraints.valid_value must hold for any placement
- No duplicate values in Puzzle; givens immutable
- If must_be_connected: verify_path_contiguity checks (k,k+1) adjacency for placed consecutive pairs
