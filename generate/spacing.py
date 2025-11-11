"""
Spacing heuristics and clue distribution metrics.

Constitution compliance: pure computation, no I/O.
"""
from typing import List, Tuple


def avg_manhattan_distance(clues: List[Tuple[int, int]]) -> float:
    """
    Calculate average Manhattan distance between all pairs of clues.
    
    Args:
        clues: List of (row, col) positions
        
    Returns:
        Average Manhattan distance
    """
    if len(clues) < 2:
        return 0.0
    
    total = 0.0
    count = 0
    for i, (r1, c1) in enumerate(clues):
        for r2, c2 in clues[i + 1:]:
            total += abs(r1 - r2) + abs(c1 - c2)
            count += 1
    
    return total / count if count > 0 else 0.0


def quadrant_variance(clues: List[Tuple[int, int]], size: int) -> float:
    """
    Calculate variance in clue distribution across quadrants.
    
    Args:
        clues: List of (row, col) positions
        size: Board dimension
        
    Returns:
        Normalized variance (0-1 scale)
    """
    if not clues:
        return 0.0
    
    # Divide board into 4 quadrants
    mid = size // 2
    quadrants = [0, 0, 0, 0]  # TL, TR, BL, BR
    
    for r, c in clues:
        if r < mid and c < mid:
            quadrants[0] += 1  # Top-left
        elif r < mid and c >= mid:
            quadrants[1] += 1  # Top-right
        elif r >= mid and c < mid:
            quadrants[2] += 1  # Bottom-left
        else:
            quadrants[3] += 1  # Bottom-right
    
    # Calculate variance
    mean = len(clues) / 4.0
    variance = sum((q - mean) ** 2 for q in quadrants) / 4.0
    
    # Normalize to 0-1 scale (max variance is when all clues in one quadrant)
    max_variance = (len(clues) - mean) ** 2 + 3 * (mean ** 2)
    max_variance /= 4.0
    
    return variance / max_variance if max_variance > 0 else 0.0


def detect_clusters(clues: List[Tuple[int, int]], max_distance: int = 2) -> List[List[Tuple[int, int]]]:
    """
    Detect clusters of clues using 8-neighbor connectivity.
    
    Args:
        clues: List of (row, col) positions
        max_distance: Maximum distance for cluster membership (unused, kept for compatibility)
        
    Returns:
        List of clusters (each cluster is a list of positions)
    """
    if not clues:
        return []
    
    clue_set = set(clues)
    visited = set()
    clusters = []
    
    def get_8_neighbors(pos):
        """Get 8-connected neighbors of a position."""
        r, c = pos
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                neighbors.append((r + dr, c + dc))
        return neighbors
    
    def bfs_cluster(start):
        """BFS to find all clues in same cluster."""
        cluster = [start]
        queue = [start]
        visited.add(start)
        
        while queue:
            current = queue.pop(0)
            for neighbor in get_8_neighbors(current):
                if neighbor in clue_set and neighbor not in visited:
                    visited.add(neighbor)
                    cluster.append(neighbor)
                    queue.append(neighbor)
        
        return cluster
    
    # Find all clusters
    for clue in clues:
        if clue not in visited:
            cluster = bfs_cluster(clue)
            clusters.append(cluster)
    
    return clusters


def spacing_score(clues: List[Tuple[int, int]], size: int, w1: float = 1.0, w2: float = 0.5) -> float:
    """
    Combined spacing score for candidate selection.
    
    Score = w1 * avg_distance - w2 * variance
    
    Args:
        clues: List of (row, col) positions
        size: Board dimension
        w1: Weight for average distance
        w2: Weight for quadrant variance
        
    Returns:
        Combined spacing score (higher is better)
    """
    avg_dist = avg_manhattan_distance(clues)
    variance = quadrant_variance(clues, size)
    return w1 * avg_dist - w2 * variance
