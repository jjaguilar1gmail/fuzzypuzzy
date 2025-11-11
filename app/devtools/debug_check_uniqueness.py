"""Debug why check_puzzle_uniqueness isn't rejecting seed 42."""
import os
import sys

THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from generate.generator import Generator
from generate.pruning import _compute_clue_density, check_puzzle_uniqueness
from core.grid import Grid
from core.constraints import Constraints
from core.position import Position
from core.puzzle import Puzzle


def build_puzzle_from_generated(gp):
    """Build a Puzzle object from GeneratedPuzzle for analysis."""
    size = gp.size
    grid = Grid(size, size, allow_diagonal=gp.allow_diagonal)
    
    for r, c in gp.blocked_cells:
        grid.get_cell(Position(r, c)).blocked = True
    
    for r, c, v in gp.givens:
        cell = grid.get_cell(Position(r, c))
        cell.value = v
        cell.given = True
    
    constraints = Constraints(
        min_value=1,
        max_value=len(gp.solution),
        allow_diagonal=gp.allow_diagonal,
        must_be_connected=True
    )
    
    return Puzzle(grid, constraints)


def debug_seed_42():
    """Debug check_puzzle_uniqueness call for seed 42."""
    print("Generating seed 42...")
    gp = Generator.generate_puzzle(
        size=9,
        difficulty="hard",
        path_mode="backbite_v1",
        seed=42,
        allow_diagonal=True,
        structural_repair_enabled=False,
    )
    
    if gp is None:
        print("Generation failed")
        return
    
    puzzle = build_puzzle_from_generated(gp)
    
    # Check conditions
    density = _compute_clue_density(puzzle)
    print(f"\nDensity: {density:.3f}")
    print(f"Allow diagonal: {puzzle.constraints.allow_diagonal}")
    print(f"Grid rows: {puzzle.grid.rows}")
    print(f"Conditions for extra guardrails:")
    print(f"  - allow_diagonal: {puzzle.constraints.allow_diagonal}")
    print(f"  - grid.rows >= 9: {puzzle.grid.rows >= 9}")
    print(f"  - density < 0.30: {density < 0.30}")
    print(f"  ALL conditions met: {puzzle.constraints.allow_diagonal and puzzle.grid.rows >= 9 and density < 0.30}")
    
    # Call check_puzzle_uniqueness
    print(f"\nCalling check_puzzle_uniqueness...")
    result = check_puzzle_uniqueness(puzzle, "logic_v3")
    print(f"Result: {result}")
    
    # If True, the guards didn't reject - why?
    if result:
        print("\n⚠️  Puzzle passed uniqueness check despite having max_gap=50")
        print("This means the density threshold condition is NOT being met!")
        print(f"Density {density:.3f} must be >= 0.30 (SPARSE_DENSITY_THRESHOLD)")


if __name__ == "__main__":
    debug_seed_42()
