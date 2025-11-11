"""Generation report writer."""

import json
from pathlib import Path
from typing import Dict
from dataclasses import dataclass, asdict


@dataclass
class GenerationReport:
    """Generation statistics and summary."""
    pack_id: str
    total_requested: int
    total_generated: int
    total_skipped: int
    total_failed: int
    difficulty_breakdown: Dict[str, Dict[str, int]]
    size_breakdown: Dict[str, int]
    average_generation_time_ms: float
    total_time_sec: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as fraction."""
        if self.total_requested == 0:
            return 0.0
        return self.total_generated / self.total_requested


def write_report(report: GenerationReport, output_file: Path, format: str = 'json'):
    """Write generation report to file.
    
    Args:
        report: GenerationReport to write
        output_file: Path to output file
        format: 'json' or 'text'
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'json':
        # Write JSON report
        report_dict = asdict(report)
        report_dict['success_rate'] = report.success_rate
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
    
    elif format == 'text':
        # Write human-readable text report
        lines = []
        lines.append("=" * 70)
        lines.append("Hidato Pack Generation Report")
        lines.append("=" * 70)
        lines.append(f"Pack ID: {report.pack_id}")
        lines.append("")
        lines.append("Summary:")
        lines.append(f"  Requested: {report.total_requested}")
        lines.append(f"  Generated: {report.total_generated}")
        lines.append(f"  Skipped:   {report.total_skipped}")
        lines.append(f"  Failed:    {report.total_failed}")
        lines.append(f"  Success:   {report.success_rate * 100:.1f}%")
        lines.append("")
        lines.append("Performance:")
        lines.append(f"  Avg time:   {report.average_generation_time_ms:.1f}ms")
        lines.append(f"  Total time: {report.total_time_sec:.2f}s")
        lines.append("")
        
        if report.difficulty_breakdown:
            lines.append("Difficulty Breakdown:")
            for diff, stats in report.difficulty_breakdown.items():
                lines.append(f"  {diff:8s}: {stats['generated']} generated, {stats['failed']} failed")
            lines.append("")
        
        if report.size_breakdown:
            lines.append("Size Distribution:")
            for size, count in report.size_breakdown.items():
                lines.append(f"  {size}×{size}: {count}")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
    
    else:
        raise ValueError(f"Unknown format: {format}")
