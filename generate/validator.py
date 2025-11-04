"""Generate module: Validator

Contains the Validator class for validating generated puzzles.
"""

class Validator:
    """Validates generated puzzles for correctness."""
    
    @staticmethod
    def validate_basic(puzzle):
        """Perform basic validation checks on a puzzle.
        
        Returns:
            (is_valid: bool, issues: List[str])
        """
        issues = []
        
        # Check for duplicate values
        values_seen = set()
        for cell in puzzle.grid.iter_cells():
            if cell.value is not None and not cell.blocked:
                if cell.value in values_seen:
                    issues.append(f"Duplicate value {cell.value}")
                values_seen.add(cell.value)
        
        # Check value range
        for cell in puzzle.grid.iter_cells():
            if cell.value is not None and not cell.blocked:
                if not puzzle.constraints.valid_value(cell.value):
                    issues.append(f"Value {cell.value} out of range")
        
        # Check contiguity if required
        if puzzle.constraints.must_be_connected:
            if not puzzle.verify_path_contiguity():
                issues.append("Path is not contiguous")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_solvability(puzzle):
        """Check if puzzle has at least one solution (placeholder).
        
        For MVP, just check that it's not obviously broken.
        """
        is_basic_valid, issues = Validator.validate_basic(puzzle)
        if not is_basic_valid:
            return False, issues
        
        # Additional solvability checks could go here
        # For now, assume serpentine puzzles are solvable
        return True, []
