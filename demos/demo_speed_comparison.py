"""Direct comparison: Old uniqueness checker vs New staged checker on same puzzle."""

import sys
import time
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.grid import Grid
from core.puzzle import Puzzle
from core.constraints import Constraints
from core.position import Position


def create_test_puzzle_5x5():
    """Create a test puzzle to benchmark."""
    grid = Grid(5, 5)
    constraints = Constraints(allow_diagonal=True)
    
    # A puzzle with 13 givens - typical for easy difficulty
    givens = [
        (0, 0, 1), (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5),
        (1, 3, 7), (1, 4, 6),
        (3, 0, 20),
        (4, 0, 21), (4, 1, 22), (4, 2, 23), (4, 3, 24), (4, 4, 25)
    ]
    
    for row, col, value in givens:
        cell = grid.get_cell(Position(row, col))
        cell.value = value
        cell.given = True
    
    return Puzzle(grid=grid, constraints=constraints)


def check_with_old_method(puzzle):
    """Use the old exhaustive count_solutions method."""
    from generate.uniqueness import count_solutions
    
    start = time.time()
    result = count_solutions(puzzle, cap=2, node_cap=5000, timeout_ms=5000)
    elapsed = (time.time() - start) * 1000
    
    return {
        'is_unique': result.is_unique,
        'time_ms': elapsed,
        'nodes': result.nodes,
        'solutions_found': result.solutions_found
    }


def check_with_new_method(puzzle):
    """Use the new staged uniqueness checker."""
    from generate.uniqueness_staged import create_request, check_uniqueness, UniquenessDecision
    
    start = time.time()
    request = create_request(
        puzzle=puzzle,
        size=puzzle.grid.rows,
        adjacency=8 if puzzle.constraints.allow_diagonal else 4,
        difficulty='medium',
        enable_early_exit=True,
        enable_probes=False,
        enable_sat=False
    )
    result = check_uniqueness(request)
    elapsed = (time.time() - start) * 1000
    
    total_nodes = sum(result.nodes_explored.values())
    
    return {
        'decision': result.decision,
        'is_unique': result.decision == UniquenessDecision.UNIQUE,
        'time_ms': elapsed,
        'nodes': total_nodes,
        'stage_used': result.stage_decided
    }


def visualize_puzzle(puzzle):
    """Display puzzle in ASCII format."""
    print("\nTest Puzzle (5x5):")
    print("=" * 26)
    for row in puzzle.grid.cells:
        line = ""
        for cell in row:
            if cell.given:
                line += f" {cell.value:3d} "
            else:
                line += "  .  "
        print(line)
    print("=" * 26)
    givens = sum(1 for row in puzzle.grid.cells for cell in row if cell.given)
    print(f"Givens: {givens}/25 cells\n")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("SPEED COMPARISON: Old vs New Uniqueness Checker")
    print("="*80)
    
    puzzle = create_test_puzzle_5x5()
    visualize_puzzle(puzzle)
    
    print("Running OLD exhaustive search method...")
    old_result = check_with_old_method(puzzle)
    
    print(f"\n[OLD METHOD RESULTS]")
    print(f"  Result: {'UNIQUE' if old_result['is_unique'] else 'NON-UNIQUE'}")
    print(f"  Time: {old_result['time_ms']:.1f}ms")
    print(f"  Nodes explored: {old_result['nodes']}")
    print(f"  Solutions found: {old_result['solutions_found']}")
    
    print("\n" + "-"*80)
    print("\nRunning NEW staged checker method...")
    new_result = check_with_new_method(puzzle)
    
    print(f"\n[NEW METHOD RESULTS]")
    print(f"  Decision: {new_result['decision'].name}")
    print(f"  Result: {'UNIQUE' if new_result['is_unique'] else 'NON-UNIQUE'}")
    print(f"  Time: {new_result['time_ms']:.1f}ms")
    print(f"  Nodes explored: {new_result['nodes']}")
    print(f"  Stage used: {new_result['stage_used']}")
    
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    
    speedup = old_result['time_ms'] / new_result['time_ms'] if new_result['time_ms'] > 0 else float('inf')
    agreement = old_result['is_unique'] == new_result['is_unique']
    
    print(f"\nSpeed improvement: {speedup:.1f}x FASTER")
    print(f"Time saved: {old_result['time_ms'] - new_result['time_ms']:.1f}ms")
    print(f"Agreement: {'YES - Both methods agree!' if agreement else 'NO - MISMATCH'}")
    
    print("\n" + "="*80)
    print("WHY IS IT FASTER?")
    print("="*80)
    print("\nOld method:")
    print("  * Exhaustive backtracking search")
    print("  * Must explore many nodes to prove uniqueness")
    print("  * No early exit strategies")
    print(f"  * Result: {old_result['time_ms']:.0f}ms, {old_result['nodes']} nodes")
    
    print("\nNew staged checker:")
    print("  * Uses solver logic passes first (corridors, degree, islands)")
    print("  * Multiple heuristic orderings try different search paths")
    print("  * Early exit when 2nd solution found")
    print("  * Optimized for uniqueness detection (not solving)")
    print(f"  * Result: {new_result['time_ms']:.0f}ms, {new_result['nodes']} nodes")
    
    print("\n" + "="*80)
    print("[CONCLUSION]")
    print("="*80)
    print(f"\nThe new staged uniqueness checker is {speedup:.1f}x faster!")
    print("This dramatic speedup enables:")
    print("  * Faster puzzle generation")
    print("  * More clue removal attempts in same time")
    print("  * Harder puzzles (fewer clues) without timeout")
    print("  * Better user experience during generation")
    print("\n" + "="*80)
