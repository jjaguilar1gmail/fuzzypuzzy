# Implementation Plan: Staged Uniqueness Validation

**Branch**: `001-staged-uniqueness-validation` | **Date**: 2025-11-10 | **Spec**: specs/001-staged-uniqueness-validation/spec.md
**Input**: Feature specification from `specs/001-staged-uniqueness-validation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Introduce a multi-stage uniqueness validation pipeline for Hidato-style puzzles to replace brittle exhaustive enumeration on large 8-neighbor boards. Pipeline stages: (1) Early-exit bounded backtracking with solution cap=2 using diverse ordering heuristics; (2) Seeded randomized solver probes with varied heuristic profiles (frontier bias, LCV weighting) to search for alternates within a strict aggregated time budget; (3) Optional SAT/CP hook performing one-solution + blocking-clause recheck under capped runtime. Output is tri-state (Unique, Non-Unique, Inconclusive) with metrics, never exceeding configured per-size budgets. Small boards (≤25 cells) still use authoritative enumeration first.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (stdlib only per constitution)  
**Primary Dependencies**: Standard library (time, heapq, dataclasses, random); optional external SAT/CP via hook (disabled by default).  
**Storage**: N/A (in-memory puzzle objects)  
**Testing**: pytest (existing test suite) + new contract/integration tests for staged uniqueness.  
**Target Platform**: Cross-platform (Windows/macOS/Linux) CLI + library usage.  
**Project Type**: Single Python project (src + specs + tests).  
**Performance Goals**: ≤100 ms median uniqueness check for ≤5x5; ≤600 ms total for ≥7x7 easy; ≤500 ms medium; ≤400 ms hard; ≥95% detection rate for known non-unique cases within budgets.  
**Constraints**: Must not mutate caller puzzles; deterministic given seed+config; solution enumeration only for ≤25 cells; memory footprint minimal (<5 MB incremental).  
**Scale/Scope**: Supports path modes (serpentine, random_walk, backbite_v1, hybrid variants); integrated into existing generation loop without structural refactor.

## Constitution Check (Pre-Design)

Principle alignment:
- Clarity & separation: New modules will remain ≤300 lines; strategies registered via lightweight registry.
- Determinism & reproducibility: Seed passed into probe stage; ordering heuristics selectable & logged.
- Safety & validation: Uniqueness checker never overwrites givens; works on puzzle copies.
- Testing discipline: New tests for solution-cap early exit, probe determinism, SAT hook fallback.
- Solver rules: Logic passes still precede any search; early-exit search obeys node/time caps.
- Generator rules: Uniqueness becomes a pipeline stage with clear input/output; budgets enforced.

GATE Result: PASS (no constitution violations anticipated). No complexity justification table needed.

## Constitution Check (Post-Design)

- All new docs adhere to separation of concerns; staged package boundaries are clear.
- Determinism ensured via seedable probes; budgets codified in data model.
- No solver/generator mutation of caller puzzles planned; interfaces emphasize pure inputs/outputs.
- Tests will accompany new behavior (unit + integration listed in structure).

GATE Result: PASS.

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
│   ├── uniqueness_staged/        # NEW: staged checker modules
│   │   ├── __init__.py
│   │   ├── early_exit.py         # Stage 1 strategies (heuristic variations)
│   │   ├── probes.py             # Stage 2 randomized probe orchestrator
│   │   ├── sat_hook.py           # Stage 3 optional SAT/CP integration (interface only)
│   │   ├── config.py             # Stage budgets, strategy enable flags
│   │   ├── result.py             # Tri-state result dataclasses
│   │   └── registry.py           # Strategy registration / discovery
│   └── pruning.py                # Existing pruning integration point (will call staged uniqueness)
├── solve/                        # Existing solver logic (reuse functions for probes)
├── core/                         # Domain objects
└── util/                         # RNG, timing helpers

tests/
├── unit/
│   ├── test_uniqueness_early_exit.py
│   ├── test_uniqueness_probes.py
│   ├── test_uniqueness_sat_hook.py
│   └── test_uniqueness_result_contract.py
├── integration/
│   ├── test_generation_pipeline_staged_uniqueness.py
│   └── test_path_modes_uniqueness_metrics.py
└── contract/
  └── test_deterministic_seeded_probes.py
```

**Structure Decision**: Single-project Python layout extended with a new `generate/uniqueness_staged` package; integrates with existing `generate/pruning.py` without refactoring solver or core domains.

## Complexity Tracking

No violations. Section intentionally minimal.
