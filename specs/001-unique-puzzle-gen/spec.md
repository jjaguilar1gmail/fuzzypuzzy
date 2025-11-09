# Feature Specification: Uniqueness-Preserving Puzzle Generator

**Feature Branch**: `001-unique-puzzle-gen`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: Build a uniqueness-preserving puzzle generator that starts from a full solved grid, removes clues, and uses your solver to ensure the result is both solvable and has a single solution. This matters because it turns your engine into a reliable puzzle factory with tunable difficulty—no junk boards, repeatable by seed.

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

### User Story 1 - Generate Valid Unique Puzzle (Priority: P1)

As a puzzle system integrator, I can request a new puzzle (size, diagonal flag, optional seed, target difficulty) and receive a grid that is solvable by the existing solver and has exactly one solution so that I can safely publish it without manual curation.

**Why this priority**: Core business value—turns solver into reliable content generator; uniqueness + solvability guarantee prevents junk output.

**Independent Test**: Call generator with parameters; verify returned puzzle passes solver (solved=True) and uniqueness test returns exactly one solution.

**Acceptance Scenarios**:

1. **Given** size 5x5 and seed 123, **When** I generate a puzzle, **Then** the puzzle is solvable and uniqueness check reports exactly one solution.
2. **Given** a request specifying diagonal adjacency off, **When** I generate, **Then** produced puzzle respects 4-neighbor adjacency rules and still unique.
3. **Given** a target difficulty = "easy", **When** generated, **Then** clue count is within easy band and solving requires only pure logic (no backtracking/search depth > configured threshold).
4. **Given** invalid size (<2), **When** I request generation, **Then** I receive a validation error without side effects.

---

### User Story 2 - Difficulty Tuning & Bands (Priority: P2)

As a content curator, I can request puzzles at difficulty bands (easy, medium, hard, extreme) so I can build a graduated catalog.

**Why this priority**: Enables broader product offering and replayability; not strictly required to ship first unique puzzle but adds immediate value.

**Independent Test**: Generate N puzzles per band; validate each band meets its defined quantitative constraints (clue density, estimated branching factor, average solver steps, max search depth).

**Acceptance Scenarios**:
1. **Given** difficulty=easy, **When** generating, **Then** clue density ≥ 40% and solver finishes with logic_v2 (no recursion) in under 200ms.
2. **Given** difficulty=hard, **When** generating, **Then** clue density between 22–30% and solver uses search-enabled solving with search depth between 5–20 nodes.
3. **Given** difficulty=extreme, **When** generating, **Then** clue density < 22% and solver search depth > 20 but within configured cap (e.g., ≤ 200 nodes) and uniqueness still verified.
4. **Given** an unsupported difficulty label, **When** requested, **Then** a clear error enumerates valid options.

---

### User Story 3 - Deterministic Reproducibility (Priority: P3)

As a developer or tester, I can supply a seed and get identical puzzle output (clue layout and values) so I can reproduce issues and create stable fixtures.

**Why this priority**: Improves QA, enables regression tests, facilitates deterministic benchmarking.

**Independent Test**: Call generator twice with same parameters and seed; assert serialized puzzle states are identical; with different seeds they differ in at least one clue location set.

**Acceptance Scenarios**:
1. **Given** seed=98765, **When** generating twice, **Then** outputs are byte-for-byte identical after normalization.
2. **Given** two different seeds, **When** generating, **Then** at least one clue position differs between outputs while both remain unique & solvable.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Minimum viable grid (2x2 or 3x3) still produces a puzzle (if trivial uniqueness fails, generator escalates or rejects).
- All clues removed attempt: generator must stop before destroying uniqueness (enforce lower clue bound per difficulty).
- Seed collision across different sizes: same seed for different size should yield different output (size part of RNG context).
- Timeout during uniqueness solving: generation aborts gracefully with retry or returns failure reason.
- Hard difficulty hitting node or time limits before uniqueness can be confirmed -> fallback strategy (e.g., re-roll or relax removal aggressiveness).
- Attempt to generate after maximum retry budget exhausted returns explicit error.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: Generator MUST accept parameters: size (NxN, N ≤ 9 in v1), allow_diagonal (bool), difficulty (enum: easy|medium|hard|extreme), seed (optional int), max_attempts (optional), timeout_ms (optional).
- **FR-002**: System MUST be able to produce a fully solved starting grid consistent with constraints (reuse solver in constructive mode or backtracking fill).
- **FR-003**: Generator MUST iteratively remove clues while maintaining a uniquely solvable puzzle (uniqueness checked after each removal or batch via solver search limited to finding >1 solution path).
- **FR-004**: Uniqueness verification MUST terminate early as soon as a second distinct solution is discovered.
- **FR-005**: Difficulty classification MUST map to configured metrics (clue density ranges, max search depth, average branching factor proxy via steps) and enforce those during or after generation.
- **FR-006**: Generator MUST return metadata: clue_count, difficulty_assessed, elapsed_ms, attempts_used, seed, uniqueness_verified (bool), solver_metrics (nodes, depth, steps for canonical solve), version.
- **FR-007**: Reproducibility: same (size, difficulty, seed, allow_diagonal) MUST yield identical clue layout and givens ordering.
- **FR-008**: Failure modes MUST be explicit: (a) timeout, (b) attempt_exhausted, (c) uniqueness_not_achievable, (d) internal_error.
- **FR-009**: Removal strategy MUST avoid removing mandatory anchors (e.g., keep value 1 and max value) unless configured otherwise.
- **FR-010**: Generator MUST enforce a lower bound on remaining clues per difficulty band to prevent degenerate puzzles.
- **FR-011**: API/CLI surface MUST provide a dry-run mode returning only predicted difficulty metrics from a solved grid without actual removal.
- **FR-012**: Uniqueness solver MUST cap resource usage (nodes, ms) and escalate (retry with different removal order or restore last clue) if exceeded.
- **FR-013**: Logging/trace (if enabled) MUST summarize: removals attempted, removals accepted, uniqueness checks performed, early abort reasons.
- **FR-014**: Validation MUST re-run final solve and confirm PASS via the built-in validation step before returning puzzle.
- **FR-015**: Errors MUST NOT leak partial internal state beyond high-level metrics and sanitized reason.
 - **FR-016**: Generator MUST optionally accept blocked cells and ensure solvability/uniqueness checks honor blocked positions; advanced blocked-cell patterning remains out of scope for v1.

