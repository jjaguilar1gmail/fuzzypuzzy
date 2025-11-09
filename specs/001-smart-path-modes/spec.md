# Feature Specification: Smart Path Modes

**Feature Branch**: `001-smart-path-modes`  
**Created**: 2025-11-09  
**Status**: Draft  
**Input**: User description: "Enhance the current slow random-walk path generator capabilities and hard serpentine fallback with faster, smarter path-building modes like backbite_v1 and partial-coverage acceptance. This ensures large puzzles generate quickly, retain variety, and never hang or revert to boring serpentine paths."

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

### User Story 1 - Fast, non-hanging generation for large sizes (Priority: P1)

As a generator user, I want puzzles (especially large sizes) to generate quickly without hangs or regressions to simplistic paths, so I can reliably produce varied puzzles at scale.

**Why this priority**: Generation time and reliability directly impact usability; hangs or fallbacks block production and degrade user trust.

**Independent Test**: Generate multiple puzzles at larger sizes with a set of seeds and confirm completion within time targets and without fallback usage.

**Acceptance Scenarios**:

1. **Given** size ≥ 7 and default settings, **When** I generate a puzzle, **Then** it completes within the defined time target and does not fall back to a trivial path mode.
2. **Given** a 9x9 grid and multiple seeds, **When** I generate puzzles, **Then** at least 90% complete within the target time and none report a fallback to the old serpentine path.

---

### User Story 2 - Smarter path modes with variety (Priority: P2)

As a generator user, I want smarter path-building modes (e.g., backbite_v1) that yield varied path shapes while respecting adjacency and blocked cells, so puzzles feel fresh and not repetitive.

**Why this priority**: Variety improves replay value and perceived quality; smarter modes avoid overly rigid structures.

**Independent Test**: Generate N puzzles with different seeds and confirm path-shape diversity across runs under the same size and settings.

**Acceptance Scenarios**:

1. **Given** a fixed size and 5 different seeds, **When** I generate puzzles using the smart mode, **Then** at least 3 distinct path-shape profiles are observed (e.g., differing turn/segment distributions).
2. **Given** blocked cells and a chosen adjacency rule, **When** I generate with the smart mode, **Then** all paths respect blocked cells and the configured 4/8-adjacency.

---

### User Story 3 - Partial-coverage acceptance with guarantees (Priority: P3)

As a generator user, I want generation to gracefully accept high partial path coverage when full coverage is too costly, so generation remains fast and robust without hanging.

**Why this priority**: Full Hamiltonian coverage is expensive for some seeds/topologies; bounded partial coverage preserves performance without blocking.

**Independent Test**: Configure a coverage threshold and time budget; verify puzzles accept partial coverage meeting the threshold within time and never hang.

**Acceptance Scenarios**:

1. **Given** a minimum coverage threshold (default 85%) and a time budget, **When** the builder cannot achieve full coverage within the budget, **Then** it accepts the best path ≥ threshold and continues generation.
2. **Given** the builder cannot reach the threshold within the budget, **When** time elapses, **Then** generation aborts with a clear error and suggested next steps (e.g., different seed/mode).

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Size maximums (e.g., upper bounds) reached with heavy blocking patterns
- 4-adjacency (orthogonal only) causing sparse neighbor graphs
- Dense blocked-cell layouts that disconnect the grid
- Seeds that produce highly tangled paths with low removability
- Time budget reached before coverage threshold or uniqueness checks complete
- Requested coverage threshold > achievable under constraints
- Determinism across repeated runs with same seed and mode

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: Provide at least one new smart path mode ("backbite_v1") selectable via configuration/CLI and as default when a smart mode is requested.
- **FR-002**: Respect grid adjacency (4 or 8) and blocked-cell constraints for all new modes.
- **FR-3**: Support partial-coverage acceptance with a configurable minimum coverage threshold (default 85%).
- **FR-004**: Enforce a configurable time budget for path building; the process MUST terminate within this budget. Default tiered budgets: sizes ≤6: 2000ms, sizes 7–8: 4000ms, size 9: 6000ms.
- **FR-005**: On failing full coverage within budget, accept best path meeting the threshold; otherwise fail fast with a clear error message.
- **FR-006**: Eliminate automatic fallback to serpentine for smart modes; serpentine remains an explicit, opt-in mode only.
- **FR-007**: Expose mode selection and coverage/time settings via CLI and programmatic APIs.
- **FR-008**: Maintain deterministic output for the same seed, size, mode, and settings.
- **FR-009**: Emit generation metrics including coverage_percent, time_ms, and mode used; surface warnings when below threshold.
- **FR-010**: Ensure generation never produces 100% clue density puzzles; enforce a minimum viable empty-cell percentage.
- **FR-011**: Backwards compatibility: keep "random_walk" available as a non-default (hidden) mode; default smart mode is "backbite_v1". Serpentine is only used when explicitly selected.

Defaults & Assumptions:

- Default minimum coverage threshold is 85%.
- Default time budget is tiered by size: ≤6: 2000ms; 7–8: 4000ms; 9: 6000ms.
- Variety is evaluated by path-shape differences across seeds; exact metric is implementation-defined but MUST be demonstrable.

Decisions:

- Minimum coverage default set to 85% (Q1: B).
- Time budget defaults are tiered by size (Q2: B): ≤6: 2000ms; 7–8: 4000ms; 9: 6000ms.
- Keep "random_walk" available but not default; default smart mode is "backbite_v1"; serpentine only when explicitly selected (Q3: C).

### Key Entities *(include if feature involves data)*

- **Path Build Settings**: mode, allow_diagonal flag, coverage_threshold, time_budget, seed.
- **Path Build Result**: coverage_percent, steps (opaque), elapsed_ms, completed_full_coverage (bool), accepted (bool), warnings (list).

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 9x9 puzzle generation completes within 6 seconds p90 using smart mode on standard hardware.
- **SC-002**: For sizes ≥ 7, 0% of generations hang or exceed the configured time budget (all terminate successfully or fail fast).
- **SC-003**: For a set of 5 seeds at a fixed size, at least 3 distinct path-shape profiles are produced (variety requirement).
- **SC-004**: For smart modes, automatic fallback to serpentine occurs 0% of the time (serpentine only when explicitly selected).
- **SC-005**: When full coverage is not achieved, accepted paths meet or exceed the configured coverage threshold 95% of the time.
