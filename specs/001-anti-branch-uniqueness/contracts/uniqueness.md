# Contract: Anti-Branch Uniqueness Probe

## Interface
- Input:
  - puzzle: CandidatePuzzle (immutable view)
  - config: UniquenessProbeConfig (size-tier budgets, seed, shuffle flags, max_solutions=2)
- Output:
  - outcome: { classification: SECOND_FOUND | EXHAUSTED | TIMEOUT | UNKNOWN | EXTENDED_EXHAUSTED | EXTENDED_REJECT | FALLBACK_CONFIRMED | FALLBACK_REJECTED,
               probes: list[ProbeOutcome],
               extended_used: bool }

## Behavior
1. Run logic fixpoint on a copy until no new placements.
2. Identify first ambiguity; choose the opposite branch of the solver’s preferred heuristic; run bounded DFS with early exit at second solution.
3. Repeat step 2 for probe_count variants by shuffling tie-break ordering (MRV/LCV/frontier) using seed-derived permutations.
4. If any probe finds second solution → classification SECOND_FOUND.
5. If all probes EXHAUST within budgets → classification EXHAUSTED.
6. If probes TIMEOUT/UNKNOWN and fallback enabled → run SAT/CP block-recheck; map to FALLBACK_*; else run single extended attempt (+50% budgets) → EXTENDED_EXHAUSTED or EXTENDED_REJECT.

## Telemetry
- Per probe: nodes_explored, time_ms, permutation_id, outcome_code, second_solution_hash (if found)
- Summary: size_tier, probe_count, extended_used, classification
