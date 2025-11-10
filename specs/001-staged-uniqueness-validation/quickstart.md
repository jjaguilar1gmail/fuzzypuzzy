# Quickstart: Staged Uniqueness Validation

## Goal
Run the staged uniqueness checker against a generated 7x7 puzzle and interpret metrics.

## Steps
1. Create a `UniquenessCheckRequest` (size=7, difficulty=medium, total_budget_ms=500).
2. Call `check_uniqueness(request)`.
3. Inspect `decision`, `stage_decided`, and `per_stage_ms`.
4. If `decision == Inconclusive` and policy demands certainty, add a clue and re-run.

## Example (Pseudo-Python)
```python
from generate.uniqueness_staged import check_uniqueness, UniquenessCheckRequest

req = UniquenessCheckRequest(
    size=7,
    adjacency='adj8',
    difficulty='medium',
    total_budget_ms=500,
    stage_budget_split={'early':0.4,'probes':0.4,'sat':0.2},
    seed=42,
    strategy_flags={'sat': False}
)
result = check_uniqueness(req)
print(result.decision, result.stage_decided, result.per_stage_ms)
```

## Notes
- Deterministic: same seed + config → identical outcomes.
- To enable SAT hook, register a solver via `register_sat_solver` before the call.
