# Quickstart: Smart Path Modes

## New CLI Flags
- --path-mode backbite_v1 | random_walk_v2 | serpentine
- --allow-partial-paths (bool)
- --min-cover <ratio> (e.g., 0.85)
- --path-time-ms <ms budget>

## Examples

### Full Coverage Backbite
```
python hidato.py --generate --size 7 --difficulty medium --path-mode backbite_v1 --seed 123
```

### Partial Acceptance (Coverage ≥ 85%)
```
python hidato.py --generate --size 9 --difficulty hard --path-mode random_walk_v2 --allow-partial-paths true --min-cover 0.85 --path-time-ms 4000 --seed 42
```
(Output includes path_coverage and reason=partial_accepted if not full coverage.)

### Retry then Switch Mode
```
# Attempt random_walk_v2 first; on failure generator switches to backbite_v1
python hidato.py --generate --size 8 --difficulty medium --path-mode random_walk_v2 --allow-partial-paths true --seed 999
```

## Interpreting Output
- path_mode_used: actual mode producing accepted path
- path_coverage: ratio of visited cells vs total
- reason: success | partial_accepted | timeout | exhausted_restarts | coverage_below_threshold

## Determinism Check
Run twice with same flags + seed to verify identical givens and coverage.
