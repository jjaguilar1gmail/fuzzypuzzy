# Data Model: Hidato Web Game & Puzzle Packs

Date: 2025-11-11
Branch: 001-hidato-web-game

## Entities

### Puzzle
- Fields: id (string), size (int), difficulty (enum: easy|medium|hard|extreme), seed (int), clue_count (int), max_gap (int), givens (array of {row:int,col:int,value:int}), solution (array of {row:int,col:int,value:int}), pack_id (string)
- Validation:
  - size between 5 and 10 for MVP
  - clue_count > 0
  - max_gap <= 12 (guardrail) 
  - givens unique by (row,col)
  - solution contiguous values 1..(size*size or path length) if provided
- Relationships: belongs to Pack

### Pack
- Fields: id (string), title (string), description (string|optional), puzzles (array of Puzzle.id), difficulty_counts (map difficulty->int), size_distribution (map size->int), created_at (timestamp)
- Validation:
  - puzzles length > 0
  - difficulty_counts keys subset of difficulty enum

### PlayerState (local only)
- Fields: puzzle_id, cell_entries (map key:"r,c" value:int), candidates (map key:"r,c" value: int[]), elapsed_time_ms (int), undo_stack (array of action objects), settings {theme:string, sound:boolean, pencilModeDefault:boolean}
- Validation:
  - candidate arrays length <=4
  - undo_stack length <=100

### GenerationRun (backend report)
- Fields: timestamp, parameters {sizes:int[], difficulties:string[], count:int, path_mode:string}, generated_count, skipped_count, average_ms, failures (array of {seed:int, reason:string})
- Validation:
  - generated_count + skipped_count >= count*sizes*difficulties

## Derived Constraints
- Daily puzzle selection: compute hash(date) mod total_puzzles; fallback to next id if missing.
- Local persistence versioning: include schema_version to migrate future changes.

## State Transitions
- PuzzleState: empty -> in_progress (first placement) -> completed (all values placed & validation pass)
- PackProgress: not_started -> active -> completed (all puzzles completed)

