"""Template pattern generators for masks.

Patterns create intentional structural shapes (corridors, rings, spirals)
that form chokepoints without feeling arbitrary.
"""
from typing import Optional
from generate.mask.models import BlockMask
from util.rng import RNG


def generate_corridor_pattern(size: int, rng: RNG, seed: int, attempt_idx: int) -> BlockMask:
    """Generate dual-corridor pattern with 1-2 chokepoints.
    
    Creates two parallel lanes with periodic gaps that funnel paths through
    specific bottlenecks.
    
    Args:
        size: Grid size (NxN)
        rng: Random number generator
        seed: Base seed for reproducibility
        attempt_idx: Generation attempt index
        
    Returns:
        BlockMask with corridor pattern
    """
    cells = set()
    
    # Vertical corridor near middle
    col = size // 2
    for row in range(1, size - 1):
        # Leave gaps every 2 rows to create chokepoints (less dense)
        if row % 2 == 0:
            cells.add((row, col))
    
    # Horizontal corridor offset (even more sparse)
    row = size // 3
    for col_i in range(1, size - 1):
        if col_i % 3 == 0:
            cells.add((row, col_i))
    
    density = len(cells) / (size * size)
    
    return BlockMask(
        grid_size=size,
        cells=cells,
        density=density,
        pattern_id="corridor",
        attempt_index=attempt_idx,
        seed=seed
    )


def generate_ring_pattern(size: int, rng: RNG, seed: int, attempt_idx: int) -> BlockMask:
    """Generate ring pattern with gated entries.
    
    Creates a minimal perimeter with strategic blocks that suggest entry points
    without creating a full ring.
    
    Args:
        size: Grid size (NxN)
        rng: Random number generator
        seed: Base seed for reproducibility
        attempt_idx: Generation attempt index
        
    Returns:
        BlockMask with ring pattern
    """
    cells = set()
    
    # Place a few strategic blocks on edges to suggest gates (4 cells max for small boards)
    # Top edge
    cells.add((1, size // 3))
    
    # Bottom edge
    cells.add((size - 2, 2 * size // 3))
    
    # Left edge
    cells.add((size // 3, 1))
    
    # Right edge
    cells.add((2 * size // 3, size - 2))
    
    density = len(cells) / (size * size)
    
    return BlockMask(
        grid_size=size,
        cells=cells,
        density=density,
        pattern_id="ring",
        attempt_index=attempt_idx,
        seed=seed
    )


def generate_spiral_pattern(size: int, rng: RNG, seed: int, attempt_idx: int) -> BlockMask:
    """Generate inward spiral pattern with periodic gaps.
    
    Creates a sparse spiral from outside to center with frequent openings
    to allow path flexibility.
    
    Args:
        size: Grid size (NxN)
        rng: Random number generator
        seed: Base seed for reproducibility
        attempt_idx: Generation attempt index
        
    Returns:
        BlockMask with spiral pattern
    """
    cells = set()
    
    # Simple sparse spiral: start from top-left, spiral inward
    # Only add cells every N steps to keep density low
    top, bottom = 0, size - 1
    left, right = 0, size - 1
    counter = 0
    step_frequency = 10  # Only add every 10th cell for very sparse pattern
    
    while top <= bottom and left <= right:
        # Top row
        for col in range(left, right + 1):
            if counter % step_frequency == 0:
                cells.add((top, col))
            counter += 1
        top += 1
        
        # Right column
        for row in range(top, bottom + 1):
            if counter % step_frequency == 0:
                cells.add((row, right))
            counter += 1
        right -= 1
        
        # Bottom row (if exists)
        if top <= bottom:
            for col in range(right, left - 1, -1):
                if counter % step_frequency == 0:
                    cells.add((bottom, col))
                counter += 1
            bottom -= 1
        
        # Left column (if exists)
        if left <= right:
            for row in range(bottom, top - 1, -1):
                if counter % step_frequency == 0:
                    cells.add((row, left))
                counter += 1
            left += 1
    
    density = len(cells) / (size * size)
    
    return BlockMask(
        grid_size=size,
        cells=cells,
        density=density,
        pattern_id="spiral",
        attempt_index=attempt_idx,
        seed=seed
    )


def generate_cross_pattern(size: int, rng: RNG, seed: int, attempt_idx: int) -> BlockMask:
    """Generate central cross/plus pattern with chokepoints.
    
    Creates a plus shape near the center with gaps that force specific
    path routing.
    
    Args:
        size: Grid size (NxN)
        rng: Random number generator
        seed: Base seed for reproducibility
        attempt_idx: Generation attempt index
        
    Returns:
        BlockMask with cross pattern
    """
    cells = set()
    
    center = size // 2
    
    # Vertical bar
    for row in range(1, size - 1):
        if row % 2 == 0:  # Gaps every other row
            cells.add((row, center))
    
    # Horizontal bar
    for col in range(1, size - 1):
        if col % 2 == 1:  # Offset gaps
            cells.add((center, col))
    
    density = len(cells) / (size * size)
    
    return BlockMask(
        grid_size=size,
        cells=cells,
        density=density,
        pattern_id="cross",
        attempt_index=attempt_idx,
        seed=seed
    )


# Pattern registry with constraints
PATTERNS = {
    "corridor": {
        "generator": generate_corridor_pattern,
        "min_size": 6,
        "max_density": 0.08,
    },
    "ring": {
        "generator": generate_ring_pattern,
        "min_size": 6,
        "max_density": 0.10,
    },
    "spiral": {
        "generator": generate_spiral_pattern,
        "min_size": 7,
        "max_density": 0.09,
    },
    "cross": {
        "generator": generate_cross_pattern,
        "min_size": 5,
        "max_density": 0.06,
    },
}


def get_pattern_generator(pattern_name: str):
    """Get pattern generator function by name.
    
    Args:
        pattern_name: Name of pattern (corridor, ring, spiral, cross)
        
    Returns:
        Generator function
        
    Raises:
        ValueError: If pattern name unknown
    """
    if pattern_name not in PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern_name}. "
                        f"Available: {', '.join(PATTERNS.keys())}")
    return PATTERNS[pattern_name]["generator"]


def get_pattern_constraints(pattern_name: str) -> dict:
    """Get size and density constraints for pattern.
    
    Args:
        pattern_name: Name of pattern
        
    Returns:
        Dict with min_size and max_density
    """
    if pattern_name not in PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern_name}")
    return {
        "min_size": PATTERNS[pattern_name]["min_size"],
        "max_density": PATTERNS[pattern_name]["max_density"],
    }
