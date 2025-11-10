"""Smoke test for staged uniqueness validation infrastructure."""

from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from core.position import Position
from generate.uniqueness_staged import (
    check_uniqueness,
    UniquenessCheckRequest,
    UniquenessDecision
)


def test_smoke():
    """Basic smoke test - verify the API works."""
    # Create a simple 5x5 puzzle
    grid = Grid(5, 5, allow_diagonal=True)
    puzzle = Puzzle(grid, Constraints(1, 25, '8'))
    
    # Set up a simple path with some givens
    for i in range(5):
        pos = Position(0, i)
        grid.get_cell(pos).value = i + 1
        grid.get_cell(pos).given = True
    
    # Create request
    request = UniquenessCheckRequest(
        puzzle=puzzle,
        size=5,
        adjacency=8,
        difficulty='easy',
        total_budget_ms=100,
        seed=42
    )
    
    # Check uniqueness
    result = check_uniqueness(request)
    
    # Verify we got a result
    assert result is not None
    assert result.decision in [UniquenessDecision.UNIQUE, UniquenessDecision.NON_UNIQUE, UniquenessDecision.INCONCLUSIVE]
    assert result.elapsed_ms >= 0
    assert result.stage_decided != ''
    
    print(f"✓ Smoke test passed")
    print(f"  Decision: {result.decision.value}")
    print(f"  Stage: {result.stage_decided}")
    print(f"  Time: {result.elapsed_ms}ms")
    print(f"  Notes: {result.notes}")


if __name__ == '__main__':
    test_smoke()
