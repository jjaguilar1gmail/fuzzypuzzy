"""Generate module: Removal

Removal scoring and heuristics for clue removal during generation.
"""


def score_candidates(givens, path, anchors, grid, enable_spacing=False):
    """Score removable clue candidates.
    
    Scores based on:
    - Distance from nearest anchor (higher score = further from anchors)
    - Local redundancy (number of alternative adjacency paths)
    - Inverse strategic value (avoid removing corridor bottlenecks)
    - Spacing impact (T018: US2 - optional spacing score)
    
    Args:
        givens: Set of current given positions
        path: Full solution path (list of positions)
        anchors: Set of anchor positions (must keep)
        grid: Grid object
        enable_spacing: Enable spacing score calculation (T018)
        
    Returns:
        List of (position, score) tuples, sorted by score descending
    """
    from core.position import Position
    
    # T018: Compute baseline spacing if enabled
    baseline_spacing = 0.0
    if enable_spacing:
        from .spacing import spacing_score
        clues = [(pos.row, pos.col) for pos in givens]
        baseline_spacing = spacing_score(clues, grid.rows)
    
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
        
        # 4. T018: Spacing improvement (optional)
        if enable_spacing:
            # Calculate spacing after removing this clue
            test_givens = givens - {pos}
            test_clues = [(p.row, p.col) for p in test_givens]
            test_spacing = spacing_score(test_clues, grid.rows)
            # Positive delta = removing improves spacing
            spacing_delta = test_spacing - baseline_spacing
            score += spacing_delta * 0.2  # Weight spacing contribution
        
        candidates.append((pos, score))
    
    # Sort by score descending (highest score = best removal candidate)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates
