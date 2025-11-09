"""Test partial path acceptance (T037-T039)."""
import pytest
from generate.generator import Generator


class TestPartialAcceptance:
    """Test partial coverage acceptance with blocked cells."""
    
    def test_partial_acceptance_blocks_remainder(self):
        """When partial path accepted, remainder cells are blocked."""
        # Note: Since our current path modes always achieve 100% coverage,
        # this test documents the expected behavior when partial acceptance is triggered
        
        # Generate with standard mode (should be 100% coverage)
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=42,
            allow_diagonal=True,
            path_mode="serpentine",
            allow_partial_paths=True,
            min_cover_ratio=0.85
        )
        
        # Should have full solution (no partial acceptance needed)
        assert len(result.solution) == 25
        
    def test_min_cover_ratio_validation(self):
        """Config validates min_cover_ratio range."""
        from generate.models import GenerationConfig
        
        # Valid ratios
        config = GenerationConfig(size=5, min_cover_ratio=0.85)
        assert config.min_cover_ratio == 0.85
        
        config = GenerationConfig(size=5, min_cover_ratio=0.50)
        assert config.min_cover_ratio == 0.50
        
        # Invalid ratios
        with pytest.raises(ValueError, match="min_cover_ratio"):
            GenerationConfig(size=5, min_cover_ratio=0.40)  # Too low
        
        with pytest.raises(ValueError, match="min_cover_ratio"):
            GenerationConfig(size=5, min_cover_ratio=1.1)  # Too high
    
    def test_allow_partial_paths_flag(self):
        """allow_partial_paths flag is respected in config."""
        from generate.models import GenerationConfig
        
        config1 = GenerationConfig(size=5, allow_partial_paths=False)
        assert config1.allow_partial_paths == False
        
        config2 = GenerationConfig(size=5, allow_partial_paths=True)
        assert config2.allow_partial_paths == True
    
    def test_path_time_ms_validation(self):
        """path_time_ms validates minimum value."""
        from generate.models import GenerationConfig
        
        # Valid
        config = GenerationConfig(size=5, path_time_ms=1000)
        assert config.path_time_ms == 1000
        
        config = GenerationConfig(size=5, path_time_ms=None)
        assert config.path_time_ms is None
        
        # Invalid
        with pytest.raises(ValueError, match="path_time_ms"):
            GenerationConfig(size=5, path_time_ms=50)  # Too low
    
    def test_path_build_result_structure(self):
        """PathBuildResult returns expected structure."""
        from core.grid import Grid
        from generate.path_builder import PathBuilder
        from util.rng import RNG
        
        rng = RNG(42)
        grid = Grid(5, 5, allow_diagonal=True)
        
        result = PathBuilder.build(grid, mode="serpentine", rng=rng, blocked=None)
        
        # Check structure
        assert hasattr(result, 'ok')
        assert hasattr(result, 'reason')
        assert hasattr(result, 'coverage')
        assert hasattr(result, 'positions')
        assert hasattr(result, 'metrics')
        
        # Check values
        assert result.ok == True
        assert result.reason == "success"
        assert result.coverage == 1.0
        assert len(result.positions) == 25
        assert "path_build_ms" in result.metrics


class TestPartialAcceptanceIntegration:
    """Integration tests for partial path acceptance."""
    
    def test_generation_with_partial_paths_enabled(self):
        """Generation works with allow_partial_paths=True."""
        result = Generator.generate_puzzle(
            size=6,
            difficulty="medium",
            seed=99,
            path_mode="backbite_v1",
            allow_partial_paths=True,
            min_cover_ratio=0.80
        )
        
        # Should complete successfully
        assert result.size == 6
        assert result.uniqueness_verified
        assert len(result.solution) >= 29  # At least 80% of 36
    
    def test_generation_with_tight_coverage_threshold(self):
        """High min_cover_ratio still allows generation."""
        result = Generator.generate_puzzle(
            size=5,
            difficulty="easy",
            seed=123,
            path_mode="serpentine",
            allow_partial_paths=True,
            min_cover_ratio=0.95
        )
        
        # Should achieve full coverage with serpentine
        assert len(result.solution) == 25
