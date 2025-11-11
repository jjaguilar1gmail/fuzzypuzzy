"""Solution diffing and divergence clustering for ambiguity detection.

T032: Implements diff_solutions() to identify ambiguity regions from multiple solutions.
"""
from typing import List, Tuple
from core.position import Position
from generate.util.connectivity import find_connected_components, get_neighbors
from generate.repair.models import AmbiguityRegion


def diff_solutions(solution1: List[Tuple[int, int, int]], 
                   solution2: List[Tuple[int, int, int]], 
                   size: int,
                   allow_diagonal: bool = True) -> List[AmbiguityRegion]:
    """Diff two solutions and cluster divergences into ambiguity regions.
    
    Args:
        solution1: First solution as list of (row, col, value)
        solution2: Second solution as list of (row, col, value)
        size: Grid size
        allow_diagonal: Whether to consider diagonal adjacency for clustering
        
    Returns:
        List of AmbiguityRegion objects representing clustered divergences
    """
    # Build value maps
    val_map1 = {(r, c): v for r, c, v in solution1}
    val_map2 = {(r, c): v for r, c, v in solution2}
    
    # Find divergent cells
    divergent_cells = set()
    all_positions = set(val_map1.keys()) | set(val_map2.keys())
    
    for pos in all_positions:
        val1 = val_map1.get(pos)
        val2 = val_map2.get(pos)
        if val1 != val2:
            divergent_cells.add(pos)  # Keep as tuple
    
    if not divergent_cells:
        return []
    
    # Cluster adjacent divergences into regions using shared utility
    regions = find_connected_components(divergent_cells, size, allow_diagonal)
    
    # Create AmbiguityRegion objects (divergence_count=2 for two solutions)
    return [AmbiguityRegion(cells=cells, divergence_count=2) for cells in regions]


def diff_multiple_solutions(solutions: List[List[Tuple[int, int, int]]], 
                           size: int,
                           allow_diagonal: bool = True) -> List[AmbiguityRegion]:
    """Diff multiple solutions and aggregate divergence frequencies.
    
    Args:
        solutions: List of solutions
        size: Grid size
        allow_diagonal: Whether to consider diagonal adjacency
        
    Returns:
        List of AmbiguityRegion objects with aggregated frequencies
    """
    if len(solutions) < 2:
        return []
    
    # Track divergence frequency per position
    divergence_count_map = {}
    
    # Compare all pairs of solutions
    for i in range(len(solutions)):
        for j in range(i + 1, len(solutions)):
            val_map_i = {(r, c): v for r, c, v in solutions[i]}
            val_map_j = {(r, c): v for r, c, v in solutions[j]}
            
            all_pos = set(val_map_i.keys()) | set(val_map_j.keys())
            for pos in all_pos:
                if val_map_i.get(pos) != val_map_j.get(pos):
                    divergence_count_map[pos] = divergence_count_map.get(pos, 0) + 1
    
    if not divergence_count_map:
        return []
    
    # Cluster divergent cells using shared utility
    divergent_cells = set(divergence_count_map.keys())
    clusters = find_connected_components(divergent_cells, size, allow_diagonal)
    
    # Create regions with aggregated frequencies
    regions = []
    for cluster in clusters:
        # Max frequency for any cell in cluster
        max_freq = max(divergence_count_map[cell] for cell in cluster)
        regions.append(AmbiguityRegion(cells=cluster, divergence_count=max_freq))
    
    return regions

