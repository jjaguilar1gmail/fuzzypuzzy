"""Generate module: Removal

Removal scoring and heuristics for clue removal during generation.
"""


def score_candidates(givens, path, anchors, grid):
    """Score removable clue candidates.
    
    Scores based on:
    - Distance from nearest anchor (higher score = further from anchors)
    - Local redundancy (number of alternative adjacency paths)
    - Inverse strategic value (avoid removing corridor bottlenecks)
    
    Args:
        givens: Set of current given positions
        path: Full solution path (list of positions)
        anchors: Set of anchor positions (must keep)
        grid: Grid object
        
    Returns:
        List of (position, score) tuples, sorted by score descending
    """
    from core.position import Position
    
    candidates = []
    
    for pos in givens:
        # Don't score anchors
        if pos in anchors:
            continue
        
        score = 0.0
        
        # 1. Distance from nearest anchor (0-1 normalized)
        min_distance = float('inf')
        for anchor in anchors:
            dist = abs(pos.row - anchor.row) + abs(pos.col - anchor.col)
            min_distance = min(min_distance, dist)
        if min_distance != float('inf'):
            max_dist = grid.rows + grid.cols
            score += (min_distance / max_dist) * 0.4
        
        # 2. Local redundancy (count neighbor givens)
        neighbor_givens = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = pos.row + dr, pos.col + dc
                if 0 <= r < grid.rows and 0 <= c < grid.cols:
                    neighbor_pos = Position(r, c)
                    if neighbor_pos in givens:
                        neighbor_givens += 1
        
        # More neighbor givens = higher redundancy = higher removal score
        score += (neighbor_givens / 8.0) * 0.3
        
        # 3. Inverse strategic value (prefer non-corridor cells)
        # For now, simple: cells with many total neighbors are less critical
        total_neighbors = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = pos.row + dr, pos.col + dc
                if 0 <= r < grid.rows and 0 <= c < grid.cols:
                    total_neighbors += 1
        
        score += (total_neighbors / 8.0) * 0.3
        
        candidates.append((pos, score))
    
    # Sort by score descending (highest score = best removal candidate)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates
