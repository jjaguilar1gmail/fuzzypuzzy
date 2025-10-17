"""Core domain model: Cell

Contains the Cell class representing a single cell in the puzzle.
"""
from core.position import Position
from core.adjacency import Adjacency

class Cell:
    """Defines a single grid cell, contains fields:
    pos: Position
    value: Optional[int]
    blocked: bool = False
    given: bool = False."""
    def __init__(self, pos=Position, value=None, blocked=False, given=False):
        self.pos = pos # Position object
        self.value = value # None if empty, else an integer value
        self.blocked = blocked # True if the cell is blocked (not usable)
        self.given = given # True if the cell's value is a given clue
    def is_empty(self):
        return self.value is None and not self.blocked
    def is_filled(self):
        return self.value is not None and not self.blocked
    def is_adjacent_to(self, other: "Cell", allow_diagonal: bool = True):
        """Check if this cell is adjacent to another cell based on adjacency rules."""
        adjacency_rules = Adjacency(allow_diagonal)
        neighbors = adjacency_rules.get_neighbors(self.pos)
        return (other.pos.row, other.pos.col) in neighbors
    
