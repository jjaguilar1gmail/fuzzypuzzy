# Research: Smart Path Modes

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Start path for backbite = serpentine (optionally strip-shuffle) | O(N) deterministic baseline; guarantees Hamiltonian; easy to mutate | Precompute random Hamiltonian via DFS (too slow), heuristic spanning tree (irregular coverage) |
| Backbite move definition (endpoint + internal neighbor + reverse) | Classic backbite preserves Hamiltonian; simple to implement | Random segment reversal (risk disconnect), endpoint splice with random node (may violate adjacency) |
| Budget steps = min(size^3, path_time_ms//2) | Scales polynomially; caps work under time budget | Fixed multiple of cells (risk under-mutation on large) |
| Convergence early-exit after no-change for size*2 steps | Avoid needless tail iterations | Always run full budget (wastes time) |
| Random_walk Warnsdorff ordering | Reduces dead-end frequency; common in Hamiltonian/knight heuristics | Pure random neighbor order (more dead ends), highest-degree-first (creates cavities) |
| Fragmentation check (avoid isolating pocket <3 cells) | Prevents early partition causing low coverage | No check (higher restart rate) |
| Limits: max_nodes=5000, max_restarts=5 | Ensures bounded runtime; predictable | Unlimited (hang risk), too small (fragile) |
| Partial acceptance threshold = 85% | Balance between speed and puzzle viability | 80% (more variance), 90% (slower acceptance) |
| Structured PathBuildResult returned | Transparent decision; generator orchestrates fallback | Silent internal fallback (loss of control/observability) |
| Blocking remainder for partial path | Simplest to integrate with existing constraints (max_value adjusts) | Attempt to fill remainder later (complex, may violate determinism) |
| Determinism via single RNG route | Complies with constitution; reproducible | Independent RNG seeds per phase (harder replay) |
| Retry logic placed in Generator | Central orchestration; maintains pipeline purity | PathBuilder self-retry (hidden complexity) |

## Detailed Rationale Summaries

1. **Backbite Initialization**: Starting from serpentine ensures a valid Hamiltonian path instantly; optional strip-shuffle adds variety by permuting row order without breaking adjacency. DFS generation was rejected for worst-case exponential stalls under heavy blocking.
2. **Backbite Move**: Only endpoint-based segment reversals guarantee maintained connectivity and Hamiltonicity; other mutation operators need expensive validation.
3. **Budget Heuristic**: size^3 provides enough mutation attempts for structural diversity (empirically > 10x length for 9x9) while still bounded.
4. **Random Walk Heuristics**: Warnsdorff ordering prioritizes forcing early commitment in low-degree regions, reducing restart frequency.
5. **Fragmentation Avoidance**: Simple region size heuristic avoids prematurely sealing off unvisited cells while keeping constant-time checks (estimate via neighbor frontier count) instead of full flood fill each step.
6. **Partial Acceptance**: Accepting high coverage allows fast progress without demanding full Hamiltonicity under pathological seeds or block configurations.
7. **Structured Result**: Distinguishing reasons (timeout, exhausted_restarts, coverage_below_threshold, success) enables adaptive strategies (switch to backbite, accept partial, etc.).
8. **Blocking Remainder**: Converting unvisited cells to blocked cells integrates smoothly with existing uniqueness and difficulty logic which already respects blocked layout.

## Alternatives Rejected
- **Full coverage or fail only**: Increased tail latency on large boards; contradicts fast generation requirement.
- **Dynamic heuristic switching inside random_walk**: Adds complexity; outer generator can pick alternate mode on structured failure.
- **Complex graph-theoretic pruning (cut vertex detection)**: Higher overhead; fragmentation heuristic suffices.

## Open Risk Notes
- Backbite path diversity metric definition (turn count + segment length variance) will need empirical verification.
- Fragmentation heuristic could allow rare isolation; add fallback detection if coverage stagnates < threshold after restart cycle.

## Next Actions
- Implement data models (PathBuildSettings, PathBuildResult).
- Finalize contracts with reason code enumeration.
