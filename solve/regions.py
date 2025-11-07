"""Solve module: Regions

Contains region segmentation for advanced solver modes with 4/8-way adjacency support.
"""

from typing import Dict, Set, List, Tuple, Literal
from core.position import Position
from core.puzzle import Puzzle
from core.grid import Grid


class EmptyRegion:
    """Represents a contiguous cluster of empty cells."""
    
    def __init__(self, region_id: int, cells: Set[Position], adjacency: Literal[4, 8]):
        self.id = region_id
        self.cells = cells
        self.size = len(cells)
        self.adjacency = adjacency
        self.boundary_values: Set[int] = set()
    
    def update_boundary_values(self, puzzle: Puzzle) -> None:
        """Update the set of known values adjacent to this region."""
        self.boundary_values.clear()
        
        for pos in self.cells:
            # Get neighbors based on adjacency rule
            if self.adjacency == 8:
                neighbors = puzzle.grid.neighbors_of(pos)  # 8-way (includes diagonals)
            else:
                neighbors = self._get_4way_neighbors(puzzle.grid, pos)  # 4-way only
            
            for neighbor_pos in neighbors:
                neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
                if neighbor_cell.value is not None:
                    self.boundary_values.add(neighbor_cell.value)
    
    def _get_4way_neighbors(self, grid: Grid, pos: Position) -> List[Position]:
        """Get 4-way (cardinal) neighbors only."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        
        for dr, dc in directions:
            new_row = pos.row + dr
            new_col = pos.col + dc
            if 0 <= new_row < grid.rows and 0 <= new_col < grid.cols:
                neighbors.append(Position(new_row, new_col))
        
        return neighbors


class RegionCache:
    """Manages region computation with incremental updates and caching."""
    
    def __init__(self):
        self.regions: List[EmptyRegion] = []
        self.pos_to_region: Dict[Position, int] = {}  # position -> region_id
        self._is_dirty = True
        self._last_puzzle_hash: int = 0
    
    def build_regions(self, puzzle: Puzzle) -> List[EmptyRegion]:
        """Build contiguous empty regions using puzzle's adjacency rule.
        
        Args:
            puzzle: Current puzzle state
            
        Returns:
            List of EmptyRegion objects
        """
        # Check if we need to rebuild
        current_hash = self._compute_puzzle_hash(puzzle)
        if not self._is_dirty and current_hash == self._last_puzzle_hash:
            return self.regions
        
        # Determine adjacency rule from puzzle constraints
        adjacency = 8 if puzzle.constraints.allow_diagonal else 4
        
        # Clear cache
        self.regions.clear()
        self.pos_to_region.clear()
        
        # Find all empty positions
        empty_positions = set()
        for cell in puzzle.grid.iter_cells():
            if cell.is_empty():
                empty_positions.add(cell.pos)
        
        # Build regions via flood fill
        visited = set()
        region_id = 0
        
        for pos in empty_positions:
            if pos not in visited:
                # Start new region
                region_cells = self._flood_fill(puzzle, pos, empty_positions, visited, adjacency)
                if region_cells:
                    region = EmptyRegion(region_id, region_cells, adjacency)
                    region.update_boundary_values(puzzle)
                    self.regions.append(region)
                    
                    # Update position mapping
                    for cell_pos in region_cells:
                        self.pos_to_region[cell_pos] = region_id
                    
                    region_id += 1
        
        # Update cache state
        self._is_dirty = False
        self._last_puzzle_hash = current_hash
        
        return self.regions
    
    def _flood_fill(self, puzzle: Puzzle, start_pos: Position, empty_positions: Set[Position], 
                   visited: Set[Position], adjacency: Literal[4, 8]) -> Set[Position]:
        """Flood fill to find connected empty region."""
        region_cells = set()
        stack = [start_pos]
        
        while stack:
            pos = stack.pop()
            if pos in visited or pos not in empty_positions:
                continue
            
            visited.add(pos)
            region_cells.add(pos)
            
            # Add neighbors based on adjacency rule
            if adjacency == 8:
                neighbors = puzzle.grid.neighbors_of(pos)  # 8-way
            else:
                neighbors = self._get_4way_neighbors(puzzle.grid, pos)  # 4-way
            
            for neighbor_pos in neighbors:
                if neighbor_pos not in visited and neighbor_pos in empty_positions:
                    stack.append(neighbor_pos)
        
        return region_cells
    
    def _get_4way_neighbors(self, grid: Grid, pos: Position) -> List[Position]:
        """Get 4-way (cardinal) neighbors only."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dr, dc in directions:
            new_row = pos.row + dr
            new_col = pos.col + dc
            if 0 <= new_row < grid.rows and 0 <= new_col < grid.cols:
                neighbors.append(Position(new_row, new_col))
        
        return neighbors
    
    def _compute_puzzle_hash(self, puzzle: Puzzle) -> int:
        """Compute hash of puzzle state for cache invalidation."""
        filled_positions = []
        for cell in puzzle.grid.iter_cells():
            if not cell.is_empty():
                filled_positions.append((cell.pos.row, cell.pos.col, cell.value))
        
        return hash(tuple(sorted(filled_positions)))
    
    def update_on_assign(self, pos: Position, value: int) -> None:
        """Mark cache as dirty when a position is assigned.
        
        Args:
            pos: Position that was assigned
            value: Value that was assigned
        """
        self._is_dirty = True
    
    def get_region_for_position(self, pos: Position) -> int | None:
        """Get region ID for a position.
        
        Args:
            pos: Position to query
            
        Returns:
            Region ID or None if position not in any region
        """
        return self.pos_to_region.get(pos)
    
    def can_fit_sequence_length(self, region: EmptyRegion, sequence_length: int) -> bool:
        """Check if region can accommodate a sequence of given length.
        
        Args:
            region: Region to check
            sequence_length: Required sequence length
            
        Returns:
            True if region is large enough
        """
        return region.size >= sequence_length
    
    def would_split_regions(self, puzzle: Puzzle, pos: Position, remaining_values: Set[int]) -> bool:
        """Check if placing a value at position would split empty regions problematically.
        
        Args:
            puzzle: Current puzzle state
            pos: Position being considered
            remaining_values: Set of values still to be placed
            
        Returns:
            True if placement would create disconnected regions too small for remaining sequence
        """
        if len(remaining_values) <= 1:
            return False  # No splitting concern for last value
        
        # This is a simplified check - full implementation would:
        # 1. Temporarily "place" value at pos
        # 2. Recompute regions 
        # 3. Check if any resulting region is too small for remaining sequences
        # For now, return False (no splitting detected)
        return False