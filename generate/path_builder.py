"""Generate module: PathBuilder

Contains the PathBuilder class for building paths during generation.
"""
from dataclasses import dataclass, field
from typing import Optional
from core.position import Position
from core.grid import Grid
from util.rng import RNG


@dataclass
class PathBuildSettings:
    """Settings for path building (T003)."""
    mode: str = "serpentine"
    max_time_ms: Optional[int] = None
    max_restarts: int = 10
    rng: Optional[RNG] = None
    blocked: Optional[list[tuple[int, int]]] = None


@dataclass
class PathBuildResult:
    """Result from path building attempt (T003)."""
    ok: bool
    reason: str  # success | timeout | exhausted_restarts | coverage_below_threshold | partial_accepted
    coverage: float  # 0.0-1.0
    positions: list[Position]
    metrics: dict = field(default_factory=dict)  # path_build_ms, turn_count, etc.


class PathBuilder:
    """Builds solution paths for puzzle generation.
    
    T027: Branch factor measurement could be added by tracking:
    - Average neighbor count at each step
    - Choice points where multiple valid moves exist
    - This would help quantify mask impact on path construction
    """
    
    @staticmethod
    def build(grid: Grid, mode="serpentine", rng=None, blocked=None, settings=None):
        """Build a complete solution path on the grid.
        
        Args:
            grid: Grid to fill with path
            mode: Path building mode ("serpentine", "random_walk", "backbite_v1", "random_walk_v2")
            rng: Random number generator (for random_walk mode)
            blocked: Optional list of (row, col) blocked positions
            settings: Optional PathBuildSettings for advanced configuration
            
        Returns:
            PathBuildResult with positions, coverage, reason, and metrics
        """
        import time
        start_time = time.time()
        
        # Legacy list return for compatibility
        if mode == "serpentine":
            path = PathBuilder._build_serpentine(grid, blocked)
            elapsed_ms = (time.time() - start_time) * 1000
            return PathBuildResult(
                ok=True,
                reason="success",
                coverage=1.0,
                positions=path,
                metrics={"path_build_ms": elapsed_ms}
            )
        elif mode == "random_walk":
            # T045: Emit deprecation warning
            import sys
            print("⚠️  WARNING: 'random_walk' is deprecated and may hang on larger grids", file=sys.stderr)
            print("    Recommended alternatives:", file=sys.stderr)
            print("      - 'backbite_v1': Fast and diverse (recommended)", file=sys.stderr)
            print("      - 'random_walk_v2': Smart random walk with Warnsdorff heuristic", file=sys.stderr)
            
            path = PathBuilder._build_random_walk(grid, rng, blocked)
            elapsed_ms = (time.time() - start_time) * 1000
            return PathBuildResult(
                ok=True,
                reason="success",
                coverage=1.0,
                positions=path,
                metrics={"path_build_ms": elapsed_ms}
            )
        elif mode == "backbite_v1":
            path = PathBuilder._build_backbite_v1(grid, rng, blocked)
            elapsed_ms = (time.time() - start_time) * 1000
            return PathBuildResult(
                ok=True,
                reason="success",
                coverage=1.0,
                positions=path,
                metrics={"path_build_ms": elapsed_ms}
            )
        elif mode == "random_walk_v2":
            path = PathBuilder._build_random_walk_v2(grid, rng, blocked)
            elapsed_ms = (time.time() - start_time) * 1000
            return PathBuildResult(
                ok=True,
                reason="success",
                coverage=1.0,
                positions=path,
                metrics={"path_build_ms": elapsed_ms}
            )
        else:
            raise ValueError(f"Unknown path mode: {mode}")
    
    @staticmethod
    def _build_backbite_v1(grid: Grid, rng, blocked=None, max_time_ms=None):
        """Build path using backbite algorithm (T013-T016).
        
        Backbite move: Pick an endpoint E, find a grid-neighbor N of E that's in the path.
        Cut the path at N, reverse the segment from N to E, making N the new endpoint.
        The path becomes: [start...N-1] + reversed[N...E] + continue
        This ensures E is now adjacent to both its new neighbors (N-1 and what was before N).
        
        Args:
            grid: Grid to fill
            rng: Random number generator
            blocked: Blocked cells
            max_time_ms: Time budget (default: tiered by size)
            
        Returns:
            List of positions in solution order
        """
        import time
        
        start_time = time.time()
        
        # T015: Tiered time budget if not specified
        if max_time_ms is None:
            size = grid.rows
            if size <= 6:
                max_time_ms = 2000
            elif size <= 8:
                max_time_ms = 4000
            else:
                max_time_ms = 6000
        
        # Initialize with serpentine baseline (guarantees Hamiltonian)
        path = PathBuilder._build_serpentine(grid, blocked)
        if not path:
            return path
        
        # Budget: min(size^3, ~half time budget to allow for mutations)
        size = grid.rows
        budget_steps = min(size ** 3, max_time_ms // 2)
        
        # Convergence: early exit if no change for size*2 steps
        no_change_limit = size * 2
        steps_no_change = 0
        last_path_hash = hash(tuple(path))
        
        blocked_set = set(blocked) if blocked else set()
        
        for step in range(budget_steps):
            # T015: Check timeout
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > max_time_ms:
                break
            
            # Pick random endpoint (head=0 or tail=last)
            is_head = rng.choice([True, False])
            
            if is_head:
                endpoint = path[0]
                # For head, we'll reverse from some position to position 0
            else:
                endpoint = path[-1]
                # For tail, we'll reverse from position len-1 to some earlier position
            
            # Get all grid neighbors of endpoint
            all_neighbors = grid.neighbors_of(endpoint)
            
            # Find neighbors that are in path (excluding immediate path neighbor)
            candidates = []
            for neighbor in all_neighbors:
                if (neighbor.row, neighbor.col) in blocked_set:
                    continue
                try:
                    neighbor_idx = path.index(neighbor)
                except ValueError:
                    continue  # Not in path
                
                # Skip the immediate path neighbor
                if is_head and neighbor_idx == 1:
                    continue
                if not is_head and neighbor_idx == len(path) - 2:
                    continue
                
                # Valid candidate
                candidates.append((neighbor, neighbor_idx))
            
            if not candidates:
                steps_no_change += 1
                if steps_no_change >= no_change_limit:
                    break
                continue
            
            # Pick random candidate
            neighbor, neighbor_idx = rng.choice(candidates)
            
            # Perform backbite: reverse the segment
            # The key is that after reversal, endpoint becomes adjacent to neighbor's previous neighbor
            if is_head:
                # Reversing from 0 to neighbor_idx means:
                # Old: path[0], path[1], ..., path[neighbor_idx], path[neighbor_idx+1], ...
                # After reversing [0:neighbor_idx+1]:
                # New: path[neighbor_idx], ..., path[1], path[0], path[neighbor_idx+1], ...
                # Now path[neighbor_idx] is first, and path[0] is followed by path[neighbor_idx+1]
                # For this to be valid, path[0] must be grid-adjacent to path[neighbor_idx+1]
                
                # Check if this move is valid (will path[0] be adjacent to path[neighbor_idx+1]?)
                if neighbor_idx + 1 < len(path):
                    next_after_segment = path[neighbor_idx + 1]
                    if endpoint not in grid.neighbors_of(next_after_segment):
                        continue  # Invalid move, skip
                
                # Valid move: reverse
                path[:neighbor_idx+1] = list(reversed(path[:neighbor_idx+1]))
            else:
                # Reversing from neighbor_idx to end means:
                # Old: ..., path[neighbor_idx-1], path[neighbor_idx], ..., path[-1]
                # After reversing [neighbor_idx:]:
                # New: ..., path[neighbor_idx-1], path[-1], ..., path[neighbor_idx]
                # Now path[-1] is adjacent to path[neighbor_idx-1], and path[neighbor_idx] is last
                # For this to be valid, path[-1] (endpoint) must be grid-adjacent to path[neighbor_idx-1]
                
                # Check if this move is valid
                if neighbor_idx > 0:
                    prev_before_segment = path[neighbor_idx - 1]
                    if endpoint not in grid.neighbors_of(prev_before_segment):
                        continue  # Invalid move, skip
                
                # Valid move: reverse
                path[neighbor_idx:] = list(reversed(path[neighbor_idx:]))
            
            # Check for change
            new_hash = hash(tuple(path))
            if new_hash == last_path_hash:
                steps_no_change += 1
                if steps_no_change >= no_change_limit:
                    break
            else:
                steps_no_change = 0
                last_path_hash = new_hash
        
        # Re-assign values to reflect final path order
        for i, pos in enumerate(path, 1):
            cell = grid.get_cell(pos)
            cell.value = i
        
        return path
        
        # Re-assign values to reflect final path order
        for i, pos in enumerate(path, 1):
            cell = grid.get_cell(pos)
            cell.value = i
        
        return path
    
    @staticmethod
    def _build_serpentine(grid: Grid, blocked=None):
        """Build a serpentine (snake) path across the grid.
        
        Goes left-to-right on even rows, right-to-left on odd rows.
        Returns positions in order 1, 2, 3, ..., N.
        Skips blocked cells if provided.
        
        Args:
            grid: Grid to fill
            blocked: Optional list of (row, col) blocked positions
            
        Returns:
            List of positions in solution order (T006: still returns list for compat)
        """
        blocked_set = set(blocked) if blocked else set()
        path = []
        value = 1
        prev_pos = None
        
        for row in range(grid.rows):
            if row % 2 == 0:  # Even rows: left to right
                cols = range(grid.cols)
            else:  # Odd rows: right to left
                cols = range(grid.cols - 1, -1, -1)
            
            for col in cols:
                pos = Position(row, col)
                
                # Skip blocked cells
                if (row, col) in blocked_set:
                    continue
                    
                cell = grid.get_cell(pos)
                if not cell.blocked:
                    # Check adjacency with previous position
                    if prev_pos is not None:
                        dr = abs(pos.row - prev_pos.row)
                        dc = abs(pos.col - prev_pos.col)
                        is_adjacent = (dr <= 1 and dc <= 1 and (dr + dc) > 0)
                        
                        if not is_adjacent:
                            # Blocked cells created a non-adjacent jump - path is invalid
                            import sys
                            print(f"WARNING: Serpentine path with blocks creates non-adjacent jump "
                                  f"from {(prev_pos.row, prev_pos.col)} to {(pos.row, pos.col)}", file=sys.stderr)
                            # Return empty path to signal failure
                            return []
                    
                    cell.value = value
                    path.append(pos)
                    prev_pos = pos
                    value += 1
        
        return path
    
    @staticmethod
    def _build_random_walk(grid: Grid, rng, blocked=None):
        """Build a random Hamiltonian path using backtracking.
        
        Args:
            grid: Grid to fill
            rng: Random number generator for reproducibility
            blocked: Optional list of (row, col) blocked positions
            
        Returns:
            List of positions in solution order
        """
        blocked_set = set(blocked) if blocked else set()
        
        # Find all valid (non-blocked) positions
        valid_positions = []
        for row in range(grid.rows):
            for col in range(grid.cols):
                if (row, col) not in blocked_set:
                    pos = Position(row, col)
                    cell = grid.get_cell(pos)
                    if not cell.blocked:
                        valid_positions.append(pos)
        
        if not valid_positions:
            return []
        
        # Backtracking search for Hamiltonian path
        path = []
        visited = set()
        
        def get_neighbors(pos):
            """Get unvisited valid neighbors, respecting grid adjacency rules."""
            # Use grid's built-in neighbor finding (respects allow_diagonal setting)
            all_neighbors = grid.neighbors_of(pos)
            
            # Filter to unvisited and non-blocked
            neighbors = [
                neighbor_pos for neighbor_pos in all_neighbors
                if neighbor_pos not in visited 
                and (neighbor_pos.row, neighbor_pos.col) not in blocked_set
            ]
            
            # Shuffle for randomness
            rng.shuffle(neighbors)
            return neighbors
        
        def backtrack(pos):
            """Recursive backtracking."""
            visited.add(pos)
            path.append(pos)
            
            # Success if we've visited all valid positions
            if len(path) == len(valid_positions):
                return True
            
            # Try neighbors
            for neighbor in get_neighbors(pos):
                if backtrack(neighbor):
                    return True
            
            # Backtrack
            visited.remove(pos)
            path.pop()
            return False
        
        # Start from random position
        start_pos = rng.choice(valid_positions)
        if backtrack(start_pos):
            # Assign values to path
            for i, pos in enumerate(path, 1):
                cell = grid.get_cell(pos)
                cell.value = i
            return path
        
        # Fallback to serpentine if random walk fails
        return PathBuilder._build_serpentine(grid, blocked)
    
    @staticmethod
    def _build_random_walk_v2(grid: Grid, rng, blocked=None, max_time_ms=None, max_restarts=5):
        """Build path using random walk with Warnsdorff heuristic (T022-T027).
        
        Warnsdorff: Prioritize neighbors with fewest onward options (reduces dead ends).
        Includes fragmentation detection and bounded retries.
        
        Args:
            grid: Grid to fill
            rng: Random number generator
            blocked: Blocked cells
            max_time_ms: Time budget (default: tiered by size)
            max_restarts: Maximum restart attempts (default: 5)
            
        Returns:
            List of positions in solution order
        """
        import time
        
        start_time = time.time()
        
        # T025: Tiered time budget if not specified
        if max_time_ms is None:
            size = grid.rows
            if size <= 6:
                max_time_ms = 3000
            elif size <= 8:
                max_time_ms = 5000
            else:
                max_time_ms = 8000
        
        blocked_set = set(blocked) if blocked else set()
        
        # Find all valid positions
        valid_positions = []
        for row in range(grid.rows):
            for col in range(grid.cols):
                if (row, col) not in blocked_set:
                    pos = Position(row, col)
                    cell = grid.get_cell(pos)
                    if not cell.blocked:
                        valid_positions.append(pos)
        
        if not valid_positions:
            return []
        
        target_count = len(valid_positions)
        max_nodes = 5000  # T025: Node limit per attempt
        
        def count_unvisited_neighbors(pos, visited):
            """Count unvisited neighbors (for Warnsdorff heuristic)."""
            neighbors = grid.neighbors_of(pos)
            return sum(
                1 for n in neighbors
                if n not in visited and (n.row, n.col) not in blocked_set
            )
        
        def check_fragmentation(pos, visited):
            """Check if adding pos would isolate a small region (T023)."""
            # Simplified heuristic: only block moves that would create isolated single cells
            # (More aggressive checks prevent completion)
            neighbors = grid.neighbors_of(pos)
            for neighbor in neighbors:
                if neighbor in visited or (neighbor.row, neighbor.col) in blocked_set:
                    continue
                # Count how many unvisited neighbors this neighbor would have after we visit pos
                future_visited = visited | {pos}
                future_count = sum(
                    1 for n2 in grid.neighbors_of(neighbor)
                    if n2 not in future_visited and (n2.row, n2.col) not in blocked_set
                )
                # Only reject if it would completely isolate a single cell
                if future_count == 0 and len(path) + 2 < target_count:  # Allow on last few moves
                    return True
            return False
        
        def get_neighbors_warnsdorff(pos, visited):
            """Get neighbors sorted by Warnsdorff heuristic (T022)."""
            neighbors = [
                n for n in grid.neighbors_of(pos)
                if n not in visited and (n.row, n.col) not in blocked_set
            ]
            
            if not neighbors:
                return []
            
            # Sort by fewest onward options (Warnsdorff)
            # Add randomness by shuffling ties
            neighbor_scores = [
                (n, count_unvisited_neighbors(n, visited | {pos}))
                for n in neighbors
            ]
            
            # Group by score and shuffle within groups
            from collections import defaultdict
            by_score = defaultdict(list)
            for n, score in neighbor_scores:
                by_score[score].append(n)
            
            # Build final list: lowest scores first, shuffled within each score
            result = []
            for score in sorted(by_score.keys()):
                group = by_score[score]
                rng.shuffle(group)
                result.extend(group)
            
            return result
        
        # T024: Restart loop
        for restart in range(max_restarts):
            # Check timeout
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > max_time_ms:
                break
            
            path = []
            visited = set()
            nodes_explored = 0
            
            def backtrack(pos):
                nonlocal nodes_explored
                nodes_explored += 1
                
                # T025: Node limit
                if nodes_explored > max_nodes:
                    return False
                
                # Check timeout
                if (time.time() - start_time) * 1000 > max_time_ms:
                    return False
                
                visited.add(pos)
                path.append(pos)
                
                # Success
                if len(path) == target_count:
                    return True
                
                # Try neighbors with Warnsdorff ordering
                for neighbor in get_neighbors_warnsdorff(pos, visited):
                    # T023: Fragmentation check
                    if check_fragmentation(neighbor, visited):
                        continue
                    
                    if backtrack(neighbor):
                        return True
                
                # Backtrack
                visited.remove(pos)
                path.pop()
                return False
            
            # Start from random position each restart
            start_pos = rng.choice(valid_positions)
            if backtrack(start_pos):
                # Success! Assign values
                for i, pos in enumerate(path, 1):
                    cell = grid.get_cell(pos)
                    cell.value = i
                return path
        
        # T026: All restarts exhausted - fallback to serpentine
        return PathBuilder._build_serpentine(grid, blocked)
