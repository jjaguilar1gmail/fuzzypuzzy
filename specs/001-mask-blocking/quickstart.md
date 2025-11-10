# Quickstart: Mask-Driven Blocking & Ambiguity-Aware Repair

## Enabling the Mask

### Basic Usage
```python
from generate.generator import Generator

# Generate with mask enabled (auto mode)
puzzle = Generator.generate_puzzle(
    size=9,
    difficulty="hard",
    seed=1234,
    mask_enabled=True  # Enable mask generation
)

# Check mask metrics
print(f"Mask pattern: {puzzle.solver_metrics['mask_pattern_id']}")
print(f"Blocked cells: {puzzle.solver_metrics['mask_cells_count']}")
print(f"Density: {puzzle.solver_metrics['mask_density']:.2%}")
```

### Using Specific Template
```python
puzzle = Generator.generate_puzzle(
    size=8,
    difficulty="medium",
    seed=5678,
    mask_enabled=True,
    mask_mode="template",      # Force template mode
    mask_template="corridor"   # Use corridor pattern
)
```

### Using Procedural Generation
```python
puzzle = Generator.generate_puzzle(
    size=7,
    difficulty="hard",
    seed=9999,
    mask_enabled=True,
    mask_mode="procedural",    # Force procedural sampling
    mask_density=0.05          # Target 5% density
)
```

## Configuration Knobs

### Mask Configuration (via GenerationConfig)
```python
from generate.models import GenerationConfig

config = GenerationConfig(
    size=9,
    difficulty="hard",
    seed=1234,
    
    # Mask settings
    mask_enabled=True,           # Master switch (default: False)
    mask_mode="auto",            # "auto" | "template" | "procedural"
    mask_template="corridor",    # When mask_mode == "template": corridor | ring | spiral | cross
    mask_density=None,           # None => auto heuristic; or float 0.0-0.10
    mask_max_attempts=5,         # Retries for invalid patterns (default: 5)
    
    # Structural repair (US2 - not yet implemented)
    structural_repair_enabled=False,     # Attempt block insertion before clue fallback
    structural_repair_max=2,             # Max block attempts (default: 2)
    structural_repair_timeout_ms=400     # Guardrail (default: 400ms)
)

puzzle = Generator.generate_puzzle(**config.__dict__)
```

## Available Patterns

- **corridor**: Dual lanes with chokepoints (min_size: 6, max_density: 8%)
- **ring**: Perimeter gates (min_size: 6, max_density: 10%)
- **spiral**: Inward spiral with gaps (min_size: 7, max_density: 9%)
- **cross**: Central plus shape (min_size: 5, max_density: 6%)

## Metrics Fields

Access via `puzzle.solver_metrics`:

```python
{
    "mask_enabled": True,
    "mask_pattern_id": "corridor",  # or "procedural:v1" or None
    "mask_cells_count": 4,
    "mask_density": 0.0617,         # Fraction of grid blocked
    "mask_attempts": 1,             # Generation attempts used
    
    # Repair fields (US2)
    "structural_repair_used": False,
    "ambiguity_regions_detected": 0
}
```

## Auto-Disable Behavior

Masks auto-disable when:
- `size < 6` (too small for meaningful structure)
- `difficulty == "easy"` (unless explicitly forced)
- Pattern generation fails after `mask_max_attempts`

When auto-disabled or failed:
- `mask_pattern_id == None`
- `mask_cells_count == 0`
- Generation proceeds normally without mask

## Error Handling

### InvalidMaskError
Raised during validation if:
- Start or end position blocked
- Mask creates disconnected regions
- Isolated small pockets detected

```python
from generate.mask.errors import InvalidMaskError

try:
    puzzle = Generator.generate_puzzle(size=7, mask_enabled=True, seed=bad_seed)
except InvalidMaskError as e:
    print(f"Mask validation failed: {e}")
    # Retry with different seed or disable mask
```

### MaskDensityExceeded
Raised if requested density > 10%:

```python
from generate.mask.errors import MaskDensityExceeded

try:
    config = GenerationConfig(size=7, mask_density=0.15)  # Too high!
except ValueError as e:
    print(f"Config validation: {e}")
```

## Testing Tips

### Deterministic Comparison
```python
# Baseline (no mask)
puzzle_baseline = Generator.generate_puzzle(size=7, difficulty="hard", seed=1234, mask_enabled=False)

# With mask
puzzle_masked = Generator.generate_puzzle(size=7, difficulty="hard", seed=1234, mask_enabled=True)

# Compare clue counts
print(f"Baseline clues: {puzzle_baseline.clue_count}")
print(f"Masked clues: {puzzle_masked.clue_count}")
print(f"Reduction: {(1 - puzzle_masked.clue_count / puzzle_baseline.clue_count) * 100:.1f}%")
```

### Density Sweep
```python
for density in [0.02, 0.03, 0.05, 0.08]:
    puzzle = Generator.generate_puzzle(
        size=8,
        difficulty="hard",
        seed=1234,
        mask_enabled=True,
        mask_mode="procedural",
        mask_density=density
    )
    print(f"Density {density:.0%}: {puzzle.clue_count} clues")
```

## Expected Impact (Success Criteria)

Based on spec targets:
- **Generation time**: ≥25% faster for hard puzzles (≥7x7)
- **Clue count**: ≥10% reduction vs baseline
- **Branching factor**: ≥15% reduction during path build
- **Uniqueness**: No increase in false UNIQUE classifications

## Next Steps

- **User Story 2**: Ambiguity-aware structural repair (not yet implemented)
- **User Story 3**: Enhanced metrics observability and batch analysis tools

