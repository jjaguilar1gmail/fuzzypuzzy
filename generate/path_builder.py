"""Generate module: PathBuilder

Contains the PathBuilder class for building paths during generation.
"""
from core.position import Position
from core.grid import Grid
from util.rng import RNG

class PathBuilder:
    """Builds solution paths for puzzle generation."""
    
    @staticmethod
    def build(grid: Grid, mode="serpentine", rng=None, blocked=None):
        """Build a complete solution path on the grid.
        
        Args:
            grid: Grid to fill with path
            mode: Path building mode ("serpentine" or "random_walk")
            rng: Random number generator (for random_walk mode)
            blocked: Optional list of (row, col) blocked positions
            
        Returns:
            List of positions in solution order (1 to N)
        """
        if mode == "serpentine":
            return PathBuilder._build_serpentine(grid, blocked)
        elif mode == "random_walk":
            return PathBuilder._build_random_walk(grid, rng, blocked)
        else:
            raise ValueError(f"Unknown path mode: {mode}")
    
    @staticmethod
    def _build_serpentine(grid: Grid, blocked=None):
        """Build a serpentine (snake) path across the grid.
        
        Goes left-to-right on even rows, right-to-left on odd rows.
        Returns positions in order 1, 2, 3, ..., N.
        Skips blocked cells if provided.
        
        Args:
            grid: Grid to fill
            blocked: Optional list of (row, col) blocked positions
        """
        blocked_set = set(blocked) if blocked else set()
        path = []
        value = 1
        
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
                    cell.value = value
                    path.append(pos)
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
            """Get unvisited valid neighbors."""
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = pos.row + dr, pos.col + dc
                    if 0 <= r < grid.rows and 0 <= c < grid.cols:
                        neighbor_pos = Position(r, c)
                        if neighbor_pos not in visited and (r, c) not in blocked_set:
                            neighbors.append(neighbor_pos)
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
