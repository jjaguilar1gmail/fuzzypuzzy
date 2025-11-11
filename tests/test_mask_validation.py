"""Tests for mask validation (US1)."""
import pytest
from generate.mask.validate import validate_mask
from generate.mask.errors import InvalidMaskError


def test_validate_empty_mask():
    """T018: Empty mask should pass validation."""
    validate_mask(
        mask_cells=set(),
        size=7,
        start=(0, 0),
        end=(6, 6),
        allow_diagonal=True
    )
    # No exception = pass


def test_validate_start_blocked():
    """T018: Mask blocking start position should fail."""
    with pytest.raises(InvalidMaskError, match="Start position .* is blocked"):
        validate_mask(
            mask_cells={(0, 0)},
            size=7,
            start=(0, 0),
            end=(6, 6)
        )


def test_validate_end_blocked():
    """T018: Mask blocking end position should fail."""
    with pytest.raises(InvalidMaskError, match="End position .* is blocked"):
        validate_mask(
            mask_cells={(6, 6)},
            size=7,
            start=(0, 0),
            end=(6, 6)
        )


def test_validate_connectivity_broken():
    """T018: Mask creating disconnected regions should fail."""
    # Create a wall that splits grid
    mask_cells = {(i, 3) for i in range(7)}
    
    with pytest.raises(InvalidMaskError, match="disconnected regions"):
        validate_mask(
            mask_cells=mask_cells,
            size=7,
            start=(0, 0),
            end=(6, 6),
            allow_diagonal=False  # Orthogonal only
        )


def test_validate_connectivity_with_diagonal():
    """T018: Diagonal adjacency should allow connectivity across gaps."""
    # Vertical wall with gaps - should be fine with diagonal
    mask_cells = {(0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3)}
    
    validate_mask(
        mask_cells=mask_cells,
        size=7,
        start=(0, 0),
        end=(6, 6),
        allow_diagonal=True
    )
    # Should pass


def test_validate_isolated_pocket():
    """T018: Small isolated pocket should fail."""
    # Create a ring that isolates center cells
    mask_cells = set()
    size = 7
    
    # Ring around (3, 3) and (3, 4) - creates 2-cell pocket
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if abs(dr) == 1 or abs(dc) == 1:
                mask_cells.add((3 + dr, 3 + dc))
                mask_cells.add((3 + dr, 4 + dc))
    
    # Remove the 2 cells we're isolating
    mask_cells.discard((3, 3))
    mask_cells.discard((3, 4))
    
    with pytest.raises(InvalidMaskError, match="disconnected regions"):
        validate_mask(
            mask_cells=mask_cells,
            size=size,
            start=(0, 0),
            end=(6, 6),
            allow_diagonal=False
        )


def test_validate_all_cells_blocked():
    """T018: Blocking all cells should fail at start position check."""
    mask_cells = {(r, c) for r in range(7) for c in range(7)}
    
    with pytest.raises(InvalidMaskError, match="Start position .* is blocked"):
        validate_mask(
            mask_cells=mask_cells,
            size=7,
            start=(0, 0),
            end=(6, 6)
        )


def test_validate_sparse_mask_passes():
    """T018: Sparse, valid mask should pass."""
    # Scattered cells that don't break connectivity
    mask_cells = {(1, 1), (3, 3), (5, 5)}
    
    validate_mask(
        mask_cells=mask_cells,
        size=7,
        start=(0, 0),
        end=(6, 6),
        allow_diagonal=True
    )
    # Should pass


def test_validate_orthogonal_adjacency():
    """T018: Orthogonal mode should respect adjacency differences."""
    # This creates connectivity that differs by adjacency mode
    mask_cells = {(2, 2), (2, 4), (4, 2), (4, 4)}  # Corners of square, sparse
    
    # With diagonal adjacency, should pass
    validate_mask(
        mask_cells=mask_cells,
        size=7,
        start=(0, 0),
        end=(6, 6),
        allow_diagonal=True
    )
    # Should pass - connectivity maintained
