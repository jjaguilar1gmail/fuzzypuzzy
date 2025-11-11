"""Structural block candidate scoring for ambiguity repair.

T033: Scores candidate blocking positions based on frequency × corridor_width × distance.
"""
from typing import List, Tuple, Set
from dataclasses import dataclass
from core.position import Position
from core.grid import Grid
from generate.repair.models import AmbiguityRegion


@dataclass
class ScoredCandidate:
    """Candidate blocking position with score."""
    position: Position
    score: float
    frequency: int
    corridor_width: float
    distance_from_givens: float


def score_structural_blocks(regions: List[AmbiguityRegion],
                            grid: Grid,
                            givens: List[Position]) -> List[ScoredCandidate]:
    """Score candidate blocking positions to resolve ambiguity.
    
    Args:
        regions: List of ambiguity regions
        grid: Current grid state
        givens: List of given (clue) positions
        
    Returns:
        List of scored candidates sorted by score (highest first)
    """
    if not regions:
        return []
    
    candidates = []
    
    for region in regions:
        # Get candidate positions adjacent to region
        candidate_positions = _get_adjacent_candidates(region.cells, grid, givens)
        
        for pos in candidate_positions:
            # Calculate score components
            frequency_score = region.divergence_count
            corridor_score = _calculate_corridor_width_score(pos, grid)
            distance_score = _calculate_distance_score(pos, givens, grid.rows)
            
            # Combined score: frequency × corridor_width × distance
            total_score = frequency_score * corridor_score * distance_score
            
            candidates.append(ScoredCandidate(
                position=pos,
                score=total_score,
                frequency=frequency_score,
                corridor_width=corridor_score,
                distance_from_givens=distance_score
            ))
    
    # Sort by score (highest first)
    candidates.sort(key=lambda c: c.score, reverse=True)
    
    return candidates


def _get_adjacent_candidates(region_cells: set,
                             grid: Grid,
                             givens: List[Position]) -> List[Position]:
    """Get candidate positions adjacent to ambiguity region.
    
    Args:
        region_cells: Set of (row, col) tuples in ambiguity region
        grid: Current grid
        givens: Given positions (to exclude)
        
    Returns:
        List of candidate Position objects (unblocked, not givens, adjacent to region)
    """
    candidates = set()
    given_tuples = {(g.row, g.col) for g in givens}
    
    for cell in region_cells:
        # Get all neighbors
        neighbors = _get_neighbors(cell, grid.rows, grid.adjacency.allow_diagonal)
        
        for neighbor in neighbors:
            # Exclude blocked cells, givens, and cells already in region
            neighbor_tuple = (neighbor.row, neighbor.col)
            cell = grid.get_cell(neighbor)
            if (not cell.blocked and
                neighbor_tuple not in given_tuples and
                neighbor_tuple not in region_cells):
                candidates.add(neighbor)
    
    return list(candidates)


def _calculate_corridor_width_score(pos: Position, grid: Grid) -> float:
    """Calculate corridor width score (narrower = higher score).
    
    Args:
        pos: Position to score
        grid: Current grid
        
    Returns:
        Score based on available exits (fewer exits = higher score)
    """
    # Count available (unblocked) neighbors
    neighbors = _get_neighbors((pos.row, pos.col), grid.rows, grid.adjacency.allow_diagonal)
    available_neighbors = sum(
        1 for n in neighbors 
        if not grid.get_cell(n).blocked
    )
    
    # Narrower corridor (fewer neighbors) = higher score
    # Use inverse: max_neighbors / (available + 1)
    max_neighbors = 8 if grid.adjacency.allow_diagonal else 4
    score = max_neighbors / (available_neighbors + 1)
    
    return score


def _calculate_distance_score(pos: Position, 
                              givens: List[Position], 
                              grid_size: int) -> float:
    """Calculate distance from givens score (farther = higher score).
    
    Args:
        pos: Position to score
        givens: Given positions
        grid_size: Grid size (rows, assuming square)
        
    Returns:
        Score based on distance from nearest given (farther = higher)
    """
    if not givens:
        return 1.0  # No givens, all positions equally far
    
    # Find minimum Manhattan distance to any given
    min_distance = min(
        abs(pos.row - g.row) + abs(pos.col - g.col)
        for g in givens
    )
    
    # Normalize by grid size and add 1 to avoid zero
    max_distance = 2 * (grid_size - 1)  # Maximum possible Manhattan distance
    normalized = (min_distance + 1) / (max_distance + 1)
    
    return normalized


def _get_neighbors(pos: Tuple[int, int], size: int, allow_diagonal: bool) -> List[Position]:
    """Get adjacent positions."""
    neighbors = []
    deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    if allow_diagonal:
        deltas += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for dr, dc in deltas:
        r, c = pos[0] + dr, pos[1] + dc
        if 0 <= r < size and 0 <= c < size:
            neighbors.append(Position(r, c))
    
    return neighbors
