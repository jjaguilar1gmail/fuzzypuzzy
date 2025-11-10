# Feature Specification: Solver-Driven Pruning

**Feature Branch**: `001-solver-driven-pruning`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "The generator will shift from a linear clue-removal process to a smarter, solver-driven system that uses binary search and frequency-based uniqueness repair to reach minimal clue counts more efficiently. It will also adjust clue placement logic—turn anchors are disabled for hard puzzles, and new repair clues target ambiguous mid-segments rather than predictable turns. Together, these upgrades allow the generator to consistently create hard, low-clue puzzles that remain unique and human-solvable."

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

### User Story 1 - Generate Minimal Hard Puzzle (Priority: P1)

User requests a hard puzzle; system produces a low-clue, unique, human-solvable puzzle by performing solver-driven pruning until target clue range is reached.

**Why this priority**: Core value proposition—efficient generation of genuinely hard puzzles with minimal but sufficient clues.

**Independent Test**: Request a hard puzzle with fixed seed; verify resulting clue count within target range, uniqueness holds, and human-solvable rating threshold met without manual intervention.

**Acceptance Scenarios**:

1. **Given** a request for difficulty=hard, **When** generation completes, **Then** clue density ∈ [24%,32%] and uniqueness validated.
2. **Given** generation in progress, **When** solver-driven pruning detects further removal breaks uniqueness, **Then** it stops and returns last unique state.

---

### User Story 2 - Efficient Clue Reduction (Priority: P2)

System replaces linear clue-removal loop with adaptive interval reduction (binary search over removable clue sets) to reduce iterations and time.

**Why this priority**: Performance and scalability—reduces average generation time and CPU cycles.

**Independent Test**: Benchmark generation time and iteration counts before/after on a fixed batch of seeds; confirm reduction without quality loss.

**Acceptance Scenarios**:

1. **Given** a batch of 20 seeds for hard puzzles, **When** using solver-driven pruning, **Then** median clue-removal iterations ≤ 40% of legacy linear approach.
2. **Given** binary search step attempting mid-range removal, **When** uniqueness fails, **Then** interval shrinks and retry occurs within max retry cap.

---

### User Story 3 - Adaptive Repair Clues (Priority: P3)

When uniqueness breaks at low clue counts, system analyzes solver frequency / ambiguity hotspots and injects a minimal repair clue in a mid-segment cell rather than predictable turns.

**Why this priority**: Maintains puzzle uniqueness while avoiding trivialization and over-reliance on structural anchors.

**Independent Test**: Force an over-pruned state; verify repair adds ≤1 clue from top 5 ambiguity cells; uniqueness restored; difficulty classification remains hard.

**Acceptance Scenarios**:

1. **Given** a near-final puzzle losing uniqueness, **When** repair triggers, **Then** exactly one repair clue chosen from ambiguity ranking and uniqueness returns.
2. **Given** a puzzle with multiple equally ambiguous segments, **When** selecting repair clue, **Then** tie-break prioritizes cell maximizing future branching reduction score.

---

### User Story 4 - Anchor Policy Adjustment (Priority: P4)

For hard and extreme puzzles, turn anchors are auto-disabled; system ensures difficulty via pruning rather than structural clue placement.

**Why this priority**: Prevents artificially inflated clue counts and predictable patterns; increases challenge authenticity.

**Independent Test**: Request hard puzzle; verify anchor set limited to endpoints only; confirm no extra turn anchors present.

**Acceptance Scenarios**:

1. **Given** difficulty=hard, **When** generation starts, **Then** turn anchors selection returns endpoints only.
2. **Given** difficulty=easy, **When** generation starts, **Then** legacy adaptive anchor behavior remains unchanged.

### User Story 5 - Deterministic Outcomes (Priority: P5)

Same seed and configuration produce identical puzzle layout and clue set under solver-driven pruning.

**Why this priority**: Reproducibility for debugging, benchmarking, and sharing.

**Independent Test**: Run generation 5 times with same parameters; verify identical output signature (clue positions + path hash).

**Acceptance Scenarios**:

1. **Given** seed=123 and config X, **When** generation repeated N times, **Then** clue position set identical each run.
2. **Given** different seeds, **When** generation runs, **Then** outputs differ in ≥ one clue position.

### Edge Cases

