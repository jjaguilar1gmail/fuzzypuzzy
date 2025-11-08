# Implementation Plan: Uniqueness-Preserving Puzzle Generator

**Branch**: `001-unique-puzzle-gen` | **Date**: 2025-11-08 | **Spec**: ./spec.md
**Input**: Feature specification from `/specs/001-unique-puzzle-gen/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a deterministic, uniqueness-preserving puzzle generator. Pipeline: PathBuilder (serpentine or RNG path via seed) → CluePlacer (seed initial anchors: 1, N, and turn-anchors) → Remove&Check loop (heuristic removal; run logic fixpoint, then bounded search; count_solutions cap=2) → Difficulty assess (logic%, nodes, max depth, corridor/degree hits) → Return GeneratedPuzzle with puzzle, full solution, and metadata. Supports optional blocked cells. Budgets: max_attempts, timeout_ms; returns best effort.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (standard library only per project guidelines)  
**Primary Dependencies**: Internal solver modules (`solve/solver.py`, `solve/corridors.py`, `solve/degree.py`), core domain (`core/*`), util tracing/validation.  
**Storage**: N/A (in-memory; optional JSON export)  
**Testing**: pytest, existing test harness; add unit + integration + contract tests for generator  
**Target Platform**: Windows/macOS/Linux (CLI)  
**Project Type**: Single library + CLI  
**Performance Goals**: Generation P95: Easy < 300ms, Medium < 800ms, Hard < 2500ms, Extreme < 5000ms (on reference machine).  
**Constraints**: Deterministic by seed; grid size ≤ 9x9; bounded nodes/time for uniqueness checks; do not mutate caller Puzzle.  
**Scale/Scope**: Single-user CLI/batch generation; supports batching packs of 10–100 puzzles.

## Constitution Check

Gates from constitution:
- Functions ≤ 60 loc, classes ≤ ~300 loc: Plan separate modules (path_builder.py, clue_placer.py, uniqueness.py, generator.py) to keep sizes small. PASS (planned)
- Determinism & reproducibility: Seed logged and used for RNG; single RNG instance. PASS
- Safety & validation: Validate inputs; validate final solution/uniqueness; never overwrite givens. PASS
- Solver rules: Run logic fixpoint before bounded search; bounded nodes/time. PASS
- Generator rules: Pipeline stages; never emit junk; return metadata; all randomness behind single RNG. PASS
- Versioning & composition: Mode strings for path_mode, clue_mode. PASS

Gate status: PASS (pre-design & post-design); Phase 0 research and Phase 1 artifacts complete with no violations.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── generate/
│   ├── path_builder.py         # Build full solution paths (serpentine or RNG)
│   ├── clue_placer.py          # Seed anchors, symmetry, percent_fill
│   ├── uniqueness.py           # count_solutions(cap=2), uniqueness checks
│   ├── difficulty.py           # compute metrics from solver trace
│   └── generator.py            # Orchestrates pipeline; public API
└── cli/
  └── hidato.py               # Add --generate options (seed, size, difficulty, etc.)

tests/
├── unit/
│   ├── test_path_builder.py
│   ├── test_clue_placer.py
│   ├── test_uniqueness.py
│   └── test_difficulty.py
└── integration/
  ├── test_generator_easy_medium.py
  ├── test_generator_hard_extreme.py
  └── test_generator_blocked_cells.py
```

**Structure Decision**: Single-project layout; new generate/ package with small modules per pipeline stage; CLI wiring in existing `hidato.py`; tests under unit/integration.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
