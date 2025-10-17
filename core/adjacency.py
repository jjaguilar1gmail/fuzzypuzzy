"""Core domain model: Adjacency

Contains the Adjacency class for adjacency relations in the puzzle.
"""

class Adjacency:
    """Centralizes adjacency rules so switching 4/8-neighbors is trivial.
    Contains fields: allow_diagonal: bool = True"""
    def __init__(self, allow_diagonal: bool = True):
        self.allow_diagonal = allow_diagonal
    def get_neighbors(self, position):
        """Returns a list of neighboring positions based on adjacency rules."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # 4-neighbors
        if self.allow_diagonal:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)] # add diagonals
        neighbors = []
        for dr, dc in directions:
            neighbors.append((position.row + dr, position.col + dc))
        return neighbors

