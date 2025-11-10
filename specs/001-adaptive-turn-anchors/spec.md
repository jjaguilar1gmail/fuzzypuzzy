# Feature Specification: Adaptive Turn Anchors

**Feature Branch**: `001-adaptive-turn-anchors`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "Refine generator turn anchors adaptive by difficulty for minimal clues without losing structure"

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

### User Story 1 - Adaptive anchors enable minimal-clue uniqueness (Priority: P1)

As a puzzle generator maintainer, I want the generator to select turn anchors adaptively by difficulty so that hard puzzles can reach truly minimal clue counts without being overconstrained by fixed anchors.

Why this priority: Achieving genuine low-clue uniqueness is the primary value for advanced difficulty puzzles; fixed turn anchors overconstrain the generation and prevent producing legitimately hard, minimal-clue boards.

Independent Test: Generate N puzzles for each difficulty band with and without adaptive anchors; measure final clue counts, uniqueness verification, and anchor counts. The adaptive variant should enable lower average clue counts on hard/extreme while preserving uniqueness.

Acceptance Scenarios:

1. Given difficulty=easy, when generating a puzzle with adaptive anchors enabled, then the generator chooses a higher number of turn anchors (preserving structural clarity) and resulting puzzles meet easy difficulty targets and verify unique solutions.
2. Given difficulty=hard, when generating with adaptive anchors enabled, then the generator chooses fewer or no turn anchors, enabling lower clue counts while still producing puzzles that verify as unique.
3. Given same seed and settings, when generating twice, then results are deterministic (same anchors, same givens).

---

### User Story 2 - Opt-out and tooling (Priority: P2)

As a developer or power-user, I want a simple way to opt out of adaptive anchors (or to tweak the policy) so that we can reproduce previous behavior or run targeted experiments.

Why this priority: Backwards compatibility and experimentability are important for debugging and reproducible research.

Independent Test: Toggle a config flag (e.g., `adaptive_turn_anchors=false`) and confirm generator applies previous fixed-anchor behavior. Also provide a debug/logging mode that prints chosen anchors and policy decisions.

Acceptance Scenarios:

1. Given `adaptive_turn_anchors=false`, when generating a puzzle, then the generator uses the legacy fixed-anchor selection logic.
2. Given `--verbose` or debug mode, when generating, then the generator prints chosen anchors and counts to stderr for inspection.

---

### User Story 3 - Metrics and guardrails (Priority: P3)

As an operator, I want the generator to record metrics about anchor selection (anchor_count, anchor_positions, policy_version) and to enforce guardrails (e.g., never block both endpoints, avoid isolating regions) so that automated tuning and monitoring can be run safely.

Why this priority: Observability enables tuning and prevents regressions where adaptive anchors accidentally break uniqueness or produce pathological grids.

Independent Test: Generate puzzles in a CI harness with anchor logging enabled and assert that anchor_count is within expected bounds for each difficulty and that uniqueness verification still passes.

Acceptance Scenarios:

1. Given generation run, when finished, then metrics include `anchor_count`, `anchor_positions`, `policy_name`, and `policy_params`.
2. Given anchor selection would create an isolated cell or region, when policy detects this, then it reduces anchor application to avoid fragmentation and logs the adjustment.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Generation on heavily-blocked grids (many pre-blocked cells): adaptive policy must fall back to conservative anchors (more anchors) to preserve connectivity.
- Tiny grids (size ≤ 3): anchors should be ignored; endpoints suffice.
- Symmetry constraints: ensure anchor selection respects configured symmetry (rotational/horizontal) where anchors are mirrored when symmetry is requested.
- When uniqueness cannot be achieved even after increasing anchors (or decreasing on hard): generator must either (a) accept a partial path (if allowed) or (b) transparently fall back to serpentine and log the reason.

## Requirements *(mandatory)*

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001 - Adaptive Anchor Policy**: The generator MUST select turn anchors based on the requested difficulty band (easy/medium/hard/extreme) according to a tunable policy. Selection must be deterministic given the same RNG seed and inputs.

- **FR-002 - Policy Defaults**: The feature MUST provide sensible default anchor-count ranges per difficulty to enable immediate use without extra configuration. Defaults (adaptive_v1):
  - Easy: endpoints plus 2–3 turn anchors (stability focus)
  - Medium: endpoints plus 1 soft (optional) turn anchor that may be dropped if redundant
  - Hard: endpoints only; any additional anchors are last-resort uniqueness repairs
  - Extreme: same as Hard (endpoints only; anchors only as last-resort repairs)

- **FR-003 - Backwards Compatibility / Opt-out**: The generator MUST support `adaptive_turn_anchors` boolean in `GenerationConfig` (default: true). When false, the generator preserves legacy fixed-anchor selection.

- **FR-004 - Observability**: The generator MUST emit metrics for each generation run: `anchor_count`, `anchor_positions`, `policy_name`, `policy_params`, and `anchor_selection_reason` (e.g., "policy", "conservative_fallback", "disabled"). These must be included in `solver_metrics` or `timings_ms` metadata.

