# Fuzzy Puzzy Number Riddle Constitution

## Core Principles
### 1. Clarity, size and seperation of concerns
- Functions ≤ 60 lines; classes ≤ ~300 lines before refactor.
- One responsibility per module.
- Core domain (Position, Cell, Grid, Constraints, Puzzle) has no I/O.
- Solvers/generators don’t print; they return data. Rendering lives in Exporters/CLI.

### 2. Determinism & reproducibility
- All generators accept a seed and must be reproducible.
- Log the seed, chosen modes (e.g., path=serpentine, clues=even), and timings for every run.

### 3. Safety & validation
- Never overwrite givens after a puzzle has been generated.
- Validate inputs on boundaries (rows/cols > 0, in-bounds positions).
- Before claiming “solved,” verify: each value used once; consecutive numbers are adjacent (per constraints).

### 4. Accessibility & UX basics
- Always provide an ASCII renderer.
- Export to JSON (puzzle + solution) with stable schema.

### 5. Testing discipline
- Contract tests for Position equality/hash, adjacency, and “givens immutable”.
- Every bug gets a test.

### 6. Solver (reasoning engine) rules
- Explainability first: Every automatic placement must record a short reason (strategy, cells, why).
- Provide hint(puzzle) that returns one next step with the same explanation.
- Monotone logic before search: Always run deterministic logic passes to a fixed point before any guessing.
- Monotone logic before search: Search (backtracking) is optional and bounded by config (node/time budgets).
- solve() must be deterministic given the same puzzle + config + seed.
- Do not mutate the caller’s Puzzle; work on a copy and return a Solution + Trace.
- Cheap checks (range, duplicate values, adjacency impossibility) must run before deeper work.

### 7. Generator (puzzle maker) rules
- When a random technique is used, accept seed and log it; generation must be replayable.
- Pipeline, not a blob: PathBuilder → CluePlacer → Validator → (optional) Uniqueness → (optional) Difficulty.
- Pipeline, not a blob: Each stage has a clear input/output and can be swapped later.
- Never emit junk: Before returning a puzzle: run structural validation and a light solvability sanity check.
- Never emit junk: If uniqueness is requested and not met within budget, return the best candidate with a reason.
- Always return: seed, path_mode, clue_mode, attempts, timings, difficulty_estimate.
- All randomness sits behind a single RNG.

### 8. Versioning & Composition (for both Solver and Generator)

- Config chooses behavior: Modes are strings (e.g., solver_mode="logic_v0", path_mode="serpentine", clue_mode="even_v0").
- Config chooses behavior: Public methods don’t change; internal versions dispatch by mode.
- Strategy registry (lightweight): Keep a dict of {name: fn} per component; new strategies only register themselves.
- Deprecations warn once, not silently change behavior.
- Contract tests across modes: The same interface tests run for every registered mode.

## Governance
- This constitution defines the minimum bar for any feature for the hidato (number riddle) puzzle code. Deviations require explicit PR justification
- Amendments must bump the version and dates below and align related templates/checklists in the repo


**Version**: 1.0.0 | **Ratified**: 2025-11-04 | **Last Amended**: 2025-11-04
