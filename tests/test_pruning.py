"""Tests for solver-driven pruning logic.

T18: Unit tests for interval reduction, ordering, and state management.
"""
import pytest
from core.position import Position
from core.cell import Cell
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from generate.pruning import (
    order_removable_clues,
    contract_interval,
    should_fallback_to_linear,
    IntervalState,
    PruningSession,
    PruningStatus,
)


class TestClueOrdering:
    """Test removable clue ordering heuristic (T01)."""
    
    def test_order_removable_clues_excludes_endpoints(self):
        """Endpoints must never be in removable list."""
        path = [Position(0, i) for i in range(5)]
        cells = []
        for i, pos in enumerate(path):
            cells.append(Cell(pos, i + 1, False, True))  # All givens
        
        grid = Grid(1, 5, cells, allow_diagonal=False)
        puzzle = Puzzle(grid, Constraints(1, 5, "4"))
        
        removable = order_removable_clues(puzzle, path)
        
        assert path[0] not in removable
        assert path[-1] not in removable
        assert len(removable) == 3
    
    def test_order_removable_clues_central_first(self):
        """Central clues scored higher for removal than edge clues."""
        path = [Position(0, i) for i in range(7)]
        cells = []
        for i, pos in enumerate(path):
            cells.append(Cell(pos, i + 1, False, True))
        
        grid = Grid(1, 7, cells, allow_diagonal=False)
        puzzle = Puzzle(grid, Constraints(1, 7, "4"))
        
        removable = order_removable_clues(puzzle, path)
        
        # Central position (0,3) should be first
        assert removable[0] == Position(0, 3)
    
    def test_order_removable_clues_empty_path(self):
        """Empty path returns empty list."""
        grid = Grid(2, 2, allow_diagonal=True)
        puzzle = Puzzle(grid, Constraints(1, 4, "8"))
        
        removable = order_removable_clues(puzzle, [])
        
        assert removable == []
    
    def test_order_removable_clues_deterministic(self):
        """Same puzzle/path produces identical ordering."""
        path = [Position(0, i) for i in range(5)]
        cells = []
        for i, pos in enumerate(path):
            cells.append(Cell(pos, i + 1, False, True))
        
        grid = Grid(1, 5, cells, allow_diagonal=False)
        puzzle = Puzzle(grid, Constraints(1, 5, "4"))
        
        removable1 = order_removable_clues(puzzle, path)
        removable2 = order_removable_clues(puzzle, path)
        
        assert removable1 == removable2


class TestIntervalContraction:
    """Test interval reduction logic (T02)."""
    
    def test_contract_interval_on_uniqueness_fail(self):
        """Uniqueness failure shrinks upper bound."""
        state = contract_interval(0, 10, "uniqueness_fail")
        
        assert state.low_index == 0
        assert state.high_index == 4  # mid-1 where mid=(0+10)//2=5
        assert state.contraction_reason == "uniqueness_fail"
    
    def test_contract_interval_on_success(self):
        """Success raises lower bound for more aggressive removal."""
        state = contract_interval(0, 10, "density_met")
        
        assert state.low_index == 6  # mid+1 where mid=5
        assert state.high_index == 10
        assert state.contraction_reason == "density_met"
    
    def test_contract_interval_converges_to_point(self):
        """Repeated contractions converge to single index."""
        low, high = 0, 10
        for _ in range(5):
            state = contract_interval(low, high, "uniqueness_fail")
            low, high = state.low_index, state.high_index
            if low >= high:
                break
        
        assert low >= high - 1


class TestLinearFallback:
    """Test fallback condition (T04)."""
    
    def test_should_fallback_when_below_threshold(self):
        """Fallback triggers when removable count <= K."""
        assert should_fallback_to_linear(6, 6) is True
        assert should_fallback_to_linear(5, 6) is True
        assert should_fallback_to_linear(3, 6) is True
    
    def test_should_not_fallback_when_above_threshold(self):
        """No fallback when removable count > K."""
        assert should_fallback_to_linear(7, 6) is False
        assert should_fallback_to_linear(10, 6) is False


class TestPruningSession:
    """Test session metrics tracking (T12)."""
    
    def test_pruning_session_initial_state(self):
        """Session starts with zero counters."""
        session = PruningSession()
        
        assert session.iteration_count == 0
        assert session.uniqueness_failures == 0
        assert session.repairs_used == 0
        assert session.interval_contractions == 0
        assert session.timeout_occurred is False
    
    def test_pruning_session_record_iteration(self):
        """Iteration recording increments counter."""
        session = PruningSession()
        session.record_iteration()
        session.record_iteration()
        
        assert session.iteration_count == 2
    
    def test_pruning_session_record_uniqueness_failure(self):
        """Uniqueness failure recording increments counter."""
        session = PruningSession()
        session.record_uniqueness_failure()
        
        assert session.uniqueness_failures == 1
    
    def test_pruning_session_record_repair(self):
        """Repair recording increments counter."""
        session = PruningSession()
        session.record_repair()
        session.record_repair()
        
        assert session.repairs_used == 2
    
    def test_pruning_session_record_interval_contraction(self):
        """Contraction recording stores history."""
        session = PruningSession()
        state1 = IntervalState(0, 10, "test")
        state2 = IntervalState(5, 10, "test2")
        
        session.record_interval_contraction(state1)
        session.record_interval_contraction(state2)
        
        assert session.interval_contractions == 2
        assert len(session.history) == 2
        assert session.history[0].low_index == 0
        assert session.history[1].low_index == 5
    
    def test_pruning_session_to_metrics(self):
        """Session exports metrics dict."""
        session = PruningSession()
        session.record_iteration()
        session.record_uniqueness_failure()
        session.record_repair()
        
        metrics = session.to_metrics()
        
        assert metrics["pruning_iterations"] == 1
        assert metrics["uniqueness_failures"] == 1
        assert metrics["repairs_used"] == 1
        assert metrics["timeout_occurred"] is False


class TestPruningStatus:
    """Test status enum values."""
    
    def test_status_enum_values(self):
        """All expected status values present."""
        assert PruningStatus.SUCCESS.value == "success"
        assert PruningStatus.SUCCESS_WITH_REPAIRS.value == "success_with_repairs"
        assert PruningStatus.ABORTED_MAX_REPAIRS.value == "aborted_max_repairs"
        assert PruningStatus.ABORTED_TIMEOUT.value == "aborted_timeout"
