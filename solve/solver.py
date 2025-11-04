"""Solve module: Solver

Contains the Solver class for deterministic solving algorithms.
"""
import copy
from core.position import Position
from core.puzzle import Puzzle

class SolverStep:
    """Represents a single solving step with explanation."""
    
    def __init__(self, position: Position, value: int, reason: str):
        self.position = position
        self.value = value
        self.reason = reason
    
    def __str__(self):
        return f"Place {self.value} at ({self.position.row + 1}, {self.position.col + 1}): {self.reason}"

class SolverResult:
    """Contains the result of a solving attempt."""
    
    def __init__(self, solved: bool, steps: list[SolverStep], message: str = ""):
        self.solved = solved
        self.steps = steps
        self.message = message

class Solver:
    """Deterministic solver for Hidato puzzles using consecutive logic."""
    
    def __init__(self, puzzle: Puzzle):
        self.original_puzzle = puzzle
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
    
    @staticmethod
    def solve(puzzle: Puzzle, mode: str = "logic_v0") -> SolverResult:
        """Solve a puzzle using the specified mode.
        
        Args:
            puzzle: The puzzle to solve
            mode: Solving mode ("logic_v0" for consecutive logic)
            
        Returns:
            SolverResult containing success status and steps
        """
        if mode == "logic_v0":
            solver = Solver(puzzle)
            return solver._solve_logic_v0()
        else:
            raise ValueError(f"Unsupported solving mode: {mode}")
    
    def _solve_logic_v0(self) -> SolverResult:
        """Solve using consecutive logic (no guessing).
        
        Strategy:
        1. Find cells that can only hold one value (forced moves)
        2. Find values that can only go in one cell (unique positions)
        3. Repeat until no more progress or solved
        """
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            # Strategy 1: Find forced moves (cells with only one possible value)
            for cell in self.puzzle.grid.iter_cells():
                if cell.is_empty():
                    possible_values = self._get_possible_values(cell.pos)
                    if len(possible_values) == 1:
                        value = list(possible_values)[0]
                        self._place_value(cell.pos, value, "Only possible value for this cell")
                        progress_made = True
            
            # Strategy 2: Find unique positions (values with only one possible cell)
            for value in range(self.puzzle.constraints.min_value, self.puzzle.constraints.max_value + 1):
                if not self._value_exists(value):
                    possible_positions = self._get_possible_positions(value)
                    if len(possible_positions) == 1:
                        pos = list(possible_positions)[0]
                        self._place_value(pos, value, "Only possible position for this value")
                        progress_made = True
            
            # Check if solved
            if self._is_solved():
                return SolverResult(True, self.steps, f"Solved in {iteration} iterations")
            
            # If no progress, stop
            if not progress_made:
                break
        
        return SolverResult(False, self.steps, f"Stuck after {iteration} iterations - no more logical moves")
    
    def _get_possible_values(self, pos: Position) -> set[int]:
        """Get all values that could legally be placed at position."""
        possible = set()
        
        for value in range(self.puzzle.constraints.min_value, self.puzzle.constraints.max_value + 1):
            if self._can_place_value(pos, value):
                possible.add(value)
        
        return possible
    
    def _get_possible_positions(self, value: int) -> set[Position]:
        """Get all positions where value could legally be placed."""
        possible = set()
        
        for cell in self.puzzle.grid.iter_cells():
            if cell.is_empty() and self._can_place_value(cell.pos, value):
                possible.add(cell.pos)
        
        return possible
    
    def _can_place_value(self, pos: Position, value: int) -> bool:
        """Check if value can be legally placed at position."""
        # Check if value already exists
        if self._value_exists(value):
            return False
        
        # Check if position is valid
        cell = self.puzzle.grid.get_cell(pos)
        if not cell.is_empty():
            return False
        
        # Check adjacency constraint
        return self._check_adjacency_constraint(pos, value)
    
    def _check_adjacency_constraint(self, pos: Position, value: int) -> bool:
        """Check adjacency constraint for placing value at position."""
        neighbors = self.puzzle.grid.neighbors_of(pos)
        
        prev_value = value - 1
        next_value = value + 1
        
        has_prev_neighbor = False
        has_next_neighbor = False
        
        # Check neighbors
        for neighbor_pos in neighbors:
            neighbor_cell = self.puzzle.grid.get_cell(neighbor_pos)
            if neighbor_cell.value == prev_value:
                has_prev_neighbor = True
            elif neighbor_cell.value == next_value:
                has_next_neighbor = True
        
        # For min value, only need next neighbor (if it exists)
        if value == self.puzzle.constraints.min_value:
            if self._value_exists(next_value):
                return has_next_neighbor
            else:
                return True
        
        # For max value, only need prev neighbor (if it exists)
        if value == self.puzzle.constraints.max_value:
            if self._value_exists(prev_value):
                return has_prev_neighbor
            else:
                return True
        
        # For middle values, check both directions
        has_prev_value = self._value_exists(prev_value)
        has_next_value = self._value_exists(next_value)
        
        if not has_prev_value and not has_next_value:
            return True
        
        if has_prev_value and not has_next_value:
            return has_prev_neighbor
        
        if has_next_value and not has_prev_value:
            return has_next_neighbor
        
        if has_prev_value and has_next_value:
            return has_prev_neighbor or has_next_neighbor
        
        return True
    
    def _value_exists(self, value: int) -> bool:
        """Check if value already exists in the puzzle."""
        for cell in self.puzzle.grid.iter_cells():
            if cell.value == value:
                return True
        return False
    
    def _place_value(self, pos: Position, value: int, reason: str):
        """Place a value at position and record the step."""
        cell = self.puzzle.grid.get_cell(pos)
        cell.value = value
        
        step = SolverStep(pos, value, reason)
        self.steps.append(step)
    
    def _is_solved(self) -> bool:
        """Check if puzzle is completely solved."""
        for cell in self.puzzle.grid.iter_cells():
            if cell.is_empty():
                return False
        return True
    
    def get_hint(self) -> SolverStep | None:
        """Get a single hint (next logical move).
        
        Returns:
            SolverStep with the hint, or None if no logical move available
        """
        # Save current state
        saved_steps = self.steps.copy()
        
        # Try to find one move
        result = self._solve_logic_v0()
        
        # Restore state but return first new step as hint
        if result.steps and len(result.steps) > len(saved_steps):
            hint = result.steps[len(saved_steps)]
            self.steps = saved_steps  # Restore state
            return hint
        
        return None
