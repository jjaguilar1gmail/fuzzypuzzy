"""Integration tests for staged uniqueness validation feature.

Tests the complete pipeline with different configurations.
"""

import sys
sys.path.insert(0, '.')

from core.grid import Grid
from core.puzzle import Puzzle
from core.constraints import Constraints
from generate.uniqueness_staged import (
    create_request,
    check_uniqueness,
    enable_stage,
    disable_stage,
    UniquenessCheckRequest,
    UniquenessDecision,
    UniquenessConfig
)


def test_create_request_helper():
    """Test the create_request helper function."""
    print("\n=== Test: create_request helper ===")
    
    grid = Grid(rows=7, cols=7, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=49, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Test with defaults
    request = create_request(
        puzzle=puzzle,
        size=7,
        difficulty='medium',
        seed=42
    )
    
    assert request.size == 7
    assert request.difficulty == 'medium'
    assert request.total_budget_ms == 500  # Medium default
    assert request.seed == 42
    assert request.strategy_flags['early_exit'] == True
    assert request.strategy_flags['probes'] == True
    assert request.strategy_flags['sat'] == False
    
    print("✓ create_request works with defaults")
    
    # Test with custom stage flags
    request2 = create_request(
        puzzle=puzzle,
        size=7,
        enable_early_exit=False,
        enable_sat=True
    )
    
    assert request2.strategy_flags['early_exit'] == False
    assert request2.strategy_flags['sat'] == True
    
    print("✓ create_request respects custom stage flags")


def test_enable_disable_stages():
    """Test programmatic API for stage control."""
    print("\n=== Test: enable/disable stages ===")
    
    grid = Grid(rows=7, cols=7, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=49, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    request = create_request(puzzle=puzzle, size=7)
    
    # Initially probes enabled
    assert request.strategy_flags['probes'] == True
    
    # Disable probes
    disable_stage(request, 'probes')
    assert request.strategy_flags['probes'] == False
    
    # Enable SAT
    enable_stage(request, 'sat')
    assert request.strategy_flags['sat'] == True
    
    print("✓ enable_stage and disable_stage work correctly")
    
    # Test error handling
    try:
        enable_stage(request, 'invalid_stage')
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert 'Unknown stage' in str(e)
        print("✓ Raises error for invalid stage name")


def test_config_validation():
    """Test UniquenessConfig validation."""
    print("\n=== Test: config validation ===")
    
    # Test from_difficulty factory
    config = UniquenessConfig.from_difficulty(size=7, difficulty='easy', seed=123)
    assert config.total_budget_ms == 600  # Easy budget
    assert config.difficulty == 'easy'
    assert config.seed == 123
    
    print("✓ from_difficulty creates correct config")
    
    # Test small board budget
    config_small = UniquenessConfig.from_difficulty(size=5, difficulty='hard')
    assert config_small.total_budget_ms == 100  # Small board override
    
    print("✓ Small board gets 100ms budget")
    
    # Test validate_budget_allocation
    config.validate_budget_allocation()
    print("✓ Budget validation passes for default config")
    
    # Test get_stage_budget
    early_budget = config.get_stage_budget('early_exit')
    assert early_budget == int(600 * 0.4)  # 40% of 600ms
    
    print("✓ get_stage_budget calculates correctly")


def test_end_to_end_pipeline():
    """Test complete pipeline with a 7x7 puzzle."""
    print("\n=== Test: end-to-end pipeline ===")
    
    grid = Grid(rows=7, cols=7, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=49, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Add a few givens
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    puzzle.grid.cells[6][6].value = 49
    puzzle.grid.cells[6][6].given = True
    
    # Run with all stages enabled (but SAT will be skipped - no solver)
    request = create_request(
        puzzle=puzzle,
        size=7,
        difficulty='medium',
        seed=42,
        enable_early_exit=True,
        enable_probes=True,
        enable_sat=False
    )
    
    result = check_uniqueness(request)
    
    # Verify result structure
    assert result is not None
    assert result.decision in [UniquenessDecision.UNIQUE, UniquenessDecision.NON_UNIQUE, UniquenessDecision.INCONCLUSIVE]
    assert result.elapsed_ms >= 0
    assert isinstance(result.per_stage_ms, dict)
    assert isinstance(result.nodes_explored, dict)
    assert result.probes_run >= 0
    
    print(f"✓ Pipeline completed: decision={result.decision.value}")
    print(f"  Stage decided: {result.stage_decided}")
    print(f"  Time: {result.elapsed_ms}ms")
    print(f"  Per-stage: {result.per_stage_ms}")
    
    # Since early_exit and probes return None (placeholder search), should be inconclusive
    assert result.decision == UniquenessDecision.INCONCLUSIVE
    assert 'stages_exhausted' in result.stage_decided or 'placeholder' in result.stage_decided
    
    print("✓ Returns inconclusive when all stages inconclusive")


def test_budget_enforcement():
    """Test that stages respect budget limits."""
    print("\n=== Test: budget enforcement ===")
    
    grid = Grid(rows=7, cols=7, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=49, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    
    # Use very small budget
    request = UniquenessCheckRequest(
        puzzle=puzzle,
        size=7,
        adjacency=8,
        difficulty='easy',
        total_budget_ms=50,  # Very tight
        seed=42
    )
    
    result = check_uniqueness(request)
    
    # Should complete within budget (even with overhead)
    assert result.elapsed_ms <= 100  # Allow some overhead
    
    print(f"✓ Completed within budget: {result.elapsed_ms}ms <= 100ms")


def test_determinism():
    """Test that same seed produces identical results."""
    print("\n=== Test: determinism ===")
    
    grid = Grid(rows=7, cols=7, allow_diagonal=True)
    constraints = Constraints(min_value=1, max_value=49, allow_diagonal=True)
    puzzle = Puzzle(grid=grid, constraints=constraints)
    puzzle.grid.cells[0][0].value = 1
    puzzle.grid.cells[0][0].given = True
    
    # Run twice with same seed
    request1 = create_request(puzzle=puzzle, size=7, seed=42)
    result1 = check_uniqueness(request1)
    
    request2 = create_request(puzzle=puzzle, size=7, seed=42)
    result2 = check_uniqueness(request2)
    
    # Should have identical decisions
    assert result1.decision == result2.decision
    assert result1.stage_decided == result2.stage_decided
    
    print("✓ Same seed produces identical decisions")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Staged Uniqueness Validation - Integration Tests")
    print("=" * 60)
    
    try:
        test_create_request_helper()
        test_enable_disable_stages()
        test_config_validation()
        test_end_to_end_pipeline()
        test_budget_enforcement()
        test_determinism()
        
        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
