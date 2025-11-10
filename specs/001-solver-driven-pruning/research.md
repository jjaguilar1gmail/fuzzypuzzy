# Research: Solver-Driven Pruning

## Decisions

- Decision: Use interval reduction (binary-search style) over an ordered list of removable clues; revert to last unique state on failure.
  - Rationale: Minimizes iterations to reach uniqueness boundary; faster convergence than linear removal.
  - Alternatives considered: Greedy remove-most-promising (risk oscillation), SA/annealing (complexity, nondeterminism).

- Decision: Sample 3–5 alternate solutions (configurable) with different solver seeds to build a divergence frequency map.
  - Rationale: Diminishing returns beyond ~5 alternates; balances cost vs. information.
  - Alternatives: Full SAT-style hitting set (too heavy), single alternate (too noisy).

- Decision: Choose repair clue from top-N (default 5) most-frequent divergence cells constrained to mid-segments/corridors.
  - Rationale: Avoids predictable turns; reduces large clusters of alternates.
  - Alternatives: Random top-N; endpoint-adjacent (risks trivialization).

- Decision: Cap repairs at 2 per generation; return best-so-far if still non-unique.
  - Rationale: Prevents runaway repairs and inflated clue counts.
  - Alternatives: Unlimited repairs; global restart (expensive).

- Decision: Fallback to linear probing for last ≤6 clues when interval reduction thrashes.
  - Rationale: Boundary near uniqueness often requires fine-grained checks.
  - Alternatives: Persist with binary search only (inefficient near boundary).

## Details & Tuning

- Interval Ordering: Sort removable clues by structural relevance (e.g., distance from endpoints, corridor centrality).
- Stopping Conditions: Stop when removal decreases below 1; or when uniqueness fails twice at same interval size.
- Alternates Generation: Respect solver time/node caps; stop early if frequency stabilizes.
- Ambiguity Score: frequency * corridor-length weight; tie-break by distance from nearest clue.
- Metrics: iterations_total, interval_steps, uniqueness_failures, repairs_used, time_ms, final_density, status.

## Open Questions (Resolved)

None. Defaults chosen; revisit thresholds after benchmarks.
