# Contracts: Staged Uniqueness Validation

This feature is internal (no external HTTP API). Contracts define Python function interfaces.

## Public Function Signatures (Proposed)

```text
generate.uniqueness_staged.check_uniqueness(request: UniquenessCheckRequest) -> UniquenessCheckResult

generate.uniqueness_staged.register_sat_solver(solver: SolverInterface) -> None

generate.uniqueness_staged.list_profiles() -> list[StrategyProfile]
```

## Behavioral Contracts

1. `check_uniqueness` MUST respect `request.total_budget_ms`.
2. For size ≤25, enumeration runs first; if Non-Unique found, later stages skipped.
3. Return decision plus metrics; never raise for timeout—use Inconclusive.
4. If SAT solver not registered, SAT stage is skipped silently.

## Error Modes

- InvalidRequestError: validation failure (budget <=0, bad enum).
- ExternalSolverError: raised only when registered solver fails internally; converted to Inconclusive with note.
