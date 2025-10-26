"""Core domain model: Constraints

Contains the Constraints class defining puzzle constraints.
"""
from core.adjacency import Adjacency
from core.position import Position

class Constraints:
    """A class that defines the rules of the game. Contains:
    max and min values allowed in the puzzle
    allow_diagonal: bool = True
    must_be_connected: bool = True.
    blocked_allowed: bool — whether blocked cells may exist (True if you support irregular shapes).
    value_set: Optional[set[int]] — optional whitelist of allowed numbers (default: full range).
    notes: Optional[str] — human-readable rule notes (nice for exports/debug).
    
    Core responsibilities:
    in_bounds(pos: Position, rows, cols) -> bool
    Returns whether pos is inside the grid rectangle.

    neighbors(pos: Position, rows, cols) -> Iterable[Position]
    Yields neighbors per allow_diagonal. Does not skip blocked cells (the Grid/Puzzle can filter).

    valid_value(n: int) -> bool
    min_value ≤ n ≤ max_value and (if provided) n in value_set.

    valid_transition(a: Position, b: Position, rows, cols) -> bool
    Returns True iff b is an allowed neighbor of a. (Keeps adjacency logic centralized.)

    assert_consistent_with_grid(grid: Grid)
    Raises if max_value exceeds number of playable cells, or if blocked rules are violated."""
    def __init__(self, min_value: int = 1, max_value: int = 100,
                 allow_diagonal: bool = True,
                 must_be_connected: bool = True,
                 blocked_allowed: bool = True,
                 value_set: set[int] = None,
                 notes: str = ""):
        self.min_value = min_value
        self.max_value = max_value
        self.allow_diagonal = allow_diagonal
        self.must_be_connected = must_be_connected
        self.blocked_allowed = blocked_allowed
        self.value_set = value_set
        self.notes = notes
    def in_bounds(self, pos, rows, cols) -> bool:
        return 0 <= pos.row < rows and 0 <= pos.col < cols
    def valid_value(self, n: int) -> bool:
        if n < self.min_value or n > self.max_value:
            return False
        if self.value_set is not None and n not in self.value_set:
            return False
        return True
    def assert_consistent_with_grid(self, grid):
        playable_cells = sum(1 for cell in grid.iter_cells() if not cell.blocked)
        if self.max_value > playable_cells:
            raise ValueError("max_value exceeds number of playable cells in the grid.")
        if not self.blocked_allowed:
            for cell in grid.iter_cells():
                if cell.blocked:
                    raise ValueError("Blocked cells are not allowed by the constraints.")
    def valid_transition(self, a, b, rows, cols) -> bool:
        adjacency = Adjacency(self.allow_diagonal)
        neighbors = adjacency.get_neighbors(a)
        return (b.row, b.col) in neighbors and self.in_bounds(b, rows, cols)
    def neighbors(self, pos, rows, cols):
        adjacency = Adjacency(self.allow_diagonal)
        for neighbor in adjacency.get_neighbors(pos):
            if self.in_bounds(Position(*neighbor), rows, cols):
                yield Position(*neighbor)
    
