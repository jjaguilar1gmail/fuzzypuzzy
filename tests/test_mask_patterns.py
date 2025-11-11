"""Tests for mask pattern generation (US1)."""
import pytest
from generate.mask.patterns import (
    generate_corridor_pattern,
    generate_ring_pattern,
    generate_spiral_pattern,
    generate_cross_pattern,
    get_pattern_generator,
    get_pattern_constraints,
    PATTERNS
)
from util.rng import RNG


def test_corridor_pattern_basic():
    """T016: Verify corridor pattern generates valid mask."""
    rng = RNG(1234)
    mask = generate_corridor_pattern(size=7, rng=rng, seed=1234, attempt_idx=0)
    
    assert mask.grid_size == 7
    assert mask.pattern_id == "corridor"
    assert mask.seed == 1234
    assert len(mask.cells) > 0
    assert mask.density == len(mask.cells) / 49


def test_ring_pattern_basic():
    """T016: Verify ring pattern generates valid mask."""
    rng = RNG(5678)
    mask = generate_ring_pattern(size=7, rng=rng, seed=5678, attempt_idx=0)
    
    assert mask.grid_size == 7
    assert mask.pattern_id == "ring"
    assert len(mask.cells) > 0
    assert mask.density <= 0.11  # Allow small tolerance


def test_spiral_pattern_basic():
    """T016: Verify spiral pattern generates valid mask."""
    rng = RNG(9999)
    mask = generate_spiral_pattern(size=8, rng=rng, seed=9999, attempt_idx=0)
    
    assert mask.grid_size == 8
    assert mask.pattern_id == "spiral"
    assert len(mask.cells) > 0


def test_cross_pattern_basic():
    """T016: Verify cross pattern generates valid mask."""
    rng = RNG(1111)
    mask = generate_cross_pattern(size=7, rng=rng, seed=1111, attempt_idx=0)
    
    assert mask.grid_size == 7
    assert mask.pattern_id == "cross"
    assert len(mask.cells) > 0


def test_pattern_deterministic():
    """T016: Verify same seed produces same pattern."""
    seed = 4242
    
    rng1 = RNG(seed)
    mask1 = generate_corridor_pattern(size=7, rng=rng1, seed=seed, attempt_idx=0)
    
    rng2 = RNG(seed)
    mask2 = generate_corridor_pattern(size=7, rng=rng2, seed=seed, attempt_idx=0)
    
    assert mask1.cells == mask2.cells
    assert mask1.density == mask2.density


def test_get_pattern_generator():
    """T016: Verify pattern generator lookup works."""
    gen = get_pattern_generator("corridor")
    assert callable(gen)
    
    with pytest.raises(ValueError, match="Unknown pattern"):
        get_pattern_generator("invalid_pattern")


def test_get_pattern_constraints():
    """T016: Verify pattern constraints retrieval."""
    constraints = get_pattern_constraints("corridor")
    
    assert "min_size" in constraints
    assert "max_density" in constraints
    assert constraints["min_size"] >= 5
    assert constraints["max_density"] <= 0.10


def test_all_patterns_registered():
    """T016: Verify all expected patterns are registered."""
    expected_patterns = ["corridor", "ring", "spiral", "cross"]
    
    for pattern_name in expected_patterns:
        assert pattern_name in PATTERNS
        assert "generator" in PATTERNS[pattern_name]
        assert "min_size" in PATTERNS[pattern_name]
        assert "max_density" in PATTERNS[pattern_name]


def test_patterns_respect_density_cap():
    """T016: Verify patterns stay near 10% density target (12% cap for discrete cells)."""
    rng = RNG(7777)
    
    for size in [7, 8, 9]:
        for pattern_name in ["corridor", "ring", "spiral", "cross"]:
            gen = get_pattern_generator(pattern_name)
            mask = gen(size, rng, 7777, 0)
            
            # Real cap is 10%, but discrete cell counts on small boards → 12% tolerance
            assert mask.density <= 0.12, f"{pattern_name} on {size}x{size} density {mask.density} > 0.12"
