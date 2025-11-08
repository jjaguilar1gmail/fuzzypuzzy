# Quickstart: Uniqueness-Preserving Puzzle Generator

## Generate a Puzzle

Basic generation (easy difficulty, 5x5):
```
python hidato.py --generate --size 5 --difficulty easy --seed 123
```

With blocked cells and symmetry:
```
python hidato.py --generate --size 7 --difficulty hard --blocked 1,3;2,5 --symmetry rotational --seed 9876
```

Specify percent fill instead of difficulty:
```
python hidato.py --generate --size 6 --percent-fill 0.45 --seed 42
```

Trace generation:
```
python hidato.py --generate --size 7 --difficulty medium --seed 55 --trace
```

## Output Fields
- size, allow_diagonal
- givens (list of clues)
- blocked_cells
- solution (full solved grid)
- difficulty_label, difficulty_score
- clue_count
- uniqueness_verified
- attempts_used
- seed, path_mode, clue_mode, symmetry
- timings_ms { total, solve, uniqueness }
- solver_metrics { nodes, depth, steps, logic_ratio }

## Failure Modes
- timeout: generation exceeded timeout_ms
- attempt_exhausted: max_attempts hit before target band
- uniqueness_not_achievable: repeated non-unique states
- internal_error: unexpected issue (with sanitized message)

## Reproducibility
Repeat command with same seed + params => identical clue layout.

## Recommended Difficulty Bands (approximate)
| Band | Clue Density | Search Depth | Time P95 |
|------|--------------|--------------|---------|
| easy | ≥ 40%        | 0            | <300ms  |
| medium | 30–40%     | ≤10          | <800ms  |
| hard | 22–30%       | 5–20         | <2500ms |
| extreme | <22%      | >20 (≤200)   | <5000ms |

## Best Practices
- Provide a seed for reproducibility when batching.
- Use percent-fill for custom density tuning; difficulty auto-assessed post-generation.
- Enable trace for tuning heuristics (removals accepted vs rejected).

## Next Steps
After generation integrate with pack builder or export to JSON for distribution.
