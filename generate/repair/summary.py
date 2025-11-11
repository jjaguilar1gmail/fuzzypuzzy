"""Summary utilities for repair metrics aggregation (T045 US3).

Aggregate ambiguity repair metrics across multiple puzzle generations.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RepairSummary:
    """Aggregated statistics for repair operations across multiple puzzles.
    
    Attributes:
        total_puzzles: Total number of puzzles analyzed
        repair_enabled_count: Number of puzzles with repair enabled
        repair_attempted_count: Number of puzzles where repair was attempted
        repair_succeeded_count: Number of puzzles where repair restored uniqueness
        total_structural_blocks: Total structural blocks applied
        total_clue_fallbacks: Total clue fallbacks used
        avg_ambiguity_regions: Average number of ambiguity regions detected
        avg_repair_time_ms: Average repair time in milliseconds
        success_rate: Percentage of successful repairs
    """
    total_puzzles: int = 0
    repair_enabled_count: int = 0
    repair_attempted_count: int = 0
    repair_succeeded_count: int = 0
    total_structural_blocks: int = 0
    total_clue_fallbacks: int = 0
    avg_ambiguity_regions: float = 0.0
    avg_repair_time_ms: float = 0.0
    success_rate: float = 0.0


def aggregate_repair_metrics(metrics_list: List[Optional[dict]]) -> RepairSummary:
    """Aggregate repair metrics from multiple puzzle generations.
    
    Args:
        metrics_list: List of repair metrics dicts (can contain None for disabled repair)
        
    Returns:
        RepairSummary with aggregated statistics
    """
    summary = RepairSummary(total_puzzles=len(metrics_list))
    
    if not metrics_list:
        return summary
    
    # Filter out None values and count enabled repairs
    valid_metrics = [m for m in metrics_list if m is not None]
    summary.repair_enabled_count = len(valid_metrics)
    
    if not valid_metrics:
        return summary
    
    # Count attempted repairs (where attempts > 0)
    attempted_metrics = [m for m in valid_metrics if m.get('attempts', 0) > 0]
    summary.repair_attempted_count = len(attempted_metrics)
    
    if not attempted_metrics:
        return summary
    
    # Count successful repairs
    succeeded_metrics = [m for m in attempted_metrics if m.get('uniqueness_restored', False)]
    summary.repair_succeeded_count = len(succeeded_metrics)
    
    # Sum totals
    summary.total_structural_blocks = sum(m.get('structural_blocks_applied', 0) for m in attempted_metrics)
    summary.total_clue_fallbacks = sum(m.get('clue_fallbacks_used', 0) for m in attempted_metrics)
    
    # Calculate averages
    total_regions = sum(m.get('ambiguity_regions_detected', 0) for m in attempted_metrics)
    total_time = sum(m.get('repair_time_ms', 0.0) for m in attempted_metrics)
    
    summary.avg_ambiguity_regions = total_regions / len(attempted_metrics)
    summary.avg_repair_time_ms = total_time / len(attempted_metrics)
    
    # Calculate success rate
    if summary.repair_attempted_count > 0:
        summary.success_rate = (summary.repair_succeeded_count / summary.repair_attempted_count) * 100
    
    return summary


def format_repair_summary(summary: RepairSummary) -> str:
    """Format repair summary as human-readable string.
    
    Args:
        summary: RepairSummary to format
        
    Returns:
        Formatted string with key statistics
    """
    lines = [
        f"Repair Summary ({summary.total_puzzles} puzzles)",
        f"  Repair enabled: {summary.repair_enabled_count}",
        f"  Repair attempted: {summary.repair_attempted_count}",
    ]
    
    if summary.repair_attempted_count > 0:
        lines.extend([
            f"  Repair succeeded: {summary.repair_succeeded_count} ({summary.success_rate:.1f}%)",
            f"  Total structural blocks: {summary.total_structural_blocks}",
            f"  Total clue fallbacks: {summary.total_clue_fallbacks}",
            f"  Avg ambiguity regions: {summary.avg_ambiguity_regions:.1f}",
            f"  Avg repair time: {summary.avg_repair_time_ms:.1f}ms",
        ])
    
    return "\n".join(lines)
