"""Generate module: Generator

Contains the Generator class for overall puzzle generation pipeline.
"""
import time
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from .path_builder import PathBuilder
from .clue_placer import CluePlacer
from .validator import Validator
from util.rng import RNG

class Generator:
    """Orchestrates the puzzle generation pipeline."""
    
    @staticmethod
    def generate(rows, cols, difficulty="easy", path_mode="serpentine", 
                clue_mode="even", seed=None):
        """Generate a complete puzzle.
        
        Args:
            rows, cols: Grid dimensions
            difficulty: Difficulty level (affects clue density)
            path_mode: Path building strategy
            clue_mode: Clue placement strategy  
            seed: Random seed for reproducibility
            
        Returns:
            (puzzle: Puzzle, metadata: dict)
        """
        start_time = time.time()
        
        # Initialize RNG
        rng = RNG(seed)
        actual_seed = rng.get_seed()
        
        # Create constraints (8-neighbor for Hidato)
        constraints = Constraints(
            min_value=1,
            max_value=rows * cols,  # No blocked cells in MVP
            allow_diagonal=True,
            must_be_connected=True
        )
        
        # Create grid
        grid = Grid(rows, cols, allow_diagonal=True)
        
        # Generate solution path
        path = PathBuilder.build(grid, mode=path_mode, rng=rng)
        
        # Choose clues
        given_positions = CluePlacer.choose(grid, path, mode=clue_mode, rng=rng)
        
        # Create puzzle (before clearing non-givens)
        puzzle = Puzzle(grid, constraints, difficulty)
        
        # Mark givens
        CluePlacer.mark_givens(grid, given_positions)
        
        # Clear non-givens to create the puzzle
        puzzle.clear_non_givens()
        
        # Validate
        is_valid, issues = Validator.validate_basic(puzzle)
        if not is_valid:
            raise ValueError(f"Generated invalid puzzle: {issues}")
        
        # Generate metadata
        end_time = time.time()
        metadata = {
            "seed": actual_seed,
            "path_mode": path_mode,
            "clue_mode": clue_mode,
            "difficulty": difficulty,
            "size": (rows, cols),
            "num_givens": len(given_positions),
            "timings_ms": {
                "total": round((end_time - start_time) * 1000, 2)
            },
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return puzzle, metadata
