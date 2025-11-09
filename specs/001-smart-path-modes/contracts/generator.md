# Contract: Generator with Partial Path Acceptance

## generate_puzzle(..., path_mode, allow_partial_paths, min_cover_ratio, path_time_ms, ...) -> GeneratedPuzzle

Behavior:
1. Build path via PathBuilder with provided settings.
2. If PathBuildResult.ok == True: proceed with clue placement/removal.
3. Else if allow_partial_paths and coverage_ratio ≥ min_cover_ratio:
   - Block all cells not in positions
   - Set Constraints.max_value = len(positions)
   - Proceed with generation (ensuring uniqueness & metrics)
4. Else:
   - Retry same mode up to N attempts OR switch to backbite_v1 if configured
   - If still failing, return error or best-attempt metadata (seed, reason, coverage)

Metrics:
- timings_ms.path_build
- generation_metrics.path_mode_used
- generation_metrics.path_coverage
- warnings when partial accepted or coverage below threshold

Determinism:
- Same seed + settings yields identical accepted path and puzzle output.
