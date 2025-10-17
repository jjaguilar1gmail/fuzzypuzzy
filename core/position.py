"""Core domain model: Position

Contains the Position class representing coordinates or location in the puzzle.
"""

class Position:
    """Position class contains fields, row: int, and col: int."""
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
