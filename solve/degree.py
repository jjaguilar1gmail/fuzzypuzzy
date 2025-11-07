"""Solve module: Degree

Contains degree analysis for advanced solver modes - tracks neighbor connectivity.
"""

from typing import Dict
from core.position import Position
from core.puzzle import Puzzle


class DegreeIndex:
    """Tracks the degree (number of legal neighbors) for each position."""
    
    def __init__(self):
        self.degree: Dict[Position, int] = {}
        self._is_dirty = True
    
    def build_degree_index(self, puzzle: Puzzle) -> Dict[Position, int]:
        """Build degree index for all empty positions.
        
        Args:
            puzzle: Current puzzle state
            
        Returns:
            Dict mapping position to degree (number of legal empty/reachable neighbors)
        """
        if not self._is_dirty:
            return self.degree.copy()
        
        self.degree.clear()
        
        for cell in puzzle.grid.iter_cells():
            if cell.is_empty():
                degree = self._calculate_degree(puzzle, cell.pos)
                self.degree[cell.pos] = degree
        
        self._is_dirty = False
        return self.degree.copy()
    
    def _calculate_degree(self, puzzle: Puzzle, pos: Position) -> int:
        """Calculate degree for a single position.
        
        Args:
            puzzle: Current puzzle state
            pos: Position to analyze
            
        Returns:
            Number of neighbors that are empty or could be part of a sequence
        """
        degree = 0
        neighbors = puzzle.grid.neighbors_of(pos)
        
        for neighbor_pos in neighbors:
            neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
            
            # Count empty neighbors
            if neighbor_cell.is_empty():
                degree += 1
            # Also count filled neighbors that could be part of a sequence
            elif neighbor_cell.value is not None:
                # This neighbor could potentially connect to sequences through pos
                degree += 1
        
        return degree
    
    def update_on_assign(self, puzzle: Puzzle, assigned_pos: Position, value: int) -> None:
        """Update degree index when a position is assigned.
        
        Args:
            puzzle: Current puzzle state
            assigned_pos: Position that was assigned
            value: Value that was assigned
        """
        # Remove the assigned position from degree tracking
        if assigned_pos in self.degree:
            del self.degree[assigned_pos]
        
        # Update degrees of neighbors
        neighbors = puzzle.grid.neighbors_of(assigned_pos)
        for neighbor_pos in neighbors:
            neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
            if neighbor_cell.is_empty() and neighbor_pos in self.degree:
                # Recalculate degree for this neighbor
                self.degree[neighbor_pos] = self._calculate_degree(puzzle, neighbor_pos)
    
    def get_degree(self, pos: Position) -> int:
        """Get degree for a position.
        
        Args:
            pos: Position to query
            
        Returns:
            Degree of position, or 0 if not tracked
        """
        return self.degree.get(pos, 0)
    
    def prune_by_degree(self, candidates: Dict[int, set[Position]], 
                       min_value: int, max_value: int) -> Dict[int, set[Position]]:
        """Prune candidates based on degree constraints.
        
        Middle sequence values need degree >= 2 (room to pass through).
        Endpoint values (min/max) may have degree == 1.
        
        Args:
            candidates: Current candidate mappings (value -> positions)
            min_value: Minimum value in puzzle  
            max_value: Maximum value in puzzle
            
        Returns:
            Pruned candidate mappings
        """
        pruned = {}
        
        for value, positions in candidates.items():
            pruned_positions = set()
            
            for pos in positions:
                degree = self.get_degree(pos)
                
                # Endpoints can have degree 1, middle values need degree >= 2
                if value == min_value or value == max_value:
                    # Endpoints: degree >= 1 (need at least one connection)
                    if degree >= 1:
                        pruned_positions.add(pos)
                else:
                    # Middle values: degree >= 2 (need to pass through)
                    if degree >= 2:
                        pruned_positions.add(pos)
            
            pruned[value] = pruned_positions
        
        return pruned
    
    def invalidate_cache(self) -> None:
        """Mark degree index as dirty, forcing recomputation."""
        self._is_dirty = True
        self.degree.clear()
    
    def get_low_degree_positions(self, threshold: int = 2) -> Dict[Position, int]:
        """Get positions with degree below threshold.
        
        Args:
            threshold: Minimum degree threshold
            
        Returns:
            Dict of position -> degree for positions below threshold
        """
        low_degree = {}
        for pos, degree in self.degree.items():
            if degree < threshold:
                low_degree[pos] = degree
        return low_degree
    
    def analyze_bottlenecks(self) -> list[Position]:
        """Identify potential bottleneck positions (degree == 1 in middle of puzzle).
        
        Returns:
            List of positions that could create connectivity issues
        """
        bottlenecks = []
        for pos, degree in self.degree.items():
            if degree == 1:
                # Degree 1 positions can be bottlenecks if not at puzzle edges
                # This is a simplified check - could be enhanced with edge detection
                bottlenecks.append(pos)
        return bottlenecks