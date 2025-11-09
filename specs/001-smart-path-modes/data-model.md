# Data Model: Smart Path Modes

## New Dataclasses (conceptual)

- PathBuildSettings
  - mode: str ("backbite_v1" | "random_walk_v2" | "serpentine")
  - allow_diagonal: bool
  - min_cover_ratio: float (default 0.85)
  - time_budget_ms: int (size-tiered defaults)
  - seed: int
  - max_nodes: int (for search-like modes)
  - max_restarts: int (default 5)

- PathBuildResult
  - ok: bool
  - reason: str ("success" | "timeout" | "exhausted_restarts" | "coverage_below_threshold" | "partial_accepted")
  - coverage_ratio: float (0..1)
  - full_length: int (target cells excluding blocked)
  - positions: list[Position]
  - mode_used: str
  - elapsed_ms: int
  - metrics: dict (steps, restarts, degree_samples, warnsdorff_hits)

- GenerationConfig additions
  - allow_partial_paths: bool (default True)
  - min_cover_ratio: float (default 0.85)
  - path_time_ms: int (tiered: ≤6:2000, 7–8:4000, 9:6000)

- GeneratedPuzzle additions
  - timings_ms.path_build: int
  - generation_metrics.path_coverage: float
  - generation_metrics.path_mode_used: str

## Validation Rules
- min_cover_ratio ∈ [0.5, 1.0]
- path_time_ms > 0
- positions length ≤ full_length; if ok==False then reason != "success"

## State Transitions
- PathBuilder(build) → PathBuildResult
- Generator(generate_puzzle)
  - if result.ok: continue
  - elif allow_partial_paths and result.coverage_ratio ≥ min_cover_ratio: accept partial (block remainder, adjust Constraints.max_value)
  - else: retry/switch mode/abort with reason
