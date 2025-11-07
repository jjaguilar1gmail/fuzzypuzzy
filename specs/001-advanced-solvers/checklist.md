# Advanced Solvers Feature Checklist (001-advanced-solvers)

Date: 2025-11-06
Branch: 001-advanced-solvers
Spec: specs/001-advanced-solvers/spec.md

## Functional Requirements

- [ ] FR-001: Modes `logic_v1`, `logic_v2`, `logic_v3` exposed via Solver.solve and REPL CLI
- [ ] FR-002: v1 two-ended propagation implemented (forward/backward frontiers)
- [ ] FR-003: v1 has no guessing; reasons tagged `Propagation`/`Forced`
- [ ] FR-004: v2 region segmentation uses puzzle adjacency (4-way or 8-way); pruning by region capacity
- [ ] FR-005: v2 deterministic; reasons tagged `RegionPrune`
- [ ] FR-006: v3 applies v2 then bounded search with defaults max_nodes=500, max_depth=20
- [ ] FR-007: v3 records `Guess:` and `Backtrack` steps distinctly
- [ ] FR-008: Accurate SolverResult fields; v3 includes search stats
- [ ] FR-009: Hint supports choosing mode; non-mutating
- [ ] FR-010: v1/v2 performance <=300ms on 15x15 medium in reference env
- [ ] FR-011: v3 terminates gracefully on limit with informative message
- [ ] FR-012: Unit tests: v1-only, v2-only, v3-only solvable puzzles
- [ ] FR-013: Deterministic ordering of steps
- [ ] FR-014: Profiling/timing integrated when enabled
- [ ] FR-015: Region map caching to avoid O(n^2) rescans
- [ ] FR-016 (Resolved): Adjacency configurable (4-way or 8-way); default 8-way
- [ ] FR-017 (Resolved): Reference env defined (Win11, i7-12700H, 32GB RAM, Py 3.11.9)

## Success Criteria (Measurable)

- [ ] SC-001: v1 deterministic coverage ≥80% on 20-puzzle v0-fail set
- [ ] SC-002: v2 deterministic coverage ≥90% (v1 set) and ≥60% (hard set)
- [ ] SC-003: v3 overall ≥95% solve rate within default cap (500 nodes) for ≥90% runs; ≥98% with 2000-cap
- [ ] SC-004: v1/v2 median solve time ≤300ms; p90 ≤450ms (reference env)
- [ ] SC-005: v3 avg explored nodes ≤40% of naive DFS baseline; depth ≤60% baseline
- [ ] SC-006: v2 hint median latency ≤150ms; p90 ≤250ms
- [ ] SC-007: Zero invalid placements in v1/v2 logic modes
- [ ] SC-008: Deterministic trace hash stable across 5 runs/puzzle/mode
- [ ] SC-009: v3 peak memory overhead ≤30MB above idle baseline (largest 20x20)
- [ ] SC-010: Graceful partial result on budget exhaustion (100% consistency checks pass)

## Tests & Tooling

- [ ] Add fixtures for three puzzle sets (v1-only, v2-only, v3-needed)
- [ ] Test REPL `solve --mode` and `hint --mode` UX
- [ ] Ensure hint does not mutate puzzle state
- [ ] Add profiling toggles to solver entry points
- [ ] Update README: document new modes and examples
- [ ] Add deterministic tie-breaker (row/col) for equal candidates

## Review

- [ ] Code style: Python 3.11, standard lib only
- [ ] Lint: ruff check . (no new warnings)
- [ ] Tests: pytest all green on reference env
- [ ] Performance sample run recorded in PR description
