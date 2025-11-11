"""Solution diffing and divergence clustering for ambiguity detection.

T032: Implements diff_solutions() to identify ambiguity regions from multiple solutions.
"""
from typing import List, Tuple
from core.position import Position
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
    
    # Cluster adjacent divergences into regions
    regions = _cluster_cells(divergent_cells, size, allow_diagonal)
    
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
    
    # Cluster divergent cells
    divergent_cells = set(divergence_count_map.keys())
    clusters = _cluster_cells(divergent_cells, size, allow_diagonal)
    
    # Create regions with aggregated frequencies
    regions = []
    for cluster in clusters:
        # Max frequency for any cell in cluster
        max_freq = max(divergence_count_map[cell] for cell in cluster)
        regions.append(AmbiguityRegion(cells=cluster, divergence_count=max_freq))
    
    return regions


def _cluster_cells(cells: set, size: int, allow_diagonal: bool) -> List[set]:
    """Cluster cells into connected components based on adjacency.
    
    Args:
        cells: Set of (row, col) tuples
        size: Grid size
        allow_diagonal: Whether diagonal adjacency counts
        
    Returns:
        List of cell clusters (each cluster is a set of tuples)
    """
    if not cells:
        return []
    
    clusters = []
    remaining = set(cells)
    
    while remaining:
        # Start new cluster with arbitrary cell
        seed = remaining.pop()
        cluster = {seed}
        frontier = [seed]
        
        # BFS to find all adjacent cells
        while frontier:
            current = frontier.pop(0)
            neighbors = _get_neighbors(current, size, allow_diagonal)
            
            for neighbor in neighbors:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    cluster.add(neighbor)
                    frontier.append(neighbor)
        
        clusters.append(cluster)
    
    return clusters


def _get_neighbors(pos: Tuple[int, int], size: int, allow_diagonal: bool) -> List[Tuple[int, int]]:
    """Get adjacent positions to given position.
    
    Args:
        pos: (row, col) tuple to get neighbors for
        size: Grid size
        allow_diagonal: Whether to include diagonal neighbors
        
    Returns:
        List of adjacent (row, col) tuples
    """
    neighbors = []
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Orthogonal
    
    if allow_diagonal:
        deltas += [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonal
    
    for dr, dc in deltas:
        r, c = pos[0] + dr, pos[1] + dc
        if 0 <= r < size and 0 <= c < size:
            neighbors.append((r, c))
    
    return neighbors
