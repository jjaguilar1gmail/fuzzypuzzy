"""Move validation logic for Hidato puzzles."""

from core.position import Position
from core.puzzle import Puzzle

class MoveValidator:
    """Validates moves in Hidato puzzles using core constraints and adjacency rules."""
    
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.grid = puzzle.grid
        self.constraints = puzzle.constraints
    
    def validate_move(self, row: int, col: int, value: int) -> tuple[bool, str]:
        """Validate a proposed move.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
            If valid, error_message is empty string.
        """
        pos = Position(row, col)
        
        # Check bounds
        if not self.constraints.in_bounds(pos, self.grid.rows, self.grid.cols):
            return False, f"Position ({row}, {col}) is out of bounds"
        
        cell = self.grid.get_cell(pos)
        
        # Check if cell is blocked
        if cell.blocked:
            return False, f"Cannot place value in blocked cell at ({row}, {col})"
        
        # Check if trying to overwrite a given
        if cell.given:
            return False, f"Cannot overwrite given value {cell.value} at ({row}, {col})"
        
        # Check if value is in valid range
        if not self.constraints.valid_value(value):
            return False, f"Value {value} is not in valid range [{self.constraints.min_value}, {self.constraints.max_value}]"
        
        # Check for duplicate values in the grid
        for other_cell in self.grid.iter_cells():
            if other_cell.pos != pos and other_cell.value == value:
                return False, f"Value {value} already exists at ({other_cell.pos.row}, {other_cell.pos.col})"
        
        # Check adjacency constraint (consecutive numbers must be adjacent)
        if not self._check_adjacency_constraint(pos, value):
            return False, f"Value {value} at ({row}, {col}) violates adjacency constraint"
        
        return True, ""
    
    def _check_adjacency_constraint(self, pos: Position, value: int) -> bool:
        """Check that placing value at pos maintains adjacency constraint.
        
        For Hidato, consecutive numbers must be adjacent on the grid.
        """
        neighbors = self.grid.neighbors_of(pos)
        
        # Find cells with values value-1 and value+1
        prev_value = value - 1
        next_value = value + 1
        
        has_prev_neighbor = False
        has_next_neighbor = False
        
        # Check if we have required neighbors
        for neighbor_pos in neighbors:
            neighbor_cell = self.grid.get_cell(neighbor_pos)
            if neighbor_cell.value == prev_value:
                has_prev_neighbor = True
            elif neighbor_cell.value == next_value:
                has_next_neighbor = True
        
        # For value 1, we only need next neighbor (if 2 exists)
        if value == self.constraints.min_value:
            # Check if value 2 exists anywhere
            has_value_2 = any(cell.value == 2 for cell in self.grid.iter_cells())
            if has_value_2:
                return has_next_neighbor
            else:
                return True  # No constraint if 2 doesn't exist yet
        
        # For max value, we only need prev neighbor (if max-1 exists)
        if value == self.constraints.max_value:
            # Check if value max-1 exists anywhere
            has_prev_value = any(cell.value == prev_value for cell in self.grid.iter_cells())
            if has_prev_value:
                return has_prev_neighbor
            else:
                return True  # No constraint if max-1 doesn't exist yet
        
        # For middle values, check both directions
        has_prev_value = any(cell.value == prev_value for cell in self.grid.iter_cells())
        has_next_value = any(cell.value == next_value for cell in self.grid.iter_cells())
        
        # If neither neighbor value exists, move is valid
        if not has_prev_value and not has_next_value:
            return True
        
        # If only one neighbor value exists, we need that neighbor
        if has_prev_value and not has_next_value:
            return has_prev_neighbor
        if has_next_value and not has_prev_value:
            return has_next_neighbor
        
        # If both neighbor values exist, we need at least one neighbor
        if has_prev_value and has_next_value:
            return has_prev_neighbor or has_next_neighbor
        
        return True
    
    def apply_move(self, row: int, col: int, value: int) -> bool:
        """Apply a move if it's valid.
        
        Returns:
            bool: True if move was applied, False if invalid
        """
        is_valid, _ = self.validate_move(row, col, value)
        if is_valid:
            pos = Position(row, col)
            self.grid.set_cell_value(pos, value)
            return True
        return False