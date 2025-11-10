# Contract: Generator Configuration (Solver-Driven Pruning)

## Flags & Parameters

- difficulty: enum{easy, medium, hard, extreme}
- path_mode: enum{serpentine, backbite_v1, random_walk_v2}
- seed: int
- allow_diagonal: bool
- pruning.enabled: bool (default true)
- pruning.target_density_hard: [0.24, 0.32]
- pruning.linear_fallback_k: 6
- pruning.max_repairs: 2
- repair.topN_divergence: 5
- repair.alternates_count: 5
- anchors.disable_turns_for_hard: true

## Outputs (Metrics)
- pruning.iterations_total: int
- pruning.interval_steps: int
- pruning.uniqueness_failures: int
- pruning.repairs_used: int
- final.density: float
- final.status: enum
- timings.time_ms: float

## Status
- success
- success_with_repairs
- aborted_max_repairs
- aborted_timeout
