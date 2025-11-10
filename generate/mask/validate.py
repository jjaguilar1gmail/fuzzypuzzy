"""Mask validation utilities."""
from collections import deque
from core.position import Position
from core.grid import Grid
from .errors import InvalidMaskError


def validate_mask(mask_cells: set[tuple[int, int]], 
                  size: int,
                  start: tuple[int, int],
                  end: tuple[int, int],
                  allow_diagonal: bool = True) -> None:
    """Validate mask meets connectivity and structural requirements.
    
    Checks:
    1. All non-blocked cells form a single connected component
    2. No isolated 1-2 cell orphan pockets fully enclosed by blocks
    3. Start and end positions are not blocked
    
    Args:
        mask_cells: Set of (row, col) positions to be blocked
        size: Grid size
        start: Starting position (row, col)
        end: Ending position (row, col)
        allow_diagonal: Whether diagonal adjacency counts
        
    Raises:
        InvalidMaskError: If validation fails
    """
    # Check start/end not blocked
    if start in mask_cells:
        raise InvalidMaskError(f"Start position {start} is blocked")
    if end in mask_cells:
        raise InvalidMaskError(f"End position {end} is blocked")
    
    # Build set of valid (non-blocked) cells
    valid_cells = set()
    for r in range(size):
        for c in range(size):
            if (r, c) not in mask_cells:
                valid_cells.add((r, c))
    
    if not valid_cells:
        raise InvalidMaskError("All cells are blocked")
    
    # BFS from arbitrary valid cell to check connectivity
    visited = set()
    queue = deque([next(iter(valid_cells))])
    visited.add(queue[0])
    
    while queue:
        r, c = queue.popleft()
        
        # Check neighbors
        for dr, dc in _get_neighbor_offsets(allow_diagonal):
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                if (nr, nc) in valid_cells and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    
    # All valid cells should be reachable
    if len(visited) != len(valid_cells):
        unreachable = len(valid_cells) - len(visited)
        raise InvalidMaskError(
            f"Mask creates disconnected regions: {unreachable} cells unreachable"
        )
    
    # Check for small orphan pockets (fully enclosed 1-2 cell chambers)
    _check_orphan_pockets(valid_cells, mask_cells, size, allow_diagonal)


def _get_neighbor_offsets(allow_diagonal: bool) -> list[tuple[int, int]]:
    """Get neighbor offsets based on adjacency mode."""
    if allow_diagonal:
        return [(-1, -1), (-1, 0), (-1, 1),
                (0, -1),          (0, 1),
                (1, -1),  (1, 0),  (1, 1)]
    else:
        return [(-1, 0), (0, -1), (0, 1), (1, 0)]


def _check_orphan_pockets(valid_cells: set[tuple[int, int]],
                         mask_cells: set[tuple[int, int]],
                         size: int,
                         allow_diagonal: bool) -> None:
    """Check for isolated small chambers (1-2 cells fully enclosed by blocks).
    
    These are disallowed as they feel unfair/unnatural.
    """
    # For each valid cell, check if it's in a small isolated pocket
    checked = set()
    
    for cell in valid_cells:
        if cell in checked:
            continue
            
        # BFS to find connected component from this cell
        pocket = set()
        queue = deque([cell])
        pocket.add(cell)
        
        while queue:
            r, c = queue.popleft()
            for dr, dc in _get_neighbor_offsets(allow_diagonal):
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    if (nr, nc) in valid_cells and (nr, nc) not in pocket:
                        pocket.add((nr, nc))
                        queue.append((nr, nc))
        
        checked.update(pocket)
        
        # If pocket is small (1-2 cells) and has no escape to grid edges, reject
        if len(pocket) <= 2:
            has_edge = any(r == 0 or r == size-1 or c == 0 or c == size-1 
                          for r, c in pocket)
            if not has_edge:
                raise InvalidMaskError(
                    f"Mask creates isolated pocket of {len(pocket)} cells at {pocket}"
                )
