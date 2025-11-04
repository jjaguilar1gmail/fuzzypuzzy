# Quickstart — Hidato Terminal MVP

This guide shows how to run the MVP in the terminal for demos. Packaging (`pip install -e .`) will come later.

## Prerequisites
- Python 3.11+
- pytest for running tests (optional)

## Run
- Start the REPL script (to be added in app/):
  - Generate a 5x5 puzzle, show, move, hint, solve, export

Example REPL session (illustrative):

```
> generate 5x5 --seed 123 --path serpentine --clues even
> show
> move 0 1 2
> hint
> solve
> export json demo/puzzle-5x5.json
> quit
```

## JSON Export Schema
- See `specs/001-hidato-terminal-mvp/contracts/puzzle.schema.json`

## Notes
- Renderer is ASCII-only for v0
- Supported sizes: 5x5, 7x7
- Adjacency default: 8-neighbor
