# CLI/REPL Command Contracts — Hidato MVP

This document defines the user-facing terminal commands for v0 (REPL-style). Not an HTTP API.

## Commands

### generate <size> [--seed <int>] [--path serpentine] [--clues even]
- Size: one of {5x5, 7x7}
- Output: prints ASCII grid and stores current puzzle in session
- Side-effects: logs metadata (seed, modes, timings)

### show
- Output: prints current puzzle in ASCII

### move <row> <col> <value>
- Validates placement against constraints; refuses to overwrite givens/blocked
- Output: success/failure message; prints updated grid on success

### hint
- Output: prints one suggested next placement with a short explanation

### solve
- Runs `logic_v0` to completion; prints final grid and a short summary

### export json <path>
- Writes current puzzle (and solution if solved) as JSON per schema

### import json <path>
- Loads a puzzle from JSON and sets it as current

### reset
- Clears non-givens, returning to initial state

### quit
- Exits REPL

## Error Messages
- Unsupported size → "Only 5x5 and 7x7 are supported in this version"
- Invalid move → specific reason (out of range, not adjacent, duplicate value, attempting to change a given/blocked)
- No puzzle loaded → "Generate or import a puzzle first"
