"""Generate module: CluePlacer

Contains the CluePlacer class for placing clues in generated puzzles.
"""
from core.position import Position
from util.rng import RNG

class CluePlacer:
    """Places clues (givens) in generated puzzles."""
    
    @staticmethod
    def choose(grid, path, mode="even", rng=None):
        """Choose which cells to mark as givens.
        
        Args:
            grid: Grid with complete solution
            path: List of positions in solution order
            mode: Clue placement mode ("even")
            rng: Random number generator
            
        Returns:
            List of positions to mark as givens
        """
        if mode == "even":
            return CluePlacer._choose_even(grid, path, rng)
        else:
            raise ValueError(f"Unknown clue mode: {mode}")
    
    @staticmethod
    def _choose_even(grid, path, rng=None):
        """Choose evenly-spaced clues plus 1 and N.
        
        For easy puzzles, place givens at:
        - First position (value 1)
        - Last position (value N) 
        - A few evenly-spaced positions in between
        """
        if not path:
            return []
        
        givens = []
        n = len(path)
        
        # Always include first and last
        givens.append(path[0])   # Value 1
        if n > 1:
            givens.append(path[-1])  # Value N
        
        # Add evenly-spaced clues in between
        if n > 4:  # Only if grid is big enough
            step = n // 4  # Roughly every 25% of the way
            for i in range(step, n - step, step):
                if path[i] not in givens:
                    givens.append(path[i])
        
        return givens
    
    @staticmethod
    def mark_givens(grid, given_positions):
        """Mark the specified positions as givens."""
        for pos in given_positions:
            cell = grid.get_cell(pos)
            cell.given = True
