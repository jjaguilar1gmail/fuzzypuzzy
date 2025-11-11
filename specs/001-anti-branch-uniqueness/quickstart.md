# Quickstart: Anti-Branch Uniqueness & Size-Aware Clue Distribution

## Overview
This feature adds tighter uniqueness verification and improved clue distribution to reduce false-unique puzzles and clustering.

## Enable Enhanced Uniqueness
Add the `--enable-anti-branch` flag to enable the anti-branch uniqueness probe:

```bash
python -m app.packgen.cli --outdir output/packs/test --sizes 8 --difficulties hard --count 5 --enable-anti-branch
```

### What It Does
- **US1 (P1)**: Multi-probe uniqueness verification with randomized tie-breaks (2-3 probes per removal)
- **US2 (P2)**: Size/difficulty-aware anchor policies, dynamic density floors, spacing-aware removal scoring, and post-density de-chunk pass
- **US3 (P3)**: Detailed telemetry with probe outcomes, spacing metrics, and generation statistics

### Path Mode Restriction
- Enhanced features only activate for `backbite_v1` and `random_v2` path modes (per FR-010)
- Other modes fall back to traditional `count_solutions(cap=2)` uniqueness checking

## Size-Tier Budgets (US1)
Automatic based on puzzle size:
- **Small (≤25 cells)**: 2,000 nodes, 250ms timeout, 2 probes
- **Medium (26-64 cells)**: 5,000 nodes, 400ms timeout, 3 probes  
- **Large (65-100 cells)**: 9,000 nodes, 600ms timeout, 3 probes
- **Very Large (>100 cells)**: Same as large

### Extended Attempt Policy
- If initial probes return UNKNOWN/TIMEOUT: one extended attempt with +50% budgets
- Classification codes: SECOND_FOUND, EXHAUSTED, TIMEOUT, UNKNOWN

## Anchor Policies (US2)
Size and difficulty-aware retention:
- **Easy**: Endpoints + 2-3 evenly spaced turn anchors
- **Medium**: Endpoints + at most 1 soft turn (removable if spacing improves)
- **Hard**: Endpoints only (extra turns added only during structural repair)

## Density Floors (US2)
Prevents over-constraint on small boards:
- **Easy**: Small 34%, Medium 30%, Large 26%
- **Medium**: Small 30%, Medium 26%, Large 22%
- **Hard**: Small 26%, Medium 22%, Large 18%

## Spacing & De-Chunk (US2)
- **Spacing Score**: `S = w1 * avg_manhattan_distance - w2 * quadrant_variance`
- **De-Chunk Pass**: After target density reached, up to 3 passes attempt to remove clues from largest cluster while preserving uniqueness and improving spacing

## Telemetry (US3)
When enabled, generation creates summary statistics:
- Accepted/reverted removals
- Probe outcomes per attempt
- Final density and spacing metrics
- Solve statistics
- De-chunk pass results

Summary data structure (available in code, logging to file not yet wired):
```json
{
  "puzzle_id": "8x8_hard_99999",
  "size": 8,
  "difficulty": "hard",
  "path_mode": "backbite_v1",
  "final_clue_count": 12,
  "final_density": 0.1875,
  "removals_accepted": 52,
  "spacing_score": 3.45,
  "largest_cluster_size": 2
}
```

## CLI Examples

### Basic Usage
```bash
# Generate with anti-branch probe enabled
python -m app.packgen.cli --outdir output/test --sizes 8 --difficulties hard --count 10 --enable-anti-branch

# Multiple sizes and difficulties
python -m app.packgen.cli --outdir output/mixed --sizes 6,8,10 --difficulties easy,medium,hard --count 30 --enable-anti-branch

# With specific seed for reproducibility
python -m app.packgen.cli --outdir output/seed-test --sizes 8 --difficulties hard --count 5 --seed 42 --enable-anti-branch
```

### Path Mode Comparison
```bash
# Backbite v1 (enhanced features active)
python -m app.packgen.cli --outdir output/backbite --sizes 8 --difficulties hard --count 10 --path-mode backbite_v1 --enable-anti-branch

# Random v2 (enhanced features active)
python -m app.packgen.cli --outdir output/random --sizes 8 --difficulties hard --count 10 --path-mode random_v2 --enable-anti-branch

# Serpentine (falls back to traditional uniqueness check)
python -m app.packgen.cli --outdir output/serpentine --sizes 8 --difficulties hard --count 10 --path-mode serpentine --enable-anti-branch
```

## Configuration Notes
- **Deterministic**: All randomness seeded from CLI seed parameter
- **Constitution Compliant**: No I/O in core logic, bounded search with node/time caps
- **Functions ≤60 Lines**: Guideline followed throughout implementation

## Success Criteria
- **SC-001**: 0% false-unique puzzles with >25 cells (multi-probe verification)
- **SC-002**: ≥95% definitive classifications without fallback (extended attempt policy)
- **SC-003**: Average spacing ≥2.5 Manhattan units for medium/large boards (spacing score + de-chunk)
- **SC-004**: Max cluster size ≤4 clues for non-trivial boards (de-chunk pass)
- **SC-005**: ≤2s average generation time (size-tier budgets)
- **SC-006**: Full telemetry for tuning (summary statistics captured)

## Troubleshooting

### High Timeout Rate
- Reduce size or switch to serpentine mode
- Check size-tier budgets in `util/logging_uniqueness.py`

### Clustering Still Present
- Verify path mode is backbite_v1 or random_v2
- Check de-chunk pass executed (max 3 passes)
- Inspect final spacing metrics in generation summary

### Generation Too Slow
- Reduce puzzle count or size range
- Disable anti-branch probe for faster (less rigorous) generation
- Use smaller timeout_ms parameter

## Implementation Files
- `solve/uniqueness_probe.py`: Core anti-branch probe logic
- `generate/spacing.py`: Spacing metrics and cluster detection
- `generate/anchors_policy.py`: Size/difficulty anchor policies  
- `util/logging_uniqueness.py`: Size-tier configs and logger
- `generate/generator.py`: Integration into removal loop and de-chunk pass
- `generate/removal.py`: Spacing-aware candidate scoring

