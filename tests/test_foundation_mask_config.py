"""Foundation tests: verify mask config flags exist and validate correctly."""
import pytest
from generate.models import GenerationConfig


def test_mask_config_flags_exist():
    """T014: Verify all mask config flags are present."""
    config = GenerationConfig(
        size=7,
        mask_enabled=True,
        mask_mode="template",
        mask_template="corridor",
        mask_density=0.05,
        mask_max_attempts=3,
        structural_repair_enabled=True,
        structural_repair_max=2,
        structural_repair_timeout_ms=400
    )
    
    assert config.mask_enabled is True
    assert config.mask_mode == "template"
    assert config.mask_template == "corridor"
    assert config.mask_density == 0.05
    assert config.mask_max_attempts == 3
    assert config.structural_repair_enabled is True
    assert config.structural_repair_max == 2
    assert config.structural_repair_timeout_ms == 400


def test_mask_mode_validation():
    """T014: Verify mask_mode validation rejects invalid values."""
    with pytest.raises(ValueError, match="mask_mode must be"):
        GenerationConfig(size=7, mask_enabled=True, mask_mode="invalid")


def test_mask_density_validation():
    """T014: Verify mask_density validation enforces 0.0-0.10 range."""
    # Valid density
    config = GenerationConfig(size=7, mask_enabled=True, mask_density=0.08)
    assert config.mask_density == 0.08
    
    # Too high
    with pytest.raises(ValueError, match="mask_density must be 0.0-0.10"):
        GenerationConfig(size=7, mask_enabled=True, mask_density=0.15)
    
    # Negative
    with pytest.raises(ValueError, match="mask_density must be 0.0-0.10"):
        GenerationConfig(size=7, mask_enabled=True, mask_density=-0.01)


def test_structural_repair_validation():
    """T014: Verify structural repair config validation."""
    # Valid config
    config = GenerationConfig(size=7, structural_repair_enabled=True, structural_repair_max=1)
    assert config.structural_repair_max == 1
    
    # Invalid max (negative)
    with pytest.raises(ValueError, match="structural_repair_max must be >= 0"):
        GenerationConfig(size=7, structural_repair_max=-1)
    
    # Invalid timeout (too low)
    with pytest.raises(ValueError, match="structural_repair_timeout_ms must be >= 100ms"):
        GenerationConfig(size=7, structural_repair_timeout_ms=50)


def test_mask_defaults():
    """T014: Verify mask defaults when not specified."""
    config = GenerationConfig(size=7)
    
    assert config.mask_enabled is False
    assert config.mask_mode == "auto"
    assert config.mask_template is None
    assert config.mask_density is None
    assert config.mask_max_attempts == 5
    assert config.structural_repair_enabled is False
    assert config.structural_repair_max == 2
    assert config.structural_repair_timeout_ms == 400
