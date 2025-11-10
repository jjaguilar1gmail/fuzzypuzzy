# Feature Specification: Mask-Driven Blocking & Ambiguity-Aware Repair

**Feature Branch**: `001-mask-blocking`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "Add a mask-driven blocking system to generation that feeds a small, validated set of blocked cells into the path builder before clues, plus an optional ambiguity-aware blocker used during uniqueness repair. This matters because blocks lower branching, create purposeful chokepoints, and let you reach few-clue, unique hard puzzles faster (and with less reliance on turn anchors) while keeping puzzles human-readable."

## Overview *(context)*
Introduce a pre-path-build "mask" of blocked cells (small, intentional, validated) to shape the Hamiltonian path and create structural chokepoints that reduce branching and support lower clue counts for hard puzzles while maintaining human readability. Additionally, extend uniqueness repair with an optional ambiguity-aware blocker that, when multi-solution ambiguity is detected, inserts a targeted block (or confirms existing structure) to eliminate alternate paths instead of adding clues. Both mechanisms aim to reach unique, few-clue hard puzzles more efficiently, reducing reliance on turn anchors.

## Goals
- Reduce branching factor early in generation for complex sizes (≥7x7) without over-constraining puzzle solvability.
- Achieve lower clue counts for hard puzzles while preserving clarity of progression (no arbitrary walls that feel unnatural).
- Provide deterministic, seed-driven mask selection that is reproducible.
- Add ambiguity-aware structural repair step that can prefer inserting a block rather than re-adding a clue when uniqueness fails late.
- Maintain human readability: blocks form purposeful patterns (corridors, bottlenecks) not random noise.

## Non-Goals
- Not implementing full UI editing of masks.
- Not integrating external SAT solving for mask derivation (reuse internal heuristics only).
- Not replacing existing pruning/anchor systems—this layer is additive.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Mask Application (Priority: P1)
As a puzzle generator (system), I want to apply a small, validated mask of blocked cells before path building so that the constructed path will naturally include purposeful chokepoints and reduced branching, producing harder puzzles with fewer clues.

**Why this priority**: Core value driver—improves hard puzzle generation efficiency and quality.

**Independent Test**: Generate puzzles of sizes 7x7, 9x9 with and without mask; compare branching metrics and average clue counts; ensure solvability and uniqueness remain intact.

**Acceptance Scenarios**:
1. **Given** a size 7x7 puzzle request with mask feature enabled and seed S, **When** generation starts, **Then** a mask ≤8% of cells is selected deterministically and validated (connectivity preserved) before path building.
2. **Given** a generated puzzle using a mask, **When** uniqueness check completes, **Then** the puzzle is solvable and unique with clue count ≤ baseline average -10% for the same difficulty target.

---

### User Story 2 - Ambiguity-Aware Structural Repair (Priority: P2)
As a uniqueness repair subsystem, I want to detect multi-solution ambiguity regions late in pruning and apply a targeted structural block (instead of adding a clue) so that uniqueness is restored with minimal increase in clue count.

**Why this priority**: Reduces regression on clue minimization late in pipeline; complements mask approach.

**Independent Test**: Force ambiguity (by removing specific clue), trigger repair; verify block inserted, uniqueness regained, clue count unchanged.

**Acceptance Scenarios**:
1. **Given** a puzzle failing uniqueness with two path variants differing in a localized corridor, **When** ambiguity-aware repair runs, **Then** it identifies an ambiguity region and inserts ≤1 block cell restoring uniqueness.
2. **Given** a puzzle where adding a block would disconnect the path, **When** ambiguity-aware repair evaluates candidate blocks, **Then** it rejects structural blocking and falls back to clue-based repair.

---

### User Story 3 - Mask & Repair Metrics Observability (Priority: P3)
As a maintainer, I want structured metrics on mask usage and ambiguity repair interventions so I can evaluate impact on performance, uniqueness success rate, and clue counts.

**Why this priority**: Enables tuning (mask size, pattern ontology) and regression detection.

**Independent Test**: After generating 50 hard puzzles with mask enabled, metrics report: average mask size, branching reduction %, ambiguity repair invocation frequency, success/failure counts.

**Acceptance Scenarios**:
1. **Given** generation runs with metrics enabled, **When** a puzzle completes, **Then** output includes: mask_cell_count, mask_pattern_id, branching_factor_before/after, clue_count, ambiguity_repair_used(Boolean).
2. **Given** 0 ambiguity occurrences across a batch, **When** metrics summary is produced, **Then** ambiguity counts are zero without errors.

---

