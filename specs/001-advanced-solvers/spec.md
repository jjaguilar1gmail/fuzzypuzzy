# Feature Specification: Advanced Solver Modes (Logic v1, v2, v3)

**Feature Branch**: `001-advanced-solvers`  
**Created**: 2025-11-06  
**Status**: Draft  
**Input**: User description: "create three more potential solving techniques: v1 stronger logic (two-ended propagation, no guessing), v2 board shape aware pruning (no guessing), v3 hybrid of v2 logic + bounded smart guess/backtracking"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Solve with Enhanced Pure Logic (Logic v1) (Priority: P1)

As a player, I can invoke `solve --mode logic_v1` (or select it in the REPL) to solve puzzles using two-ended propagation logic without any guessing, so moderately harder puzzles than v0 are solved deterministically.

**Why this priority**: Enables greater puzzle coverage while keeping deterministic/no-guess guarantees; foundation for higher modes.

**Independent Test**: Generate a medium puzzle known unsolved by `logic_v0` but solvable by two-ended propagation; run `solve --mode logic_v1` and verify solved flag True with only logical steps.

**Acceptance Scenarios**:

1. **Given** a puzzle with two disjoint numeric anchors (e.g., 1 and 10 placed), **When** mode `logic_v1` runs, **Then** it extends candidate frontiers from both ends and fills at least one forced value bridging toward completion.
2. **Given** a puzzle solvable via propagation but not by current v0 single-step constraints, **When** solving in `logic_v1`, **Then** result is solved with steps count > 0 and no guess/backtrack records.

---

### User Story 2 - Shape/Region Aware Logic (Logic v2) (Priority: P2)

As a player, I can use `solve --mode logic_v2` to apply region segmentation (contiguous empty areas) and prune impossible placements based on span limits between known consecutive numbers, increasing deterministic solvability depth without guessing.

**Why this priority**: Adds spatial reasoning to pure logic, reducing candidate explosion and enabling harder deterministic solves.

**Independent Test**: Construct a puzzle where region size constraints eliminate all but one placement for a missing number; run `logic_v2` and confirm correct placement due to region span pruning absent in v1.

**Acceptance Scenarios**:

1. **Given** a puzzle with a known gap between value A and B (A+K=B) and multiple regions, **When** `logic_v2` evaluates region sizes, **Then** only regions with size ≥ K are considered for intermediate values, pruning others.
2. **Given** a region whose shape physically disconnects required adjacency chain, **When** `logic_v2` analyzes adjacency continuity, **Then** it rejects that region for the sequence.

---

### User Story 3 - Hybrid Logic + Bounded Smart Search (Logic v3) (Priority: P3)

As a player, I can select `solve --mode logic_v3` to run all deterministic logic (v2) first, then perform a bounded depth best-first speculative search with pruning and early backtrack to finish harder puzzles, while retaining step explanations distinguishing logic from guesses.

**Why this priority**: Extends coverage to puzzles beyond strict logic using controlled, explainable guessing without full brute force.

**Independent Test**: Use a puzzle unsolved by v2; run v3 with a configured guess limit (e.g., 100 nodes) and verify solution found within limit; repeat with lower limit to confirm graceful partial failure messaging.

**Acceptance Scenarios**:

