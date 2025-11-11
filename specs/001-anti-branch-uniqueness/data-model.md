# Data Model: Anti-Branch Uniqueness & Size-Aware Clue Distribution

## Entities

### CandidatePuzzle
- Fields: id, size, grid_cells, clues (list[CellRef]), path_mode, difficulty
- Relationships: feeds into uniqueness probes; anchors derived from path

### SizeTierPolicy
- Fields: tier_name, min_size, max_size, max_nodes, timeout_ms, probe_count, extended_factor (float)
- Relationships: consumed by UniquenessProbeConfig

### UniquenessProbeConfig
- Fields: seed, size_tier (ref), shuffle_strategy, max_solutions=2
- Relationships: passed to AntiBranchProbe

### ProbeOutcome
- Fields: probe_index, outcome_code, nodes_explored, time_ms, permutation_id, second_solution_hash (optional)
- Relationships: aggregated into RemovalAttemptLog

### RemovalAttemptLog
- Fields: attempt_id, candidate_id, size_tier, probe_outcomes (list), extended_used (bool), final_decision, reason_code
- Relationships: emitted as telemetry record

### TelemetryRecord
- Fields: timestamp, path_mode, size, difficulty, removal_attempts, spacing_score, quadrant_variance, clue_density
- Relationships: consumed by summary aggregator

### SpacingMetrics
- Fields: avg_manhattan_distance, quadrant_variance, cluster_count, largest_cluster_size
- Relationships: influences candidate scoring

### AnchorPolicy
- Fields: difficulty, size_tier, retain_endpoints (bool), max_turn_anchors, soft_turn_allowed (bool)
- Relationships: applied before clue removal stage

### DensityPolicy
- Fields: difficulty, size_tier, min_density_floor
- Relationships: termination condition for removal loop

## State Transitions
1. Path construction → Anchor policy applied → Initial clue set
2. Clue removal loop:
   - Select candidate using safety + spacing score
   - Run uniqueness two-phase multi-probe
   - Accept → update clues; Reject → revert
3. Target density reached → De-chunk phase (cluster reduction) using uniqueness checks
4. Final puzzle validation → telemetry summary emission

## Validation Rules
- second_solution_hash present only if outcome_code=SECOND_FOUND
- extended_used implies at least one probe had outcome UNKNOWN or TIMEOUT prior
- spacing_score recalculated after each accepted removal
- density must never drop below floor defined by DensityPolicy

## Notes
Data model avoids implementation details; emphasizes traceability for tuning.
