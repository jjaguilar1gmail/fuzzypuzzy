# Feature Specification: Staged Uniqueness Validation

**Feature Branch**: `001-staged-uniqueness-validation`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "The uniqueness validation system will be upgraded to use a staged multi-strategy approach that combines fast early-exit searches, randomized solver probes, and optional SAT/CP-based checks to confirm uniqueness within strict time budgets. This matters because full enumeration becomes intractable for large 8-neighbor boards, and a layered method can confidently detect non-unique puzzles without stalling generation."

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

### User Story 1 - Fast, bounded uniqueness checks (Priority: P1)

As a puzzle generator, I need uniqueness validation that reliably detects multi-solution puzzles quickly and finishes within strict time budgets, so puzzle generation does not stall on large 8-neighbor boards.

**Why this priority**: Directly impacts throughput and product correctness (avoid shipping non-unique puzzles or timeouts).

**Independent Test**: Generate 7x7 boards with a 500 ms budget; confirm non-unique puzzles are flagged within time and unique puzzles either pass or are marked "Inconclusive" without exceeding budget.

**Acceptance Scenarios**:

1. Given a 7x7 candidate puzzle with two solutions, When the staged checker runs with a 500 ms budget, Then it returns Non-Unique within 500 ms.
2. Given a 7x7 candidate likely unique, When the staged checker runs with a 500 ms budget, Then it returns Unique or Inconclusive within 500 ms.

---

### User Story 2 - Configurable strategy & budgets (Priority: P2)

As a developer, I need to configure the strategy order, enable/disable stages, and set per-stage and total time budgets so the checker can be tuned for different sizes and environments.

**Why this priority**: Control over speed/accuracy trade-offs is essential for different workloads, CI runs, and device performance.

**Independent Test**: Change configuration to disable SAT/CP and allocate 100% of budget to early-exit + randomized probes; verify behavior and timings change deterministically.

**Acceptance Scenarios**:

1. Given SAT/CP stage disabled, When running on 7x7 with 300 ms budget, Then the checker never invokes SAT/CP and respects the 300 ms limit.

---

### User Story 3 - Deterministic, seedable probes (Priority: P3)

As a CI pipeline, I need the randomized probe stage to be seedable so test runs are deterministic and failures reproducible.

**Why this priority**: Reproducibility reduces flakiness and accelerates debugging.

**Independent Test**: Run the checker twice with the same seed and config; verify identical outcomes and metrics.

**Acceptance Scenarios**:

1. Given a fixed seed and configuration, When running randomized probes twice, Then the same decision and probe counts are produced.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Time budget exhausted mid-stage → return Inconclusive with partial metrics; no stage may exceed its slice.
- Small boards (≤ 25 cells) → exhaustive enumeration supersedes staged approach and must return definitive Unique/Non-Unique.
- Randomized probes find a conflicting completion late in budget → must immediately return Non-Unique (early exit wins).
- Optional SAT/CP disabled → pipeline skips that stage without altering earlier stage semantics.
- Degenerate inputs (empty grid, blocked-only grid) → return Inconclusive with reason invalid-input; no crash.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: Provide a staged uniqueness checker with at least three strategies: (a) fast early-exit search (bounded expansion with immediate return on counterexample), (b) randomized solver probes, and (c) optional SAT/CP verification as a final stage.
- **FR-002**: Enforce a strict total wall-time budget per check (default: 500 ms for ≥7x7, 100 ms for ≤5x5); each stage receives a configurable percentage of the total.
- **FR-003**: For small boards (≤ 25 cells), run exhaustive enumeration (within a high cap) ahead of staged strategies and return definitive Unique or Non-Unique.
- **FR-004**: Return a tri-state decision: Unique, Non-Unique, or Inconclusive, plus metrics including stage timings, nodes explored, and earliest-stage decision source.
- **FR-005**: On Inconclusive, apply a generation policy: accept, retry with a new seed, or escalate budget—policy must be configurable per difficulty.
- **FR-006**: Randomized probe stage MUST be seedable; given the same seed and configuration, results are reproducible.
- **FR-007**: Expose configuration to enable/disable individual strategies and adjust per-stage budgets without code changes.
- **FR-008**: Integrate with pruning/generation so that uniqueness checks never block the main loop beyond the configured budget; the API must be non-blocking from the caller’s perspective.
- **FR-009**: Produce structured logs/metrics suitable for tests: per-stage duration (ms), explored nodes, number of probes, decision reason, and timeouts.
- **FR-010**: Maintain compatibility with existing result types and error handling; callers must not need to change for the default path.
- **FR-011**: Provide reference tests covering: (a) definite non-unique detection on 7x7 within budget, (b) definitive unique decision for ≤5x5 via enumeration, and (c) Inconclusive path honoring budgets.

*Clarifications resolved:*

- **FR-012**: External solver usage: Core implementation remains stdlib-only. Provide an optional hook interface for SAT/CP integration; shipped disabled by default. If no external solver registered, the SAT/CP stage is skipped silently.
- **FR-013**: Inconclusive policy default: For ≥7x7 puzzles the generator ACCEPTS Inconclusive decisions (treated as provisionally unique) and records a metric/warning; no automatic retry or budget escalation unless explicitly configured.
- **FR-014**: Default per-difficulty total budgets (≥7x7): Easy 600 ms, Medium 500 ms, Hard 400 ms (distributed across stages by configurable percentages). ≤5x5 still uses 100 ms enumeration target.

### Key Entities *(include if feature involves data)*

- **UniquenessCheckRequest**: size, adjacency mode (4/8-neighbor), difficulty, total_budget_ms, stage_budget_split, seed, strategy_flags.
- **UniquenessCheckResult**: decision (Unique|Non-Unique|Inconclusive), stage_decided, elapsed_ms, per_stage_ms, nodes_explored, probes_run, notes.
- **Strategy**: id, enabled, budget_share, parameters (e.g., depth limits, probe count), capabilities (detect_non_unique, prove_unique, neither).

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: ≥ 95% of demonstrably non-unique 7x7 candidates are detected as Non-Unique within 500 ms total budget.
- **SC-002**: ≤ 0.5% false-positive rate on known-unique test sets (never label Unique as Non-Unique).
- **SC-003**: ≤ 100 ms median check time for ≤5x5 puzzles with definitive classification via enumeration.
- **SC-004**: End-to-end generation throughput impact ≤ 10% for 5x5 and ≤ 25% for 7x7 relative to current baseline, using default budgets.
- **SC-005**: Given identical seed and config, randomized probe outcomes are deterministic (decision and metrics match across runs).

## Assumptions & Dependencies

- The primary generator continues to prefer in-memory checks with strict budgets to avoid blocking end-to-end generation.
- For ≤ 25 cells (e.g., ≤5x5), exhaustive enumeration is feasible within default budgets and serves as ground truth.
- Optional SAT/CP checks rely on an externally registered solver via hook; if absent the stage is skipped without affecting earlier stages.
- Randomized components are always driven by provided seeds to ensure reproducibility in CI and local runs.
- Default adjacency is 8-neighbor; configuration must carry adjacency through to all strategies consistently.
