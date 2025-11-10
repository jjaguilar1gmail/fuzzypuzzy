"""Compare old vs new uniqueness checking methods."""

import sys
import time
sys.path.insert(0, '.')

from core.grid import Grid
from core.puzzle import Puzzle
from core.constraints import Constraints
from generate.uniqueness import count_solutions
from generate.uniqueness_staged import create_request, check_uniqueness, UniquenessDecision


def test_comparison_on_puzzle(size: int, num_givens: int, seed: int):
    """Compare old vs new method on a puzzle."""
    print(f"\n{'='*70}")
    print(f"Testing {size}x{size} puzzle with {num_givens} givens (seed={seed})")
    print('='*70)
    
    # Create puzzle
    grid = Grid(rows=size, cols=size, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=size*size, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Place some givens
    import random
    rng = random.Random(seed)
    
    # Always place corners
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    
    puzzle.grid.cells[size-1][size-1].value = size * size
    puzzle.grid.cells[size-1][size-1].given = True
    
    # Place additional random givens
    placed = 2
    attempts = 0
    max_attempts = num_givens * 10  # Prevent infinite loop
    
    while placed < num_givens and attempts < max_attempts:
        attempts += 1
        row = rng.randint(0, size-1)
        col = rng.randint(0, size-1)
        if puzzle.grid.cells[row][col].value == 0:
            # Place a value proportional to position
            value = ((row * size) + col + 1)  # Deterministic value based on position
            if value > 0 and value <= size * size:
                puzzle.grid.cells[row][col].value = value
                puzzle.grid.cells[row][col].given = True
                placed += 1
    
    actual_givens = sum(1 for row in puzzle.grid.cells for cell in row if cell.given)
    print(f"Puzzle setup: {size}x{size} board, {actual_givens} givens placed")
    
    # Test OLD method
    print(f"\n🔹 OLD METHOD (count_solutions):")
    old_start = time.time()
    old_result = count_solutions(puzzle, cap=2, node_cap=5000, timeout_ms=5000)
    old_elapsed = (time.time() - old_start) * 1000
    
    print(f"  Result: {'UNIQUE' if old_result.is_unique else 'NON-UNIQUE'}")
    print(f"  Solutions found: {old_result.solutions_found}")
    print(f"  Nodes explored: {old_result.nodes}")
    print(f"  Time: {old_elapsed:.1f}ms")
    
    # Test NEW method
    print(f"\n🔸 NEW METHOD (staged uniqueness):")
    new_start = time.time()
    request = create_request(
        puzzle=puzzle,
        size=size,
        adjacency=8,
        difficulty='medium',
        seed=seed,
        enable_early_exit=True,
        enable_probes=False,
        enable_sat=False
    )
    new_result = check_uniqueness(request)
    new_elapsed = (time.time() - new_start) * 1000
    
    print(f"  Decision: {new_result.decision.value.upper()}")
    print(f"  Stage: {new_result.stage_decided}")
    print(f"  Nodes explored: {sum(new_result.nodes_explored.values())}")
    print(f"  Time: {new_elapsed:.1f}ms")
    print(f"  Per-stage timing: {new_result.per_stage_ms}")
    
    # Comparison
    print(f"\n📊 COMPARISON:")
    if new_elapsed < old_elapsed:
        speedup = old_elapsed / new_elapsed if new_elapsed > 0 else float('inf')
        print(f"  ⚡ NEW method FASTER: {speedup:.1f}x speedup")
        print(f"  ⏱️  Time saved: {old_elapsed - new_elapsed:.1f}ms")
    else:
        slowdown = new_elapsed / old_elapsed if old_elapsed > 0 else float('inf')
        print(f"  🐌 NEW method SLOWER: {slowdown:.1f}x slowdown")
        print(f"  ⏱️  Time lost: {new_elapsed - old_elapsed:.1f}ms")
    
    # Check agreement
    old_is_unique = old_result.is_unique
    new_is_unique = new_result.decision == UniquenessDecision.UNIQUE
    new_is_non_unique = new_result.decision == UniquenessDecision.NON_UNIQUE
    
    if new_result.decision == UniquenessDecision.INCONCLUSIVE:
        print(f"  ℹ️  NEW method inconclusive (would fallback to old method)")
    elif (old_is_unique and new_is_unique) or (not old_is_unique and new_is_non_unique):
        print(f"  ✅ Methods AGREE on result")
    else:
        print(f"  ⚠️  Methods DISAGREE:")
        print(f"      Old: {'UNIQUE' if old_is_unique else 'NON-UNIQUE'}")
        print(f"      New: {new_result.decision.value.upper()}")
    
    return {
        'old_time': old_elapsed,
        'new_time': new_elapsed,
        'old_unique': old_is_unique,
        'new_decision': new_result.decision,
        'agree': (old_is_unique and new_is_unique) or (not old_is_unique and new_is_non_unique) or new_result.decision == UniquenessDecision.INCONCLUSIVE
    }


def main():
    """Run comparison tests."""
    print("=" * 70)
    print("UNIQUENESS CHECKER COMPARISON: Old vs New")
    print("=" * 70)
    
    results = []
    
    # Test 1: Small puzzle (4x4) with few givens - likely non-unique
    results.append(test_comparison_on_puzzle(size=4, num_givens=3, seed=42))
    
    # Test 2: Small puzzle (4x4) with more givens - maybe unique
    results.append(test_comparison_on_puzzle(size=4, num_givens=6, seed=123))
    
    # Test 3: Medium puzzle (5x5) with few givens
    results.append(test_comparison_on_puzzle(size=5, num_givens=4, seed=99))
    
    # Test 4: Medium puzzle (5x5) with more givens
    results.append(test_comparison_on_puzzle(size=5, num_givens=8, seed=456))
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    
    total_old_time = sum(r['old_time'] for r in results)
    total_new_time = sum(r['new_time'] for r in results)
    agreements = sum(1 for r in results if r['agree'])
    
    print(f"\nTotal time:")
    print(f"  Old method: {total_old_time:.1f}ms")
    print(f"  New method: {total_new_time:.1f}ms")
    
    if total_new_time < total_old_time:
        speedup = total_old_time / total_new_time
        print(f"  ⚡ Overall speedup: {speedup:.1f}x")
    else:
        slowdown = total_new_time / total_old_time
        print(f"  🐌 Overall slowdown: {slowdown:.1f}x")
    
    print(f"\nAgreement: {agreements}/{len(results)} tests")
    print(f"  {'✅ All methods agree!' if agreements == len(results) else '⚠️ Some disagreements found'}")
    
    print(f"\n{'='*70}")


if __name__ == '__main__':
    main()
