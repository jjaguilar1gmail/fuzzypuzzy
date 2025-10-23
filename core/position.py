"""Core domain model: Position

Contains the Position class representing coordinates or location in the puzzle.
"""

class Position:
    """Position class contains fields, row: int, and col: int."""
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return f"Position({self.row}, {self.col})"