### Key Entities *(include if feature involves data)*

- **GeneratedPuzzle**: Attributes: size, allow_diagonal, givens (list of (row,col,value)), blocked_cells (if any), difficulty_label, clue_count, seed, metadata (timings, solver metrics), version.
- **GenerationConfig**: Input parameters controlling generation & constraints (ranges for difficulty, limits for attempts/time/nodes).
- **UniquenessCheckResult**: {is_unique: bool, solutions_found: int (1 or 2), nodes, depth, elapsed_ms}.
- **DifficultyProfile**: Range definitions (clue_density_min/max, max_search_depth, expected_max_nodes, strategy_usage flags).

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of generated puzzles returned as SUCCESS are solvable by existing solver within configured resource caps (no false positives) across 100-sample test per difficulty.
- **SC-002**: 0% multi-solution escapes: no puzzle labeled unique yields >1 solution in an independent verification run (sample size: 200 across bands).
- **SC-003**: Reproducibility: Same seed & params yields identical clue layout in 100/100 repeated runs.
- **SC-004**: Generation time P95 per difficulty: Easy < 300ms, Medium < 800ms, Hard < 2500ms, Extreme < 5000ms (on reference machine baseline used in existing perf tests).
- **SC-005**: Difficulty band adherence: ≥ 95% of generated puzzles fall within defined clue density & solver depth bands; outliers flagged, not silently mis-labeled.
- **SC-006**: Uniqueness check early-abort efficiency: ≥ 80% of non-unique candidate states discarded before exceeding 50% of node cap.
- **SC-007**: Failure classification accuracy: 100% of failed generations return a specific failure code (no generic/ambiguous errors) in test harness of 50 induced failures.

## Assumptions

- The "search-enabled" solver mode remains the highest tier used for uniqueness search; no new algorithm tier required initially.
- Constructing a solved grid via backtracking is acceptable and performance-feasible for target sizes (≤ 9x9 initial scope).
- Extreme puzzles can legitimately approach search depth limits; we accept higher generation latency for that band.
- Max grid size for v1 is 9x9 (cap enforced for performance and scope control).
- Basic support for blocked cells is included in v1; generator and solver honor blocked positions during removal and uniqueness checks. Complex blocked-cell patterns are deferred.
- Difficulty estimation relies on observed solve metrics rather than heuristic pattern catalog.

## Out of Scope

- Multi-shape / irregular region puzzles.
- Parallel generation batching.
- Web API layer; this spec covers core library / CLI invocation only.
- Advanced analytics (e.g., entropy scoring) beyond basic metrics.

## Decisions

- Grid size cap (v1): 9x9
- Difficulty labeling: Prefer accurate labeling even if occasional over-shoot occurs
- Blocked cells in v1: Include basic support (uniqueness and solving respect blocked cells)

## Risks & Mitigations

- Risk: Uniqueness checking expensive on sparse hard puzzles. Mitigation: Early exit on second solution, adaptive removal rollback.
- Risk: RNG removal order biases difficulty distribution. Mitigation: Shuffle candidate removals per attempt; maintain deterministic sequence per seed.
- Risk: Over-aggressive clue stripping leads to high retry counts. Mitigation: Progressive removal phases with periodic uniqueness checkpoints.
- Risk: Performance regressions. Mitigation: Add generation benchmark test gating P95 thresholds.

## Acceptance Test Matrix (High-Level)

| Scenario | Input Params | Expected | Metrics Verified |
|----------|--------------|----------|------------------|
| Easy unique | size=5, diff=easy, seed=1 | Unique puzzle | clue_density ≥ 40%, depth=0 |
| Medium unique | size=7, diff=medium, seed=2 | Unique puzzle | depth ≤ 10 |
| Hard unique | size=7, diff=hard, seed=3 | Unique puzzle | depth 5–20 |
| Extreme unique | size=9, diff=extreme, seed=4 | Unique puzzle | depth > 20, < cap |
| Repro same seed | repeat same params | Identical clues | hash match |
| Non-unique caught | forced ambiguous state | Failure/retry | second solution detected early |
| Timeout path | artificially low timeout | Failure code=timeout | attempts ≤ 1 |
| Invalid size | size=1 | Validation error | no generation begun |
