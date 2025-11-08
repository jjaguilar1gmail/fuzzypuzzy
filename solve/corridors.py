"""Solve module: Corridors

Contains corridor/segment bridging functionality for logic_v2+ solver modes.
"""

from typing import Dict, Set, Tuple, List, Optional
from collections import deque
from core.position import Position
from core.puzzle import Puzzle


class CorridorMap:
    """Manages corridor feasibility analysis between placed values."""
    
    def __init__(self):
        # (start_value, end_value) -> set of positions on any valid corridor
        self.corridor_cache: Dict[Tuple[int, int], Set[Position]] = {}
        self._cache_dirty = True
    
    def corridors_between(self, puzzle: Puzzle, start_value: int, end_value: int) -> Set[Position]:
        """Find all positions that lie on valid corridors between two placed values.
        
        Args:
            puzzle: Current puzzle state
            start_value: Starting value (must be placed)
            end_value: Ending value (must be placed, > start_value)
            
        Returns:
            Set of positions that could be part of a corridor connecting start to end
        """
        if start_value >= end_value:
            return set()
        
        cache_key = (start_value, end_value)
        
        # Check cache
        if not self._cache_dirty and cache_key in self.corridor_cache:
            return self.corridor_cache[cache_key].copy()
        
        # Find positions of start and end values
        start_pos = self._find_value_position(puzzle, start_value)
        end_pos = self._find_value_position(puzzle, end_value)
        
        if start_pos is None or end_pos is None:
            return set()
        
        sequence_length = end_value - start_value - 1  # intermediate values needed
        
        if sequence_length <= 0:
            # Adjacent values, no intermediate corridor needed
            corridor_cells = set()
        else:
            # Use multi-source BFS to find all positions reachable within sequence_length steps
            corridor_cells = self._find_corridor_bfs(puzzle, start_pos, end_pos, sequence_length)
        
        # Cache result
        self.corridor_cache[cache_key] = corridor_cells
        self._cache_dirty = False  # Mark cache as clean after compute
        return corridor_cells.copy()
    
    def compute_corridor(self, start_value: int, end_value: int, puzzle: Puzzle) -> Set[Position]:
        """Public method to compute corridor between two values.
        
        Args:
            start_value: Starting value (must be placed)
            end_value: Ending value (must be placed, > start_value)
            puzzle: Current puzzle state
            
        Returns:
            Set of empty positions in the corridor
        """
        return self.corridors_between(puzzle, start_value, end_value)
    
    def _find_value_position(self, puzzle: Puzzle, value: int) -> Optional[Position]:
        """Find the position where a value is placed."""
        for cell in puzzle.grid.iter_cells():
            if cell.value == value:
                return cell.pos
        return None
    
    def _find_corridor_bfs(self, puzzle: Puzzle, start_pos: Position, end_pos: Position, 
                          max_length: int) -> Set[Position]:
        """Use dual multi-source BFS to find corridor positions via distance-sum inequality.
        
        Uses the condition: distA[p] + distB[p] <= (t-1) where t = end_value - start_value.
        This is more efficient and accurate than nested BFS.
        
        Args:
            puzzle: Current puzzle state
            start_pos: Starting position (contains start value)
            end_pos: Target position (contains end value)
            max_length: Corridor length threshold (t-1 where t is the gap)
            
        Returns:
            Set of empty positions satisfying the distance-sum inequality
        """
        if max_length <= 0:
            return set()
        
        # Get empty neighbors of anchors as frontier sources
        start_frontier = []
        for neighbor in puzzle.grid.neighbors_of(start_pos):
            cell = puzzle.grid.get_cell(neighbor)
            if cell.is_empty():
                start_frontier.append(neighbor)
        
        end_frontier = []
        for neighbor in puzzle.grid.neighbors_of(end_pos):
            cell = puzzle.grid.get_cell(neighbor)
            if cell.is_empty():
                end_frontier.append(neighbor)
        
        if not start_frontier or not end_frontier:
            return set()
        
        # Multi-source BFS from start frontier
        dist_from_start = self._multi_source_bfs(puzzle, start_frontier, max_length)
        
        # Multi-source BFS from end frontier
        dist_from_end = self._multi_source_bfs(puzzle, end_frontier, max_length)
        
        # Find corridor positions: distA + distB <= max_length (which is t-1)
        corridor_positions = set()
        for pos in dist_from_start:
            if pos in dist_from_end:
                if dist_from_start[pos] + dist_from_end[pos] <= max_length:
                    corridor_positions.add(pos)
        
        return corridor_positions
    
    def _multi_source_bfs(self, puzzle: Puzzle, sources: List[Position], 
                         max_dist: int) -> Dict[Position, int]:
        """Perform multi-source BFS to compute minimum distances from any source.
        
        Args:
            puzzle: Current puzzle state
            sources: List of starting positions
            max_dist: Maximum distance to explore
            
        Returns:
            Dictionary mapping position to minimum distance from any source
        """
        distances = {}
        queue = deque()
        
        # Initialize with all sources at distance 0
        for source in sources:
            distances[source] = 0
            queue.append((source, 0))
        
        while queue:
            pos, dist = queue.popleft()
            
            # Skip if we found a better path
            if distances[pos] < dist:
                continue
            
            # Don't explore beyond max_dist
            if dist >= max_dist:
                continue
            
            # Explore neighbors
            for neighbor in puzzle.grid.neighbors_of(pos):
                cell = puzzle.grid.get_cell(neighbor)
                
                # Only traverse empty cells
                if cell.is_empty():
                    new_dist = dist + 1
                    
                    # Update if we found a shorter path
                    if neighbor not in distances or distances[neighbor] > new_dist:
                        distances[neighbor] = new_dist
                        queue.append((neighbor, new_dist))
        
        return distances
    
    def _can_reach_in_steps(self, puzzle: Puzzle, from_pos: Position, to_pos: Position, 
                           max_steps: int) -> bool:
        """Check if to_pos is reachable from from_pos within max_steps through empty cells.
        
        Args:
            puzzle: Current puzzle state
            from_pos: Starting position
            to_pos: Target position
            max_steps: Maximum allowed steps
            
        Returns:
            True if reachable within steps
        """
        if from_pos == to_pos:
            return max_steps >= 0
        
        if max_steps <= 0:
            return False
        
        # BFS to check reachability
        queue = deque([(from_pos, 0)])
        visited = {from_pos}
        
        while queue:
            pos, dist = queue.popleft()
            
            if dist >= max_steps:
                continue
            
            for neighbor_pos in puzzle.grid.neighbors_of(pos):
                if neighbor_pos == to_pos:
                    return dist + 1 <= max_steps
                
                if neighbor_pos not in visited:
                    neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
                    
                    # Can move through empty cells or to the target
                    if neighbor_cell.is_empty():
                        visited.add(neighbor_pos)
                        queue.append((neighbor_pos, dist + 1))
        
        return False
    
    def invalidate_cache(self) -> None:
        """Mark cache as dirty, forcing recomputation."""
        self._cache_dirty = True
        self.corridor_cache.clear()
    
    def get_all_sequence_gaps(self, puzzle: Puzzle) -> List[Tuple[int, int, int]]:
        """Find all gaps between placed consecutive sequences.
        
        Returns:
            List of (start_value, end_value, gap_length) tuples
        """
        gaps = []
        placed_values = set()
        
        # Find all placed values (skip None values from blocked cells)
        for cell in puzzle.grid.iter_cells():
            if not cell.is_empty() and cell.value is not None:
                placed_values.add(cell.value)
        
        # Look for gaps
        sorted_values = sorted(placed_values)
        
        for i in range(len(sorted_values) - 1):
            current_val = sorted_values[i]
            next_val = sorted_values[i + 1]
            
            gap_length = next_val - current_val - 1
            if gap_length > 0:
                gaps.append((current_val, next_val, gap_length))
        
        return gaps
    
    def prune_candidates_by_corridors(self, puzzle: Puzzle, candidates: Dict[int, Set[Position]]) -> Dict[int, Set[Position]]:
        """Prune candidate positions that don't lie on valid corridors for sequence gaps.
        
        Args:
            puzzle: Current puzzle state
            candidates: Current candidate mappings (value -> positions)
            
        Returns:
            Pruned candidate mappings
        """
        pruned = {value: positions.copy() for value, positions in candidates.items()}
        
        # Get all sequence gaps
        gaps = self.get_all_sequence_gaps(puzzle)
        
        for start_value, end_value, gap_length in gaps:
            # Find corridor positions
            corridor_positions = self.corridors_between(puzzle, start_value, end_value)
            
            # Prune candidates for intermediate values
            for intermediate_val in range(start_value + 1, end_value):
                if intermediate_val in pruned:
                    # Keep only positions that are on valid corridors
                    pruned[intermediate_val] &= corridor_positions
        
        return pruned