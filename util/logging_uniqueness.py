"""
Line-delimited JSON telemetry logging for uniqueness probe and spacing metrics.

Constitution compliance: structured logging, stream-friendly, deterministic.
"""
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass
class SizeTierPolicy:
    """Size-tier-specific budgets and thresholds."""
    tier_name: str
    min_cells: int
    max_cells: int
    max_nodes: int
    timeout_ms: float
    probe_count: int
    extended_factor: float = 1.5
    min_density_floor: float = 0.25
    min_spacing: float = 2.0


# Default size tier policies (from research.md D3, D8)
DEFAULT_SIZE_TIERS = [
    SizeTierPolicy("small", 1, 25, 2_000, 250, 2, 1.5, 0.34, 2.0),
    SizeTierPolicy("medium", 26, 64, 5_000, 400, 3, 1.5, 0.30, 2.8),
    SizeTierPolicy("large", 65, 100, 9_000, 600, 3, 1.5, 0.26, 3.5),
    SizeTierPolicy("very_large", 101, 9999, 9_000, 600, 3, 1.5, 0.22, 4.0),
]


def get_size_tier_policy(cells: int) -> SizeTierPolicy:
    """Get policy for given cell count."""
    for policy in DEFAULT_SIZE_TIERS:
        if policy.min_cells <= cells <= policy.max_cells:
            return policy
    return DEFAULT_SIZE_TIERS[-1]  # Fallback to very_large


class UniquenessLogger:
    """Stream-friendly logger for uniqueness probe telemetry."""
    
    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            output_path: Optional file path; if None, logs to stdout
        """
        self.output_path = output_path
        self.file_handle = None
        if output_path:
            self.file_handle = open(output_path, 'w', encoding='utf-8')
    
    def log_record(self, record: Dict[str, Any]) -> None:
        """
        Emit a line-delimited JSON record.
        
        Args:
            record: Dictionary to serialize
        """
        line = json.dumps(record, separators=(',', ':'))
        if self.file_handle:
            self.file_handle.write(line + '\n')
            self.file_handle.flush()
        else:
            print(line)
    
    def log_removal_attempt(self, attempt_log: Any) -> None:
        """Log a removal attempt with probe outcomes."""
        # Convert dataclass to dict
        record = asdict(attempt_log) if hasattr(attempt_log, '__dataclass_fields__') else attempt_log
        record['timestamp'] = time.time()
        record['type'] = 'removal_attempt'
        self.log_record(record)
    
    def log_summary(self, summary: Dict[str, Any]) -> None:
        """Log final generation summary."""
        summary['timestamp'] = time.time()
        summary['type'] = 'summary'
        self.log_record(summary)
    
    def close(self) -> None:
        """Close file handle if open."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
