# Implementation Plan: Smart Path Modes

**Branch**: `001-smart-path-modes` | **Date**: 2025-11-09 | **Spec**: specs/001-smart-path-modes/spec.md  
**Input**: Feature specification from `/specs/001-smart-path-modes/spec.md`

**Note**: Generated via /speckit.plan workflow.

## Summary

Replace the slow/unstable random_walk and silent serpentine fallback with smart, bounded path-building modes:
1. Add `backbite_v1`: start from a valid Hamiltonian path (serpentine or strip-shuffle) and apply randomized backbite end-reversal moves within a step/time budget to yield organic, fully-connected paths in (amortized) linear time.
2. Refactor `random_walk`: add Warnsdorff-style neighbor ordering, component/degree checks, and strict limits (max_nodes, max_time_ms, max_restarts) so it exits gracefully with diagnostics.
3. Introduce partial-coverage acceptance: accept ≥85% coverage by treating remaining unvisited cells as blocked and adjusting constraints.max_value.
4. Eliminate silent serpentine fallback: PathBuilder returns structured result (ok, reason, coverage) so Generator can retry, switch to backbite_v1, or accept partial.

## Technical Context

**Language/Version**: Python 3.11 (stdlib only)  
**Primary Dependencies**: Internal modules only (core.grid, util.rng, generate.*)  
**Storage**: N/A (in-memory)  
**Testing**: pytest (extend with new path + partial coverage tests)  
**Target Platform**: Cross-platform CLI  
**Project Type**: Single-module puzzle generator/solver repo  
**Performance Goals**: 9x9 generation ≤ 6000ms p90 (smart modes); zero hangs  
**Constraints**: Determinism by seed; bounded time/node budgets; path coverage threshold  
**Scale/Scope**: Grid sizes 2–9; supports blocked cells; 4/8 adjacency.

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Determinism | PASS | Single RNG thread through new modes |
| Separation | PASS | PathBuilder returns data only |
| Safety | PASS | No silent fallback; structured reasons |
| Never emit junk | PASS | Coverage + uniqueness checked; partial requires threshold |
| Logging | PASS | Extend metrics with path_build_ms, coverage |
| Reproducibility | PASS | backbite_v1 & heuristics ordered deterministically |

## Project Structure

Documentation additions under `specs/001-smart-path-modes/` (research.md, data-model.md, contracts/, quickstart.md).  
Source changes isolated to `generate/path_builder.py`, `generate/generator.py`, and new tests.

**Structure Decision**:
- `generate/path_builder.py`: add backbite_v1, refactor random_walk, export PathBuildResult
- `generate/generator.py`: integrate partial acceptance logic & config flags
- `tests/`: new unit + property tests

## Complexity Tracking

No constitution violations introduced. Return type adaptation wrapped; legacy API (list of positions) still derivable from PathBuildResult.positions.

## Phase 0: Research (Output: research.md)

