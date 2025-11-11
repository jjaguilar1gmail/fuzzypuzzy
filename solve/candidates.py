"""Solve module: Candidates

Contains the CandidateModel for bidirectional value/position mapping used by advanced solver modes.
"""

from typing import Dict, Set
from core.position import Position
from core.puzzle import Puzzle


class CandidateModel:
    """Maintains bidirectional mappings between values and positions for efficient solver operations.
    
    This enables fast MRV (Min Remaining Values), single-position checks, and incremental updates.
    Used by logic_v1+ solver modes.
    """
    
    def __init__(self):
        # value → set of candidate positions
        self.value_to_positions: Dict[int, Set[Position]] = {}
        # position → set of candidate values  
        self.pos_to_values: Dict[Position, Set[int]] = {}
    
    def init_from(self, puzzle: Puzzle) -> None:
        """Initialize candidate mappings from current puzzle state.
        
        Args:
            puzzle: Current puzzle to analyze
        """
        self.value_to_positions.clear()
        self.pos_to_values.clear()
        
        # Find which values still need to be placed
        unplaced_values = set()
        for value in range(puzzle.constraints.min_value, puzzle.constraints.max_value + 1):
            if not self._value_exists_in_puzzle(puzzle, value):
                unplaced_values.add(value)
                self.value_to_positions[value] = set()
        
        # Find candidates for each empty cell, but only track positions 
        # that could potentially hold unplaced values
        for cell in puzzle.grid.iter_cells():
            # Skip blocked cells - they cannot hold values
            if cell.blocked:
                continue
            if cell.is_empty():
                candidates = self._compute_candidates_for_position(puzzle, cell.pos)
                # Filter to only unplaced values
                candidates = candidates.intersection(unplaced_values)
                
                # Only add position to model if it has at least one candidate
                if candidates:
                    self.pos_to_values[cell.pos] = candidates
                    
                    # Update reverse mapping
                    for value in candidates:
                        self.value_to_positions[value].add(cell.pos)
    
    def _compute_candidates_for_position(self, puzzle: Puzzle, pos: Position) -> Set[int]:
        """Compute all legal candidate values for a position."""
        candidates = set()
        
        for value in range(puzzle.constraints.min_value, puzzle.constraints.max_value + 1):
            if self._can_place_value(puzzle, pos, value):
                candidates.add(value)
        
        return candidates
    
    def _can_place_value(self, puzzle: Puzzle, pos: Position, value: int) -> bool:
        """Check if value can be legally placed at position."""
        # Check if value already exists
        if self._value_exists_in_puzzle(puzzle, value):
            return False
        
        # Check adjacency constraint
        return self._check_adjacency_constraint(puzzle, pos, value)
    
    def _value_exists_in_puzzle(self, puzzle: Puzzle, value: int) -> bool:
        """Check if value already exists in the puzzle."""
        for cell in puzzle.grid.iter_cells():
            if cell.value == value:
                return True
        return False
    
    def _check_adjacency_constraint(self, puzzle: Puzzle, pos: Position, value: int) -> bool:
        """Check adjacency constraint for placing value at position."""
        neighbors = puzzle.grid.neighbors_of(pos)
        
        prev_value = value - 1
        next_value = value + 1
        
        has_prev_neighbor = False
        has_next_neighbor = False
        
        # Check neighbors
        for neighbor_pos in neighbors:
            neighbor_cell = puzzle.grid.get_cell(neighbor_pos)
            if neighbor_cell.value == prev_value:
                has_prev_neighbor = True
            elif neighbor_cell.value == next_value:
                has_next_neighbor = True
        
        # For min value, only need next neighbor (if it exists)
        if value == puzzle.constraints.min_value:
            if self._value_exists_in_puzzle(puzzle, next_value):
                return has_next_neighbor
            else:
                return True
        
        # For max value, only need prev neighbor (if it exists)
        if value == puzzle.constraints.max_value:
            if self._value_exists_in_puzzle(puzzle, prev_value):
                return has_prev_neighbor
            else:
                return True
        
        # For middle values, check both directions
        has_prev_value = self._value_exists_in_puzzle(puzzle, prev_value)
        has_next_value = self._value_exists_in_puzzle(puzzle, next_value)
        
        if not has_prev_value and not has_next_value:
            return True
        
        if has_prev_value and not has_next_value:
            return has_prev_neighbor
        
        if has_next_value and not has_prev_value:
            return has_next_neighbor
        
        if has_prev_value and has_next_value:
            return has_prev_neighbor or has_next_neighbor
        
        return True
    
    def remove_value_from_pos(self, value: int, pos: Position) -> None:
        """Remove a value from position's candidates and update reverse mapping.
        
        Args:
            value: Value to remove
            pos: Position to remove from
        """
        if pos in self.pos_to_values:
            self.pos_to_values[pos].discard(value)
        
        if value in self.value_to_positions:
            self.value_to_positions[value].discard(pos)
    
    def remove_candidate(self, value: int, pos: Position) -> None:
        """Remove a candidate value from a position (alias for remove_value_from_pos).
        
        Args:
            value: Value to remove as candidate
            pos: Position to remove candidate from
        """
        self.remove_value_from_pos(value, pos)
    
    def assign(self, value: int, pos: Position) -> None:
        """Assign value to position and update all candidate mappings.
        
        Args:
            value: Value being assigned
            pos: Position being assigned to
        """
        # Remove all candidates for this position
        if pos in self.pos_to_values:
            old_candidates = self.pos_to_values[pos].copy()
            for old_value in old_candidates:
                if old_value in self.value_to_positions:
                    self.value_to_positions[old_value].discard(pos)
            del self.pos_to_values[pos]
        
        # Remove all positions for this value
        if value in self.value_to_positions:
            old_positions = self.value_to_positions[value].copy()
            for old_pos in old_positions:
                if old_pos in self.pos_to_values:
                    self.pos_to_values[old_pos].discard(value)
            self.value_to_positions[value].clear()
    
    def candidates_for_value(self, value: int) -> Set[Position]:
        """Get all candidate positions for a value.
        
        Args:
            value: Value to query
            
        Returns:
            Set of positions where value could be placed
        """
        return self.value_to_positions.get(value, set()).copy()
    
    def candidates_for_pos(self, pos: Position) -> Set[int]:
        """Get all candidate values for a position.
        
        Args:
            pos: Position to query
            
        Returns:
            Set of values that could be placed at position
        """
        return self.pos_to_values.get(pos, set()).copy()
    
    def single_candidate_positions(self) -> Dict[int, Position]:
        """Find values that have exactly one candidate position.
        
        Returns:
            Dict mapping value to its single candidate position
        """
        singles = {}
        for value, positions in self.value_to_positions.items():
            if len(positions) == 1:
                singles[value] = next(iter(positions))
        return singles
    
    def single_candidate_values(self) -> Dict[Position, int]:
        """Find positions that have exactly one candidate value.
        
        Returns:
            Dict mapping position to its single candidate value
        """
        singles = {}
        for pos, values in self.pos_to_values.items():
            if len(values) == 1:
                singles[pos] = next(iter(values))
        return singles
    
    def has_empty_candidates(self) -> bool:
        """Check if any position or value has zero candidates (contradiction).
        
        Returns:
            True if contradiction detected
        """
        # Check for positions with no candidates
        for pos, values in self.pos_to_values.items():
            if len(values) == 0:
                return True
        
        # Check for values with no positions
        for value, positions in self.value_to_positions.items():
            if len(positions) == 0:
                return True
        
        return False