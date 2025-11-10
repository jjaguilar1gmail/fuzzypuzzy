# Task Breakdown: Solver-Driven Pruning

Generated: 2025-11-10
Branch: 001-solver-driven-pruning
Spec: specs/001-solver-driven-pruning/spec.md
Plan: specs/001-solver-driven-pruning/plan.md
Research: specs/001-solver-driven-pruning/research.md

## Milestone Overview

| Milestone | Goals | Related FRs | Exit Criteria |
|-----------|-------|-------------|---------------|
| M1: Core Pruning Engine | Interval reduction & removable clue ordering | FR-001, FR-002, FR-014 | Engine removes batches, contracts interval, reverts on uniqueness fail |
| M2: Uniqueness & Repair | Ambiguity profiling & targeted repair clues | FR-004, FR-005, FR-006, FR-007 | Repair adds ≤1 clue per cycle; uniqueness restored or abort after cap |
| M3: Difficulty & Anchors | Hard mode anchor policy changes | FR-003, FR-008, FR-009, FR-013 | Hard puzzles use endpoints only; difficulty band maintained |
| M4: Metrics & Determinism | Collect & expose run metrics | FR-010, FR-011, FR-012, FR-016 | Metrics JSON emitted; deterministic multi-run hash matches |
| M5: CLI & Config | Expose flags and ranges | FR-001..FR-016 | Flags present; validation errors handled |
| M6: Testing & Benchmarks | Coverage across logic, performance | SC-001..SC-009 | Test suite passes; benchmarks recorded |
| M7: Docs & Final Verification | Quickstart, README, success criteria report | SC-001..SC-009 | Documentation complete; verification report stored |

## Task List

### Core Pruning Engine (M1)
1. T01 Removable Clue Ordering
   - Implement ordering heuristic (distance from endpoints + corridor centrality).
   - Acceptance: Ordering stable across runs with same seed.
2. T02 Interval Reduction Loop
   - Implement binary-search style contraction over indices (low/high).
   - Acceptance: Logs contraction reasons; stops at size 1 or density met.
3. T03 Revert on Uniqueness Fail
   - Snapshot puzzle state before batch; revert if uniqueness fails.
   - Acceptance: No residual removed clues after failed batch.
4. T04 Linear Fallback for Boundary
   - Switch to single-clue probing when remaining removable set ≤ K (default 6).
   - Acceptance: Fallback triggers and shrinks clue count further or exits cleanly.

### Uniqueness & Repair (M2)
5. T05 Alternate Solutions Sampling
   - Generate 3–5 alternates under time cap; collect differing cells.
   - Acceptance: Alternates list length within configured range; time ≤ limit.
6. T06 Ambiguity Profile Construction
   - Frequency scoring + corridor weighting.
   - Acceptance: Profile sorted descending by score; ties deterministic.
7. T07 Repair Candidate Selection
   - Choose top-N mid-segment (avoid turns) cell; inject clue.
   - Acceptance: Injection reduces alternate count; recorded rationale.
8. T08 Repair Cycle Cap Enforcement
   - Abort uniqueness repair after cap; set status aborted_max_repairs.
   - Acceptance: Status and metrics reflect cap breach.

### Difficulty & Anchors (M3)
9. T09 Disable Turn Anchors for Hard/Extreme
   - Modify anchor selection to endpoints only for hard+.
   - Acceptance: Hard puzzle generation shows Anchor Count = 2.
10. T10 Preserve Legacy Behavior (Easy/Medium)
    - Ensure unchanged anchor logic for easy/medium.
    - Acceptance: Existing anchor tests still pass.
11. T11 Difficulty Band Validation Post-Repair
    - Recalculate difficulty after each repair; rollback alternate repair if downgraded.
    - Acceptance: Hard puzzles remain in hard band ≥95%.

### Metrics & Determinism (M4)
12. T12 Metrics Aggregator Structure
    - Collect iterations, contractions, uniqueness failures, repairs.
    - Acceptance: Metrics JSON section present; types correct.
13. T13 Deterministic Hashing
    - Stable hash of clue positions + path signature + difficulty.
    - Acceptance: 5 identical runs produce identical hash.
14. T14 Status Classification Logic
    - Map metrics to status enum.
    - Acceptance: All four statuses reachable in controlled test scenarios.
15. T15 Timeout Handling
    - Abort long alternates sampling; set aborted_timeout if exceeded.
    - Acceptance: Timeout scenario produces correct status and partial metrics.

### CLI & Config (M5)
16. T16 Add Pruning Flags
    - pruning.enabled, max_repairs, target_density_hard, linear_fallback_k.
    - Acceptance: Flags parsed & validated; help text updated.
17. T17 Config Validation
    - Density ranges sensible; max_repairs ≥ 0; fallback_k ≥ 1.
    - Acceptance: Invalid config raises descriptive error.

### Testing & Benchmarks (M6)
18. T18 Unit Tests: Interval Reduction
    - Cases: contraction, uniqueness fail revert, fallback switch.
19. T19 Unit Tests: Ambiguity Profile & Repair
    - Cases: uniform ambiguity, tie-break determinism.
20. T20 Integration Tests: Hard Puzzle Endpoints Only
    - Confirm anchors constraint.
21. T21 Integration Tests: Repair Cycle Cap
    - Force scenario needing >2 repairs.
22. T22 Benchmark Script
    - Measure median time & iterations for 20 seeds pre/post.
23. T23 Determinism Test Harness
    - Multiple seeds & repeated runs.
24. T24 Edge Case Tests
    - Small grid hard mode, timeout scenario, non-unique after repairs.

### Docs & Final Verification (M7)
25. T25 Update Quickstart & README
    - Add pruning usage, metrics interpretation.
26. T26 Success Criteria Report
    - Generate verification summary (SC-001..SC-009).
27. T27 Final Constitution Audit
    - Confirm no domain/IO leakage; function lengths.
28. T28 Post-Implementation Cleanup
    - Remove deprecated linear removal code path if fully superseded (unless used by fallback).

## Mapping Tasks to Requirements / Success Criteria

| Task | FR/SC Coverage |
|------|----------------|
| T01–T04 | FR-001, FR-002, FR-014 |
| T05–T08 | FR-004–FR-007, SC-004, SC-005 |
| T09–T11 | FR-003, FR-008, FR-009, FR-013, SC-007 |
| T12–T15 | FR-010–FR-012, FR-016, SC-002, SC-003, SC-008, SC-009 |
| T16–T17 | FR-001..FR-016 (exposure), SC-001..SC-009 (enables measurement) |
| T18–T24 | All FR; SC-001..SC-009 validation |
| T25–T26 | Documentation & success criteria communication |
| T27–T28 | Constitution compliance & maintainability |

## Risk & Mitigation Notes
- Ambiguity Profiling Performance: Cache candidate evaluations; reduce alternates_count if slow.
- Over-Repair Risk: Cap at 2, log reason, return best-so-far.
- Boundary Thrashing: Early detection triggers linear fallback.
- Difficulty Downgrade After Repair: Alternate cell choice; if repeated, accept higher clue count.

## Done Definition per Milestone
- All tasks in milestone PASS tests + metrics verified + docs updated.

## Next Steps
- Begin with T01–T04; create feature flag scaffolding first (T16) to allow incremental activation.
