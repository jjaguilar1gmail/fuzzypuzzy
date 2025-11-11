# Feature Specification: Anti-Branch Uniqueness & Size-Aware Clue Distribution

**Feature Branch**: `001-anti-branch-uniqueness`  
**Created**: 2025-11-11  
**Status**: Draft  
**Input**: User description: "Tighten uniqueness verification and de-bunch clues by upgrading the ‘is-unique?’ check to a targeted anti-branch probe (early-exit second-solution hunt) and by making anchor/density/spacing rules size-aware. This matters because your current cap-and-timeout checks can falsely certify uniqueness on small boards, and fixed turn anchors plus high minimum densities tend to cluster clues, hurting playability. Make sure you: Remove any ‘assume unique after one solution’ path for >25 cells. Implement the two-phase check at removal time: logic fixpoint → anti-branch DFS (max_solutions=2, strict node/time budgets). Run 2–3 randomized probes (shuffle MRV/LCV/frontier ties); accept removal only if all exhaust without a 2nd solution. Reserve SAT/CP blocking (solve → block → re-solve with cap) for ‘unknown’ cases. Log outcomes (found-second / exhausted / timeout) and tune budgets per size. Also, only test on backbit_v1 and random_v2 (never serpentine, we should ignore for testing)."

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

### User Story 1 - Prevent False Uniqueness (Priority: P1)

A puzzle generator maintainer wants every published puzzle (especially >25 cells) to be truly unique (exactly one solution) so that players aren’t misled by puzzles that accidentally pass a shallow solver check.

**Why this priority**: False uniqueness is a core integrity risk; shipping multi-solution puzzles degrades trust and replay value.

**Independent Test**: Run generation on a batch of mixed sizes (5–12) and confirm that the anti-branch probe either finds a second solution (puzzle rejected) or exhausts all probes without a second solution (puzzle accepted). No puzzle >25 cells is accepted after a single-solution confirmation.

**Acceptance Scenarios**:
1. **Given** a candidate puzzle with two solutions, **When** anti-branch DFS runs (max_solutions=2), **Then** a second solution is found and removal is rejected.
2. **Given** a candidate puzzle with one solution, **When** 3 randomized anti-branch probes run, **Then** all probes exhaust within budgets with zero second solutions and puzzle is accepted.
3. **Given** a candidate puzzle triggering timeout limits without second solution found, **When** SAT/CP blocking fallback executes, **Then** it either confirms uniqueness (accept) or finds second (reject) or marks as unknown (reject with logged reason).

### User Story 2 - Reduce Clue Clustering (Priority: P2)

A puzzle designer wants anchors and clue density rules to scale with board size so clues are evenly distributed and not bunched near initial turns.

**Why this priority**: Clustering lowers strategic value and perceived quality; size-aware spacing improves fairness and aesthetic.

**Independent Test**: Generate puzzles across sizes 5–12 and measure average Manhattan spacing of clues versus target ranges per size; confirm thresholds met.

**Acceptance Scenarios**:
1. **Given** size 5 board, **When** generation completes, **Then** minimum average spacing ≥ defined small-board threshold and no >30% clues occupy same quadrant.
2. **Given** size 10 board, **When** generation completes, **Then** anchor clues appear in ≥3 distinct regions with adaptive density target met.

### User Story 3 - Actionable Logging & Metrics (Priority: P3)

A maintainer wants detailed outcome logs (found-second / exhausted / timeout / fallback-result) plus per-size budget stats to tune heuristics without re-reading solver code.

**Why this priority**: Metrics accelerate iteration; maintainers can adjust budgets and probe counts empirically.

**Independent Test**: Inspect a generation run log; verify each removal attempt includes phase results, budgets consumed, outcome classification, and cumulative summary by size.

