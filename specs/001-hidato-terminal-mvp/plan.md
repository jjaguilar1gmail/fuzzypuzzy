# Implementation Plan: Hidato Terminal MVP

**Branch**: `001-hidato-terminal-mvp` | **Date**: 2025-11-04 | **Spec**: specs/001-hidato-terminal-mvp/spec.md
**Input**: Feature specification from `/specs/001-hidato-terminal-mvp/spec.md`

## Summary

Goal: Deliver a terminal-playable Hidato MVP that can generate easy puzzles (5x5, 7x7), render them in ASCII, accept validated moves, provide hints, and auto-solve using simple consecutive logic. For v0, run as a script/REPL; packaging (`pip install -e .`) comes later.

Approach: Implement a reproducible generation pipeline (PathBuilder serpentine → CluePlacer even → Validator), a deterministic logic solver (consecutive constraints, no guessing), ASCII renderer (moved out of core to I/O), and JSON serializer. Use mode-based dispatch for extensibility (e.g., `PathBuilder.build(mode="serpentine")`, `CluePlacer.choose(mode="even")`, `Solver.solve(mode="logic_v0")`).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Standard library only for v0 (json, dataclasses optional); future YAML/SVG optional later
**Storage**: Files (JSON export/import for puzzles and metadata)
**Testing**: pytest (already present), expand unit + integration tests
**Target Platform**: Cross-platform terminal (Windows/macOS/Linux); MVP verified on Windows PowerShell
**Project Type**: Single Python project with packages: core, generate, solve, io, app, util, tests
**Performance Goals**: From spec: 5x5 generate < 2s, 7x7 < 3s; auto-solve 5x5 < 2s, 7x7 < 4s
**Constraints**:
- Reproducibility: all generation accepts a seed; log seed and modes
- Core purity: no I/O in core (move current printing out of `core.grid`)
- Renderer: ASCII only for v0; JSON serializer available; no SVG yet
- Deterministic solver: do not mutate caller’s Puzzle; return result + trace explanation
**Scale/Scope**: Single-user terminal play; small grids (≤ 7x7) for demo

## Constitution Check

Gates derived from constitution:
- Core domain has no I/O → ACTION: Move `print_grid`/`pretty_print_grid` from `core/grid.py` to I/O renderer (PASS after change)
- Determinism & reproducibility with seed logging (PASS – plan includes `util.rng` and metadata logging)
- Safety & validation: enforce range, adjacency; never overwrite givens (PASS – covered in solver/validator)
- Accessibility: ASCII renderer; JSON export (PASS – planned)
- Testing discipline: add unit tests for core contracts; every bug gets a test (PASS – planned)
- Solver rules: explainable steps, monotone logic before search, deterministic, work on copy (PASS – planned for `logic_v0`)
- Generator rules: pipeline stages, uniqueness/sanity checks before emitting (PASS – planned)
- Versioning & composition: mode strings, registry, stable public methods (PASS – aligned with mode API)

Gate status: PASS with one planned refactor (move printing out of core).

## Project Structure

### Documentation (this feature)

```text
specs/001-hidato-terminal-mvp/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contracts, JSON schema)
└── tasks.md             # Phase 2 (created by /speckit.tasks later)
```

### Source Code (repository root)

```text
core/         # Pure domain: Position, Cell, Grid, Constraints, Adjacency, Puzzle (no I/O)
solve/        # Solver entry (Solver), strategies registry, uniqueness, difficulty (v0: logic_v0)
generate/     # PathBuilder (serpentine), CluePlacer (even), Symmetry (optional), Validator, Generator
io/           # serializers (JSON), exporters/renderer (ASCII), parsers (JSON in)
app/          # API facade, presets, REPL (simple commands for play)
util/         # rng (seeded), profiling, logging, config
tests/        # unit + integration (generation/solve/renderer contracts)
```

**Structure Decision**: Maintain current packages; enforce separation (renderer in io/, REPL in app/). Introduce lightweight strategy registries for mode-based dispatch in `generate` and `solve`.

## Complexity Tracking

No constitution violations expected after moving renderer out of core. No additional complexity justifications needed.
