# Quickstart: Uniqueness-Preserving Puzzle Generator

## Generate a Puzzle

Basic generation (easy difficulty, 5x5):
```
python hidato.py --generate --size 5 --difficulty easy --seed 123
```

With blocked cells and symmetry:
```
python hidato.py --generate --size 7 --difficulty hard --blocked '1,3;2,5' --symmetry rotational --seed 9876
```

Specify percent fill instead of difficulty:
```
python hidato.py --generate --size 6 --percent-fill 0.45 --seed 42
```

Print reproducibility info:
```
python hidato.py --generate --size 7 --difficulty medium --seed 55 --print-seed
```

## Output Fields
- size, allow_diagonal
- givens (list of clues with positions and values)
- blocked_cells
- solution (full solved grid)
- difficulty_label, difficulty_score
- clue_count, clue_density
- logic_ratio (percentage of logic-only steps)
- search_depth (maximum search depth required)
- uniqueness_verified
- attempts_used
- seed, path_mode, clue_mode, symmetry
- timings_ms { total, solve, uniqueness }

## Failure Modes
- timeout: generation exceeded timeout_ms
- attempt_exhausted: max_attempts hit before target band
- uniqueness_not_achievable: repeated non-unique states
- internal_error: unexpected issue (with sanitized message)

## Reproducibility
Repeat command with same seed + params => identical clue layout.

Example:
```
python hidato.py --generate --size 5 --seed 42
# Run again with same seed
python hidato.py --generate --size 5 --seed 42
# => Same puzzle output
```

## Recommended Difficulty Bands (approximate)
| Band | Clue Density | Search Depth | Time P95 |
|------|--------------|--------------|---------|
| easy | ≥ 50%        | 0-5          | <300ms  |
| medium | 35–50%     | 5–15         | <800ms  |
| hard | 25–35%       | 10–25        | <2500ms |
| extreme | 15–25%    | >20 (≤200)   | <5000ms |

Note: Actual assessed difficulty may differ from requested due to puzzle characteristics.

## Best Practices
- Provide a seed for reproducibility when batching.
- Use percent-fill for custom density tuning; difficulty auto-assessed post-generation.
- Use --print-seed to get exact reproduction commands.
- Blocked cells are supported but may increase generation time.

## Next Steps
After generation integrate with pack builder or export to JSON for distribution.