1. **Given** a puzzle stalled after logic v2, **When** `logic_v3` initiates search, **Then** it selects a cell with minimal candidate branching and records a Guess step before proceeding.
2. **Given** search exceeding configured node or depth cap, **When** limit reached, **Then** solver returns partial steps and a message indicating limit exhaustion without crashing.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Puzzle with only min and max clues (e.g., 1 and N) widely separated: ensure v1 frontiers don't loop infinitely.
- Region consisting of isolated single-cell islands: v2 must not misclassify disconnected cells as contiguous region.
- Multiple equally minimal candidate cells for v3 guess selection: tie-break deterministic (row/col order) for reproducibility.
- Bounded search hits depth limit but there exists a shallower alternative: ensure heuristic ordering (fewest candidates) reduces this risk.
- All deterministic logic yields no placements: v1/v2 return a clear "No logical moves" message rather than empty success.
- Invalid mode string: raise ValueError consistent with existing solver API.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST expose modes `logic_v1`, `logic_v2`, `logic_v3` via existing `Solver.solve(puzzle, mode=...)` and REPL command `solve --mode <mode>`.
- **FR-002**: `logic_v1` MUST implement two-ended propagation: from each placed value create forward/backward frontier sets and derive forced placements when frontier intersects uniquely.
- **FR-003**: `logic_v1` MUST remain guess-free and record reasons tagged `Propagation` or `Forced`.
- **FR-004**: `logic_v2` MUST compute contiguous empty regions using the puzzle's adjacency rule (configurable 4-way or 8-way; default 8-way for standard Hidato) and prune candidate positions for sequences based on region capacity.
- **FR-005**: `logic_v2` MUST remain deterministic and produce reasons tagged `RegionPrune`.
- **FR-006**: `logic_v3` MUST apply v2 logic first, then initiate bounded search limited by configurable `max_nodes` and `max_depth` parameters (defaults: 500 nodes, depth 20).
- **FR-007**: `logic_v3` MUST record guess steps distinctly (e.g., reason prefix `Guess:`) and backtrack with explanation `Backtrack`.
- **FR-008**: All modes MUST return `SolverResult` with accurate `solved` flag, steps, and message summarizing iterations and (for v3) search stats (nodes explored, branching factor average).
- **FR-009**: Hint retrieval MUST support selecting a mode; REPL `hint --mode logic_v2` uses that logic pipeline to derive next step without mutating puzzle state.
- **FR-010**: Performance: logic modes (v1, v2) MUST complete on 15x15 medium puzzles (<50% filled) under 300ms on the reference environment: Windows 11 x64, Intel Core i7-12700H (12C/20T), 32GB RAM, Python 3.11.9.
- **FR-011**: `logic_v3` MUST terminate early with informative message if limits reached without solution.
- **FR-012**: System MUST provide unit tests covering at least one puzzle each: solvable by v1 not v0, solvable by v2 not v1, solvable by v3 not v2.
- **FR-013**: Deterministic ordering: given same puzzle and mode, produced step list MUST be stable between runs.
- **FR-014**: Logging/profiling integration: each mode MUST optionally emit timing via existing profiling decorator when enabled.
- **FR-015**: Region computation MUST avoid O(n^2) repeated scans; reuse cached region map until mutation; recompute only affected regions.

*Clarifications Resolved:*

- **FR-016**: Region adjacency definition follows the puzzle's adjacency setting (supports 4-way and 8-way; default 8-way for standard Hidato).
- **FR-017**: Reference performance environment = Windows 11 x64, Intel Core i7-12700H (12C/20T), 32GB RAM, Python 3.11.9.

### Key Entities *(include if feature involves data)*

- **PropagationFrontier**: Represents set of candidate positions expanding from a placed value forward (+1) or backward (-1). Attributes: anchor_value, direction (+/-), candidate_cells.
- **EmptyRegion**: Contiguous cluster of empty cells; attributes: id, cells, size, boundary_values (nearest known numbers), capacity_range (min_possible_value, max_possible_value) derived.
- **SequenceGap**: Represents an interval between two known placed values (start, end) with missing length (end-start-1); used to test region feasibility.
- **SearchNode**: State snapshot for v3 search; attributes: depth, chosen_pos, chosen_value, remaining_values_set, puzzle_state_hash.
- **SearchStats**: Accumulates counters: nodes_explored, max_depth_reached, pruned_nodes, guesses_made.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: logic_v1 deterministic solve coverage ≥80% on curated 20-medium-puzzle set that logic_v0 fails (set recorded with fixed seed list).
- **SC-002**: logic_v2 deterministic coverage ≥90% on the v1 set plus ≥60% on a harder 20-puzzle set (total 40 puzzles); both sets pre-versioned in test fixtures.
- **SC-003**: logic_v3 total solve rate ≥95% across combined 40-puzzle corpus within default node cap (500) for ≥90% of runs (runs = distinct seeds/config combos) and ≥98% if node cap increased to 2000.
- **SC-004**: Median time per deterministic solve (v1/v2) on 15x15 medium puzzles ≤300ms; p90 ≤450ms; measured on reference env (Win11 i7-12700H Python 3.11.9) over ≥30 runs.
- **SC-005**: v3 average explored nodes ≤40% of naive DFS baseline (baseline measured by instrumented brute-force on same corpus) and average max search depth ≤60% of baseline depth.
- **SC-006**: Hint latency (v2) median ≤150ms; p90 ≤250ms for 15x15 medium puzzles.
- **SC-007**: Zero invalid placements in logic modes (v1/v2) across full test corpus (validated by adjacency + uniqueness post-check per step).
- **SC-008**: Deterministic trace reproducibility: identical step sequence hash (SHA256 over reason+pos+value) across 5 repeated runs per puzzle per mode.
- **SC-009**: Memory footprint: peak RSS increase during v3 search ≤30MB over idle baseline for largest tested 20x20 puzzle (measured via psutil if available; otherwise skip metric documentation).
- **SC-010**: Early termination correctness: when budgets exceeded (max_nodes or timeout_ms), solver returns partial trace and message; 100% of such cases maintain puzzle consistency (no orphan chain). Verified by simulated budget thresholds in tests.
