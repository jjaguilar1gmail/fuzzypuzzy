# Feature Specification: Fix v2/v3 solvers for 5x5 deterministic

**Feature Branch**: `001-fix-v2-v3-solvers`  
**Created**: 2025-11-07  
**Status**: Draft  
**Input**: User description: "Fix v2 and v3 solvers so they can solve the classic 5x5 deterministic puzzle with 5 constraints."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Logic-only solve of classic 5x5 (Priority: P1)

As a puzzle author/maintainer, I can run the solver in logic-only mode (v2) on the classic 5x5 deterministic Hidato with 5 givens (1, 7, 13, 19, 25; 8-direction adjacency) and see it complete to a valid full solution without stalling.

**Why this priority**: Demonstrates correctness and transparency of the baseline logic engine. This puzzle is the canonical regression for our reasoning rules.

**Independent Test**: Run the logic-only mode against the canonical 5x5 input and verify the solution, step count, and that no search/backtracking occurs. Produces value by increasing trust and enabling deterministic demos.

**Acceptance Scenarios**:

1. **Given** the classic 5x5 puzzle with 5 givens and 8-adjacency, **When** I run logic-only mode, **Then** the solver completes with a valid path 1→25 and preserves givens.
2. **Given** the same puzzle, **When** I run logic-only mode, **Then** it uses zero backtracking/guess steps; if no further deterministic moves exist, it stops at maximal deterministic progress with a clear "no more logical moves" status.

---

### User Story 2 - Bounded-search completion under strict limits (Priority: P1)

As an engineer, I can run bounded-search mode (v3) on the same classic 5x5 and it always solves within strict, documented limits (time, node count, depth), producing the same solution every run.

**Why this priority**: Ensures we have a safety net even if logic-only falls short; gives deterministic CI-ready behavior.

**Independent Test**: Execute v3 on the canonical puzzle and assert time ≤ 1s on a reference machine, backtrack nodes ≤ 5,000, depth ≤ 25, with solved=true and a valid path.

**Acceptance Scenarios**:

1. **Given** the classic 5x5 puzzle, **When** I run bounded-search mode, **Then** solved=true with validation passing and limits respected (time ≤ 1s, nodes ≤ 5,000, depth ≤ 25).
2. **Given** repeated runs, **When** I execute the same command 5 times, **Then** the solution, step trace summary, and metrics are identical (deterministic behavior).

---

### User Story 3 - Transparent trace and validation (Priority: P2)

As a maintainer, I can view a concise, step-by-step trace (logic deductions and/or search decisions) for the run and a final validator report confirming all constraints.

**Why this priority**: Builds trust and makes debugging/regressions straightforward.

**Independent Test**: Enable tracing and confirm the output contains strategy labels, before/after candidate counts, and a final validator section that proves a contiguous 1→25 chain with givens preserved.

**Acceptance Scenarios**:

1. **Given** tracing enabled, **When** a solve completes, **Then** the trace shows each applied strategy/decision and the number of placements/eliminations per step.
2. **Given** a final solution, **When** validated, **Then** it passes adjacency (8-neighborhood) and givens consistency checks with an explicit PASS status.

### Edge Cases

- Conflicting givens (e.g., impossible adjacency gaps) are detected early with a clear error message.
- Alternate adjacency (4-neighborhood only) puzzles still solve or clearly report unsolvable under the specified mode without hanging.
- Multiple-solution puzzles are reported as such if encountered; bounded-search returns one valid solution and indicates non-uniqueness [if detected].
- Timeouts or bound exceedance in v3 return an explicit, actionable message and leave partial state consistent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Logic-only mode (v2) MUST terminate deterministically (no infinite loops) and report one of: solved, no-progress possible, or invalid puzzle (with reason).
- **FR-002**: For the classic 5x5 deterministic puzzle (givens 1,7,13,19,25; 8-adjacency), logic-only mode MUST attempt a full solve and, if no further deductions exist, stop at maximal deterministic progress with zero backtracking; it MUST perform at least one elimination via corridor or degree pruning on this puzzle.
- **FR-003**: Bounded-search mode (v3) MUST solve the classic 5x5 within limits: time ≤ 1s on reference hardware, backtrack nodes ≤ 5,000, depth ≤ 25, with deterministic behavior across runs.
- **FR-004**: Final solutions MUST be validated: sequence 1..25 forms a contiguous path per the adjacency constraint, and all givens are preserved at their positions.
- **FR-005**: Runs MUST be reproducible and independent of RNG seeding for the canonical puzzle; repeated executions yield identical outcomes and metrics.
- **FR-006**: On failure (unsatisfiable, bound exceeded, timeout), the solver MUST return a clear status and human-readable reason without corrupting puzzle state.
- **FR-007**: Provide a single test entry point (script or command) to run both v2 and v3 scenarios on the canonical puzzle and output a compact PASS/FAIL summary.

### Behavioral Constraints

- Logic-only mode (v2) applies corridor pruning (based on distance-sum) and degree pruning (based on empty-neighbor counts) within its fixpoint loop.
- Bounded-search mode (v3) applies a full v2 fixpoint at every search node before branching, uses a deterministic value-first MRV ordering with frontier/LCV tie-breaking, and may use a tiny transposition cache provided determinism is preserved.

### Key Entities *(include if feature involves data)*

- **Puzzle**: A grid with dimensions, givens (value, fixed), and an adjacency mode (4 or 8); immutable givens constraints.
- **Constraints**: Minimum/maximum values, adjacency rule, and validation rules for a completed path.
- **Solution**: Ordered placements 1..N covering the grid (N=25 for 5x5), with metadata: solved flag, steps, timing, node/depth counts (v3), and determinism indicators.
- **Trace**: Human-readable sequence of deductions/decisions with before/after counts and summary metrics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the classic 5x5 deterministic puzzle, v3 completes with solved=true, time ≤ 100 ms, nodes ≤ 2,000, depth ≤ 25, and identical results across 5 runs.
- **SC-002**: Final solution validator reports PASS for 1..25 contiguity and givens preservation in 100% of runs.
- **SC-003**: Trace (when enabled) is ≤ 200 lines and includes per-step action names and counts (placements/eliminations).
- **SC-004**: v2 uses zero backtracking, reaches a fixpoint in ≤ 2 full passes of its strategies, and performs at least one elimination via corridor or degree pruning on the canonical puzzle with runtime ≤ 250 ms.

### Assumptions

- Adjacency for the canonical case is 8-neighborhood (diagonals allowed).
- The "classic 5x5 deterministic puzzle with 5 constraints" refers to givens at positions/value anchors for 1, 7, 13, 19, 25.
- Reference hardware is the developer's workstation class machine; relative performance target (≤ 1s) is used rather than absolute throughput.

