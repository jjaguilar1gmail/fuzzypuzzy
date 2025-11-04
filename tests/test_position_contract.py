"""Contract tests for Position equality and hash behavior."""
# import pytest
from core.position import Position

def test_position_equality():
    """Test that Position instances with same coordinates are equal."""
    pos1 = Position(1, 2)
    pos2 = Position(1, 2)
    pos3 = Position(2, 1)
    
    assert pos1 == pos2
    assert pos1 != pos3
    assert pos2 != pos3

def test_position_equality_with_none():
    """Test that Position doesn't equal None or other types."""
    pos = Position(1, 2)
    
    assert pos != None
    assert pos != "not a position"
    assert pos != (1, 2)

def test_position_hash():
    """Test that Position instances can be hashed and used in sets/dicts."""
    pos1 = Position(1, 2)
    pos2 = Position(1, 2)
    pos3 = Position(2, 1)
    
    # Same positions should have same hash
    assert hash(pos1) == hash(pos2)
    
    # Can use in set
    position_set = {pos1, pos2, pos3}
    assert len(position_set) == 2  # pos1 and pos2 are duplicates
    
    # Can use as dict key
    position_dict = {pos1: "value1", pos3: "value3"}
    assert position_dict[pos2] == "value1"  # pos2 == pos1

def test_position_repr():
    """Test that Position has a useful string representation."""
    pos = Position(1, 2)
    repr_str = repr(pos)
    
    assert "Position" in repr_str
    assert "1" in repr_str
    assert "2" in repr_str

if __name__ == "__main__":
    test_position_equality()
    test_position_equality_with_none()
    test_position_hash()
    test_position_repr()
    print("All Position contract tests passed.")