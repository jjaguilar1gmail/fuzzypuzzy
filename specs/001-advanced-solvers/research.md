# Research (Phase 0) — Advanced Solver Modes

Date: 2025-11-06
Branch: 001-advanced-solvers

This document consolidates design decisions, rationales, and alternatives for v1–v3 solver modes. All prior NEEDS CLARIFICATION items are resolved.

## Decisions and Rationale

### Adjacency & Regions
- Decision: Support both 4-way and 8-way adjacency; default 8-way for standard Hidato.
- Rationale: Some variants restrict diagonal adjacency; region logic must match puzzle rules.
- Alternatives: Force 8-way only (simpler) — rejected to preserve flexibility.

### Candidate Model (v1+)
- Decision: Maintain bidirectional maps: value → {positions}, position → {values}; update incrementally on placement/removal.
- Rationale: Enables MRV, single-position/value checks, and fast pruning.
- Alternatives: Recompute from scratch each pass — rejected due to O(n^2) overhead.

### Two-ended Propagation (v1)
- Decision: Build frontiers from anchors in both directions (k-1 and k+1). If intersection produces a single feasible position/value, place.
- Rationale: Bridges gaps deterministicly without search.
- Alternatives: Only local single-step checks — insufficient for mid-range puzzles.

### Early Contradictions (v1–v3)
- Decision: On any placement, immediately verify adjacent feasibility for k±1 (if required by constraints) and global uniqueness/dup range.
- Rationale: Fails fast; prunes dead branches early in v3.

### Region Segmentation (v2)
- Decision: Use flood fill to compute contiguous empty regions per current adjacency rule; cache region map and update incrementally on placement.
- Rationale: Needed for island elimination and capacity checks.
- Alternatives: Recompute whole-board each pass — rejected for performance.

### Segment Bridging (v2)
- Decision: For placed A and B (A<B), compute corridor feasibility for A+1..B-1 using multi-source BFS constrained to empty cells; reject cells not on any corridor.
- Rationale: Enforces continuity of the sequence.
- Alternatives: Simple Manhattan bounds — inaccurate under holes and diagonals.

### Degree Pruning (v2)
- Decision: Track per-cell legal-neighbor degree under current constraints; eliminate mid-sequence candidates with degree <2 (endpoints may be 1).
- Rationale: Ensures room to pass through.
- Alternatives: Ignore degree — leads to dead-ends later.

### Edge/Turn Nudges (v2)
- Decision: Add optional deterministic nudges only when logically forced (no ambiguity); otherwise skip.
- Rationale: Avoid accidental guessing.
- Alternatives: Heuristic biases without proof — rejected for v2.

### Search Strategy (v3)
- Decision: MRV (fewest candidates) primary ordering; tie-break with LCV (least constraining) and then row/col. Bias picks adjacent to existing path first (frontier continuity) when tied.
- Rationale: Reduces branching and keeps sequences coherent.
- Alternatives: Pure DFS or BFS — higher branching or depth blowups.

### Transposition Table (v3, optional)
- Decision: Use Zobrist-like hashing over (pos,value) pairs; store explored states with best-known remaining size; skip if budget low.
- Rationale: Avoid re-exploring equivalent states.
- Alternatives: No memoization — acceptable but slower.

### Budgets & Timeouts (v3)
- Decision: Configurable caps: max_nodes=20000, max_depth=50, timeout_ms=500; solver stops cleanly and reports usage.
- Rationale: Bounded search per constitution; UX needs predictable limits.
- Alternatives: Unlimited — rejected.

## Patterns & Best Practices

- Determinism: Stable iteration order; avoid set nondeterminism by sorting when committing steps.
- Immutability at API: Deep copy of puzzle for solve/hint.
- Profiling hooks: Decorate entry points; expose counters for telemetry.
- Testability: Deterministic seeds for generated fixtures; clear unit tests per mode.

## Open Items

None — all clarifications in spec resolved.
