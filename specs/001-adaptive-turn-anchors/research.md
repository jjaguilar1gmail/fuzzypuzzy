# Phase 0 Research: Adaptive Turn Anchors

Date: 2025-11-10
Branch: 001-adaptive-turn-anchors
Spec: specs/001-adaptive-turn-anchors/spec.md

## Decisions

- Policy defaults (adaptive_v1):
  - Easy: endpoints + 2–3 hard anchors (stability)
  - Medium: endpoints + 1 soft (droppable) anchor if helpful; may be removed if redundant
  - Hard: endpoints only; extra anchors only for last-resort uniqueness repairs
  - Extreme: same as Hard
- Exposure: `anchor_policy_name='adaptive_v1'` by default; `legacy` restores fixed-anchor behavior; keep boolean `adaptive_turn_anchors` for convenience.
- Soft anchor semantics: droppable if uniqueness holds without it or if it overconstrains and harms variety.
- Repair semantics: on uniqueness failure, analyze differing solution segments and add a clue in the most ambiguous segment (midpoint/high branching factor).
- Distribution controls: impose minimum index gap between adjacent givens; prefer 4-neighbor adjacency in ultra-sparse hard puzzles to reduce needed anchors.

## Rationale

- Fixed anchors overconstrain puzzles and block minimal-clue outcomes on hard/extreme. Adaptive tiers let easy/medium remain readable while enabling minimal-clue uniqueness in hard modes.
- Soft anchors create a graceful path for medium difficulty — aid readability but do not force over-constraint.
- Surgical repair reduces added clues to the most informative locations, improving puzzle quality vs. restoring many turns.
- Distribution and adjacency preferences reduce clustering and visually repetitive structures.

## Alternatives Considered

- Uniform anchor reduction across difficulties — rejected due to readability loss for beginners.
- Global random anchor selection — rejected for determinism and uneven results.
- Always 8-neighbor adjacency — rejected for ultra-sparse hard puzzles; 4-neighbor raises constraint naturally.

## Open Points Resolved

- Default counts chosen per spec (see above).
- Policy selection model chosen (policy name + boolean convenience).
- Metrics to expose: `anchor_count`, `anchor_positions`, `policy_name`, `policy_params`, `anchor_selection_reason`.

