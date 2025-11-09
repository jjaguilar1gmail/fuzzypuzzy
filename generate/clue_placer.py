"""Generate module: CluePlacer

Contains the CluePlacer class for placing clues in generated puzzles.
"""
from core.position import Position
from util.rng import RNG


class CluePlacer:
    """Places clues (givens) in generated puzzles."""
    
    @staticmethod
    def choose(grid, path, mode="even", rng=None, turn_anchors=True, symmetry=None):
        """Choose which cells to mark as givens.
        
        Args:
            grid: Grid with complete solution
            path: List of positions in solution order
            mode: Clue placement mode ("even" or "anchor_removal_v1")
            rng: Random number generator
            turn_anchors: Whether to include turn points as anchors
            symmetry: Optional symmetry mode ("rotational", "horizontal", or None)
            
        Returns:
            List of positions to mark as givens
        """
        if mode == "even":
            return CluePlacer._choose_even(grid, path, rng)
        elif mode == "anchor_removal_v1":
            return CluePlacer._choose_anchors(grid, path, rng, turn_anchors, symmetry)
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
    def _choose_anchors(grid, path, rng, turn_anchors=True, symmetry=None):
        """Choose anchor-based givens: 1, N, and turn points.
        
        Args:
            grid: Grid with solution
            path: Solution path
            rng: RNG for randomness
            turn_anchors: Include turn points (path direction changes)
            symmetry: Optional symmetry constraint
            
        Returns:
            List of anchor positions
        """
        if not path:
            return []
        
        givens = []
        
        # Always include first and last
        givens.append(path[0])   # Value 1
        if len(path) > 1:
            givens.append(path[-1])  # Value N
        
        # Add turn anchors if requested
        if turn_anchors and len(path) > 2:
            for i in range(1, len(path) - 1):
                prev_pos = path[i - 1]
                curr_pos = path[i]
                next_pos = path[i + 1]
                
                # Check if direction changes
                dr1 = curr_pos.row - prev_pos.row
                dc1 = curr_pos.col - prev_pos.col
                dr2 = next_pos.row - curr_pos.row
                dc2 = next_pos.col - curr_pos.col
                
                if (dr1, dc1) != (dr2, dc2):
                    givens.append(curr_pos)
        
        # Apply symmetry if requested
        if symmetry:
            givens = CluePlacer._apply_symmetry(givens, grid, symmetry)
        
        return list(set(givens))  # Remove duplicates
    
    @staticmethod
    def _apply_symmetry(givens, grid, mode):
        """Apply symmetry constraint to givens.
        
        Args:
            givens: List of positions
            grid: Grid
            mode: "rotational" or "horizontal"
            
        Returns:
            Extended list with symmetric positions
        """
        symmetric_givens = list(givens)
        
        if mode == "rotational":
            # 180-degree rotation around center
            center_r = (grid.rows - 1) / 2.0
            center_c = (grid.cols - 1) / 2.0
            for pos in givens:
                mirror_r = int(2 * center_r - pos.row)
                mirror_c = int(2 * center_c - pos.col)
                if 0 <= mirror_r < grid.rows and 0 <= mirror_c < grid.cols:
                    symmetric_givens.append(Position(mirror_r, mirror_c))
        
        elif mode == "horizontal":
            # Horizontal mirror (flip across vertical center)
            for pos in givens:
                mirror_c = grid.cols - 1 - pos.col
                symmetric_givens.append(Position(pos.row, mirror_c))
        
        return symmetric_givens
    
    @staticmethod
    def mark_givens(grid, given_positions):
        """Mark the specified positions as givens."""
        for pos in given_positions:
            cell = grid.get_cell(pos)
            cell.given = True
