# Research: Mask-Driven Blocking & Ambiguity-Aware Repair

## Decisions

### D1. Mask Pattern Sources
- Decision: Support both template-based patterns (corridor, ring, spiral) and procedural sampling.
- Rationale: Templates give human-readable funnels; procedural offers flexible density sweeps.
- Alternatives: Templates only (too rigid), Procedural only (risk of unnatural shapes).

### D2. Mask Density & Size Gating
- Decision: Default density by difficulty/size: Easy 0–2%, Medium ≈2–3%, Hard ≈3–6%; Auto-disable for sizes ≤5 unless forced.
- Rationale: Maintain solvability and readability; hard puzzles benefit from more structure.
- Alternatives: Fixed density across sizes (ignores scale effects).

### D3. Validation Rules
- Decision: (a) All non-blocked cells must be a single connected component; (b) No 1–2-cell orphan pockets fully enclosed by blocks; (c) Start/end not blocked.
- Rationale: Prevent dead boards and micro-chambers that feel unfair.
- Alternatives: Connectivity only (allows orphan pockets) → rejected.

### D4. Reproducibility
- Decision: Mask generation driven by RNG(seed, size, difficulty, attempt_idx) → deterministic; record pattern_id and attempt count.
- Rationale: Constitution requires reproducibility.
- Alternatives: External randomness → rejected.

### D5. Ambiguity Detection & Repair Strategy
- Decision: When ≥2 solutions found, diff solution paths; cluster divergence cells into ambiguity regions; score candidates by (frequency × corridor width × distance from nearest clue), pick top; try ≤1 block at a time, ≤2 total.
- Rationale: Structural fix preserves low clue counts; targeted and controlled.
- Alternatives: Always add clues → increases clue count, undermines goals.

### D6. Early-Exit Probes Enhancement
- Decision: Ensure v2 logic (islands/bridges/degree) runs at every probe node; add transposition table keyed on (placements_hash, mask_signature) with LRU cap.
- Rationale: Leverage mask throughout search; avoid repeated work.
- Alternatives: Root-only logic passes; no TT → slower, less effective.

### D7. Difficulty Metrics
- Decision: Prefer trace-based metrics (logic% completion, node count, max depth) over clue count; store both for analysis.
- Rationale: Mask can reduce clues—difficulty should reflect reasoning effort.

## Patterns Ontology (Templates)
- Corridor: parallel lanes with 1–2 chokepoints.
- Ring: perimeter with 1–2 gated entries.
- Spiral: inward spiral with periodic gaps.
- Central choke: plus/cross shapes near center.

Constraints per template: min_size, max_density, symmetry notes.

## Procedural Sampler
- Input: blocked_ratio, rng
- Algo: biased noise (favor edges/center depending on mode), ensure sparsity (no dense 2x2 blocks), validate; retry up to `max_mask_attempts`.

## Ambiguity Scoring Details
- frequency: count of divergence appearances across solutions (usually 2, but probe multiple branches when available)
- corridor width: fewer escape routes → higher score
- distance from clues: farther from strong givens → higher score (more impactful)
- tie-breakers: prefer cells that keep symmetry or avoid visual clutter

## Budgets & Caps
- max_mask_attempts: 5 (default)
- structural_repair_max: 2
- structural_repair_timeout_ms: 400
- transposition_table_max_entries: 4k per-check

## Metrics to Log
- mask_cells_count, mask_density, mask_pattern_id, mask_attempts
- branching_factor_before/after, uniqueness_decision, elapsed_ms
- ambiguity_regions_detected, repair_used (block|clue|none), repair_attempts

## Open Questions
- NONE (defaults selected to avoid blocking)

