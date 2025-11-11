# Contract: Clue Spacing & De-Chunking

## Scoring Function
- Input: puzzle (current givens), metrics (SpacingMetrics), policy (SizeTierPolicy)
- Output: score S = w1 * avg_manhattan_distance - w2 * quadrant_variance
- Purpose: When multiple safe removals are available, prefer the one that increases spacing score.

## De-Chunk Pass
- Trigger: After target density floor reached.
- Algorithm:
  1. Compute clusters of clues using 8-neighbor connectivity.
  2. Identify largest cluster; enumerate safe removals inside it.
  3. For each candidate, run uniqueness probe; accept first that preserves uniqueness and improves spacing score.
  4. Repeat until no improvement or cluster below threshold.

## Telemetry
- Emit per pass: largest_cluster_size, spacing_score_before/after, removals_accepted/reverted.
