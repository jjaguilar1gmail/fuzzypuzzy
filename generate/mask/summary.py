"""Summary utilities for mask metrics aggregation (T044 US3).

Aggregate mask generation metrics across multiple puzzle generations.
"""
from dataclasses import dataclass
from typing import List, Optional
from generate.mask.metrics import MaskGenerationMetrics


@dataclass
class MaskSummary:
    """Aggregated statistics for mask generation across multiple puzzles.
    
    Attributes:
        total_puzzles: Total number of puzzles analyzed
        masks_enabled_count: Number of puzzles with mask enabled
        masks_applied_count: Number of puzzles where mask was successfully applied
        avg_density: Average mask density when applied
        avg_cells_blocked: Average number of cells blocked
        avg_attempts: Average number of generation attempts
        patterns_used: Dictionary of pattern_id -> count
    """
    total_puzzles: int = 0
    masks_enabled_count: int = 0
    masks_applied_count: int = 0
    avg_density: float = 0.0
    avg_cells_blocked: float = 0.0
    avg_attempts: float = 0.0
    patterns_used: dict = None
    
    def __post_init__(self):
        if self.patterns_used is None:
            self.patterns_used = {}


def aggregate_mask_metrics(metrics_list: List[Optional[dict]]) -> MaskSummary:
    """Aggregate mask metrics from multiple puzzle generations.
    
    Args:
        metrics_list: List of mask metrics dicts (can contain None for disabled masks)
        
    Returns:
        MaskSummary with aggregated statistics
    """
    summary = MaskSummary(total_puzzles=len(metrics_list))
    
    if not metrics_list:
        return summary
    
    # Filter out None values and count enabled masks
    valid_metrics = [m for m in metrics_list if m is not None]
    summary.masks_enabled_count = len(valid_metrics)
    
    if not valid_metrics:
        return summary
    
    # Count successfully applied masks
    applied_metrics = [m for m in valid_metrics if m.get('selected', False)]
    summary.masks_applied_count = len(applied_metrics)
    
    if not applied_metrics:
        return summary
    
    # Calculate averages for applied masks
    total_density = sum(m.get('density', 0.0) for m in applied_metrics)
    total_cells = sum(m.get('cells_count', 0) for m in applied_metrics)
    total_attempts = sum(m.get('attempts', 0) for m in applied_metrics)
    
    summary.avg_density = total_density / len(applied_metrics)
    summary.avg_cells_blocked = total_cells / len(applied_metrics)
    summary.avg_attempts = total_attempts / len(applied_metrics)
    
    # Count pattern usage
    for m in applied_metrics:
        pattern_id = m.get('pattern_id')
        if pattern_id:
            summary.patterns_used[pattern_id] = summary.patterns_used.get(pattern_id, 0) + 1
    
    return summary


def format_mask_summary(summary: MaskSummary) -> str:
    """Format mask summary as human-readable string.
    
    Args:
        summary: MaskSummary to format
        
    Returns:
        Formatted string with key statistics
    """
    lines = [
        f"Mask Generation Summary ({summary.total_puzzles} puzzles)",
        f"  Masks enabled: {summary.masks_enabled_count}",
        f"  Masks applied: {summary.masks_applied_count}",
    ]
    
    if summary.masks_applied_count > 0:
        lines.extend([
            f"  Avg density: {summary.avg_density:.3f}",
            f"  Avg cells blocked: {summary.avg_cells_blocked:.1f}",
            f"  Avg attempts: {summary.avg_attempts:.1f}",
        ])
        
        if summary.patterns_used:
            lines.append("  Patterns used:")
            for pattern_id, count in sorted(summary.patterns_used.items(), key=lambda x: -x[1]):
                lines.append(f"    {pattern_id}: {count}")
    
    return "\n".join(lines)
