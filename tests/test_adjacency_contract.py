"""Contract tests for Adjacency neighbor calculation."""
# import pytest
from core.adjacency import Adjacency
from core.position import Position

def test_adjacency_4_neighbors():
    """Test 4-neighbor adjacency (orthogonal only)."""
    adj = Adjacency(allow_diagonal=False)
    pos = Position(1, 1)
    
    neighbors = adj.get_neighbors(pos)
    expected = [(0, 1), (2, 1), (1, 0), (1, 2)]  # up, down, left, right
    
    assert len(neighbors) == 4
    for neighbor in expected:
        assert neighbor in neighbors

def test_adjacency_8_neighbors():
    """Test 8-neighbor adjacency (includes diagonals)."""
    adj = Adjacency(allow_diagonal=True)
    pos = Position(1, 1)
    
    neighbors = adj.get_neighbors(pos)
    expected = [
        (0, 1), (2, 1), (1, 0), (1, 2),  # orthogonal
        (0, 0), (0, 2), (2, 0), (2, 2)   # diagonal
    ]
    
    assert len(neighbors) == 8
    for neighbor in expected:
        assert neighbor in neighbors

def test_adjacency_edge_position():
    """Test adjacency at grid edges (may return out-of-bounds coords)."""
    adj = Adjacency(allow_diagonal=False)
    pos = Position(0, 0)  # Top-left corner
    
    neighbors = adj.get_neighbors(pos)
    expected = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Some out-of-bounds
    
    assert len(neighbors) == 4
    for neighbor in expected:
        assert neighbor in neighbors

def test_adjacency_consistency():
    """Test that adjacency rules are applied consistently."""
    adj4 = Adjacency(allow_diagonal=False)
    adj8 = Adjacency(allow_diagonal=True)
    pos = Position(2, 3)
    
    neighbors4 = adj4.get_neighbors(pos)
    neighbors8 = adj8.get_neighbors(pos)
    
    # 8-neighbors should include all 4-neighbors
    for neighbor in neighbors4:
        assert neighbor in neighbors8
    
    # 8-neighbors should have exactly 4 more than 4-neighbors
    assert len(neighbors8) == len(neighbors4) + 4

if __name__ == "__main__":
    test_adjacency_4_neighbors()
    test_adjacency_8_neighbors()
    test_adjacency_edge_position()
    test_adjacency_consistency()
    print("All Adjacency contract tests passed.")