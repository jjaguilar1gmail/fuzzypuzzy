"""Solve module: Solver

Contains the Solver class for deterministic solving algorithms.
"""
import copy
from typing import TYPE_CHECKING
from core.position import Position
from core.puzzle import Puzzle
from solve.corridors import CorridorMap
from solve.degree import DegreeIndex
from solve.regions import RegionCache, EmptyRegion
from hidato_io.exporters import ascii_print
if TYPE_CHECKING:
    from solve.candidates import CandidateModel

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
    
    def __init__(self, solved: bool, steps: list[SolverStep], message: str = "", solved_puzzle: 'Puzzle' = None,
                 nodes: int = 0, depth: int = 0, progress_made: bool = False):
        self.solved = solved
        self.steps = steps
        self.message = message
        self.solved_puzzle = solved_puzzle
        self.nodes = nodes  # For search-based solvers
        self.depth = depth  # For search-based solvers
        self.progress_made = progress_made  # For logic-only solvers

class Solver:
    """Deterministic solver for Hidato puzzles using consecutive logic."""
    
    def __init__(self, puzzle: Puzzle):
        self.original_puzzle = puzzle
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
    
    @staticmethod
    def solve(puzzle: Puzzle, mode: str = "logic_v0", **config) -> SolverResult:
        """Solve a puzzle using the specified mode.
        
        Args:
            puzzle: The puzzle to solve (will be modified in-place if solved)
            mode: Solving mode ("logic_v0", "logic_v1", "logic_v2", "logic_v3")
            **config: Mode-specific configuration options
            
        Returns:
            SolverResult containing success status and steps
        """
        solver = Solver(puzzle)
        
        if mode == "logic_v0":
            result = solver._solve_logic_v0()
        elif mode == "logic_v1":
            result = solver._solve_logic_v1(**config)
        elif mode == "logic_v2":
            result = solver._solve_logic_v2(**config)
        elif mode == "logic_v3":
            result = solver._solve_logic_v3(**config)
        else:
            raise ValueError(f"Unsupported solving mode: {mode}")
        
        # If solved, apply the solution to the original puzzle
        if result.solved and result.solved_puzzle:
            Solver._apply_solution_to_puzzle(puzzle, result.solved_puzzle)
        
        return result
    
    @staticmethod
    def count_solutions(puzzle: Puzzle, cap: int = 2, max_nodes: int = 10000, 
                       timeout_ms: int = 5000, max_depth: int = 50) -> dict:
        """Count the number of solutions up to a cap.
        
        This method explores the search space and counts distinct solutions.
        It terminates early when the cap is reached for efficiency.
        
        Args:
            puzzle: The puzzle to analyze (not modified)
            cap: Maximum number of solutions to find (default 2 for uniqueness check)
            max_nodes: Maximum search nodes to explore
            timeout_ms: Timeout in milliseconds
            max_depth: Maximum search depth
            
        Returns:
            dict with:
                solutions_found: int (number of distinct solutions found, capped at cap)
                nodes: int (nodes explored)
                depth: int (max depth reached)
                timed_out: bool (whether timeout occurred)
                exhausted: bool (whether search space was exhausted)
        """
        import time
        from solve.candidates import CandidateModel
        
        start_time = time.time()
        nodes_explored = 0
        max_search_depth = 0
        solutions_found = 0
        timed_out = False
        exhausted = False
        def clear_nongivens(puzzle_state: Puzzle) -> None:
            """Clear all non-given cell values in the puzzle state."""
            for cell in puzzle_state.grid.iter_cells():
                if not cell.given and not cell.blocked:
                    cell.value = None

        def is_timeout() -> bool:
            return (time.time() - start_time) * 1000 > timeout_ms
        
        def is_complete(puzzle_state) -> bool:
            """Check if puzzle is completely filled and valid."""
            # All non-blocked cells must have values
            for cell in puzzle_state.grid.iter_cells():
                if cell.blocked:
                    continue
                if cell.is_empty():
                    return False
            # Verify it's a valid solution
            temp_solver = Solver(puzzle_state)
            return temp_solver._is_solved()
        
        def get_next_empty_cell(puzzle_state):
            """Find the next empty non-blocked cell using MRV (min remaining values)."""
            best_pos = None
            best_count = None
            # Scan all cells and pick the one with the fewest legal values
            for row in range(puzzle_state.grid.rows):
                for col in range(puzzle_state.grid.cols):
                    pos = Position(row, col)
                    cell = puzzle_state.grid.get_cell(pos)
                    if cell.blocked or not cell.is_empty():
                        continue
                    # Compute possible values count for MRV
                    possible = get_possible_values(puzzle_state, pos)
                    cnt = len(possible)
                    if cnt == 0:
                        # Early detect dead-end: no values possible for this cell
                        return pos  # Will lead to immediate backtrack
                    if best_count is None or cnt < best_count:
                        best_count = cnt
                        best_pos = pos
                        # Perfect heuristic if only one possible value
                        if best_count == 1:
                            return best_pos
            return best_pos
        
        def get_possible_values(puzzle_state, pos):
            """Get possible values for a position based on Hidato adjacency rules."""
            # Position must be empty and not blocked
            cell = puzzle_state.grid.get_cell(pos)
            if not cell.is_empty() or cell.blocked:
                return []
            
            # Find which values are already placed and their positions
            placed_values = {}
            for cell in puzzle_state.grid.iter_cells():
                # Skip blocked cells
                if cell.blocked:
                    continue
                if cell.value is not None:
                    placed_values[cell.value] = cell.pos
            
            possible = []
            neighbors = puzzle_state.grid.neighbors_of(pos)
            
            for value in range(puzzle_state.constraints.min_value, 
                             puzzle_state.constraints.max_value + 1):
                # Skip if value is already placed
                if value in placed_values:
                    continue
                
                # Check adjacency constraints
                prev_value = value - 1
                next_value = value + 1
                
                # If previous value is placed, current position must be adjacent to it
                if prev_value >= puzzle_state.constraints.min_value and prev_value in placed_values:
                    if placed_values[prev_value] not in neighbors:
                        continue  # Not adjacent to previous value
                
                # If next value is placed, current position must be adjacent to it
                if next_value <= puzzle_state.constraints.max_value and next_value in placed_values:
                    if placed_values[next_value] not in neighbors:
                        continue  # Not adjacent to next value
                
                # Value is valid for this position
                possible.append(value)
            
            return possible
        
        def search_recursive(puzzle_state, depth: int) -> None:
            """Recursive search that counts all solutions up to cap."""
            nonlocal nodes_explored, max_search_depth, solutions_found, timed_out, exhausted
            
            # Early termination if we've found enough solutions
            if solutions_found >= cap:
                return
            
            nodes_explored += 1
            max_search_depth = max(max_search_depth, depth)
            
            # Check termination conditions
            if nodes_explored > max_nodes or depth > max_depth:
                exhausted = True
                return
            
            if is_timeout():
                timed_out = True
                return
            
            # Check if puzzle is complete
            if is_complete(puzzle_state):
                solutions_found += 1
                return
            
            # Find next empty cell
            pos = get_next_empty_cell(puzzle_state)
            if pos is None:
                # No empty cells but not complete - contradiction
                return
            
            # Get possible values for this position
            possible_values = get_possible_values(puzzle_state, pos)
            
            if not possible_values:
                # No valid values - dead end
                return
            
            # Try each possible value (explore all branches)
            for value in possible_values:
                # Early exit if we've found enough solutions
                if solutions_found >= cap:
                    return
                
                # Create new puzzle state with this assignment
                temp_solver = Solver(puzzle_state)
                new_puzzle = temp_solver._copy_puzzle(puzzle_state)
                new_cell = new_puzzle.grid.get_cell(pos)
                new_cell.value = value
                
                # Recursive search
                search_recursive(new_puzzle, depth + 1)
        
        # Create a working copy of the puzzle
        solver = Solver(puzzle)
        new_puzzle = solver._copy_puzzle(puzzle)
        clear_nongivens(new_puzzle)
        search_recursive(new_puzzle, 0)

        return {
            'solutions_found': solutions_found,
            'nodes': nodes_explored,
            'depth': max_search_depth,
            'timed_out': timed_out,
            'exhausted': exhausted or nodes_explored > max_nodes
        }
    
    @staticmethod
    def _apply_solution_to_puzzle(original_puzzle: Puzzle, solved_puzzle: Puzzle) -> None:
        """Apply the solution from solved_puzzle to original_puzzle.
        
        Args:
            original_puzzle: The puzzle to modify
            solved_puzzle: The solved puzzle to copy values from
        """
        # Copy all non-given cell values from solved puzzle to original puzzle
        for row in range(original_puzzle.grid.rows):
            for col in range(original_puzzle.grid.cols):
                pos = Position(row, col)
                original_cell = original_puzzle.grid.get_cell(pos)
                solved_cell = solved_puzzle.grid.get_cell(pos)
                
                # Only copy values for non-given cells
                if not original_cell.given and solved_cell.value is not None:
                    original_cell.value = solved_cell.value
    
    @staticmethod
    def apply_logic_fixpoint(puzzle_state: Puzzle, max_passes: int = 10, **logic_options) -> tuple[bool, bool, list[SolverStep]]:
        """
        Apply logic_v2 strategies to a puzzle state until fixpoint (no progress).
        This operates in-place on the puzzle_state for use within search.
        
        Args:
            puzzle_state: Puzzle to apply logic to (modified in-place)
            max_passes: Maximum iterations before stopping
            **logic_options: Options for logic_v2 (tie_break, enable_*)
            
        Returns:
            Tuple of (progress_made, solved, steps) where:
                progress_made: Whether any placement/elimination occurred
                solved: Whether puzzle is fully solved
                steps: List of SolverStep objects documenting changes
        """
        temp_solver = Solver(puzzle_state)
        result = temp_solver._solve_logic_v2(max_logic_passes=max_passes, **logic_options)
        
        # The temp_solver worked on a deep copy; we need to copy changes back to puzzle_state
        Solver._apply_solution_to_puzzle(puzzle_state, temp_solver.puzzle)
        
        # Check if puzzle_state is solved: all cells filled + valid path
        # Fast check: any empty cells?
        all_filled = all(not cell.is_empty() for cell in puzzle_state.grid.iter_cells())
        if not all_filled:
            return (result.progress_made or len(result.steps) > 0, False, result.steps)
        
        # All filled, now verify it's a valid Hidato solution
        final_solver = Solver(puzzle_state)
        actually_solved = final_solver._is_solved()
        
        return (result.progress_made or len(result.steps) > 0, actually_solved, result.steps)
    
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
                return SolverResult(True, self.steps, f"Solved in {iteration} iterations", self.puzzle)
            
            # If no progress, stop
            if not progress_made:
                break
        
        return SolverResult(False, self.steps, f"Stuck after {iteration} iterations - no more logical moves", self.puzzle)
    
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
    
    def _record_elimination(self, strategy: str, count: int, details: str = ""):
        """Record an elimination step without placement (for pruning strategies)."""
        # Use a placeholder position for elimination-only steps
        placeholder_pos = Position(-1, -1)
        reason = f"{strategy}: eliminated {count} candidate(s)"
        if details:
            reason += f" - {details}"
        step = SolverStep(placeholder_pos, -1, reason)
        self.steps.append(step)
    
    def _is_solved(self) -> bool:
        """Check if puzzle is completely solved with valid Hidato constraints."""
        # Check 1: All cells filled
        for cell in self.puzzle.grid.iter_cells():
            if cell.is_empty():
                return False
        
        # Check 2: All required values present  
        placed_values = set()
        value_positions = {}
        for cell in self.puzzle.grid.iter_cells():
            if cell.value is not None:
                placed_values.add(cell.value)
                value_positions[cell.value] = cell.pos
        
        required_values = set(range(self.puzzle.constraints.min_value, 
                                   self.puzzle.constraints.max_value + 1))
        if placed_values != required_values:
            return False
        
        # Check 3: Valid Hidato path (consecutive values are adjacent)
        for value in range(self.puzzle.constraints.min_value, 
                          self.puzzle.constraints.max_value):
            current_pos = value_positions[value]
            next_pos = value_positions[value + 1]
            
            neighbors = self.puzzle.grid.neighbors_of(current_pos)
            if next_pos not in neighbors:
                return False  # Consecutive values not adjacent
        
        return True
    
    def get_hint(self, mode: str = "logic_v0", **config) -> SolverStep | None:
        """Get a single hint (next logical move) using specified mode.
        
        Args:
            mode: Solving mode to use for hint generation
            **config: Mode-specific configuration options
        
        Returns:
            SolverStep with the hint, or None if no logical move available
        """
        # Save current state
        saved_puzzle = copy.deepcopy(self.puzzle)
        saved_steps = self.steps.copy()
        
        # Try to find one move using specified mode
        if mode == "logic_v0":
            result = self._solve_logic_v0()
        elif mode == "logic_v1":
            result = self._solve_logic_v1(**config)
        elif mode == "logic_v2":
            result = self._solve_logic_v2(**config)
        elif mode == "logic_v3":
            result = self._solve_logic_v3(**config)
        else:
            raise ValueError(f"Unsupported hint mode: {mode}")
        
        # Restore state but return first new step as hint
        self.puzzle = saved_puzzle
        if result.steps and len(result.steps) > len(saved_steps):
            hint = result.steps[len(saved_steps)]
            self.steps = saved_steps  # Restore state
            return hint
        
        return None
    
    def _solve_logic_v1(self, max_logic_passes: int = 50, tie_break: str = "row_col", **kwargs) -> SolverResult:
        """Solve using logic_v1: two-ended propagation + enhanced uniqueness.
        
        Args:
            max_logic_passes: Maximum iterations before giving up
            tie_break: Tie-breaking strategy for equal candidates
            
        Returns:
            SolverResult with solve status and steps
        """
        from solve.candidates import CandidateModel
        
        max_iterations = max_logic_passes
        iteration = 0
        
        # Initialize candidate model
        candidates = CandidateModel()
        candidates.init_from(self.puzzle)
        
        while iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            # Check for early contradictions
            if candidates.has_empty_candidates():
                # For v1, treat this as no-progress (will return 'Stuck' below)
                break
            
            # Strategy 1: Single candidate values (positions with only one possible value)
            single_values = candidates.single_candidate_values()
            for pos, value in single_values.items():
                # Check if value is already placed before assigning
                if not self._value_exists(value):
                    self._place_value(pos, value, f"Single candidate: only {value} fits here")
                    candidates.assign(value, pos)
                    progress_made = True
            
            # Strategy 2: Single candidate positions (values with only one possible position)  
            single_positions = candidates.single_candidate_positions()
            if single_positions:
                if tie_break == "row_col":
                    # Process in deterministic order
                    sorted_items = sorted(single_positions.items())
                    for val, position in sorted_items:
                        if not self._value_exists(val):
                            self._place_value(position, val, f"Single position: only place for {val}")
                            candidates.assign(val, position)
                            progress_made = True
                else:
                    # Process in arbitrary order
                    for value, pos in single_positions.items():
                        if not self._value_exists(value):
                            self._place_value(pos, value, f"Single position: only place for {value}")
                            candidates.assign(value, pos)
                            progress_made = True
            
            # Strategy 3: Two-ended propagation
            progress_made |= self._apply_two_ended_propagation(candidates)
            
            # Strategy 4: Enhanced adjacency checks (early contradiction detection)
            if self._detect_adjacency_contradictions():
                # For v1 tests, don't throw hard failure; treat as no progress
                break
            
            # Check if solved
            if self._is_solved():
                return SolverResult(True, self.steps, f"Solved using logic_v1 in {iteration} iterations", self.puzzle)
            
            # If no progress, stop
            if not progress_made:
                break
        
        return SolverResult(False, self.steps, f"Stuck after {iteration} iterations using logic_v1 - no more logical moves", self.puzzle)
    
    def _apply_two_ended_propagation(self, candidates: 'CandidateModel') -> bool:
        """Apply two-ended propagation logic.
        
        For each placed value, build frontiers extending in both directions
        and look for forced placements where frontiers intersect uniquely.
        
        Args:
            candidates: Current candidate model
            
        Returns:
            True if progress was made
        """
        progress = False
        
        # Find all placed values
        placed_values = {}
        for cell in self.puzzle.grid.iter_cells():
            if not cell.is_empty():
                placed_values[cell.value] = cell.pos
        
        # For each placed value, try to extend sequences
        for value, pos in placed_values.items():
            # Try forward propagation (value -> value+1, value+2, ...)
            progress |= self._propagate_from_anchor(candidates, value, pos, direction=1)
            
            # Try backward propagation (value -> value-1, value-2, ...)  
            progress |= self._propagate_from_anchor(candidates, value, pos, direction=-1)
        
        return progress
    
    def _propagate_from_anchor(self, candidates: 'CandidateModel', anchor_value: int, 
                              anchor_pos: Position, direction: int) -> bool:
        """Propagate from an anchor value in one direction.
        
        Args:
            candidates: Current candidate model
            anchor_value: Starting value
            anchor_pos: Position of starting value
            direction: +1 for forward, -1 for backward
            
        Returns:
            True if progress made
        """
        progress = False
        current_pos = anchor_pos
        current_value = anchor_value
        
        # Extend sequence until we can't go further
        for step in range(1, 10):  # Limit propagation depth
            # Guard against None values
            if current_value is None:
                break
                
            next_value = current_value + direction
            
            # Check bounds
            if (next_value < self.puzzle.constraints.min_value or 
                next_value > self.puzzle.constraints.max_value):
                break
            
            # If next value already placed, continue from there
            next_pos = self._find_value_position(next_value)
            if next_pos is not None:
                current_pos = next_pos
                current_value = next_value
                continue
            
            # Find candidates for next value that are adjacent to current position
            next_candidates = candidates.candidates_for_value(next_value)
            adjacent_candidates = set()
            
            for neighbor_pos in self.puzzle.grid.neighbors_of(current_pos):
                if neighbor_pos in next_candidates:
                    adjacent_candidates.add(neighbor_pos)
            
            # If exactly one adjacent candidate, place it
            if len(adjacent_candidates) == 1:
                next_pos = list(adjacent_candidates)[0]  # Get the single candidate
                self._place_value(next_pos, next_value, f"Two-ended propagation: {next_value} from {current_value}")
                candidates.assign(next_value, next_pos)
                current_pos = next_pos
                current_value = next_value
                progress = True
            else:
                # No unique propagation possible, stop
                break
        
        return progress
    
    def _find_value_position(self, value: int) -> Position | None:
        """Find position where a value is placed."""
        for cell in self.puzzle.grid.iter_cells():
            if cell.value == value:
                return cell.pos
        return None
    
    def _detect_adjacency_contradictions(self) -> bool:
        """Detect early adjacency contradictions.
        
        Returns:
            True if contradiction detected
        """
        # Check each placed value has viable neighbors for required adjacencies
        for cell in self.puzzle.grid.iter_cells():
            # Skip blocked or empty cells
            if cell.blocked or cell.value is None:
                continue
            else:
                value = cell.value
                pos = cell.pos
                
                # Check if required neighbors (value±1) can be placed
                prev_value = value - 1
                next_value = value + 1
                
                neighbors = self.puzzle.grid.neighbors_of(pos)
                
                # For non-endpoint values, check both directions
                if (prev_value >= self.puzzle.constraints.min_value and 
                    not self._value_exists(prev_value)):
                    # Need to place prev_value adjacent
                    has_viable_neighbor = False
                    for neighbor_pos in neighbors:
                        neighbor_cell = self.puzzle.grid.get_cell(neighbor_pos)
                        if neighbor_cell.is_empty():
                            has_viable_neighbor = True
                            break
                    if not has_viable_neighbor:
                        return True  # Contradiction
                
                if (next_value <= self.puzzle.constraints.max_value and 
                    not self._value_exists(next_value)):
                    # Need to place next_value adjacent
                    has_viable_neighbor = False
                    for neighbor_pos in neighbors:
                        neighbor_cell = self.puzzle.grid.get_cell(neighbor_pos)
                        if neighbor_cell.is_empty():
                            has_viable_neighbor = True
                            break
                    if not has_viable_neighbor:
                        return True  # Contradiction
        
        return False
    
    def _solve_logic_v2(self, max_logic_passes: int = 50, tie_break: str = "row_col",
                       enable_island_elim: bool = True, enable_segment_bridging: bool = True,
                       enable_degree_prune: bool = True, **kwargs) -> SolverResult:
        """Solve using logic_v2: region-aware logic + v1 features.
        
        Region-aware techniques:
        - Island elimination: Remove disconnected empty regions that can't form valid paths
        - Corridor bridging: Detect must-use narrow passages between regions
        - Degree pruning: Eliminate positions that would create impossible connectivity
        
        Args:
            max_logic_passes: Maximum iterations before giving up
            tie_break: Tie-breaking strategy for equal candidates  
            enable_island_elim: Enable island elimination logic
            enable_segment_bridging: Enable corridor bridging logic
            enable_degree_prune: Enable degree-based pruning
            
        Returns:
            SolverResult with solve status and steps
        """
        from solve.candidates import CandidateModel
        from solve.regions import RegionCache
        from solve.corridors import CorridorMap
        from solve.degree import DegreeIndex
        
        max_iterations = max_logic_passes
        iteration = 0
        overall_progress = False  # Track if ANY progress was made across all iterations
        
        # Initialize advanced analysis structures
        candidates = CandidateModel()
        candidates.init_from(self.puzzle)
        
        regions = RegionCache()
        regions.build_regions(self.puzzle)
        
        corridors = CorridorMap()
        
        degrees = DegreeIndex()
        degrees.build_degree_index(self.puzzle)
        
        while iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            # Check for early contradictions
            if candidates.has_empty_candidates():
                return SolverResult(False, self.steps, f"Contradiction detected at iteration {iteration}", self.puzzle)
            
            # Apply all logic_v1 strategies first (inherit proven techniques)
            progress_made |= self._apply_logic_v1_strategies(candidates, tie_break)
            
            # Region-aware Strategy 1: Island Elimination
            if enable_island_elim:
                progress_made |= self._apply_island_elimination(candidates, regions)
            
            # Region-aware Strategy 2: Corridor Bridging  
            if enable_segment_bridging:
                progress_made |= self._apply_corridor_bridging(candidates, corridors)
            
            # Region-aware Strategy 3: Degree-based Pruning
            if enable_degree_prune:
                progress_made |= self._apply_degree_pruning(candidates, degrees)
            
            # Update analysis structures if progress was made
            if progress_made:
                overall_progress = True  # Track that we made progress this run
                regions.build_regions(self.puzzle)
                corridors.invalidate_cache()
                degrees.build_degree_index(self.puzzle)
            
            # Check if solved
            if self._is_solved():
                return SolverResult(True, self.steps, f"Solved using logic_v2 in {iteration} iterations", 
                                  self.puzzle, progress_made=True)
            
            # If no progress, stop
            if not progress_made:
                break
        
        return SolverResult(False, self.steps, f"Stuck after {iteration} iterations using logic_v2 - no more logical moves", 
                          self.puzzle, progress_made=overall_progress)
    
    def _solve_logic_v3(self, max_logic_passes: int = 50, tie_break: str = "row_col",
                       enable_island_elim: bool = True, enable_segment_bridging: bool = True,
                       enable_degree_prune: bool = True, max_nodes: int = 20000, 
                       max_depth: int = 50, timeout_ms: int = 500, 
                       ordering: str = "mrv_lcv_frontier", **kwargs) -> SolverResult:
        """Solve using logic_v3: v2 + bounded search.
        
        Combines all logical techniques (v1 + v2) with intelligent backtracking search.
        Uses MRV (Minimum Remaining Values) and LCV (Least Constraining Value) heuristics
        with bounded exploration to find solutions when pure logic isn't sufficient.
        
        Args:
            max_logic_passes: Maximum logic iterations per search node
            tie_break: Tie-breaking strategy for logical moves
            enable_island_elim: Enable island elimination logic
            enable_segment_bridging: Enable corridor bridging logic  
            enable_degree_prune: Enable degree-based pruning
            max_nodes: Maximum search nodes before termination
            max_depth: Maximum search depth
            timeout_ms: Time limit in milliseconds
            ordering: Search ordering strategy ("mrv_lcv", "frontier", "row_col")
            
        Returns:
            SolverResult with solve status, steps, and search stats
        """
        import time
        from solve.candidates import CandidateModel
        
        start_time = time.time()
        nodes_explored = 0
        max_search_depth = 0
        # Micro-optimization: on very small boards, skip heavier heuristics
        small_board = (self.puzzle.grid.rows * self.puzzle.grid.cols) <= 25
        use_segment_bridging = enable_segment_bridging and not small_board
        use_degree_prune = enable_degree_prune and not small_board
        
        def is_timeout() -> bool:
            return (time.time() - start_time) * 1000 > timeout_ms
        
        def search_recursive(puzzle_state, depth: int) -> bool:
            """Recursive backtracking search with bounded exploration."""
            nonlocal nodes_explored, max_search_depth
            
            nodes_explored += 1
            max_search_depth = max(max_search_depth, depth)
            
            # Check termination conditions
            if nodes_explored > max_nodes or depth > max_depth or is_timeout():
                return False
            
            # Apply logic_v2 fixpoint in-place at this node (Bug #1 fix)
            progress_made, solved, logic_steps = Solver.apply_logic_fixpoint(
                puzzle_state,
                max_passes=max_logic_passes,
                tie_break=tie_break,
                enable_island_elim=enable_island_elim,
                enable_segment_bridging=use_segment_bridging,
                enable_degree_prune=use_degree_prune
            )
            
            # Add logic steps to trace
            self.steps.extend(logic_steps)
            
            # Check if solved after logic
            if solved:
                return True
                
            # Check if puzzle is solved using proper Hidato validation
            temp_solver = Solver(puzzle_state)
            if temp_solver._is_solved():
                return True
            
            # Prepare for search: build candidate model
            candidates = CandidateModel()
            candidates.init_from(puzzle_state)
            
            # Check for contradictions
            if candidates.has_empty_candidates():
                return False
            
            # Choose next value and position using heuristics (MRV by value - Bug #2 fix)
            choice = self._choose_search_variable(candidates, ordering)
            if choice is None:
                return False
            
            value, best_pos = choice
            
            # For LCV/frontier ordering, we may want to try other positions for this value
            # Get all positions where this value could go
            available_positions = list(candidates.value_to_positions.get(value, [best_pos]))
            
            # Order positions using LCV/frontier if enabled
            if "lcv" in ordering.lower() or "frontier" in ordering.lower():
                # Frontier positions first, then others
                frontier = self._get_frontier_positions(available_positions)
                non_frontier = [p for p in available_positions if p not in frontier]
                # Sort each group by row, col for determinism
                frontier.sort(key=lambda p: (p.row, p.col))
                non_frontier.sort(key=lambda p: (p.row, p.col))
                ordered_positions = frontier + non_frontier
            else:
                # Just deterministic row-col ordering
                ordered_positions = sorted(available_positions, key=lambda p: (p.row, p.col))
            
            # Try each position for the chosen value
            for pos in ordered_positions:
                # Check if value is already placed (safety check)
                if self._value_exists_in_puzzle(puzzle_state, value):
                    break
                
                # Create new puzzle state with this assignment
                new_puzzle = self._copy_puzzle(puzzle_state)
                new_cell = new_puzzle.grid.get_cell(pos)
                new_cell.value = value
                
                # Record the guess
                step = SolverStep(pos, value, f"Search guess: value {value} at {pos}, depth {depth}")
                self.steps.append(step)
                
                # Recursive search
                if search_recursive(new_puzzle, depth + 1):
                    # Solution found in new_puzzle! Copy to puzzle_state so parent sees it
                    self._copy_solution_to_puzzle(new_puzzle, puzzle_state)
                    return True
                
                # Backtrack: remove the guess step
                self.steps.pop()
            
            return False
        
        # Start the bounded search
        success = search_recursive(self.puzzle, 0)
        
        # Prepare result with search statistics
        elapsed_ms = (time.time() - start_time) * 1000
        
        if success:
            message = f"Solved using logic_v3 in {nodes_explored} nodes, depth {max_search_depth}, {elapsed_ms:.1f}ms"
            return SolverResult(True, self.steps, message, self.puzzle, 
                              nodes=nodes_explored, depth=max_search_depth, progress_made=True)
        else:
            if is_timeout():
                reason = f"timeout after {timeout_ms}ms"
            elif nodes_explored > max_nodes:
                reason = f"node limit {max_nodes}"
            elif max_search_depth > max_depth:
                reason = f"depth limit {max_depth}"
            else:
                reason = "exhausted search space"
            
            message = f"Failed using logic_v3: {reason} ({nodes_explored} nodes, {elapsed_ms:.1f}ms)"
            return SolverResult(False, self.steps, message, None,
                              nodes=nodes_explored, depth=max_search_depth, progress_made=False)
    
    def _apply_logic_v1_strategies(self, candidates: 'CandidateModel', tie_break: str) -> bool:
        """Apply all logic_v1 strategies (reusable for logic_v2).
        
        Args:
            candidates: Current candidate model
            tie_break: Tie-breaking strategy
            
        Returns:
            True if progress was made
        """
        progress = False
        
        # Strategy 1: Single candidate values (positions with only one possible value)
        single_values = candidates.single_candidate_values()
        for pos, value in single_values.items():
            # Check if value is already placed before assigning
            if not self._value_exists(value):
                self._place_value(pos, value, f"Single candidate: only {value} fits here")
                candidates.assign(value, pos)
                progress = True
        
        # Strategy 2: Single candidate positions (values with only one possible position)  
        single_positions = candidates.single_candidate_positions()
        if single_positions:
            if tie_break == "row_col":
                # Process in deterministic order
                sorted_items = sorted(single_positions.items())
                for val, position in sorted_items:
                    if not self._value_exists(val):
                        self._place_value(position, val, f"Single position: only place for {val}")
                        candidates.assign(val, position)
                        progress = True
            else:
                # Process in arbitrary order
                for value, pos in single_positions.items():
                    if not self._value_exists(value):
                        self._place_value(pos, value, f"Single position: only place for {value}")
                        candidates.assign(value, pos)
                        progress = True
        
        # Strategy 3: Two-ended propagation
        progress |= self._apply_two_ended_propagation(candidates)
        
        return progress
    
    def _apply_island_elimination(self, candidates: 'CandidateModel', regions: 'RegionCache') -> bool:
        """Apply island elimination: remove isolated regions that can't form valid paths.
        
        Args:
            candidates: Current candidate model
            regions: Region analysis cache
            
        Returns:
            True if progress was made
        """
        progress = False
        elimination_count = 0
        
        # Find empty regions
        empty_regions = regions.regions
        
        for region in empty_regions:
            # Check if region is too small to hold any valid sequence
            min_sequence_length = self._compute_min_sequence_for_region(region)
            
            if region.size < min_sequence_length:
                # This region is too small - eliminate all candidates in it
                for pos in region.cells:
                    if pos in candidates.pos_to_values:
                        old_values = list(candidates.pos_to_values[pos])
                        for value in old_values:
                            candidates.remove_candidate(value, pos)
                            elimination_count += 1
                            progress = True
                            # Note: Don't place values here, just eliminate impossible candidates
        
        if elimination_count > 0:
            self._record_elimination("region_capacity", elimination_count, 
                                    f"{len([r for r in empty_regions if r.size < self._compute_min_sequence_for_region(r)])} insufficient regions")
        
        return progress
    
    def _apply_corridor_bridging(self, candidates: 'CandidateModel', corridors: 'CorridorMap') -> bool:
        """Apply corridor bridging: identify must-use passages between regions.
        
        Args:
            candidates: Current candidate model
            corridors: Corridor analysis cache
            
        Returns:
            True if progress was made
        """
        progress = False
        elimination_count = 0
        gap_count = 0
        
        # Get sequence gaps that need bridging
        gaps = corridors.get_all_sequence_gaps(self.puzzle)
        
        for start_value, end_value, gap_size in gaps:
            if gap_size > 1:  # Only process gaps that need bridging
                gap_count += 1
                # Find corridor positions between these values
                corridor_positions = corridors.corridors_between(self.puzzle, start_value, end_value)
                
                # Apply corridor-based pruning
                candidate_dict = {}
                for val in range(start_value + 1, end_value):
                    if val in candidates.value_to_positions:
                        candidate_dict[val] = candidates.value_to_positions[val]
                
                if candidate_dict:
                    pruned_candidates = corridors.prune_candidates_by_corridors(self.puzzle, candidate_dict)
                    
                    # Update the candidate model with pruned results
                    for value, valid_positions in pruned_candidates.items():
                        if value in candidates.value_to_positions:
                            old_positions = candidates.value_to_positions[value].copy()
                            invalid_positions = old_positions - valid_positions
                            
                            for pos in invalid_positions:
                                candidates.remove_candidate(value, pos)
                                elimination_count += 1
                                progress = True
        
        if elimination_count > 0:
            self._record_elimination("corridor", elimination_count, 
                                    f"{gap_count} gap(s) with {len(gaps)} total segments")
        
        return progress
    
    def _apply_degree_pruning(self, candidates: 'CandidateModel', degrees: 'DegreeIndex') -> bool:
        """Apply degree-based pruning: eliminate positions that would create impossible connectivity.
        
        Args:
            candidates: Current candidate model
            degrees: Degree analysis index
            
        Returns:
            True if progress was made
        """
        progress = False
        elimination_count = 0
        
        # Build current degree index
        degree_map = degrees.build_degree_index(self.puzzle)
        
        # Check degree constraints for each candidate placement
        for pos, values in list(candidates.pos_to_values.items()):
            current_degree = degree_map.get(pos, 0)
            
            for value in list(values):
                # Check degree constraints based on value position in sequence
                min_value = self.puzzle.constraints.min_value
                max_value = self.puzzle.constraints.max_value
                
                # Endpoint values (min/max) need degree >= 1
                # Middle values need degree >= 2
                required_degree = 1 if (value == min_value or value == max_value) else 2
                
                if current_degree < required_degree:
                    candidates.remove_candidate(value, pos)
                    elimination_count += 1
                    progress = True
        
        if elimination_count > 0:
            low_degree_positions = len([p for p, d in degree_map.items() if d < 2])
            self._record_elimination("degree", elimination_count, 
                                    f"{low_degree_positions} low-degree position(s)")
        
        return progress
    
    def _compute_min_sequence_for_region(self, region: 'EmptyRegion') -> int:
        """Compute minimum sequence length needed for a region to be useful.
        
        Args:
            region: Empty region to analyze
            
        Returns:
            Minimum number of consecutive values needed
        """
        # A region needs at least 1 position to be useful
        # More sophisticated analysis could consider connectivity requirements
        return 1
    
    def _compute_required_values_for_corridor(self, corridor) -> set:
        """Compute which values must pass through a critical corridor.
        
        Args:
            corridor: Critical corridor passage
            
        Returns:
            Set of values that must use this corridor
        """
        # Simplified implementation: assume any unplaced value could be required
        required = set()
        for value in range(self.puzzle.constraints.min_value, self.puzzle.constraints.max_value + 1):
            if not self._value_exists(value):
                required.add(value)
        return required
    
    def _choose_search_variable(self, candidates: 'CandidateModel', ordering: str) -> tuple[int, Position] | None:
        """Choose next value and position for search using heuristics.
        
        Bug #2 fix: MRV operates on VALUES (choose value with fewest positions),
        not positions (old behavior chose position with fewest values).
        
        Args:
            candidates: Current candidate model
            ordering: Search ordering strategy
            
        Returns:
            Tuple of (value, position) to try, or None if no candidates
        """
        if not candidates.value_to_positions:
            return None
        
        if "mrv" in ordering.lower():
            # MRV by VALUE: Choose value with Minimum Remaining positions (Bug #2 fix)
            min_positions = min(len(positions) for positions in candidates.value_to_positions.values())
            mrv_values = [val for val, positions in candidates.value_to_positions.items() 
                         if len(positions) == min_positions]
            
            # Deterministic tie-break: choose smallest value
            chosen_value = min(mrv_values)
            
            # Now choose position for this value
            available_positions = list(candidates.value_to_positions[chosen_value])
            
            if "frontier" in ordering.lower():
                # LCV/Frontier: Prefer positions near already-placed values
                frontier_positions = self._get_frontier_positions(available_positions)
                if frontier_positions:
                    chosen_pos = min(frontier_positions, key=lambda p: (p.row, p.col))
                    return (chosen_value, chosen_pos)
            
            # Default to row-col ordering for tie breaking
            chosen_pos = min(available_positions, key=lambda p: (p.row, p.col))
            return (chosen_value, chosen_pos)
        
        elif "frontier" in ordering.lower():
            # Choose positions on the frontier (adjacent to placed values)
            # Pick any value and filter to frontier positions
            first_value = min(candidates.value_to_positions.keys())
            all_positions = list(candidates.value_to_positions[first_value])
            frontier_positions = self._get_frontier_positions(all_positions)
            if frontier_positions:
                chosen_pos = min(frontier_positions, key=lambda p: (p.row, p.col))
                return (first_value, chosen_pos)
        
        # Default: smallest value, row-col ordered position
        chosen_value = min(candidates.value_to_positions.keys())
        available_positions = list(candidates.value_to_positions[chosen_value])
        chosen_pos = min(available_positions, key=lambda p: (p.row, p.col))
        return (chosen_value, chosen_pos)
    
    def _order_values_lcv(self, candidates: 'CandidateModel', pos: Position, values: list) -> list:
        """Order values using Least Constraining Value heuristic.
        
        Args:
            candidates: Current candidate model  
            pos: Position being assigned
            values: Candidate values to order
            
        Returns:
            Values ordered by LCV (least constraining first)
        """
        def count_constraints(value: int) -> int:
            """Count how many other candidates this value would eliminate."""
            constraint_count = 0
            
            # Check all other positions
            for other_pos, other_values in candidates.pos_to_values.items():
                if other_pos == pos:
                    continue
                
                # Would this assignment eliminate this value from other positions?
                if value in other_values:
                    # Check if positions are adjacent (value constraint)
                    neighbors = self.puzzle.grid.neighbors_of(pos)
                    if other_pos in neighbors:
                        constraint_count += 1
            
            return constraint_count
        
        # Sort by constraint count (ascending - least constraining first)
        return sorted(values, key=count_constraints)
    
    def _get_frontier_positions(self, positions: list) -> list:
        """Get positions that are adjacent to already-placed values.
        
        Args:
            positions: Candidate positions to filter
            
        Returns:
            Subset of positions on the frontier
        """
        frontier = []
        
        for pos in positions:
            neighbors = self.puzzle.grid.neighbors_of(pos)
            
            # Check if any neighbor has a placed value
            for neighbor_pos in neighbors:
                neighbor_cell = self.puzzle.grid.get_cell(neighbor_pos)
                if not neighbor_cell.is_empty():
                    frontier.append(pos)
                    break
        
        return frontier
    
    def _copy_puzzle(self, puzzle: Puzzle) -> Puzzle:
        """Create a deep copy of a puzzle for search.
        
        Args:
            puzzle: Puzzle to copy
            
        Returns:
            Independent copy of the puzzle
        """
        from copy import deepcopy
        return deepcopy(puzzle)
    
    def _copy_solution_to_puzzle(self, source: Puzzle, target: Puzzle) -> None:
        """Copy solution from source puzzle to target puzzle.
        
        Args:
            source: Puzzle with solution
            target: Puzzle to update with solution
        """
        for cell in source.grid.iter_cells():
            target_cell = target.grid.get_cell(cell.pos)
            if not target_cell.given and not target_cell.blocked:
                target_cell.value = cell.value
    
    def _value_exists_in_puzzle(self, puzzle: Puzzle, value: int) -> bool:
        """Check if value exists in a specific puzzle instance.
        
        Args:
            puzzle: Puzzle to check
            value: Value to look for
            
        Returns:
            True if value is already placed in puzzle
        """
        for cell in puzzle.grid.iter_cells():
            if cell.value == value:
                return True
        return False