- **FR-005 - Safety Guardrails**: Anchor selection MUST avoid creating isolated single cells or disconnected regions. If selection would cause fragmentation, the policy MUST adjust anchors (increase anchors or move anchors) to preserve connectivity.

- **FR-006 - Symmetry Respect**: When a symmetry mode is requested, anchor positions MUST be symmetric under the chosen symmetry transform.

- **FR-007 - Determinism & Reproducibility**: Using the same seed and configuration (including the policy version) MUST produce identical anchor selections and puzzles.

- **FR-008 - Configurable Parameters**: Expose optional parameters: `anchor_policy_name` (default: `adaptive_v1`), `anchor_counts` (per-difficulty overrides), and `anchor_tolerance` (how aggressively to reduce anchors for harder puzzles). The legacy behavior MUST be available via `anchor_policy_name='legacy'`.

- **FR-010 - Soft Anchor Semantics**: A soft anchor (medium difficulty) MAY be dropped if it is redundant (e.g., does not improve uniqueness or structural clarity) or causes over-constraint; this decision MUST be deterministic given the same seed/state.

- **FR-011 - Last-Resort Repairs**: For hard and extreme, additional anchors MAY be introduced only as a last-resort uniqueness repair when uniqueness verification fails under clue removal; the policy MUST document this as `anchor_selection_reason='repair'`.

- **FR-009 - Non-regression**: Existing generator acceptance tests and uniqueness checks must continue to pass after enabling adaptive anchors.

### Key Entities *(include if feature involves data)*

- **AnchorPolicy**: Named policy (e.g., `adaptive_v1`) with parameters: per-difficulty anchor_counts, anchor_tolerance, symmetry behavior.
- **TurnAnchor**: A coordinate (row,col) chosen as an anchor (must be a path cell) and an anchor role (must_keep / soft_anchor).
- **AnchorMetrics**: Struct holding `anchor_count`, `anchor_positions`, `policy_name`, `policy_params`, `anchor_selection_reason`.

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 - Minimal-clue enabling**: For difficulty=hard and difficulty=extreme puzzles, enabling `adaptive_turn_anchors` MUST reduce the median clue count by at least 10% (relative to legacy fixed anchors) while preserving uniqueness verification for ≥ 95% of generated puzzles in a representative 100-seed sample.

- **SC-2 - Anchor bounds**: For each difficulty band, the observed `anchor_count` across 100 runs MUST fall within these bounds (unless a last-resort repair is logged):
  - Easy: 2–3 (plus endpoints)
  - Medium: 0–1 soft (plus endpoints)
  - Hard: 0 (plus endpoints), except when `anchor_selection_reason='repair'`
  - Extreme: 0 (plus endpoints), except when `anchor_selection_reason='repair'`

- **SC-003 - Determinism**: Re-running generation with the same seed and identical settings MUST produce bitwise-identical puzzle givens and anchor selections in 100% of attempts (deterministic behavior).

- **SC-004 - No fragmentation**: In all CI generation runs, the generator MUST never produce puzzles with isolated cells or disconnected path regions as a result of anchor placement.

- **SC-005 - Backwards compatibility**: When `adaptive_turn_anchors=false`, generator metrics and outputs MUST match legacy behavior within test tolerance.

### Assumptions

- The project continues to use Python 3.11 standard library only and the existing RNG threading model (seed determinism) remains unchanged.
- Existing `PathBuildResult` and `GenerationConfig` structures are available and will be extended (non-breaking) to include anchor metadata.
- Reasonable default anchor counts per difficulty are acceptable; the team will tune them after initial rollout.

### Decisions (resolved)

- D1: Default anchor counts per difficulty (adaptive_v1): Easy 2–3; Medium 1 soft (droppable); Hard 0 (repairs allowed); Extreme 0 (repairs allowed).
- D2: Exposure: `anchor_policy_name='adaptive_v1'` by default; `anchor_policy_name='legacy'` restores fixed-anchor behavior. A convenience boolean `adaptive_turn_anchors` remains supported for quick toggles.

## Implementation Notes (developer-facing, non-normative)

- Add `adaptive_turn_anchors` (bool) and `anchor_policy_name` (str) to `GenerationConfig` with defaults.
- Implement `AnchorPolicy` as a small policy object consulted during anchor selection; keep policy deterministic and pure (only depends on seed and grid state).
- Emit `anchor_*` metrics into `solver_metrics` for visibility; add unit tests that assert metrics exist and fall in expected ranges.
- When symmetry is active, generate anchor positions respecting symmetry by reflecting choices.
- Add unit tests: (1) anchor counts per difficulty, (2) uniqueness retained with adaptive on, (3) opt-out reproduces prior behavior.

## Test Cases (high level)

- Generate 100 puzzles per difficulty (easy/medium/hard/extreme) with adaptive ON using a fixed seed series; assert `anchor_count` distribution falls in bounds and uniqueness ≥ 95% for hard/extreme.
- Run regression suite (existing 31 tests) with `adaptive_turn_anchors` toggled off and on to ensure no regressions.
- Edge-case: heavily-blocked grid with `allow_partial_paths` enabled — assert that anchor fallback preserves connectivity and partial acceptance behavior functions.

---

**End of spec**
