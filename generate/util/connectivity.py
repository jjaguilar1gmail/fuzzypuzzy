"""Shared connectivity utilities for BFS and graph operations.

Used by both mask validation and repair clustering to avoid duplication.
"""
from collections import deque
from typing import List, Set, Tuple


def get_neighbor_offsets(allow_diagonal: bool) -> List[Tuple[int, int]]:
    """Get neighbor offsets based on adjacency mode.
    
    Args:
        allow_diagonal: Whether to include diagonal neighbors
        
    Returns:
        List of (row_offset, col_offset) tuples
    """
    if allow_diagonal:
        return [(-1, -1), (-1, 0), (-1, 1),
                (0, -1),          (0, 1),
                (1, -1),  (1, 0),  (1, 1)]
    else:
        return [(-1, 0), (0, -1), (0, 1), (1, 0)]


def get_neighbors(pos: Tuple[int, int], size: int, allow_diagonal: bool) -> List[Tuple[int, int]]:
    """Get adjacent positions to given position.
    
    Args:
        pos: (row, col) tuple to get neighbors for
        size: Grid size
        allow_diagonal: Whether to include diagonal neighbors
        
    Returns:
        List of adjacent (row, col) tuples within grid bounds
    """
    row, col = pos
    neighbors = []
    
    for dr, dc in get_neighbor_offsets(allow_diagonal):
        nr, nc = row + dr, col + dc
        if 0 <= nr < size and 0 <= nc < size:
            neighbors.append((nr, nc))
    
    return neighbors


def bfs_reachable(start: Tuple[int, int], 
                  valid_cells: Set[Tuple[int, int]], 
                  size: int, 
                  allow_diagonal: bool) -> Set[Tuple[int, int]]:
    """Perform BFS to find all cells reachable from start.
    
    Args:
        start: Starting (row, col) position
        valid_cells: Set of valid (not blocked) cells
        size: Grid size
        allow_diagonal: Whether diagonal adjacency counts
        
    Returns:
        Set of all cells reachable from start via valid cells
    """
    if start not in valid_cells:
        return set()
    
    visited = {start}
    queue = deque([start])
    
    while queue:
        r, c = queue.popleft()
        
        for dr, dc in get_neighbor_offsets(allow_diagonal):
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                if (nr, nc) in valid_cells and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    
    return visited


def find_connected_components(cells: Set[Tuple[int, int]], 
                              size: int, 
                              allow_diagonal: bool) -> List[Set[Tuple[int, int]]]:
    """Cluster cells into connected components based on adjacency.
    
    Args:
        cells: Set of (row, col) tuples to cluster
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
        frontier = deque([seed])
        
        # BFS to find all adjacent cells
        while frontier:
            current = frontier.popleft()
            neighbors = get_neighbors(current, size, allow_diagonal)
            
            for neighbor in neighbors:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    cluster.add(neighbor)
                    frontier.append(neighbor)
        
        clusters.append(cluster)
    
    return clusters