def validate_solution(puzzle: Puzzle, original_givens: dict) -> dict:
    """
    Validate a solved puzzle against Hidato rules.
    
    Args:
        puzzle: The puzzle to validate
        original_givens: Dict mapping Position -> value for original given cells
        
    Returns:
        Dict with keys:
            - status: 'PASS' or 'FAIL'
            - all_filled: bool - All cells have values
            - givens_preserved: bool - Original givens unchanged
            - contiguous_path: bool - Consecutive values are adjacent
            - values_complete: bool - All values 1..N present exactly once
            - message: str - Human-readable result
    """
    report = {
        'status': 'FAIL',
        'all_filled': True,
        'givens_preserved': True,
        'contiguous_path': True,
        'values_complete': True,
        'message': ''
    }
    
    # Check 1: All cells filled
    for cell in puzzle.grid.iter_cells():
        if cell.is_empty():
            report['all_filled'] = False
            report['message'] = f"Cell at {cell.pos} is empty"
            return report
    
    # Check 2: Givens preserved
    for pos, expected_value in original_givens.items():
        actual_value = puzzle.grid.get_cell(pos).value
        if actual_value != expected_value:
            report['givens_preserved'] = False
            report['message'] = f"Given at {pos} changed from {expected_value} to {actual_value}"
            return report
    
    # Check 3: All values present (no duplicates, no missing)
    placed_values = set()
    value_positions = {}
    for cell in puzzle.grid.iter_cells():
        if cell.value is not None:
            if cell.value in placed_values:
                report['values_complete'] = False
                report['message'] = f"Value {cell.value} appears multiple times"
                return report
            placed_values.add(cell.value)
            value_positions[cell.value] = cell.pos
    
    required_values = set(range(puzzle.constraints.min_value, puzzle.constraints.max_value + 1))
    if placed_values != required_values:
        missing = required_values - placed_values
        extra = placed_values - required_values
        report['values_complete'] = False
        if missing:
            report['message'] = f"Missing values: {sorted(missing)}"
        else:
            report['message'] = f"Extra values: {sorted(extra)}"
        return report
    
    # Check 4: Contiguous path (consecutive values adjacent)
    for value in range(puzzle.constraints.min_value, puzzle.constraints.max_value):
        current_pos = value_positions[value]
        next_pos = value_positions[value + 1]
        
        neighbors = puzzle.grid.neighbors_of(current_pos)
        if next_pos not in neighbors:
            report['contiguous_path'] = False
            report['message'] = f"Values {value} at {current_pos} and {value + 1} at {next_pos} are not adjacent"
            return report
    
    # All checks passed
    report['status'] = 'PASS'
    report['message'] = f"Valid Hidato solution: all {len(placed_values)} values correctly placed in contiguous path"
    return report

