# Research: Staged Uniqueness Validation

## Decisions

- Early-exit search: Use bounded backtracking with solution_cap=2, diversified by heuristic profiles (position order, value order, frontier bias). Hard wall-time per run: 100–200 ms.
- Randomized probes: Seeded runs with varied heuristic parameters; sequential by default to keep stdlib; parallelization can be simulated via short sequential bursts respecting total budget.
- SAT/CP hook: Optional interface only; disabled by default. If present, perform one-solution query then add blocking clause and re-run under cap to detect second solution.
- Budgets: ≥7x7 defaults — Easy 600 ms, Medium 500 ms, Hard 400 ms (aggregated across stages). ≤5x5 — 100 ms enumeration target.
- Small boards: Always run enumeration first; treat as ground truth to avoid probabilistic ambiguity.
- Outcomes: Tri-state with metrics (Unique, Non-Unique, Inconclusive), never exceed budget.

## Rationale

- Full enumeration is factorial/exponential for 8-neighbor boards; fast counterexample detection suffices for the majority of non-unique cases.
- Diversified heuristics reduce correlation among early-exit runs, increasing likelihood of finding alternates without deep search.
- Seeded probes + strict budgets preserve determinism and throughput in CI and production.
- Optional SAT/CP brings strong verification when available without imposing dependencies on default builds.

## Alternatives Considered

- Single-strategy deepening search: Higher variance, easy to stall; rejected in favor of layered approach with strict budgets.
- Always-on SAT/CP: Strong but adds heavy deps and environment fragility; rejected by policy (stdlib-only default).
- Monte-Carlo completion sampling without constraints: Too noisy; poor precision vs diversified guided search.

## Unknowns Resolved

- External solver policy: stdlib-only core with optional hook (resolved via spec FR-012).
- Inconclusive default handling: Accept for ≥7x7 with metric (resolved via spec FR-013).
- Default budgets per difficulty (≥7x7): 600/500/400 ms (resolved via spec FR-014).

## Implementation Notes

- Reuse existing solver passes (corridors, degree, islands) before search expansion in each probe.
- Use a small registry of heuristic profiles (e.g., row-major vs. center-out; min-remaining-values vs. degree-biased).
- Metrics object to aggregate per-stage timings, nodes, and decision source.
- Respect constitution: no mutation of caller puzzles; deterministic given seed+config; bounded search only.