Research Topics & Decisions:
1. Backbite Initialization: Use serpentine baseline; optional strip-shuffle (permute row segments) for variety.
2. Backbite Move: Random endpoint; pick candidate internal node neighbor; reverse segment to form new endpoint connection; skip if no topology change.
3. Budget Heuristic: steps = min(size^3, path_time_ms // 2); early abort if no change in last size*2 iterations.
4. Warnsdorff Ordering: Sort neighbors by onward unvisited degree ascending to reduce dead-ends in random_walk.
5. Fragmentation Check: Skip move that would isolate pocket <3 cells before 85% coverage.
6. Limits: max_nodes=5000, max_restarts=5, max_time_ms=path_time_ms.
7. Partial Coverage Policy: Accept if coverage ≥ min_cover_ratio (default 0.85); otherwise return ok=False reason=coverage_below_threshold.
8. Result Schema: PathBuildResult(ok, reason, coverage_ratio, full_length, positions, mode_used, elapsed_ms, metrics{steps, restarts}).
9. Determinism: All random choices through RNG; neighbor ordering stable.
10. Fallback Handling: Generator orchestrates retries; PathBuilder never auto-substitutes.

Action: Produce `research.md` enumerating each decision with rationale and alternatives table.

## Phase 1: Design & Contracts (Outputs: data-model.md, contracts/, quickstart.md)

Design Tasks:
- Add dataclasses: PathBuildSettings, PathBuildResult.
- Extend GenerationConfig: allow_partial_paths, min_cover_ratio, path_time_ms.
- Refactor PathBuilder.build: dispatch + structured result for all modes.
- Implement backbite_v1 loop with budget + convergence detection.
- Enhance random_walk: heuristics, limits, partial returns.
- Update Generator: interpret PathBuildResult; adjust constraints for partial acceptance; metrics enrichment.
- CLI: add flags --path-mode backbite_v1 (default smart), --allow-partial-paths, --min-cover, --path-time-ms.

Internal Contracts (to write):
1. contracts/path_builder.md – semantics per mode, result fields, reasons catalog (timeout, partial, exhausted_restarts, coverage_below_threshold, success).
2. contracts/generator.md – decision matrix (accept partial / retry same mode / switch mode / abort) based on (ok, reason, coverage, attempts).

Quickstart Enhancements:
- Example: full backbite_v1 generation.
- Example: partial acceptance (show coverage).
- Example: mode switch after failed random_walk attempt.

Testing Outline:
- Determinism: Same seed → identical PathBuildResult.positions & metrics snapshot.
- Coverage Enforcement: Force low time budget to trigger partial acceptance path.
- Threshold Rejection: Set min_cover_ratio > reachable to confirm failure reason.
- Random Walk Guardrails: max_restarts honored; returns structured non-hang.
- Backbite Diversity: Path shape variance across seeds (turn count distribution).
- Performance: Benchmark 9x9 across 5 seeds under 6000ms p90.

Post-Design Constitution Re-check (expected PASS): determinism, separation, logging, safe failure modes.

## Phase 2 (Future – not executed here)

Will create tasks.md enumerating incremental implementation steps: (1) data models, (2) PathBuildResult integration, (3) backbite core, (4) random_walk refactor, (5) partial acceptance & generator integration, (6) CLI flags, (7) tests, (8) docs, (9) benchmarks.

## Next Steps
1. Create research.md.
2. Create data-model.md.
3. Draft contracts (path_builder.md, generator.md).
4. Add quickstart examples.
5. Run update-agent-context script (add new modes & flags).
6. Proceed to tasks specification file generation.

# Implementation Plan: Smart Path Modes

**Branch**: `001-smart-path-modes` | **Date**: 2025-11-09 | **Spec**: specs/001-smart-path-modes/spec.md
**Input**: Feature specification from `/specs/001-smart-path-modes/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace the slow/unstable random_walk and silent serpentine fallback with smart, bounded path-building modes:
- Add `backbite_v1`: start from a valid Hamiltonian path (serpentine or strip-shuffle) and apply randomized backbite end-reversal moves within a step/time budget to yield organic, fully-connected paths in linear time.
- Refactor `random_walk`: add Warnsdorff-style neighbor ordering, component/degree checks, and strict limits (max_nodes, max_time_ms, max_restarts) so it exits gracefully with diagnostics.
- Introduce partial-coverage acceptance: allow accepting ≥85% coverage by blocking the remainder and reducing max_value accordingly.
- Eliminate silent serpentine fallback: return a structured result (ok, reason, coverage) so Generator can retry, switch to backbite_v1, or accept partials.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (standard library only)
**Primary Dependencies**: Internal modules only (core.grid, util.rng, generate.*)
**Storage**: N/A (in-memory)
**Testing**: pytest (existing); add unit tests for path modes and partial coverage
**Target Platform**: Windows/macOS/Linux (CLI Python)
**Project Type**: Single repo with generator/solver modules
**Performance Goals**: 9x9 generation ≤ 6000ms p90 for smart mode; no hangs
**Constraints**: Deterministic by seed; bounded by time/node budgets; adhere to constitution
**Scale/Scope**: Sizes 2–9; blocked cells supported; 4/8-adjacency

## Constitution Check

Gates to pass:
- Determinism & reproducibility: All new modes accept seed and use single RNG. PASS (design enforces RNG).
- Pipeline separation: PathBuilder returns data only; no I/O. PASS (PathBuilder API retained).
- Safety & validation: No fallback that mutates givens; explicit return object. PASS (design returns {ok, reason, coverage}).
- Never emit junk: Generator validates/decides based on structured result; uniqueness optional stays bounded. PASS.
- Logging: seed, path_mode, timings captured. PASS (extend metrics with coverage/time/mode).

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
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Single project; implement under existing modules:
- `generate/path_builder.py`: add backbite_v1; refactor random_walk; return structured PathBuildResult
- `generate/generator.py`: add config flags (allow_partial_paths, min_cover_ratio, path_time_ms); handle structured result
- `tests/`: add unit tests for new modes and partial coverage

## Complexity Tracking

No violations expected. Modes plug into existing registry without new projects. Return-type change is compatible when gated within PathBuilder API.
