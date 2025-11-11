"""JSON export functions for puzzles and pack metadata."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from generate.models import GeneratedPuzzle


def export_puzzle(
    puzzle: GeneratedPuzzle,
    output_file: Path,
    puzzle_id: str,
    pack_id: str,
    include_solution: bool = False,
):
    """Export a generated puzzle to JSON format matching contract schema.
    
    Args:
        puzzle: GeneratedPuzzle from engine
        output_file: Path to write JSON file
        puzzle_id: Unique puzzle identifier within pack
        pack_id: Parent pack identifier
        include_solution: Whether to include full solution
    """
    # Extract givens from puzzle (GeneratedPuzzle.givens is list of (row, col, value))
    givens = []
    for row, col, value in puzzle.givens:
        givens.append({
            'row': row,
            'col': col,
            'value': value,
        })
    
    # Build puzzle JSON
    puzzle_json = {
        'schema_version': '1.0',
        'id': puzzle_id,
        'pack_id': pack_id,
        'size': puzzle.size,
        'difficulty': puzzle.difficulty_label,
        'seed': puzzle.seed,
        'clue_count': puzzle.clue_count,
        'max_gap': None,  # Not directly available in GeneratedPuzzle
        'givens': givens,
    }
    
    # Include solution if requested
    if include_solution and puzzle.solution:
        solution = []
        for row, col, value in puzzle.solution:
            solution.append({
                'row': row,
                'col': col,
                'value': value,
            })
        puzzle_json['solution'] = solution
    else:
        puzzle_json['solution'] = None
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(puzzle_json, f, indent=2)


def export_pack_metadata(
    output_file: Path,
    pack_id: str,
    title: str,
    description: str | None,
    puzzle_ids: List[str],
    difficulty_counts: Dict[str, int],
    size_distribution: Dict[str, int],
):
    """Export pack metadata to JSON format matching contract schema.
    
    Args:
        output_file: Path to write metadata.json
        pack_id: Unique pack identifier
        title: Human-readable pack title
        description: Optional pack description
        puzzle_ids: List of puzzle IDs in this pack
        difficulty_counts: Count per difficulty level
        size_distribution: Count per grid size
    """
    metadata = {
        'schema_version': '1.0',
        'id': pack_id,
        'title': title,
        'puzzles': puzzle_ids,
        'difficulty_counts': difficulty_counts,
        'size_distribution': size_distribution,
        'created_at': datetime.utcnow().isoformat() + 'Z',
    }
    
    if description:
        metadata['description'] = description
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def validate_against_schema(file_path: Path, schema_type: str):
    """Validate exported JSON against schema.
    
    Args:
        file_path: Path to JSON file
        schema_type: 'puzzle' or 'pack'
        
    Raises:
        Exception if validation fails
    """
    # Load the file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Basic validation (full schema validation would require jsonschema library)
    if schema_type == 'puzzle':
        required_fields = ['id', 'size', 'difficulty', 'seed', 'clue_count', 'givens']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate givens format
        if not isinstance(data['givens'], list):
            raise ValueError("Givens must be an array")
        
        for given in data['givens']:
            if not all(k in given for k in ['row', 'col', 'value']):
                raise ValueError("Each given must have row, col, value")
    
    elif schema_type == 'pack':
        required_fields = ['id', 'title', 'puzzles', 'created_at']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(data['puzzles'], list):
            raise ValueError("Puzzles must be an array")
    
    else:
        raise ValueError(f"Unknown schema type: {schema_type}")