### Edge Cases
- Mask causes path builder failure (no Hamiltonian path possible) → system must fallback to no-mask generation for that attempt.
- Mask disconnects grid into isolated regions → mask validation rejects and regenerates pattern.
- Ambiguity repair proposes a block on a cell already given or required for path continuity → candidate rejected, alternative evaluated or fallback to clue addition.
- Excessive mask density (>10% cells) on small boards (≤5x5) → feature auto-disables to avoid trivialization.
- Diagonal adjacency vs orthogonal: mask patterns adapt so chokepoints remain meaningful (no diagonal shortcuts invalidating chokepoint intent).
- Repeated repair attempts risk oscillation (adding/removing uniqueness) → cap repair to 2 structural attempts before reverting to clue-based repair.
- Seed collision with mask pattern generation still yields reproducible result across runs.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST provide an optional mask-generation phase before path building when enabled.
- **FR-002**: System MUST validate any generated mask for: connectivity preservation, max density threshold, and absence of blocking start/end anchor positions.
- **FR-003**: System MUST deterministically derive mask from (seed, size, difficulty) triple.
- **FR-004**: System MUST allow mask feature to auto-disable for sizes <6 or difficulty <"medium" unless explicitly forced.
- **FR-005**: System MUST record mask metrics (cell count, pattern id, density %, validation time ms).
- **FR-006**: System MUST detect ambiguity regions during uniqueness repair (≥2 distinct solution path segments overlapping region boundary).
- **FR-007**: System MUST evaluate structural block candidates (≤3) and select one that restores uniqueness without exceeding block density cap.
- **FR-008**: System MUST fallback to clue reintroduction when no safe structural block candidate passes validation.
- **FR-009**: System MUST avoid introducing unsolvable states; structural block insertion MUST re-run solvability check before acceptance.
- **FR-010**: System MUST expose metrics for ambiguity repair (attempts, successes, failures, fallback path).
- **FR-011**: System MUST cap total structural blocks added during repair to ≤2 per puzzle.
- **FR-012**: System MUST ensure final puzzle readability by disallowing isolated single-cell chambers (no cell fully enclosed by blocks unless part of path endpoints logic).
- **FR-013**: System MUST provide a configuration flag to disable ambiguity-aware repair independently of initial mask usage.
- **FR-014**: System MUST maintain reproducibility: same seed & config produce identical mask and repair decisions.
- **FR-015**: System MUST NOT reduce uniqueness verification accuracy (no increase in false UNIQUE classification; measured via comparison baseline).

### Key Entities
- **BlockMask**: Represents the set of blocked cells selected pre-path; attributes: pattern_id, cells, density_percent, validation_status.
- **MaskPattern**: Abstract description (e.g., "dual corridor", "central choke", "ring gap"); attributes: min_size, max_density, suitability_criteria.
- **AmbiguityRegion**: Localized area where multiple path continuations exist; attributes: boundary_cells, divergence_points, candidate_block_cells.
- **RepairAction**: Either structural_block or clue_addition; attributes: action_type, target_cell, outcome (success/fallback), uniqueness_delta.
- **GenerationMetrics**: Aggregated metrics for mask and repair phases (branching_factor_before/after, time_ms, clue_count, attempts, repair_invocations).

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Hard puzzles (≥7x7) average generation time reduced ≥25% vs baseline (mask disabled) over 50-sample batch.
- **SC-002**: Average clue count for hard puzzles reduced by ≥10% vs baseline without increasing unsolvable rate (>0%).
- **SC-003**: Branching factor (measured as average candidate positions per step during path build) reduced by ≥15% when mask enabled.
- **SC-004**: Ambiguity-aware structural repair resolves ≥60% of detected ambiguity cases without adding clues.
- **SC-005**: Zero increase in false uniqueness decisions (agreement with baseline checker remains ≥99%).
- **SC-006**: Reproducibility: same seed produces identical mask & repair decisions (100% consistency across 5 repeated runs).
- **SC-007**: Maximum mask density never exceeds 10% of total non-blocked cells for hard puzzles (enforced by validation). 
- **SC-008**: User readability proxy: ≤5% of puzzles trigger readability audit failures (structural isolation rule) in validation batch.

## Assumptions
- A small mask (≤10%) provides chokepoints without harming solvability.
- Existing solver heuristics can confirm solvability post-block insertion within acceptable time budget.
- Ambiguity detection leverages already available uniqueness probing artifacts (no dedicated heavy solver needed).
- Readability audits use simple structural heuristics (no advanced aesthetic scoring required).

## Dependencies
- Relies on existing path builder to accept blocked cells input.
- Uses current uniqueness staged checker for ambiguity detection triggers.

## Risks & Mitigations
- Over-constraining masks → Mitigation: validation rejects and retries with reduced density.
- Structural repair introduces unsolvable puzzle → Mitigation: mandatory solvability re-check before acceptance.
- Performance regression due to added validation overhead → Mitigation: cap validation time; abort mask phase if exceeded.
- Ambiguity misclassification → Mitigation: fallback always available (clue-based repair) and metrics monitoring.

## Out of Scope
- Dynamic user-provided mask editing UI.
- Multi-phase adaptive masks (only single pre-build phase in this iteration).

## No Clarifications Required
All critical scope decisions have reasonable defaults; no [NEEDS CLARIFICATION] markers included.

## Acceptance Summary
Feature is considered successful when success criteria SC-001..SC-008 are met across controlled benchmark runs without violating FR-009 (solvability) or FR-015 (uniqueness accuracy).