**Acceptance Scenarios**:
1. **Given** a batch generation run, **When** completed, **Then** a summary shows counts of outcomes per size (second-found, exhausted, timeout, fallback-confirmed, fallback-rejected).
2. **Given** a single removal attempt, **When** logged, **Then** entry includes: puzzle size, attempt index, probe count, DFS nodes explored, time used, outcome code, and second-solution hash if found.

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Extremely small puzzles (≤16 cells) where logic fixpoint solves immediately: ensure anti-branch still runs at least 1 probe to rule out alternate path ordering.
- Large puzzles (>100 cells) hitting node budget repeatedly: must escalate to SAT/CP fallback; if fallback inconclusive within its cap, reject removal.
- Timeouts in all randomized probes without second solution: treat as UNKNOWN → escalate; if still unknown reject (do not accept by absence of evidence).
- Anchor distribution on very narrow sizes (e.g., 5×8 rectangle if supported later): spacing rules adapt by shorter dimension.
- Randomization seeds producing identical tie orders: shuffle must ensure true permutation of MRV/LCV candidate list.
- Fallback SAT unavailable (disabled configuration): if uniqueness remains UNKNOWN after standard probes, perform one extended DFS attempt (expanded budgets +50% nodes/time). If still UNKNOWN, reject removal and log outcome EXTENDED_REJECT.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The generator MUST remove any path that assumes uniqueness after one solution for puzzles with >25 cells.
- **FR-002**: Each clue removal attempt MUST execute a two-phase uniqueness check: (a) logic fixpoint; (b) anti-branch DFS with max_solutions=2 and size-tiered node/time budgets.
- **FR-003**: The DFS phase MUST stop immediately if a second solution is found and classify outcome as SECOND_FOUND.
- **FR-004**: The system MUST run 2–3 randomized anti-branch probes (exact count size-tiered) shuffling tie-break orders (MRV/LCV/frontier) and accept removal ONLY if all probes exhaust without second solution.
- **FR-005**: The system MUST invoke SAT/CP blocking fallback only for outcomes classified UNKNOWN (e.g., repeated timeouts without evidence of second solution) and re-check uniqueness under block constraints.
- **FR-006**: The system MUST log per attempt: size, attempt index, probe index, node budget used, time used (ms), outcome code (SECOND_FOUND | EXHAUSTED | TIMEOUT | UNKNOWN | FALLBACK_CONFIRMED | FALLBACK_REJECTED), and hash/signature of second solution if found.
- **FR-007**: Size-aware spacing rules MUST adapt anchor positions and clue density targets based on board area (threshold tiers: ≤25, 26–64, 65–100, >100 cells) ensuring minimum average Manhattan distance thresholds per tier.
- **FR-008**: Clue clustering prevention MUST enforce: (a) no quadrant contains >35% of clues (square boards); (b) anchors appear in at least ⌈min(3, size_tier_regions)⌉ distinct regions for mid/large boards.
- **FR-009**: Randomization MUST ensure tie candidate permutations differ between probes (no identical ordering) and record the permutation ID.
- **FR-010**: Generator MUST restrict testing modes to path_mode in {backbite_v1, random_v2}; MUST skip serpentine mode entirely for uniqueness metrics collection.
- **FR-011**: Budgets (time ms, node counts, probe counts) MUST be configurable per size tier and surfaced in summary logs.
- **FR-012**: Summary logs MUST aggregate counts per outcome code and size tier at end of run.
- **FR-013**: If SAT/CP fallback is disabled and outcome UNKNOWN remains after standard probes, system MUST run exactly one extended DFS attempt (expanded budgets per size tier: nodes/time +50%). Accept removal only if extended attempt exhausts without second solution; otherwise reject.
- **FR-016**: Persistent timeouts (all probes TIMEOUT without second solution) MUST trigger extended attempt (if not yet run). After extended attempt, if still TIMEOUT/UNKNOWN, removal is rejected (no multi-tier escalation).
- **FR-014**: Acceptance decision MUST be binary (ACCEPT / REJECT) with justification referencing outcomes.
- **FR-015**: All logged data MUST be parsable (structured line prefix or JSON) for downstream analysis scripts.

### Key Entities

- **CandidatePuzzle**: Represents puzzle state during clue removal; attributes: size, cells, clues list, anchors, path_mode.
- **UniquenessProbeConfig**: Size-tiered budgets (max_nodes, max_time_ms, probe_count), shuffle strategy flags.
- **ProbeOutcome**: Captures per-probe result fields: outcome_code, nodes_explored, time_ms, second_solution_hash?, permutation_id.
- **RemovalAttemptLog**: Aggregated attempt data: candidate_id, size_tier, list<ProbeOutcome>, fallback_used?, final_decision, reason.
- **SizeTierPolicy**: Defines thresholds for spacing, anchor count targets, probe counts.
- **SummaryMetrics**: Aggregated counts by size tier and outcome code.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 0% of accepted puzzles >25 cells exhibit multiple solutions when re-checked independently with extended budgets (batch audit sample ≥100).
- **SC-002**: ≥95% of clue removal attempts reach a definitive uniqueness classification (SECOND_FOUND or EXHAUSTED) without requiring SAT/CP fallback on sizes ≤64 cells.
- **SC-003**: Average clue quadrant distribution variance reduced by ≥30% compared to baseline (pre-feature) across sizes 25–100.
- **SC-004**: Average Manhattan spacing between clues meets tier minimums: small (≥2.0), medium (≥2.8), large (≥3.5), very large (≥4.0).
- **SC-005**: Unknown classification rate after all fallbacks ≤2% across generation batch of ≥200 puzzles; all UNKNOWN without fallback are rejected.
- **SC-006**: Logging completeness: 100% of removal decisions include at least one ProbeOutcome; summary emitted once per run.

## Assumptions

- SAT/CP fallback is optionally available; when disabled UNKNOWN puzzles are rejected (tentative pending clarification).
- Size tiers chosen for simplicity; may refine later without altering acceptance semantics.
- Hashing second solutions uses canonical ordering to avoid collision risk.
- Randomization uses secure PRNG not required (standard pseudo-random sufficient for probe diversity).

## Open Clarifications

None. Policies for fallback-disabled UNKNOWN and persistent timeout handling resolved (single extended attempt then reject).
