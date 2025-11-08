"""
Unit tests for trace formatting utilities.

Tests concise, actionable trace output with strategy labels and counts.
"""

import pytest
from core.position import Position
from solve.solver import SolverStep
from util.trace import TraceFormatter, format_steps_summary


class TestTraceFormatter:
    """Test trace formatting utilities."""
    
    def test_format_single_step(self):
        """Test formatting a single solver step."""
        step = SolverStep(Position(0, 1), 5, "Only possible value for this cell")
        formatter = TraceFormatter()
        
        formatted = formatter.format_step(step)
        
        assert "5" in formatted
        assert "(1, 2)" in formatted or "0, 1" in formatted  # Position format may vary
        assert "Only possible value" in formatted
    
    def test_format_multiple_steps_with_grouping(self):
        """Test grouping similar steps for concise output."""
        steps = [
            SolverStep(Position(0, 0), 1, "Given"),
            SolverStep(Position(0, 1), 2, "Only possible value for this cell"),
            SolverStep(Position(0, 2), 3, "Only possible value for this cell"),
            SolverStep(Position(1, 0), 4, "Only possible position for this value"),
        ]
        
        formatter = TraceFormatter(group_similar=True)
        summary = formatter.format_steps(steps)
        
        # Should group similar reasoning and show counts
        assert "Only possible value" in summary
        assert "2 cells" in summary  # Grouped count for the two similar steps
        assert "Given" in summary
        assert "Only possible position" in summary
    
    def test_format_pruning_steps(self):
        """Test formatting pruning/elimination steps."""
        step = SolverStep(Position(2, 3), 15, "Eliminated by corridor bridging: distance-sum inequality")
        formatter = TraceFormatter()
        
        formatted = formatter.format_step(step)
        
        assert "corridor" in formatted.lower()
        assert "15" in formatted
        # Position (2,3) is 0-indexed, formats as (3, 4) in 1-indexed display
        assert "(3, 4)" in formatted
    
    def test_format_search_steps(self):
        """Test formatting search decision steps."""
        step = SolverStep(Position(1, 1), 7, "Search guess: value 7 at Position(1, 1), depth 3")
        formatter = TraceFormatter()
        
        formatted = formatter.format_step(step)
        
        assert "7" in formatted
        assert "search" in formatted.lower() or "guess" in formatted.lower()
        assert "depth" in formatted.lower()
    
    def test_limit_trace_lines(self):
        """Test limiting trace output to reasonable length."""
        # Create many steps
        steps = [
            SolverStep(Position(i % 5, i // 5), i + 1, f"Step {i}")
            for i in range(300)
        ]
        
        formatter = TraceFormatter(max_lines=200)
        summary = formatter.format_steps(steps)
        
        # Should be limited (allow a few extra for truncation message)
        lines = summary.strip().split('\n')
        assert len(lines) <= 205  # Allow for truncation message
        
        # Should indicate truncation
        if len(steps) > 200:
            assert "truncated" in summary.lower() or "..." in summary


class TestStepsSummary:
    """Test high-level summary functions."""
    
    def test_format_steps_summary_basic(self):
        """Test basic summary formatting."""
        steps = [
            SolverStep(Position(0, 0), 1, "Given"),
            SolverStep(Position(0, 1), 2, "Only possible value"),
            SolverStep(Position(0, 2), 3, "Only possible position"),
        ]
        
        summary = format_steps_summary(steps)
        
        assert isinstance(summary, str)
        assert "3" in summary or "three" in summary.lower()  # Count
        assert len(summary) > 0
    
    def test_format_steps_summary_by_strategy(self):
        """Test grouping summary by strategy."""
        steps = [
            SolverStep(Position(0, 0), 1, "Given"),
            SolverStep(Position(0, 1), 2, "Only possible value for this cell"),
            SolverStep(Position(0, 2), 3, "Only possible value for this cell"),
            SolverStep(Position(1, 0), 4, "Only possible position for this value"),
            SolverStep(Position(1, 1), 5, "Search guess: value 5 at Position(1, 1), depth 1"),
        ]
        
        summary = format_steps_summary(steps, group_by_strategy=True)
        
        # Should mention different strategies
        assert "possible value" in summary.lower() or "forced" in summary.lower()
        assert "possible position" in summary.lower() or "unique" in summary.lower()
        # Should show counts per strategy
        assert "2" in summary  # 2 "only possible value" steps
    
    def test_format_empty_steps(self):
        """Test handling empty step list."""
        summary = format_steps_summary([])
        
        assert isinstance(summary, str)
        assert "no steps" in summary.lower() or "empty" in summary.lower() or len(summary) == 0
