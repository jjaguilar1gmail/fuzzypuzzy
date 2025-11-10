# Data Model: Staged Uniqueness Validation

## Entities

### UniquenessCheckRequest
- size: int
- adjacency: enum {adj4, adj8}
- difficulty: enum {easy, medium, hard}
- total_budget_ms: int
- stage_budget_split: dict {stage_name: percent}
- seed: int
- strategy_flags: dict {stage_name: enabled}

### UniquenessCheckResult
- decision: enum {Unique, Non-Unique, Inconclusive}
- stage_decided: str
- elapsed_ms: int
- per_stage_ms: dict {stage_name: ms}
- nodes_explored: dict {stage_name: int}
- probes_run: int
- notes: str

### StrategyProfile
- id: str
- enabled: bool
- budget_share: float
- params: dict (e.g., value_order, position_order, frontier_bias, lcv_weight)
- capabilities: set {detect_non_unique, prove_unique}

## Validation Rules
- total_budget_ms > 0
- sum(stage_budget_split.values) == 1.0 (within tolerance)
- If size ≤ 25 then enumeration is required before staged strategies
- seed must be reproducible and logged
- SAT/CP stage requires registered external solver; otherwise skipped

## State Transitions
- Request → Stage 1 (early-exit) →
  - If Non-Unique: Result(Non-Unique)
  - Else → Stage 2 (probes) →
    - If Non-Unique: Result(Non-Unique)
    - Else → Stage 3 (SAT/CP, optional) →
      - If Non-Unique: Result(Non-Unique)
      - Else: Result(Unique|Inconclusive) depending on small-board enumeration or budget status
