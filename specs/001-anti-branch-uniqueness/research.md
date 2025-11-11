# Research: Anti-Branch Uniqueness & Size-Aware Clue Distribution

## Decisions

### D1: Path Mode Scope
- **Decision**: Expand evaluation to all currently implemented path modes: serpentine, backbite_v1, random_v2, random_walk. Exclude jitter/strip-shuffle until implementation confirmed.
- **Rationale**: Broader telemetry accelerates general heuristic tuning; limiting to two modes risks overfitting.
- **Alternatives Considered**:
  - Restrict to backbite_v1/random_v2 (lower surface area; faster initial delivery) – rejected: less representative.
  - Include placeholder modes (jitter/strip-shuffle) – rejected: potential non-existent code paths causing noise.

### D2: Tie-Break Randomization Strategy
- **Decision**: Shuffle candidate ordering at each ambiguity only once per probe using Fisher–Yates on MRV/LCV candidate list; record permutation ID.
- **Rationale**: Ensures diversity with minimal overhead; per-node shuffle adds variance without proportional benefit.
- **Alternatives**: Per-node shuffle (higher CPU), static rotation (insufficient diversity).

### D3: Size-Tier Budgets
- **Decision**: Tiers and defaults:
  - Small (≤25 cells): max_nodes=2_000, timeout_ms=250, probes=2
  - Medium (26–64): max_nodes=5_000, timeout_ms=400, probes=3
  - Large (65–100): max_nodes=9_000, timeout_ms=600, probes=3
  - Very Large (>100): initial support deferred (log warning, fallback to Large)
- **Rationale**: Empirical balance: prevents stalls while allowing second-solution detection.
- **Alternatives**: Uniform budgets (simpler, but inefficient for size extremes); adaptive dynamic growth (complex; harder reproducibility).

### D4: Extended Attempt Policy (Fallback Disabled)
- **Decision**: Single extended DFS attempt (+50% nodes/time) for UNKNOWN/timeouts; then reject if inconclusive.
- **Rationale**: Matches user selection; bounded complexity.
- **Alternatives**: Multi-tier escalation (runtime inflation); immediate rejection (could raise false-negative uniqueness barriers).

### D5: Spacing Metric
- **Decision**: Use average Manhattan distance between clues plus quadrant variance (normalized) → combined score S = w1 * avg_distance - w2 * variance.
- **Rationale**: Simple, interpretable, tunable weights.
- **Alternatives**: Gini density (harder to explain), pairwise Chebyshev matrix (O(n^2) cost higher for large boards).

### D6: De-Chunk Pass Strategy
- **Decision**: After reaching target density, repeatedly attempt removals within largest cluster defined by adjacency of clues; apply uniqueness probe for each candidate until no safe removal found or cluster size below threshold.
- **Rationale**: Directly targets worst cluster; avoids global rescoring each iteration.
- **Alternatives**: Global simulated annealing, density equalization sweep (higher complexity).

### D7: Anchor Policy by Difficulty & Size
- **Decision**:
  - Endpoints always retained.
  - Easy: endpoints + 2–3 evenly spaced turns (size-dependent; at most 1 per 2 rows/cols).
  - Medium: endpoints + at most 1 soft turn (removable if spacing already acceptable).
  - Hard: endpoints only; extra turns added only as repair if spacing metric falls below threshold.
- **Rationale**: Mirrors difficulty scaling; fosters exploration on harder puzzles.
- **Alternatives**: Uniform anchor retention (causes small-board clustering); aggressive removal on Easy (risk of under-constrained boards).

### D8: Clue Density Floors
- **Decision**: Dynamic floor by size & difficulty:
  - Easy: small 34%, medium 30%, large 26%
  - Medium: small 30%, medium 26%, large 22%
  - Hard: small 26%, medium 22%, large 18%
- **Rationale**: Provides room to spread clues on small boards while maintaining solvability.
- **Alternatives**: Single global floor (clustering), fully adaptive solver-driven floor (complex; deferred).

### D9: Probe Outcome Classification Codes
- **Decision**: SECOND_FOUND, EXHAUSTED, TIMEOUT, UNKNOWN, EXTENDED_EXHAUSTED, EXTENDED_REJECT, FALLBACK_CONFIRMED, FALLBACK_REJECTED.
- **Rationale**: Granularity aids tuning decisions.
- **Alternatives**: Collapsing TIMEOUT/UNKNOWN (loses diagnostic specificity).

### D10: Telemetry Format
- **Decision**: Line-delimited JSON records for each removal attempt + final summary JSON block.
- **Rationale**: Stream-friendly, easy to parse.
- **Alternatives**: Single large JSON (memory spike risk), custom text DSL (extra parser effort).

## Clarifications Resolved
- Path mode scope expanded beyond spec baseline.
- Extended attempt policy defined.
- Spacing/clustering metrics chosen.
- Anchor, density tiering policies established.

## Rejected Alternatives Summary Table
| Area | Alternative | Reason Rejected |
|------|-------------|-----------------|
| Budgets | Uniform budgets | Inefficient for extremes |
| Tie-break | Per-node shuffle | Excess CPU cost |
| Spacing | Gini density only | Less intuitive tuning |
| Anchors | Uniform retention | Causes low-quality small puzzles |
| Density | Global floor | Clustering & over-constraint |
| Telemetry | Monolithic JSON | Memory use / harder incremental analysis |

## Rationale Synthesis
The hybrid approach balances integrity (multi-probe uniqueness checks) with performance (bounded DFS), while spatial heuristics and post-pass de-chunking mitigate clustering without heavy global optimization passes. Logging facilitates iterative tuning in future phases.
