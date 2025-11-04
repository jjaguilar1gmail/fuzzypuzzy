# Phase 0: Research & Decisions — Hidato Terminal MVP

Created: 2025-11-04
Branch: 001-hidato-terminal-mvp
Spec: specs/001-hidato-terminal-mvp/spec.md

## Decisions

- Decision: Adjacency default = 8-neighbor for Hidato
  - Rationale: Standard Hidato rules allow diagonals; aligns with user expectation for easy puzzles
  - Alternatives: 4-neighbor (orthogonal only) — simpler but less standard; may yield fewer easy serpentine paths

- Decision: Blocked cells in MVP = none (rectangular shape)
  - Rationale: Simplicity for serpentine generation; reduces validation complexity and improves demo speed
  - Alternatives: Support blocked shapes via ShapeFactory — postpone to later modes

- Decision: Generator path_mode = "serpentine" (left→right then right→left rows, or top→bottom snake)
  - Rationale: Deterministic, trivial to validate; guarantees a Hamiltonian path on rectangle
  - Alternatives: Random DFS path — less predictable, harder to explain; keep for later

- Decision: Clue mode = "even" (seed a handful of evenly spaced numbers plus 1 and N)
  - Rationale: Ensures solvability with simple logic; meets requirement to include 1 and N
  - Alternatives: Difficulty-based adaptive clues — later work

- Decision: Solver mode = "logic_v0" (consecutive-logic only)
  - Rationale: Easy to explain; runs to fixed point; deterministic without search
  - Alternatives: Backtracking search — optional future mode with bounds

- Decision: Renderer = ASCII only (v0), moved to io/exporters.py
  - Rationale: Constitution requires core purity; ASCII sufficient for presentation
  - Alternatives: SVG/PNG — later

- Decision: Serialization = JSON only (v0) in io/serializers.py
  - Rationale: Portability and stability; meets constitution
  - Alternatives: YAML — later

- Decision: REPL minimal command set in app/api.py (or app/repl.py)
  - Rationale: Quick demo; no packaging required for v0; later add CLI entry point

- Decision: Reproducibility via util.rng (seeded)
  - Rationale: Constitution requirement; log seed, modes, timings with each generation

## Open Questions (resolved here)

- Size presets: Support {5x5, 7x7} explicitly; reject others with message
- Timeouts/budgets: 3s generate (7x7), 4s solve (7x7) as soft goals; generator attempts capped at small number even though serpentine is O(1)
- Data captured on export: seed, path_mode, clue_mode, size, givens, adjacency, must_be_connected, timings

## Notes

- All components should log mode strings and seed into a metadata dict returned alongside the Puzzle for easy printing/export.
