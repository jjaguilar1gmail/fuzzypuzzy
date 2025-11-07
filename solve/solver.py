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
    
    def __init__(self, solved: bool, steps: list[SolverStep], message: str = "", solved_puzzle: 'Puzzle' = None):
        self.solved = solved
        self.steps = steps
        self.message = message
        self.solved_puzzle = solved_puzzle

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
                return SolverResult(False, self.steps, f"Contradiction detected at iteration {iteration}", self.puzzle)
            
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
                return SolverResult(False, self.steps, f"Adjacency contradiction at iteration {iteration}", self.puzzle)
            
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
            if not cell.is_empty():
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
                regions.build_regions(self.puzzle)
                corridors.invalidate_cache()
                degrees.build_degree_index(self.puzzle)
            
            # Check if solved
            if self._is_solved():
                return SolverResult(True, self.steps, f"Solved using logic_v2 in {iteration} iterations", self.puzzle)
            
            # If no progress, stop
            if not progress_made:
                break
        
        return SolverResult(False, self.steps, f"Stuck after {iteration} iterations using logic_v2 - no more logical moves", self.puzzle)
    
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
        
        def apply_logic_v2(puzzle_state) -> bool:
            """Apply all logic_v2 techniques to current puzzle state."""
            # Create solver instance for this state
            temp_solver = Solver(puzzle_state)
            
            # Apply logic_v2 techniques until no progress
            result = temp_solver._solve_logic_v2(
                max_logic_passes=max_logic_passes,
                tie_break=tie_break,
                enable_island_elim=enable_island_elim,
                enable_segment_bridging=enable_segment_bridging,
                enable_degree_prune=enable_degree_prune
            )
            
            # Copy steps to main solver
            self.steps.extend(temp_solver.steps)
            
            return result.solved
        
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
            
            # Apply all logical techniques first
            if apply_logic_v2(puzzle_state):
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
            
            # Choose next variable using heuristics
            best_pos = self._choose_search_variable(candidates, ordering)
            if best_pos is None:
                return False
            
            # Get candidate values for chosen position
            candidate_values = list(candidates.pos_to_values[best_pos])
            
            # Order values using LCV (Least Constraining Value) if enabled
            if "lcv" in ordering.lower():
                candidate_values = self._order_values_lcv(candidates, best_pos, candidate_values)
            
            # Try each candidate value
            for value in candidate_values:
                # Check if value is already placed (safety check)
                if self._value_exists_in_puzzle(puzzle_state, value):
                    continue
                
                # Create new puzzle state with this assignment
                new_puzzle = self._copy_puzzle(puzzle_state)
                new_cell = new_puzzle.grid.get_cell(best_pos)
                new_cell.value = value
                
                # Record the guess
                step = SolverStep(best_pos, value, f"Search guess: trying {value} at depth {depth}")
                self.steps.append(step)
                
                # Recursive search
                if search_recursive(new_puzzle, depth + 1):
                    # Solution found! Update original puzzle
                    self._copy_solution_to_puzzle(new_puzzle, self.puzzle)
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
            return SolverResult(True, self.steps, message, self.puzzle)
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
            return SolverResult(False, self.steps, message, self.puzzle)
    
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
                            progress = True
                            # Note: Don't place values here, just eliminate impossible candidates
        
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
        
        # Get sequence gaps that need bridging
        gaps = corridors.get_all_sequence_gaps(self.puzzle)
        
        for start_value, end_value, gap_size in gaps:
            if gap_size > 1:  # Only process gaps that need bridging
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
                                progress = True
        
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
                    progress = True
        
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
    
    def _choose_search_variable(self, candidates: 'CandidateModel', ordering: str) -> Position | None:
        """Choose next variable for search using heuristics.
        
        Args:
            candidates: Current candidate model
            ordering: Search ordering strategy
            
        Returns:
            Position to branch on, or None if no candidates
        """
        if not candidates.pos_to_values:
            return None
        
        if "mrv" in ordering.lower():
            # MRV: Choose position with Minimum Remaining Values
            min_candidates = min(len(vals) for vals in candidates.pos_to_values.values())
            mrv_positions = [pos for pos, vals in candidates.pos_to_values.items() 
                           if len(vals) == min_candidates]
            
            if "frontier" in ordering.lower():
                # Prefer positions near already-placed values
                frontier_positions = self._get_frontier_positions(mrv_positions)
                if frontier_positions:
                    return min(frontier_positions, key=lambda p: (p.row, p.col))
            
            # Default to row-col ordering for tie breaking
            return min(mrv_positions, key=lambda p: (p.row, p.col))
        
        elif "frontier" in ordering.lower():
            # Choose positions on the frontier (adjacent to placed values)
            all_positions = list(candidates.pos_to_values.keys())
            frontier_positions = self._get_frontier_positions(all_positions)
            if frontier_positions:
                return min(frontier_positions, key=lambda p: (p.row, p.col))
        
        # Default: row-col ordering
        all_positions = list(candidates.pos_to_values.keys())
        return min(all_positions, key=lambda p: (p.row, p.col))
    
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
