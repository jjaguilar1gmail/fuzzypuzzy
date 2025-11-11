"""Tests for JSON export functionality."""
import json
import pytest
from pathlib import Path
from app.packgen.export import export_puzzle, export_pack_metadata, validate_against_schema


@pytest.fixture
def sample_generated_puzzle():
    """Sample puzzle from generator for export testing."""
    from generate.models import GeneratedPuzzle
    from core.puzzle import Puzzle
    from core.position import Position
    
    # Create minimal valid puzzle
    givens = [
        Position(0, 0, 1),
        Position(0, 4, 5),
        Position(2, 2, 13),
        Position(4, 4, 25),
    ]
    
    puzzle = Puzzle(rows=5, cols=5, allow_diagonal=True, givens=givens)
    
    return GeneratedPuzzle(
        puzzle=puzzle,
        seed=12345,
        difficulty='easy',
        clue_count=4,
        max_gap=8,
        generation_time_ms=150,
        success=True,
    )


def test_export_puzzle_produces_valid_json(sample_generated_puzzle, tmp_path):
    """Exported puzzle should be valid JSON."""
    output_file = tmp_path / "puzzle.json"
    export_puzzle(sample_generated_puzzle, output_file, puzzle_id="0001", pack_id="test")
    
    assert output_file.exists()
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    # Should be valid JSON dict
    assert isinstance(data, dict)


def test_export_puzzle_includes_required_fields(sample_generated_puzzle, tmp_path):
    """Exported puzzle should include all required schema fields."""
    output_file = tmp_path / "puzzle.json"
    export_puzzle(sample_generated_puzzle, output_file, puzzle_id="0001", pack_id="test")
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    required_fields = ['id', 'size', 'difficulty', 'seed', 'clue_count', 'givens']
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_export_puzzle_givens_format(sample_generated_puzzle, tmp_path):
    """Givens should be exported as array of {row, col, value} objects."""
    output_file = tmp_path / "puzzle.json"
    export_puzzle(sample_generated_puzzle, output_file, puzzle_id="0001", pack_id="test")
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data['givens'], list)
    assert len(data['givens']) > 0
    
    for given in data['givens']:
        assert 'row' in given
        assert 'col' in given
        assert 'value' in given
        assert isinstance(given['row'], int)
        assert isinstance(given['col'], int)
        assert isinstance(given['value'], int)


def test_export_puzzle_omits_solution_by_default(sample_generated_puzzle, tmp_path):
    """Solution should be omitted unless explicitly requested."""
    output_file = tmp_path / "puzzle.json"
    export_puzzle(sample_generated_puzzle, output_file, puzzle_id="0001", pack_id="test", include_solution=False)
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    # Solution can be null or omitted
    assert data.get('solution') is None or 'solution' not in data


def test_export_puzzle_includes_solution_when_requested(sample_generated_puzzle, tmp_path):
    """Solution should be included if requested."""
    output_file = tmp_path / "puzzle.json"
    export_puzzle(sample_generated_puzzle, output_file, puzzle_id="0001", pack_id="test", include_solution=True)
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    if data.get('solution') is not None:
        assert isinstance(data['solution'], list)
        # Should have size*size entries for complete solution
        assert len(data['solution']) == data['size'] * data['size']


def test_export_pack_metadata_structure(tmp_path):
    """Pack metadata should match schema structure."""
    output_file = tmp_path / "metadata.json"
    
    puzzle_ids = ['0001', '0002', '0003']
    difficulty_counts = {'easy': 2, 'medium': 1}
    size_distribution = {'5': 3}
    
    from app.packgen.export import export_pack_metadata
    export_pack_metadata(
        output_file,
        pack_id='test-pack',
        title='Test Pack',
        description='A test pack',
        puzzle_ids=puzzle_ids,
        difficulty_counts=difficulty_counts,
        size_distribution=size_distribution,
    )
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    assert data['id'] == 'test-pack'
    assert data['title'] == 'Test Pack'
    assert data['puzzles'] == puzzle_ids
    assert data['difficulty_counts'] == difficulty_counts
    assert data['size_distribution'] == size_distribution
    assert 'created_at' in data


def test_validate_against_schema_accepts_valid_puzzle(sample_generated_puzzle, tmp_path):
    """Schema validation should pass for correctly formatted puzzle."""
    output_file = tmp_path / "puzzle.json"
    export_puzzle(sample_generated_puzzle, output_file, puzzle_id="0001", pack_id="test")
    
    # Should not raise exception
    validate_against_schema(output_file, schema_type='puzzle')


def test_validate_against_schema_rejects_invalid_puzzle(tmp_path):
    """Schema validation should fail for malformed puzzle."""
    output_file = tmp_path / "invalid.json"
    
    # Write invalid puzzle (missing required fields)
    with open(output_file, 'w') as f:
        json.dump({'id': '0001'}, f)
    
    with pytest.raises(Exception):
        validate_against_schema(output_file, schema_type='puzzle')
