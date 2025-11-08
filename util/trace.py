"""
Trace formatting utilities for solver output.

Provides concise, actionable formatting of solver steps with:
- Strategy grouping
- Step counts
- Line limits
"""

from collections import defaultdict
from typing import List, Dict


class TraceFormatter:
    """Formats solver steps into concise, readable traces."""
    
    def __init__(self, group_similar: bool = False, max_lines: int = 200):
        """
        Initialize trace formatter.
        
        Args:
            group_similar: Whether to group similar steps together
            max_lines: Maximum number of output lines
        """
        self.group_similar = group_similar
        self.max_lines = max_lines
    
    def format_step(self, step) -> str:
        """
        Format a single solver step.
        
        Args:
            step: SolverStep object
            
        Returns:
            Formatted string representation
        """
        # Convert 0-indexed to 1-indexed for human readability
        row = step.position.row + 1
        col = step.position.col + 1
        return f"  Place {step.value} at ({row}, {col}): {step.reason}"
    
    def format_steps(self, steps: List) -> str:
        """
        Format multiple solver steps with optional grouping.
        
        Args:
            steps: List of SolverStep objects
            
        Returns:
            Formatted multi-line string
        """
        if not steps:
            return "No steps recorded."
        
        if self.group_similar:
            return self._format_grouped(steps)
        else:
            return self._format_sequential(steps)
    
    def _format_sequential(self, steps: List) -> str:
        """Format steps sequentially without grouping."""
        lines = []
        for i, step in enumerate(steps):
            if i >= self.max_lines:
                remaining = len(steps) - i
                lines.append(f"\n... ({remaining} more steps truncated)")
                break
            lines.append(self.format_step(step))
        return '\n'.join(lines)
    
    def _format_grouped(self, steps: List) -> str:
        """Format steps with similar reasoning grouped together."""
        # Group by strategy
        groups = defaultdict(list)
        for step in steps:
            strategy = self._extract_strategy(step.reason)
            groups[strategy].append(step)
        
        lines = []
        line_count = 0
        
        for strategy, group_steps in groups.items():
            if line_count >= self.max_lines:
                remaining = len(steps) - sum(len(g) for g in list(groups.values())[:line_count])
                lines.append(f"\n... ({remaining} more steps truncated)")
                break
            
            if len(group_steps) == 1:
                lines.append(self.format_step(group_steps[0]))
                line_count += 1
            else:
                lines.append(f"\n{strategy} ({len(group_steps)} cells):")
                line_count += 1
                for step in group_steps[:5]:  # Show first few examples
                    if line_count >= self.max_lines:
                        break
                    row = step.position.row + 1
                    col = step.position.col + 1
                    lines.append(f"    {step.value} at ({row}, {col})")
                    line_count += 1
                if len(group_steps) > 5:
                    lines.append(f"    ... and {len(group_steps) - 5} more")
                    line_count += 1
        
        return '\n'.join(lines)
    
    def _extract_strategy(self, reason: str) -> str:
        """Extract strategy name from reason string."""
        reason_lower = reason.lower()
        
        if "only possible value" in reason_lower:
            return "Only possible value (forced move)"
        elif "only possible position" in reason_lower:
            return "Only possible position (unique placement)"
        elif "corridor" in reason_lower:
            return "Corridor bridging elimination"
        elif "degree" in reason_lower:
            return "Degree-based pruning"
        elif "island" in reason_lower:
            return "Island elimination"
        elif "search guess" in reason_lower or "guess" in reason_lower:
            return "Search decision (backtracking)"
        elif "given" in reason_lower:
            return "Given"
        else:
            return "Other reasoning"


def format_steps_summary(steps: List, group_by_strategy: bool = False) -> str:
    """
    Format a high-level summary of solver steps.
    
    Args:
        steps: List of SolverStep objects
        group_by_strategy: Whether to break down by strategy type
        
    Returns:
        Summary string
    """
    if not steps:
        return "No steps recorded."
    
    if not group_by_strategy:
        return f"Solved in {len(steps)} steps."
    
    # Count by strategy
    formatter = TraceFormatter()
    strategy_counts = defaultdict(int)
    for step in steps:
        strategy = formatter._extract_strategy(step.reason)
        strategy_counts[strategy] += 1
    
    lines = [f"Solved in {len(steps)} steps:"]
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {strategy}: {count}")
    
    return '\n'.join(lines)


def format_validation_report(report: Dict) -> str:
    """
    Format a validation report for display.
    
    Args:
        report: Validation report dictionary with keys:
            - status: 'PASS' or 'FAIL'
            - all_filled: bool
            - givens_preserved: bool
            - contiguous_path: bool
            - values_complete: bool
            - message: str
            
    Returns:
        Formatted report string
    """
    status = report.get('status', 'UNKNOWN')
    message = report.get('message', '')
    
    if status == 'PASS':
        symbol = "✓"
        header = "VALIDATION PASSED"
    else:
        symbol = "✗"
        header = "VALIDATION FAILED"
    
    lines = [
        f"\n{'='*60}",
        f"{symbol} {header}",
        f"{'='*60}",
        f"\nValidation Checks:",
        f"  All cells filled:     {'✓' if report.get('all_filled') else '✗'}",
        f"  Givens preserved:     {'✓' if report.get('givens_preserved') else '✗'}",
        f"  Contiguous path:      {'✓' if report.get('contiguous_path') else '✗'}",
        f"  Values complete:      {'✓' if report.get('values_complete') else '✗'}",
        f"\n{message}",
        f"{'='*60}\n"
    ]
    
    return '\n'.join(lines)
