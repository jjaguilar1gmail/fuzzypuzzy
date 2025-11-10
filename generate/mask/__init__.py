"""Mask generation module for puzzle blocking.

Main orchestrator for generating, validating, and applying masks.
"""
from typing import Optional, TYPE_CHECKING
from generate.mask.models import BlockMask
from generate.mask.errors import InvalidMaskError, MaskDensityExceeded
from generate.mask.patterns import get_pattern_generator, get_pattern_constraints
from generate.mask.procedural import generate_procedural_mask
from generate.mask.density import (
    should_auto_disable_mask,
    compute_density_heuristic,
    select_default_pattern
)
from generate.mask.validate import validate_mask
from generate.mask.rng import make_mask_rng

if TYPE_CHECKING:
    from generate.models import GenerationConfig


def build_mask(
    config: 'GenerationConfig',
    size: int,
    difficulty: str,
    start: tuple[int, int],
    end: tuple[int, int],
    allow_diagonal: bool = True
) -> Optional[BlockMask]:
    """Generate and validate a mask for puzzle generation.
    
    Orchestrates:
    1. Check auto-disable conditions
    2. Select pattern or use procedural
    3. Generate mask with retries
    4. Validate connectivity and constraints
    5. Return validated mask or None
    
    Args:
        config: Generation configuration
        size: Grid size
        difficulty: Difficulty level
        start: Start position (row, col)
        end: End position (row, col)
        allow_diagonal: Whether diagonal adjacency allowed
        
    Returns:
        Validated BlockMask or None if generation failed/disabled
    """
    # Check auto-disable
    if not config.mask_enabled:
        return None
    
    if should_auto_disable_mask(size, difficulty):
        return None
    
    # Determine density
    if config.mask_density is not None:
        target_density = config.mask_density
    else:
        target_density = compute_density_heuristic(size, difficulty)
    
    # Try mask generation with retries
    for attempt_idx in range(config.mask_max_attempts):
        try:
            mask = _generate_mask_attempt(
                config=config,
                size=size,
                difficulty=difficulty,
                target_density=target_density,
                attempt_idx=attempt_idx
            )
            
            # Validate mask
            validate_mask(
                mask_cells=mask.cells,
                size=size,
                start=start,
                end=end,
                allow_diagonal=allow_diagonal
            )
            
            # Success!
            return mask
            
        except (InvalidMaskError, MaskDensityExceeded) as e:
            # Retry with next attempt
            if attempt_idx == config.mask_max_attempts - 1:
                # Last attempt failed, give up
                return None
            continue
    
    return None


def _generate_mask_attempt(
    config: 'GenerationConfig',
    size: int,
    difficulty: str,
    target_density: float,
    attempt_idx: int
) -> BlockMask:
    """Single mask generation attempt.
    
    Args:
        config: Generation configuration
        size: Grid size
        difficulty: Difficulty level
        target_density: Target density fraction
        attempt_idx: Current attempt index
        
    Returns:
        BlockMask (may be invalid)
        
    Raises:
        MaskDensityExceeded: If generated mask exceeds density cap
    """
    rng = make_mask_rng(config.seed or 0, size, difficulty, attempt_idx)
    
    # Select generation mode
    if config.mask_mode == "template":
        # Use specified template
        pattern_name = config.mask_template or select_default_pattern(size, difficulty)
        
        # Check pattern constraints
        constraints = get_pattern_constraints(pattern_name)
        if size < constraints["min_size"]:
            # Fall back to procedural
            return generate_procedural_mask(
                size=size,
                target_density=target_density,
                rng=rng,
                seed=config.seed or 0,
                attempt_idx=attempt_idx
            )
        
        # Generate pattern
        generator = get_pattern_generator(pattern_name)
        mask = generator(size, rng, config.seed or 0, attempt_idx)
        
        # Check density doesn't exceed cap
        if mask.density > 0.10:
            raise MaskDensityExceeded(f"Pattern {pattern_name} density {mask.density:.3f} > 0.10")
        
        return mask
        
    elif config.mask_mode == "procedural":
        # Use procedural sampling
        return generate_procedural_mask(
            size=size,
            target_density=target_density,
            rng=rng,
            seed=config.seed or 0,
            attempt_idx=attempt_idx
        )
        
    else:  # "auto"
        # Try template first, fall back to procedural
        pattern_name = config.mask_template or select_default_pattern(size, difficulty)
        
        try:
            constraints = get_pattern_constraints(pattern_name)
            if size >= constraints["min_size"]:
                generator = get_pattern_generator(pattern_name)
                mask = generator(size, rng, config.seed or 0, attempt_idx)
                
                if mask.density <= 0.10:
                    return mask
        except Exception:
            pass
        
        # Fall back to procedural
        return generate_procedural_mask(
            size=size,
            target_density=target_density,
            rng=rng,
            seed=config.seed or 0,
            attempt_idx=attempt_idx
        )

