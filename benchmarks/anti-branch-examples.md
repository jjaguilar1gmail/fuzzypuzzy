# Anti-Branch Uniqueness: Before/After Examples

## Overview
This document provides example seeds and commands to compare puzzle generation before and after enabling the anti-branch uniqueness feature.

## Baseline (Without Anti-Branch)

### Example Seeds for Testing
```bash
# 8x8 Hard puzzles (baseline)
python -m app.packgen.cli --outdir benchmarks/baseline-8x8-hard --sizes 8 --difficulties hard --count 10 --seed 12345

# 6x6 Medium puzzles (baseline)
python -m app.packgen.cli --outdir benchmarks/baseline-6x6-medium --sizes 6 --difficulties medium --count 10 --seed 67890

# Mixed sizes Easy (baseline)
python -m app.packgen.cli --outdir benchmarks/baseline-mixed-easy --sizes 5,6,7,8 --difficulties easy --count 20 --seed 11111
```

## Enhanced (With Anti-Branch)

### Same Seeds with Enhanced Features
```bash
# 8x8 Hard with anti-branch probe
python -m app.packgen.cli --outdir benchmarks/enhanced-8x8-hard --sizes 8 --difficulties hard --count 10 --seed 12345 --enable-anti-branch

# 6x6 Medium with anti-branch probe
python -m app.packgen.cli --outdir benchmarks/enhanced-6x6-medium --sizes 6 --difficulties medium --count 10 --seed 67890 --enable-anti-branch

# Mixed sizes Easy with anti-branch probe
python -m app.packgen.cli --outdir benchmarks/enhanced-mixed-easy --sizes 5,6,7,8 --difficulties easy --count 20 --seed 11111 --enable-anti-branch
```

## Specific Test Cases

### Known Problematic Seeds
These seeds have been identified as producing false-unique or highly clustered puzzles in baseline mode:

```bash
# Seed 99999 - Known clustering issue on 8x8 hard backbite
python -m app.packgen.cli --outdir benchmarks/seed-99999-baseline --sizes 8 --difficulties hard --count 1 --seed 99999 --path-mode backbite_v1

python -m app.packgen.cli --outdir benchmarks/seed-99999-enhanced --sizes 8 --difficulties hard --count 1 --seed 99999 --path-mode backbite_v1 --enable-anti-branch

# Seed 42 - Standard test seed
python -m app.packgen.cli --outdir benchmarks/seed-42-baseline --sizes 8 --difficulties hard --count 1 --seed 42

python -m app.packgen.cli --outdir benchmarks/seed-42-enhanced --sizes 8 --difficulties hard --count 1 --seed 42 --enable-anti-branch

# Seed 31415 - Large board stress test
python -m app.packgen.cli --outdir benchmarks/seed-31415-baseline --sizes 10 --difficulties hard --count 1 --seed 31415

python -m app.packgen.cli --outdir benchmarks/seed-31415-enhanced --sizes 10 --difficulties hard --count 1 --seed 31415 --enable-anti-branch
```

## Path Mode Comparisons

### Backbite v1 (Enhanced features active)
```bash
# Baseline
python -m app.packgen.cli --outdir benchmarks/backbite-baseline --sizes 8 --difficulties hard --count 5 --seed 54321 --path-mode backbite_v1

# Enhanced
python -m app.packgen.cli --outdir benchmarks/backbite-enhanced --sizes 8 --difficulties hard --count 5 --seed 54321 --path-mode backbite_v1 --enable-anti-branch
```

### Random v2 (Enhanced features active)
```bash
# Baseline
python -m app.packgen.cli --outdir benchmarks/random-baseline --sizes 8 --difficulties hard --count 5 --seed 54321 --path-mode random_v2

# Enhanced
python -m app.packgen.cli --outdir benchmarks/random-enhanced --sizes 8 --difficulties hard --count 5 --seed 54321 --path-mode random_v2 --enable-anti-branch
```

### Serpentine (Enhanced features inactive - fallback mode)
```bash
# Baseline
python -m app.packgen.cli --outdir benchmarks/serpentine-baseline --sizes 8 --difficulties hard --count 5 --seed 54321 --path-mode serpentine

# Enhanced (will use traditional count_solutions)
python -m app.packgen.cli --outdir benchmarks/serpentine-enhanced --sizes 8 --difficulties hard --count 5 --seed 54321 --path-mode serpentine --enable-anti-branch
```

## Performance Benchmarks

### Generation Time Comparison
```bash
# Baseline: 100 puzzles mixed sizes
time python -m app.packgen.cli --outdir benchmarks/perf-baseline-100 --sizes 6,7,8 --difficulties medium,hard --count 100 --seed 77777

# Enhanced: Same configuration
time python -m app.packgen.cli --outdir benchmarks/perf-enhanced-100 --sizes 6,7,8 --difficulties medium,hard --count 100 --seed 77777 --enable-anti-branch
```

### Size Scaling Test
```bash
# Small boards (5x5-7x7)
python -m app.packgen.cli --outdir benchmarks/small-enhanced --sizes 5,6,7 --difficulties hard --count 20 --seed 10001 --enable-anti-branch

# Medium boards (8x8-9x9)
python -m app.packgen.cli --outdir benchmarks/medium-enhanced --sizes 8,9 --difficulties hard --count 20 --seed 10002 --enable-anti-branch

# Large boards (10x10-12x12)
python -m app.packgen.cli --outdir benchmarks/large-enhanced --sizes 10,11,12 --difficulties hard --count 10 --seed 10003 --enable-anti-branch
```

## Metrics to Compare

When analyzing before/after results, check:

1. **Uniqueness Verification**:
   - Baseline: Manual verification with external solver
   - Enhanced: Guaranteed by multi-probe anti-branch DFS

2. **Clue Density**:
   - Count: Number of givens / total cells
   - Distribution: Check density_floor compliance

3. **Spacing Quality**:
   - Average Manhattan distance between clues
   - Quadrant variance (should be <0.35)
   - Largest cluster size (should be ≤4)

4. **Generation Time**:
   - Total time per puzzle
   - Success rate (puzzles generated / attempts)

5. **Difficulty Accuracy**:
   - Check if final puzzles match requested difficulty band
   - Compare assessed_difficulty_label in output

## Expected Improvements

| Metric | Baseline | Enhanced | Success Criterion |
|--------|----------|----------|-------------------|
| False-unique rate | ~5-10% | 0% | SC-001 |
| Definitive classifications | ~80% | ≥95% | SC-002 |
| Average spacing (8x8) | ~1.8-2.2 | ≥2.5 | SC-003 |
| Max cluster size | 5-8 | ≤4 | SC-004 |
| Generation time | Baseline | ≤2s avg | SC-005 |
| Telemetry | None | Full stats | SC-006 |

## Analysis Scripts

```bash
# Parse generation logs
python scripts/analyze_generation_logs.py benchmarks/enhanced-*/pack.json --compare benchmarks/baseline-*/pack.json

# Check spacing metrics
python scripts/check_spacing_quality.py benchmarks/enhanced-8x8-hard/

# Verify uniqueness (external)
python scripts/verify_uniqueness_external.py benchmarks/enhanced-8x8-hard/puzzles/
```

## Notes

- All seeds should produce deterministic results
- Enhanced mode may generate slightly fewer clues due to stricter uniqueness checking
- Path modes backbite_v1 and random_v2 show largest improvements
- Generation time may increase by 10-30% due to multi-probe verification
- De-chunk pass typically removes 0-3 additional clues after target density
