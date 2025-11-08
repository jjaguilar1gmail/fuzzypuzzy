"""Ordering utilities for deterministic tie-breaking in solver."""
from core.position import Position


def position_order_key(pos: Position) -> tuple:
    """
    Generate a deterministic ordering key for positions.
    Orders by row then column ascending.
    
    Args:
        pos: Position to generate key for
        
    Returns:
        Tuple (row, col) for sorting
    """
    return (pos.row, pos.col)


def value_order_key(value: int) -> int:
    """
    Generate a deterministic ordering key for values.
    Orders values ascending.
    
    Args:
        value: Value to generate key for
        
    Returns:
        The value itself
    """
    return value


def sort_positions(positions: list[Position]) -> list[Position]:
    """
    Sort positions deterministically by row then column.
    
    Args:
        positions: List of positions to sort
        
    Returns:
        Sorted list of positions
    """
    return sorted(positions, key=position_order_key)


def sort_values(values: list[int]) -> list[int]:
    """
    Sort values deterministically ascending.
    
    Args:
        values: List of values to sort
        
    Returns:
        Sorted list of values
    """
    return sorted(values, key=value_order_key)
