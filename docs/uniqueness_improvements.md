# Uniqueness Improvements Summary

Moved from `app/devtools/UNIQUENESS_IMPROVEMENTS.md`.

## Problem Statement

**Original Issue (Seed 42):**
- Generated puzzle: 26 clues (32% density)
- Max gap: ~50 values (between givens 15 and 66)
- Missing anchors in Q2 (22-41) and Q3 (42-61) quartiles
- Clues bunched at edges: values 1-16 at bottom-right, 66-81 at top-right
- Massive empty left side allowing multiple distinct solution paths
- User correctly identified: "large empty spaces + bunched clues = non-unique"

## Root Cause

The `backbite_v1` path mode creates long head/tail clusters with massive mid-range gaps. On 8-neighbor grids, large uniform empty regions bounded by two distant anchor clusters admit multiple Hamiltonian paths, violating uniqueness despite passing basic solver checks.

## Implemented Solutions (A–H)

### A. Anchor Dispersion Check
Reject puzzles with largest consecutive missing span > 12. Applied unconditionally for 9x9+ diagonal boards.

### B. Minimal Spine Anchoring
Gap-driven injection: only add anchors to break gaps > 12 (replaces broad quartile injection that over-densified puzzles).

### C. Region Span Analysis
Flood-fill empty regions; compute capacity vs needed value span; reject extreme mismatches (threshold 20).

### D. Bi-directional Path Search
For large gaps (>15), greedy forward/backward bridging; detect divergent bridge paths → non-unique.

### E. Flex Zone Heuristic
Counts cells whose blocking doesn’t change ambiguity score; large flex zones (>30 at <28% density) imply routing freedom → reject.

### F. Smart Removal Scoring
Score = 0.6*interiorness + 0.4*endpoint_distance − gap_penalty (10 if unsafe). Prefers removing interior cluster cells while preserving max_gap.

### G. Iterative Gap-Safe Thinning
Batch removal loop: remove top-K safe candidates; uniqueness verify; shrink batch on failure; preserves gap constraint while lowering density.

### H. De-chunking Pass
Find large contiguous given clusters (>8); remove interior cells (with uniqueness checks) to disperse anchors spatially.

## Final Results (Seed 42)
Before: 26 clues (32%), max_gap≈50, missing Q2/Q3, bunched right edge.
After: 31 clues (38.3%), max_gap=11, all quartiles covered, 100% rows/cols with clues.

Multiple seeds stabilize 35–44% density with max_gap ≤ 12 (hard difficulty range compromise for backbite_v1).

## Key Constants & Thresholds
- MAX_VALUE_GAP = 12
- SPARSE_DENSITY_THRESHOLD = 0.30
- Region mismatch threshold = 20
- Bi-directional trigger gap > 15
- Flex zone threshold = 30 (<28% density)
- De-chunk cluster size > 8; budget 10 removals
- Thinning iterations ≤ 15; initial batch size 5
- Tail/Head reject length ≥ 7

## Performance
Typical 9x9 hard generation with uniqueness guardrails: ~1200–1500ms (including pruning passes). Acceptable latency for deterministic generation with structural validation.

## Trade-offs
- Backbite_v1 can’t reliably achieve ultra-low densities (<30%) with guaranteed uniqueness after dispersion constraints; system enforces structural soundness instead of chasing lower clue counts.
- Staged uniqueness checker may return INCONCLUSIVE on trivial full-given puzzles; pipeline falls back to classic counter seamlessly.

## Recommended Future Enhancements
1. SAT/CP optional module for deeper ambiguity elimination (disabled by default).
2. Adaptive max_gap thresholds scaled by board size and anchor count.
3. Corridor-based repair (structural block insertion) once ambiguity regions are mapped.
4. Tuning density targets per path mode (custom difficulty calibration). 

## Conclusion
Combining minimal spine anchoring, dispersion-aware guardrails, cluster de-chunking, and gap-safe thinning solves the original non-uniqueness symptom (massive value gaps + anchor clustering) while maintaining challenging yet structurally unique puzzles.
