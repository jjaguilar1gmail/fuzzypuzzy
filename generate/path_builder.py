"""Generate module: PathBuilder

Contains the PathBuilder class for building paths during generation.
"""
from core.position import Position
from core.grid import Grid
from util.rng import RNG

class PathBuilder:
    """Builds solution paths for puzzle generation."""
    
    @staticmethod
    def build(grid: Grid, mode="serpentine", rng=None):
        """Build a complete solution path on the grid.
        
        Args:
            grid: Grid to fill with path
            mode: Path building mode ("serpentine")
            rng: Random number generator (for future modes)
            
        Returns:
            List of positions in solution order (1 to N)
        """
        if mode == "serpentine":
            return PathBuilder._build_serpentine(grid)
        else:
            raise ValueError(f"Unknown path mode: {mode}")
    
    @staticmethod
    def _build_serpentine(grid: Grid):
        """Build a serpentine (snake) path across the grid.
        
        Goes left-to-right on even rows, right-to-left on odd rows.
        Returns positions in order 1, 2, 3, ..., N.
        """
        path = []
        value = 1
        
        for row in range(grid.rows):
            if row % 2 == 0:  # Even rows: left to right
                cols = range(grid.cols)
            else:  # Odd rows: right to left
                cols = range(grid.cols - 1, -1, -1)
            
            for col in cols:
                pos = Position(row, col)
                cell = grid.get_cell(pos)
                
                # Skip blocked cells (though none in current MVP)
                if not cell.blocked:
                    cell.value = value
                    path.append(pos)
                    value += 1
        
        return path
