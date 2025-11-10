# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context
# Implementation Plan: Adaptive Turn Anchors

**Branch**: `001-adaptive-turn-anchors` | **Date**: 2025-11-10 | **Spec**: specs/001-adaptive-turn-anchors/spec.md
**Input**: Feature specification from `/specs/001-adaptive-turn-anchors/spec.md`

## Summary

Implement a tiered, adaptive turn-anchor policy in the Hidato generator to enable minimal-clue uniqueness for hard/extreme puzzles while preserving structural clarity for easy/medium. Anchors are tagged hard (permanent) vs soft (droppable). Uniqueness repair becomes surgical: when multiple completions are detected, add a clue within the most ambiguous segment between solutions (midpoint/high branching). Add distribution/adjacency controls (min index gaps, 4-neighbor preference in ultra-sparse cases) to reduce clustering and improve aesthetics.

## Technical Context

**Language/Version**: Python 3.11 (stdlib only)  
**Primary Dependencies**: Internal modules only (core.grid, core.position, generate.generator, solve.solver)  
**Storage**: N/A (in-memory)  
**Testing**: pytest (existing suite + new tests for anchors)  
**Target Platform**: Cross-platform (local CLI); development on Windows Powershell  
**Project Type**: Single repository with domain modules (no web)  
**Performance Goals**: Maintain current generation latencies (e.g., backbite_v1 9x9 ~38ms avg) and determinism; uniqueness repair should add negligible overhead for most seeds  
**Constraints**: Constitution: no prints inside generators (return metrics), single RNG determinism, pipeline staging (PathBuilder → CluePlacer/Removal → Validator/Uniqueness → Difficulty)  
**Scale/Scope**: Small codebase change; new config fields and metrics; tests for 4 difficulties

## Constitution Check

Gates to verify (from constitution):
- Determinism & reproducibility: Use single RNG; record seed/modes.  
  Status: PASS — anchor policy must be deterministic and captured via `anchor_policy_name` and metrics.
- Separation of concerns: Generators don’t print; return data/metrics.  
  Status: PASS — expose `anchor_*` metrics in result; CLI may print when `--verbose`.
- Pipeline boundaries: Keep stages distinct.  
  Status: PASS — anchor selection sits within clue/anchor selection stage; uniqueness repair remains in uniqueness validation stage.
- Safety & validation: Never overwrite givens; validate before returning.  
  Status: PASS — repair adds clues intentionally; no inplace overwrite of existing givens.

Re-check after Phase 1: Expected PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-adaptive-turn-anchors/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
core/          # Domain model (Position, Cell, Grid, Constraints, Puzzle)
generate/      # Generator pipeline (PathBuilder, Generator, removal, uniqueness)
solve/         # Solvers and validators
tests/         # pytest suite (add anchor tests)
hidato.py      # CLI (surface anchor policy flags in future PR if desired)
```

**Structure Decision**: Keep single-project structure. Implement policy in `generate/generator.py`; add small policy helper if needed (e.g., `generate/anchor_policy.py`).

## Complexity Tracking

No deviations required at this time.
└── tests/
