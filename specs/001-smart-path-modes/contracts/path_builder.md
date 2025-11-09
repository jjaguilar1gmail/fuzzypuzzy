# Contract: PathBuilder Smart Modes

## build(settings: PathBuildSettings) -> PathBuildResult

Input (PathBuildSettings):
- mode: str
- allow_diagonal: bool
- min_cover_ratio: float
- time_budget_ms: int
- seed: int
- max_nodes: int
- max_restarts: int

Output (PathBuildResult):
- ok: bool
- reason: str (success | timeout | exhausted_restarts | coverage_below_threshold | partial_accepted)
- coverage_ratio: float
- full_length: int
- positions: list[Position]
- mode_used: str
- elapsed_ms: int
- metrics: dict

### Mode Behaviors
- serpentine: Immediate full coverage; reason=success.
- backbite_v1: Mutation loop until budget or convergence; success if full_length reached; else partial or timeout.
- random_walk_v2: Guided expansion; may restart; success on full_length; partial on coverage≥threshold and time/node limit reached.

### Error Handling
- Invalid mode → ValueError
- Negative time_budget_ms → ValueError
- If coverage < min_cover_ratio and budget exhausted → ok=False reason=coverage_below_threshold

### Determinism
Same seed + settings → identical positions sequence and metrics.
