"""Procedural mask sampling based on density ratio.

Generates masks by biased random sampling with sparsity constraints.
"""
from generate.mask.models import BlockMask
from util.rng import RNG


def generate_procedural_mask(
    size: int,
    target_density: float,
    rng: RNG,
    seed: int,
    attempt_idx: int,
    edge_bias: float = 0.6
) -> BlockMask:
    """Generate mask via biased random sampling.
    
    Samples cells with bias toward edges/center (configurable) while
    avoiding dense 2x2 blocks that look unnatural.
    
    Args:
        size: Grid size (NxN)
        target_density: Target fraction of cells to block (0.0-0.10)
        rng: Random number generator
        seed: Base seed for reproducibility
        attempt_idx: Generation attempt index
        edge_bias: Bias factor for edge cells (0.0 = uniform, 1.0 = strong edge bias)
        
    Returns:
        BlockMask with procedurally sampled cells
    """
    cells = set()
    total_cells = size * size
    target_count = int(total_cells * target_density)
    
    # Build candidate list with bias weights
    candidates = []
    for row in range(size):
        for col in range(size):
            # Skip corners and edges initially (path endpoints likely there)
            if (row == 0 or row == size - 1) and (col == 0 or col == size - 1):
                continue
            
            # Calculate weight based on distance from edges
            dist_from_edge = min(row, col, size - 1 - row, size - 1 - col)
            
            # Higher weight = more likely to sample
            # edge_bias > 0.5 → favor edges
            # edge_bias < 0.5 → favor center
            if edge_bias >= 0.5:
                weight = 1.0 + edge_bias * (size - dist_from_edge)
            else:
                weight = 1.0 + (1.0 - edge_bias) * dist_from_edge
            
            candidates.append(((row, col), weight))
    
    # Weighted sampling without replacement
    sampled = 0
    while sampled < target_count and candidates:
        # Weighted random choice
        total_weight = sum(w for _, w in candidates)
        r = rng.random() * total_weight
        
        cumulative = 0.0
        selected_idx = 0
        for idx, (pos, weight) in enumerate(candidates):
            cumulative += weight
            if r <= cumulative:
                selected_idx = idx
                break
        
        cell, _ = candidates.pop(selected_idx)
        
        # Check sparsity constraint (no dense 2x2 blocks)
        if _would_create_dense_block(cell, cells, size):
            continue
        
        cells.add(cell)
        sampled += 1
    
    density = len(cells) / total_cells
    
    return BlockMask(
        grid_size=size,
        cells=cells,
        density=density,
        pattern_id=f"procedural:v1",
        attempt_index=attempt_idx,
        seed=seed
    )


def _would_create_dense_block(cell: tuple[int, int], 
                              existing: set[tuple[int, int]],
                              size: int) -> bool:
    """Check if adding cell would create a solid 2x2 block.
    
    Args:
        cell: Candidate cell (row, col)
        existing: Already blocked cells
        size: Grid size
        
    Returns:
        True if adding this cell creates a 2x2 solid block
    """
    row, col = cell
    
    # Check all possible 2x2 blocks that include this cell
    # Top-left corner of 2x2
    for dr in [-1, 0]:
        for dc in [-1, 0]:
            r0, c0 = row + dr, col + dc
            
            # Check if this 2x2 is in bounds
            if r0 < 0 or c0 < 0 or r0 + 1 >= size or c0 + 1 >= size:
                continue
            
            # Check if all 4 cells would be blocked (including candidate)
            block_cells = {
                (r0, c0), (r0, c0 + 1),
                (r0 + 1, c0), (r0 + 1, c0 + 1)
            }
            
            # Count how many are already blocked + candidate
            blocked_count = sum(1 for bc in block_cells if bc in existing or bc == cell)
            
            if blocked_count == 4:
                return True
    
    return False
