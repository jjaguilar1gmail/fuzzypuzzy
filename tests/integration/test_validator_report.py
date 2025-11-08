"""
Integration tests for final validator report.

Tests that solved puzzles produce PASS reports with:
- Givens preserved
- All values 1..N present
- Contiguous path (consecutive values adjacent)
"""

import json
from pathlib import Path
import pytest
from core.position import Position
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver, validate_solution


class TestValidatorReport:
    """Test final validation reporting."""
    
    @pytest.fixture
    def solved_canonical_5x5(self):
        """Load and solve canonical 5x5 puzzle."""
        fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
        constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
        puzzle = Puzzle(grid, constraints)
        
        # Store givens for validation
        givens = {}
        for given in data['givens']:
            pos = Position(given['row'], given['col'])
            grid.set_cell_value(pos, given['value'])
            grid.get_cell(pos).given = True
            givens[pos] = given['value']
        
        # Solve
        result = Solver.solve(puzzle, mode='logic_v3')
        assert result.solved, "Fixture should solve"
        
        return puzzle, givens
    
    def test_validator_reports_pass_for_solved_puzzle(self, solved_canonical_5x5):
        """Test that validator reports PASS for correctly solved puzzle."""
        puzzle, original_givens = solved_canonical_5x5
        
        report = validate_solution(puzzle, original_givens)
        
        assert report['status'] == 'PASS'
        assert report['all_filled'] is True
        assert report['givens_preserved'] is True
        assert report['contiguous_path'] is True
        assert report['values_complete'] is True
    
    def test_validator_checks_givens_preserved(self, solved_canonical_5x5):
        """Test that validator detects if givens were changed."""
        puzzle, original_givens = solved_canonical_5x5
        
        # Corrupt a given
        for pos, value in original_givens.items():
            cell = puzzle.grid.get_cell(pos)
            cell.value = value + 1  # Change given value
            break
        
        report = validate_solution(puzzle, original_givens)
        
        assert report['status'] == 'FAIL'
        assert report['givens_preserved'] is False
        assert 'given' in report['message'].lower()
    
    def test_validator_checks_all_cells_filled(self):
        """Test that validator detects unfilled cells."""
        # Create puzzle with some empty cells
        fixture_path = Path(__file__).parent / "fixtures" / "canonical_5x5.json"
        with open(fixture_path, 'r') as f:
            data = json.load(f)
        
        grid = Grid(data['rows'], data['cols'], allow_diagonal=(data['adjacency'] == '8'))
        constraints = Constraints(data['min_value'], data['max_value'], data['adjacency'])
        puzzle = Puzzle(grid, constraints)
        
        givens = {}
        for given in data['givens']:
            pos = Position(given['row'], given['col'])
            grid.set_cell_value(pos, given['value'])
            grid.get_cell(pos).given = True
            givens[pos] = given['value']
        
        # Don't solve - leave empty
        report = validate_solution(puzzle, givens)
        
        assert report['status'] == 'FAIL'
        assert report['all_filled'] is False
        assert 'empty' in report['message'].lower() or 'filled' in report['message'].lower()
    
    def test_validator_checks_contiguous_path(self, solved_canonical_5x5):
        """Test that validator detects non-contiguous path."""
        puzzle, original_givens = solved_canonical_5x5
        
        # Break contiguity by swapping two non-adjacent cells
        # Find two cells that are not neighbors
        cells_with_values = [(cell.pos, cell.value) for cell in puzzle.grid.iter_cells() 
                            if cell.value is not None and not cell.given]
        
        if len(cells_with_values) >= 2:
            pos1, val1 = cells_with_values[0]
            pos2, val2 = cells_with_values[1]
            
            # Swap values
            puzzle.grid.get_cell(pos1).value = val2
            puzzle.grid.get_cell(pos2).value = val1
            
            report = validate_solution(puzzle, original_givens)
            
            # Might fail on contiguity or values_complete depending on swap
            assert report['status'] == 'FAIL'
    
    def test_validator_checks_values_complete(self, solved_canonical_5x5):
        """Test that validator detects missing/duplicate values."""
        puzzle, original_givens = solved_canonical_5x5
        
        # Create duplicate by changing a non-given cell
        for cell in puzzle.grid.iter_cells():
            if not cell.given and cell.value is not None:
                cell.value = 1  # Create duplicate of min value
                break
        
        report = validate_solution(puzzle, original_givens)
        
        assert report['status'] == 'FAIL'
        assert report['values_complete'] is False or report['contiguous_path'] is False
    
    def test_validator_report_format(self, solved_canonical_5x5):
        """Test that validator report has expected format."""
        puzzle, original_givens = solved_canonical_5x5
        
        report = validate_solution(puzzle, original_givens)
        
        # Check required keys
        assert 'status' in report
        assert 'all_filled' in report
        assert 'givens_preserved' in report
        assert 'contiguous_path' in report
        assert 'values_complete' in report
        assert 'message' in report
        
        # Status should be PASS or FAIL
        assert report['status'] in ['PASS', 'FAIL']
        
        # Message should be a string
        assert isinstance(report['message'], str)
        assert len(report['message']) > 0
    
    def test_validator_report_message_descriptive(self, solved_canonical_5x5):
        """Test that PASS message is clear and descriptive."""
        puzzle, original_givens = solved_canonical_5x5
        
        report = validate_solution(puzzle, original_givens)
        
        assert report['status'] == 'PASS'
        # Should mention key validations
        message = report['message'].lower()
        assert 'valid' in message or 'pass' in message or 'success' in message
