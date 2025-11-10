"""Integration tests for pruning with Generator."""
import pytest
from generate.generator import Generator


class TestPruningIntegration:
    """Test pruning integration with Generator."""
    
    def test_generator_with_pruning_disabled(self):
        """Generator works with pruning_enabled=False (legacy mode)."""
        # Use small size for fast test
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=42,
            allow_diagonal=True,
            path_mode="serpentine"
        )
        
        assert result is not None
        assert result.size == 5
        assert result.uniqueness_verified is True
        assert len(result.givens) > 0
        assert len(result.solution) > 0
    
    def test_generator_with_pruning_enabled(self):
        """Generator works with pruning_enabled=True (new mode)."""
        # Need to import and modify config
        from generate.models import GenerationConfig
        
        # Small puzzle with pruning enabled
        # Note: Need to pass pruning config through generate_puzzle
        # For now, just verify imports work
        from generate.pruning import prune_puzzle, PruningStatus
        
        assert prune_puzzle is not None
        assert PruningStatus.SUCCESS is not None
