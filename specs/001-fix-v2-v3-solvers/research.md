# Research: Fix v2/v3 solvers for 5x5 deterministic

Created: 2025-11-07 | Branch: 001-fix-v2-v3-solvers

## Decision 1: Apply v2 logic in-place at every v3 node
- Decision: Run a full v2 fixpoint on the current search state copy, not a deep-copied temp that is discarded. Return (progress_made, solved) and loop until no progress.
- Rationale: Ensures maximal pruning before branching; eliminates exponential blow-up from unpruned frontiers.
- Alternatives: (a) Copy back from temp solver each pass (works but more overhead); (b) Skip fixpoint (observed exponential growth).

## Decision 2: MRV/LCV on values (not positions)
- Decision: Choose the value k with minimal |positions(k)| (MRV on values). Order positions by LCV/frontier: prefer positions that keep neighbors open for k±1.
- Rationale: For Hidato, values anchor the chain; value-MRV massively reduces branching on sparse boards.
- Alternatives: Position-MRV (current) — leads to large branching factors on 5×5 with 5 clues.

## Decision 3: Corridor cache lifecycle
- Decision: Recompute corridor sets when placements invalidate cache; set _cache_dirty=false after compute.
- Rationale: Enable caching benefits across repeated checks; correctness preserved via invalidation on state change.
- Alternatives: Always recompute (slower); partial invalidation beyond scope.

## Decision 4: Degree metric uses empty neighbors only
- Decision: DegreeIndex counts only empty neighbors; endpoints require ≥1, middle values require ≥2 to remain viable at a cell.
- Rationale: Prior design double-counted arbitrary filled neighbors; empty-neighbor degree is a safe lower bound per position.
- Alternatives: Degree per (pos,value) considering placed k±1 — higher precision but more complexity; defer.

## Decision 5: Corridor via distance-sum (two BFS)
- Decision: Compute multi-source BFS distances from frontier around start and end; corridor = {p | distA[p]+distB[p] ≤ (t-1)} over empty cells only.
- Rationale: Standard, fast, and sharp corridor characterization; avoids nested BFS O(V·E).
- Alternatives: One-sided BFS + nested reachability checks (current) — slower and noisier.

## Decision 6: Minimal region capacity check
- Decision: For a gap (k, k+t), require at least (t-1) empty cells in some connected component that intersects the corridor; otherwise prune candidates outside feasible regions.
- Rationale: Coarse but effective island elimination; prevents impossible splits.
- Alternatives: Full-blown region DP with value spans — out of scope for v0.

## Decision 7: Inequality guard (off-by-one)
- Decision: Maintain condition distA[p] + distB[p] ≤ (t-1) where t = end-start; sequence length between anchors is (t-1).
- Rationale: Prevent over-permissive corridors; aligns with path length needs.
- Alternatives: ≤ t (too loose), < (t-1) (too strict).

## Decision 8: Logic fixpoint return signature
- Decision: `apply_logic_fixpoint(state) -> (progress_made: bool, solved: bool)` to enable outer loops to repeat logic before branching.
- Rationale: Search must branch only at logic fixpoints to keep nodes minimal.
- Alternatives: Single-pass boolean — loses progress signal and causes premature branching.

## Decision 9: Tiny transposition table
- Decision: Optional memo keyed by tuple of size-N array mapping value→(row,col|-1). Store best-known status and prune repeats.
- Rationale: Eliminates re-exploration of equivalent partial states; cheap on 5×5.
- Alternatives: Hash of candidates — less stable; omit table — still OK after #1–#5, but memo helps.

## Consolidated Best Practices
- Deterministic ordering: tie-break by (row,col) and value to ensure reproducibility.
- Traceability: Each pruning step returns count and reason tag (corridor/degree/region) and affected cells/values.
- Performance: Reuse data structures; lazily invalidate caches; avoid nested BFS.