- All clues removable except endpoints: system must stop at uniqueness boundary without infinite loop.
- Binary search interval collapses to size 1 repeatedly: fallback to linear probing for final few clues.
- Repair attempt adds clue but uniqueness still fails: perform second repair; cap at 2 repairs then abort with graceful degradation message.
- Frequency profile yields uniform ambiguity (flat distribution): choose central path cell by distance heuristic.
- Solver time exceeds threshold during pruning iteration: abort current iteration, shrink interval, record timeout metric.
- Hard difficulty requested on very small grid (e.g., 4x4): enforce minimum clue floor to avoid unsolvable states.
- Seed produces pathological branching (excess mid-segment symmetry): ensure deterministic tie-break prevents oscillation.
- No valid repair candidates (all cells already clues): generation ends early and returns best-so-far puzzle flagged as "maximized clues".

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support solver-driven pruning phase that iteratively tests clue removal batches guided by interval reduction.
- **FR-002**: System MUST apply an adaptive interval (binary search style) over ordered removable clue candidates to minimize iterations.
- **FR-003**: System MUST produce hard puzzles with clue density in configured target range (default 24%–32%).
- **FR-004**: System MUST detect loss of uniqueness after a removal batch and revert to last unique state.
- **FR-005**: System MUST compute an ambiguity/frequency profile (per empty cell: candidate solution frequency) when uniqueness fails.
- **FR-006**: System MUST select at most one repair clue from top-N ambiguous mid-segment cells (default N=5) per repair cycle.
- **FR-007**: System MUST cap repair cycles at a configurable limit (default 2) and abort further pruning if limit reached.
- **FR-008**: System MUST disable turn anchors automatically for difficulty ≥ hard (keep endpoints only).
- **FR-009**: System MUST preserve existing adaptive anchor behavior for easy and medium difficulties.
- **FR-010**: System MUST expose deterministic output given identical seed and configuration parameters.
- **FR-011**: System MUST record metrics: pruning iterations, interval contractions, uniqueness failures, repair count, final clue density, generation time.
- **FR-012**: System MUST fail gracefully with a diagnostic message if minimum clue target cannot be met without breaking uniqueness.
- **FR-013**: System MUST ensure human-solvable rating (difficulty scoring heuristic) stays within "hard" band after repairs.
- **FR-014**: System MUST provide fallback linear removal for final ≤K clues when interval reduction becomes inefficient (default K=6).
- **FR-015**: System MUST reject removal batches that would remove required structural endpoints.
- **FR-016**: System MUST return status classification: success, success-with-repairs, aborted-max-repairs, aborted-timeout.

### Key Entities *(include if feature involves data)*

- **Puzzle**: Grid + Clue set + Path signature + Difficulty rating; attributes: size, clue_positions, uniqueness_status.
- **Clue Removal Batch**: Proposed set of clues to remove; attributes: batch_size, candidate_positions.
- **Pruning Session**: Aggregates metrics across removal attempts; attributes: iteration_count, uniqueness_failures, repairs_used.
- **Ambiguity Profile**: Ranking of cells by frequency of appearing in multiple alternate solutions; attributes: cell_position, frequency_score, segment_index.
- **Repair Candidate**: Cell chosen for clue injection; attributes: position, rationale (ambiguity, branching reduction).
- **Interval State**: Current removable clue range; attributes: low_index, high_index, contraction_reason.
- **Metrics Report**: Structured output of generation statistics; attributes: final_density, time_ms, status, difficulty_band.

### Non-Goals (Explicit Exclusions)

- NG-001: Introducing new external dependencies or non-standard library components.
- NG-002: Real-time interactive pruning visualization.
- NG-003: Multi-solution puzzle generation (focus remains on uniqueness).
- NG-004: Changes to solver core algorithms beyond metrics and ambiguity profiling hooks.

### Assumptions

- A1: Existing solver can provide frequency or candidate ambiguity counts via internal tracing without large performance penalty.
- A2: Human-solvable rating heuristic already implemented; we reuse its band thresholds.
- A3: Hard puzzle target clue density 24%–32% is acceptable baseline; adjustable via configuration.
- A4: Endpoints always retained as mandatory clues.
- A5: Repair clue injection does not require re-running full generation pipeline—only uniqueness and difficulty recalculation.
- A6: Determinism relies on stable ordering of candidate clues and consistent tie-break strategy.
- A7: Binary search interval operations treat removable clue list as logically ordered by structural relevance (e.g., descending distance from endpoints).

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Median clue density for hard puzzles across 50 seeds decreases to ≤32% (baseline legacy ≥38%).
- **SC-002**: Median generation time for hard puzzles (9x9) ≤ 6.0s on reference machine (baseline legacy ≤ 8.0s).
- **SC-003**: Uniqueness validation success rate ≥ 98% after pruning + possible repairs.
- **SC-004**: Average pruning iterations reduced by ≥40% vs legacy linear method.
- **SC-005**: Repair cycles used on ≤30% of hard puzzle runs; second repair required ≤10% of runs.
- **SC-006**: Deterministic reproducibility: hash(signature) identical across 5 repeated runs per seed (100% consistency).
- **SC-007**: Human-solvable rating band correctly classifies ≥95% generated hard puzzles as hard (no downgrade to easy/medium).
- **SC-008**: Abort rate due to timeouts < 2% across benchmark batch.
- **SC-009**: Final status "success-with-repairs" produced only when uniqueness restored by ≤2 clues; never exceeds repair cap.

### Validation Approach (High-Level)

- Benchmark suite of predefined seeds; capture metrics pre/post implementation.
- Diff reports for clue sets confirm reduction while retaining uniqueness.
- Spot-check ambiguity profiles to ensure repair clues reside in mid-segments (not turns).
- Re-run determinism tests for reproducibility metrics.

### Risks & Mitigations

- R1: Over-aggressive removal causing frequent repair -> Mitigation: early uniqueness boundary detection threshold.
- R2: Ambiguity profiling too slow -> Mitigation: cache candidate evaluations; cap profile scope.
- R3: Binary search oscillation near boundary -> Mitigation: fallback linear pass for final K clues.
- R4: Misclassification of difficulty after repair -> Mitigation: re-evaluate difficulty; if downgraded, attempt alternative repair candidate.

### Open Questions

None (reasonable defaults chosen; no critical ambiguities requiring clarification).

### Completion Signal

Feature considered ready for planning when benchmark harness and configuration toggles (hard density range, repair caps) are defined.
