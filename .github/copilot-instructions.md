# fuzzypuzzy Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-04

## Active Technologies
- Python 3.11.x + Standard library only (dataclasses optional) (001-advanced-solvers)
- N/A (in-memory puzzle state) (001-advanced-solvers)
- Python 3.11 (standard library only; dataclasses optional) + Standard library (collections, dataclasses, time, heapq) (001-fix-v2-v3-solvers)
- Python 3.11 (standard library only per project guidelines) + Internal solver modules (`solve/solver.py`, `solve/corridors.py`, `solve/degree.py`), core domain (`core/*`), util tracing/validation. (001-unique-puzzle-gen)
- N/A (in-memory; optional JSON export) (001-unique-puzzle-gen)
- Python 3.11 (stdlib only) + Internal modules only (core.grid, util.rng, generate.*) (001-smart-path-modes)
- N/A (in-memory) (001-smart-path-modes)

- Python 3.11+ + Standard library only for v0 (json, dataclasses optional); future YAML/SVG optional later (001-hidato-terminal-mvp)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 001-smart-path-modes: Added Python 3.11 (stdlib only) + Internal modules only (core.grid, util.rng, generate.*)
- 001-unique-puzzle-gen: Added Python 3.11 (standard library only per project guidelines) + Internal solver modules (`solve/solver.py`, `solve/corridors.py`, `solve/degree.py`), core domain (`core/*`), util tracing/validation.
- 001-fix-v2-v3-solvers: Added Python 3.11 (standard library only; dataclasses optional) + Standard library (collections, dataclasses, time, heapq)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
