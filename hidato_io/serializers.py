"""I/O adapters: Serializers

Contains the Serializers class for JSON/YAML serialization.
"""
import json
from datetime import datetime

def to_json(puzzle, metadata=None):
    """Converts a Puzzle to JSON string with optional metadata."""
    data = puzzle.to_dict()
    if metadata:
        data["metadata"] = metadata
    if "metadata" not in data:
        data["metadata"] = {}
    data["metadata"]["exported_at"] = datetime.now().isoformat()
    return json.dumps(data, indent=2)

def from_json(json_string):
    """Creates a Puzzle from JSON string. Returns (puzzle, metadata)."""
    from core.puzzle import Puzzle
    from core.grid import Grid
    from core.constraints import Constraints
    
    data = json.loads(json_string)
    puzzle = Puzzle(Grid(1, 1), Constraints())  # Temporary
    puzzle.from_dict(data)
    metadata = data.get("metadata", {})
    return puzzle, metadata

def save_json(puzzle, filepath, metadata=None):
    """Saves puzzle to JSON file."""
    with open(filepath, 'w') as f:
        f.write(to_json(puzzle, metadata))

def load_json(filepath):
    """Loads puzzle from JSON file. Returns (puzzle, metadata)."""
    with open(filepath, 'r') as f:
        return from_json(f.read())

class Serializers:
    """A placeholder Serializers class for serialization adapters."""
    pass
