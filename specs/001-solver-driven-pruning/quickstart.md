# Quickstart: Solver-Driven Pruning

## Generate a hard 9x9 with pruning

- Use a fixed seed for reproducibility.
- Backbite path mode stresses pruning.

Example (CLI):

```
python hidato.py --generate --size 9 --difficulty hard --path-mode backbite_v1 --seed 12345 --verbose
```

Expect:
- Anchor Policy: adaptive_v1; Anchor Count: 2 (endpoints only)
- Final Clue Density: ~24–32% (target)
- Status: success or success_with_repairs
- Metrics include iterations, contractions, repairs_used, time_ms

## Tuning knobs
- pruning.target_density_hard: adjust acceptable range
- pruning.max_repairs: cap at 2 to avoid inflation
- repair.alternates_count: 3–5 typical
- pruning.linear_fallback_k: 6 for final boundary probing

## Reproducibility tips
- Always capture: seed, difficulty, path_mode, and pruning config in outputs.
- Re-run with the same config to verify determinism.
